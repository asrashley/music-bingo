"""
Holder for global database objects
"""

from contextlib import contextmanager
from functools import wraps
import secrets
import threading
from typing import (
    ContextManager, Generator, List, Optional,
    Tuple, cast
)

import sqlalchemy  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.orm.session import Session, close_all_sessions  # type: ignore

from musicbingo.options import DatabaseOptions
from .base import Base
from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .modelmixin import ModelMixin
from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .song import Song
from .token import Token
from .track import Track
from .user import User

class SchemaVersions:
    TABLES = [User, Token, Directory, Song, Game, Track, BingoTicket, BingoTicketTrack]
    def __init__(self):
        for table in self.TABLES:
            setattr(self, table.__tablename__, 0)

    def tables(self) -> List[str]:
        """returns list of table names"""
        return [tbl.__tablename__ for tbl in self.TABLES] # type: ignore

    def versions(self) -> List[Tuple]:
        """
        Return list of each table with its version
        """
        versions: List[Tuple] = []
        for table in self.TABLES:
            versions.append((table, getattr(self, table.__tablename__))) # type: ignore
        return versions

    def __repr__(self) -> str:
        versions = []
        for key, value in self.__dict__.items():
            versions.append(f'{key}={value}')
        return 'SchemaVersions(' + ','.join(versions) + ')'


class DatabaseConnection:
    _bind_lock = threading.RLock()
    _connection: Optional["DatabaseConnection"] = None

    @classmethod
    def bind(cls, opts: DatabaseOptions, create_tables=True, engine=None, debug=False):
        """
        setup database to be able to use it
        """
        with DatabaseConnection._bind_lock:
            if DatabaseConnection._connection is not None:
                return
            self = DatabaseConnection(opts, create_tables=create_tables,
                                      engine=engine, debug=debug)
            DatabaseConnection._connection = self
            self.connect()

    def __init__(self, settings: DatabaseOptions, create_tables: bool,
                 engine: Optional[sqlalchemy.engine.Engine],
                 debug: bool):
        self.settings = settings
        self.debug = debug
        self.engine = engine
        self.Session: Optional[Session] = None
        self.schema = SchemaVersions()
        self.create_tables = create_tables

    def connect(self):
        """
        Connect to database, create tables and migrate existing tables.
        """
        if self.engine is None:
            bind_args = self.settings.to_dict()
            connect_str = self.settings.connection_string()
            print(f'bind database: {connect_str}')
            if self.debug:
                self.engine = sqlalchemy.create_engine(connect_str, pool_pre_ping=True, echo=True)
            else:
                self.engine = sqlalchemy.create_engine(connect_str, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        self.detect_schema_versions()
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)
        with self.session_scope() as session:
            self.create_and_migrate_tables(session)
            if self.debug:
                SchemaVersion.show(session)
            session.commit()

    @classmethod
    def close(cls):
        """
        Close all connections to database and release DatabaseConnection object.
        """
        with DatabaseConnection._bind_lock:
            if DatabaseConnection._connection is None:
                return
            close_all_sessions()
            if DatabaseConnection._connection.engine is not None:
                DatabaseConnection._connection.engine.dispose()
            DatabaseConnection._connection = None

    def create_and_migrate_tables(self, session):
        """
        Create all tables and apply any migrations
        """
        if self.debug:
            SchemaVersion.show(session)
        for table in SchemaVersions.TABLES:
            ver = session.query(SchemaVersion).filter_by(table=table.__name__).one_or_none()
            if ver is not None:
                setattr(self.schema, table.__name__, ver.version)
        if self.debug:
            print(self.schema)
        statements = []
        for table in SchemaVersions.TABLES:
            version = getattr(self.schema, table.__tablename__)
            #if version == 0 and self.schema.SongBase == 1 and table in [Song, Track]:
            #    version = 1
            if version > 0 and version < table.__schema_version__:
                insp = sqlalchemy.inspect(self.engine)
                existing_columns = set({col['name'] for col in insp.get_columns(table.__tablename__)})
                mapper = sqlalchemy.inspect(table)
                column_types = {}
                for col in mapper.columns:
                    column_types[col.key] = col
                if self.debug:
                    print(f'Migrate {table.__tablename__}')
                statements += table.migrate_schema(self.engine, existing_columns, column_types, version)
        for cmd in statements:
            print(cmd)
            session.execute(cmd)
        session.flush()
        for table, version in self.schema.versions():
            if version > 0 and version < table.__schema_version__:
                table.migrate_data(session, version)
        session.flush()
        for table, version in self.schema.versions():
            ver = session.query(SchemaVersion).filter_by(table=table.__tablename__).one_or_none()
            if ver is None:
                ver = SchemaVersion(table=table.__tablename__, version=table.__schema_version__)
                session.add(ver)
            else:
                ver.version = table.__schema_version__

    def detect_schema_versions(self):
        insp = sqlalchemy.inspect(self.engine)
        tables = insp.get_table_names()
        if self.debug:
            print('Found tables:', tables)
        if 'SongBase' in tables and 'Track' not in tables:
            for name in self.schema.tables():
                if name in tables:
                    setattr(self.schema, name, 1)
            self.schema.Track = 1
            self.schema.Song = 1
        else:
            for name in self.schema.tables():
                if name in tables:
                    setattr(self.schema, name, 2)
            self.schema.SongBase = 0

    def create_superuser(self):
        with self.session_scope() as session:
            admin = User.get(session, username="admin")
            if admin is not None:
                return
            password = secrets.token_urlsafe(14)
            groups_mask = Group.admin.value + Group.users.value
            admin = User(username="admin", email="admin@music.bingo",
                         groups_mask=groups_mask,
                         password=User.hash_password(password))
            # TODO: investigate why groups_mask not working when
            # creating admin account
            admin.set_groups([Group.admin, Group.users])
            session.add(admin) # pylint: disable=no-member
            print(
                f'Created admin account "{admin.username}" ({admin.email}) with password "{password}"')

    @contextmanager
    def session_scope(self) -> Generator[DatabaseSession, None, None]:
        """Provide a transactional scope around a series of operations."""
        assert self.Session is not None
        session = cast(DatabaseSession, self.Session())
        try:
            yield session
            session.commit() # pylint: disable=no-member
        except BaseException:
            session.rollback() # pylint: disable=no-member
            raise
        finally:
            session.close() # pylint: disable=no-member


def session_scope() -> ContextManager[DatabaseSession]:
    """Provide a transactional scope around a series of operations."""
    assert DatabaseConnection._connection is not None
    return DatabaseConnection._connection.session_scope()


def db_session(func):
    """decorator for functions that need a database session"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        assert DatabaseConnection._connection is not None
        conn = DatabaseConnection._connection
        with conn.session_scope() as session:
            return func(*args, session, **kwargs)
    return decorated_function
