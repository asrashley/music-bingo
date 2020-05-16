"""
Holder for global database objects
"""

from contextlib import contextmanager
from functools import wraps
import os
import secrets
import threading
from typing import Generator, List, NewType, Optional

import sqlalchemy  # type: ignore
from sqlalchemy.orm import mapper  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.orm.session import close_all_sessions  # type: ignore

from musicbingo.options import DatabaseOptions
from .base import Base
from .bingoticket import BingoTicket
from .directory import Directory
from .game import Game
from .modelmixin import ModelMixin
from .song import Song
from .track import Track
from .user import User

DatabaseSession = NewType('DatabaseSession', object)  # sqlalchemy.orm.session.Session)


class SchemaVersion(Base, ModelMixin):
    __tablename__ = 'SchemaVersion'
    __plural__ = 'SchemaVersions'

    table = sqlalchemy.Column(sqlalchemy.String(32), primary_key=True, nullable=False)
    version = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    # def __init__(self, table: str, version: int):
    #    self.table = table
    #    self.version = version


class SchemaVersions:
    def __init__(self):
        self.User = 0
        self.Directory = 0
        self.Song = 0
        self.SongBase = 0
        self.Game = 0
        self.Track = 0
        self.BingoTicket = 0

    def tables(self) -> List[str]:
        """returns list of table names"""
        return list(self.__dict__.keys())

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
        self.Session: Optional[sqlalchemy.Session] = None
        self.schema = SchemaVersions()
        self.create_tables = create_tables

    def connect(self):
        """
        Connect to database, create tables and migrate existing tables.
        """
        if self.engine is None:
            bind_args = self.settings.to_dict()
            connect_str = self.settings.connection_string();
            if self.debug:
                print(f'bind database: {connect_str}')
                self.engine = sqlalchemy.create_engine(connect_str, echo=True)
            else:
                self.engine = sqlalchemy.create_engine(connect_str)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)
        with self.engine.begin() as conn:
            with self.session_scope() as session:
                self.detect_schema_versions(conn, session)
                self.create_and_migrate_tables(conn, session)
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

    def create_and_migrate_tables(self, connection, session):
        """
        Create all tables and apply any migrations
        """
        tables = [User, Directory, Song, Game, Track, BingoTicket]
        Base.metadata.create_all(connection)
        if self.debug:
            SchemaVersion.show(session)
        for table in tables:
            ver = session.query(SchemaVersion).filter_by(table=table.__name__).one_or_none()
            if ver is not None:
                setattr(self.schema, table.__name__, ver.version)
        if self.debug:
            print(self.schema)
        statements = []
        for table in tables:
            version = getattr(self.schema, table.__name__)
            if version == 0 and self.schema.SongBase == 1 and table in [Song, Track]:
                version = 1
            if version > 0 and version < table.__schema_version__:
                mapper = sqlalchemy.inspect(table)
                columns = {}
                for col in mapper.columns:  # insp.get_columns(table.__name__):
                    columns[col.key] = col
                statements += table.migrate(self.engine, columns, version)
        for cmd in statements:
            print(cmd)
            session.execute(cmd)
        for table in tables:
            ver = session.query(SchemaVersion).filter_by(table=table.__name__).one_or_none()
            if ver is None:
                ver = SchemaVersion(table=table.__name__, version=table.__schema_version__)
                session.add(ver)
            else:
                ver.version = table.__schema_version__

    def detect_schema_versions(self, connection, session):
        insp = sqlalchemy.inspect(self.engine)
        tables = insp.get_table_names()
        if self.debug:
            print('Found tables:', tables)
        if 'SongBase' in tables and 'Track' not in tables:
            for name in self.schema.tables():
                if name in tables:
                    setattr(self.schema, name, 1)
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
            session.add(admin)
            print(
                f'Created admin account "{admin.username}" ({admin.email}) with password "{password}"')

    @contextmanager
    def session_scope(self) -> Generator[DatabaseSession, None, None]:
        """Provide a transactional scope around a series of operations."""
        assert self.Session is not None
        session = self.Session()
        try:
            yield session
            session.commit()
        except BaseException:
            session.rollback()
            raise
        finally:
            session.close()


def session_scope():
    assert DatabaseConnection._connection is not None
    return DatabaseConnection._connection.session_scope()


def db_session(func):
    """decorator for functions that need a database session"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        assert DatabaseConnection._connection is not None
        conn = DatabaseConnection._connection
        with conn.session_scope() as session:
            return func(*args, session=session, **kwargs)
    return decorated_function
