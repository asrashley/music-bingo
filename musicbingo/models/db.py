"""
Holder for global database objects
"""

from contextlib import contextmanager
from functools import wraps
import logging
import secrets
import threading
# import traceback
from typing import ContextManager, Generator, Optional, cast

import sqlalchemy  # type: ignore
from sqlalchemy.orm import sessionmaker, scoped_session  # type: ignore
from sqlalchemy.orm.session import Session, close_all_sessions  # type: ignore

from musicbingo.options import DatabaseOptions
from .album import Album
from .artist import Artist
from .base import Base
from .bingoticket import BingoTicket, BingoTicketTrack
from .directory import Directory
from .game import Game
from .group import Group
from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .song import Song
from .token import Token
from .track import Track
from .user import User

class DatabaseConnection:
    """
    Class to handle database connection, table creation, Schema migration and
    sessions.
    """
    TABLES = [User, Token, Directory, Album, Artist, Song, Game, Track,
              BingoTicket, BingoTicketTrack]

    _bind_lock = threading.RLock()
    _connection: Optional["DatabaseConnection"] = None

    @classmethod
    def bind(cls, opts: DatabaseOptions, create_tables=True, engine=None,
             debug=False, echo=False, create_superuser=False):
        """
        setup database to be able to use it
        """
        with DatabaseConnection._bind_lock:
            if DatabaseConnection._connection is not None:
                return
            self = DatabaseConnection(opts, create_tables=create_tables,
                                      engine=engine, debug=debug, echo=echo)
            DatabaseConnection._connection = self
            self.connect(create_superuser)

    def __init__(self, settings: DatabaseOptions, create_tables: bool,
                 engine: Optional[sqlalchemy.engine.Engine],
                 debug: bool = False, echo: bool = False):
        self.settings = settings
        self.debug = debug
        self.echo = echo
        self.engine = engine
        self.log = logging.getLogger(__name__)
        # pylint: disable=invalid-name
        self.Session: Optional[Session] = None
        self.schema = SchemaVersion(self.TABLES, self.settings)
        self.create_tables = create_tables

    def connect(self, create_superuser=False):
        """
        Connect to database, create tables and migrate existing tables.
        """
        if self.engine is None:
            connect_str = self.settings.connection_string()
            # print(f'bind database: {connect_str}')
            self.engine = sqlalchemy.create_engine(connect_str, pool_pre_ping=True, echo=self.echo)
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        self.detect_schema_versions()
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)
        with self.session_scope() as session:
            self.create_and_migrate_tables(session)
            if self.debug:
                self.schema.show()
            if create_superuser:
                if User.total_items(session) == 0:
                    self.create_superuser(username=User.__DEFAULT_ADMIN_USERNAME__,
                                          password=User.__DEFAULT_ADMIN_PASSWORD__)
            session.commit() # pylint: disable=no-member

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
            print(self.schema)
        statements = []
        for table in DatabaseConnection.TABLES:
            mapper = sqlalchemy.inspect(table)
            self.schema.set_column_types(table.__tablename__, mapper.columns)
        for table in DatabaseConnection.TABLES:
            version = self.schema.get_version(table.__tablename__)
            if version == 0:
                continue
            if self.debug:
                print(f'Migrate {table.__tablename__}')
            statements += table.migrate_schema(self.engine, self.schema)
        for cmd in statements:
            if self.debug:
                print(cmd)
            session.execute(cmd)
        session.flush()
        for table in DatabaseConnection.TABLES:
            version = self.schema.get_version(table.__tablename__)
            if version == 0:
                continue
            table.migrate_data(session, self.schema)
            self.schema.set_version(table.__tablename__, table.__schema_version__)
        session.commit()

    def detect_schema_versions(self):
        """
        Do first level checking of database schema version
        """
        insp = sqlalchemy.inspect(self.engine)
        tables = [name.lower() for name in insp.get_table_names()]
        if self.debug:
            print('Found tables:', tables)
        if 'songbase' in tables and 'track' not in tables:
            base_version = 1
        else:
            base_version = 2
        for table in DatabaseConnection.TABLES:
            if table.__tablename__.lower() not in tables:
                continue
            existing_columns = set({col['name'] for col in insp.get_columns(table.__tablename__)})
            self.schema.set_version(table.__tablename__, base_version)
            self.schema.set_existing_columns(table.__tablename__, existing_columns)
        if base_version == 1:
            self.schema.set_version('Track', 1)
            self.schema.set_version('Song', 1)
        else:
            self.schema.set_version('SongBase', 0)

    def create_superuser(self, username: Optional[str] = None,
                         password: Optional[str] = None):
        """
        Create an admin user
        """
        with self.session_scope() as session:
            admin = User.get(session, username="admin")
            if admin is not None:
                return
            if username is None:
                username = User.__DEFAULT_ADMIN_USERNAME__
            if password is None:
                password = secrets.token_urlsafe(14)
            groups_mask = Group.ADMIN.value + Group.USERS.value
            admin = User(username=username,
                         email="admin@music.bingo",
                         groups_mask=groups_mask,
                         password=User.hash_password(password))
            # TODO: investigate why groups_mask not working when
            # creating admin account
            admin.set_groups([Group.ADMIN, Group.USERS])
            session.add(admin) # pylint: disable=no-member
            print('Created admin account "{0}" ({1}) with password "{2}"'.format(
                admin.username, admin.email, password))

    @contextmanager
    def session_scope(self) -> Generator[DatabaseSession, None, None]:
        """Provide a transactional scope around a series of operations."""
        assert self.Session is not None
        session = cast(DatabaseSession, self.Session())
        try:
            # self.log.debug('yield session %s', session)
            yield session
            # self.log.debug('commit session %s', session)
            session.commit() # pylint: disable=no-member
        except BaseException:
            # self.log.debug('rollback session: %s %s', session, err)
            session.rollback() # pylint: disable=no-member
            raise
        finally:
            # self.log.debug('close session %s', session)
            # traceback.print_stack()
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

def current_options() -> Optional[DatabaseOptions]:
    """
    get current options used by the database.
    Returns None if database is not open
    """
    if DatabaseConnection._connection is None:
        return None
    return DatabaseConnection._connection.settings
