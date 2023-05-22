"""
Database connection options
"""
import json
import urllib

from pathlib import Path
from typing import Any, Dict, List, Optional

from .extra import ExtraOptions
from .option_field import OptionField

class DatabaseOptions(ExtraOptions):
    """
    Database connection options
    """

    DESCRIPTION = "Database connection options"
    SHORT_PREFIX = "db"
    LONG_PREFIX = "database"
    OPTIONS: List[OptionField] = [
        OptionField('connect_timeout', int,
                    'Timeout (in seconds) when connecting to database',
                    None, 1, 3600, None),
        OptionField('create_db', bool, 'Create database if not found (sqlite only)',
                    None, None, None, None),
        OptionField('driver', str, 'Database driver', None, None, None, None),
        OptionField('name', str, 'Database name (or filename for sqlite)', None, None, None, None),
        OptionField('host', str, 'Hostname of database server', None, None, None, None),
        OptionField('passwd', str, 'Password for connecting to database', None, None, None, None),
        OptionField('port', int, 'Port to use to connect to database', None, 1, 65535, None),
        OptionField('provider', str, 'Database provider (sqlite, mysql) [%(default)s]',
                    'sqlite', None, None, None),
        OptionField('ssl', json.loads, 'TLS options', None, None, None, None),
        OptionField('user', str, 'Username for connecting to database', None, None, None, None),
    ]
    DEFAULT_FILENAME: Optional[str] = 'bingo.db3'

    def __init__(self,
                 database_provider: str = 'sqlite',
                 database_connect_timeout: Optional[int] = None,
                 database_create_db: Optional[bool] = None,
                 database_driver: Optional[str] = None,
                 database_host: Optional[str] = None,
                 database_name: Optional[str] = None,
                 database_passwd: Optional[str] = None,
                 database_port: Optional[int] = None,
                 database_ssl: Optional[Dict] = None,
                 database_user: Optional[str] = None,
                 **_,
                 ):
        # For mysql connect options, see:
        # https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
        assert database_provider is not None
        self.provider = database_provider
        self.driver = database_driver
        self.host = database_host
        self.user = database_user
        self.passwd = database_passwd
        self.name = database_name
        self.create_db = database_create_db
        self.port = database_port
        self.connect_timeout = database_connect_timeout
        if isinstance(database_ssl, str):
            database_ssl = json.loads(database_ssl)
        self.ssl = database_ssl
        if self.name is None and self.provider == 'sqlite' and self.DEFAULT_FILENAME is not None:
            basedir = Path(__file__).parents[1]
            filename = basedir / self.DEFAULT_FILENAME
            self.name = str(filename)
        self.load_environment_settings()
        if self.provider == 'sqlite' and self.create_db is None:
            self.create_db = True

    def load_environment_settings(self) -> None:
        """
        Check environment for database settings
        """
        super().load_environment_settings()
        if isinstance(self.ssl, str):
            self.ssl = json.loads(self.ssl)

    def connection_string(self) -> str:
        """
        Create a connection URL containing all the database settings
        """
        if self.provider == 'sqlite':
            return f'sqlite:///{self.name}'
        if self.host is None:
            host = ''
        elif self.port:
            host = f'{self.host}:{self.port}/'
        else:
            host = f'{self.host}/'
        uri = f'{self.provider}://{self.user}:{self.passwd}@{host}{self.name}'
        opts = {}
        if self.ssl:
            opts['ssl'] = 'true'
            for key, value in self.ssl.items():
                if key == 'ssl_mode' or not value:
                    continue
                opts[key] = value
        if self.connect_timeout:
            opts['connect_timeout'] = str(self.connect_timeout)
        if self.driver:
            opts['driver'] = self.driver
        cgi_params = []
        for key, value in opts.items():
            cgi_params.append(f'{key}={urllib.parse.quote_plus(value)}')
        if cgi_params:
            uri += '?' + '&'.join(cgi_params)
        return uri

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to a dictionary
        """
        retval = {}
        for key, value in self.__dict__.items():
            if key[0] == '_':
                continue
            if key == 'ssl' and value is not None:
                value = json.dumps(value)
            retval[key] = value
        return retval

    def update(self, **kwargs) -> bool:
        changed = False
        for key, value in kwargs.items():
            if key in self.__dict__:
                if key == 'ssl' and isinstance(value, str):
                    value = json.loads(value)
                if getattr(self, key) != value:
                    setattr(self, key, value)
                    changed = True
        return changed
