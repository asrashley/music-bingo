"""
Container for options used by both Bingo Game and clip generation
"""
from abc import ABC, abstractmethod
import argparse
from configparser import ConfigParser
from enum import IntEnum, auto
import json
from pathlib import Path
import os
import secrets
from typing import cast, AbstractSet, Any, Callable, Dict, Optional, Sequence, Union
import urllib

from musicbingo.palette import Palette


class GameMode(IntEnum):
    """Enumeration of game operating modes"""
    BINGO = auto()
    QUIZ = auto()
    CLIP = auto()


class ExtraOptions(ABC):
    """
    Base class for additional option sections
    """
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        """
        adds command line options for database settings
        """
        TypeConvert = Union[Callable[[str], Any], argparse.FileType]
        # pylint: disable=no-member
        group = parser.add_argument_group(title=cls.LONG_PREFIX,  # type: ignore
                                          description=cls.DESCRIPTION)  # type: ignore
        for name, ftype, hlp in cls.OPTIONS:  # type: ignore
            group.add_argument(
                f"--{cls.SHORT_PREFIX}{name}",  # type: ignore
                dest=f"{cls.LONG_PREFIX}_{name}",  # type: ignore
                nargs='?', help=hlp, type=cast(TypeConvert, ftype))

    def load_environment_settings(self):
        """
        Check environment for database settings
        """
        # pylint: disable=no-member
        for field, cls, _ in self.OPTIONS:
            try:
                env = (self.SHORT_PREFIX + field).upper()
                value = cls(os.environ[env])
                setattr(self, field, value)
            except ValueError as err:
                print(f'Failed to parse {env}: {err}')
            except KeyError:
                pass

    @abstractmethod
    def update(self, **kwargs):
        """
        Apply supplied arguments to this settings section
        """
        raise NotImplementedError("method must be implemented by super class")


class DatabaseOptions(ExtraOptions):
    """
    Database connection options
    """

    DESCRIPTION = "Database connection options"
    SHORT_PREFIX = "db"
    LONG_PREFIX = "database"
    OPTIONS = [
        ('connect_timeout', int, 'Timeout (in seconds) when connecting to database'),
        ('create_db', bool, 'Create database if not found (sqlite only)'),
        ('driver', str, 'Database driver'),
        ('name', str, 'Database name (or filename for sqlite)'),
        ('host', str, 'Hostname of database server'),
        ('passwd', str, 'Password for connecting to database'),
        ('port', int, 'Port to use to connect to database'),
        ('provider', str, 'Database driver (sqlite, mysql) [%(default)s]'),
        ('ssl', json.loads, 'TLS options'),
        ('user', str, 'Username for connecting to database'),
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

    def load_environment_settings(self):
        """
        Check environment for database settings
        """
        super().load_environment_settings()
        if self.provider == 'sqlite' and self.create_db is None:
            self.create_db = True
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
            cgi_params.append('{0}={1}'.format(
                key, urllib.parse.quote_plus(value)))
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
            if key == 'ssl':
                value = json.dumps(value)
            retval[key] = value
        return retval

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__:
                if key == 'ssl' and isinstance(value, str):
                    value = json.loads(value)
                setattr(self, key, value)

class SmtpOptions(ExtraOptions):
    """
    Options for sending emails
    """
    DESCRIPTION = "Email server connection options"
    SHORT_PREFIX = "smtp"
    LONG_PREFIX = "smtp"
    OPTIONS = [
        ('port', int, 'SMTP port'),
        ('server', str, 'server hostname'),
        ('sender', str, 'email address to use for sending'),
        ('reply_to', str, 'email address to use as "reply to" address'),
        ('username', str, 'username to use to authenticate'),
        ('password', str, 'password to use to authenticate'),
        ('starttls', bool, 'use STARTTLS rather than SSL'),
    ]

    def __init__(self,
                 smtp_port: int = 25,
                 smtp_server: str = 'localhost',
                 smtp_sender: Optional[str] = None,
                 smtp_reply_to: Optional[str] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 smtp_starttls: bool = False,
                 **_,
                 ):
        self.port = smtp_port
        self.server = smtp_server
        self.sender = smtp_sender
        self.reply_to = smtp_reply_to
        self.username = smtp_username
        self.password = smtp_password
        self.starttls = smtp_starttls
        self.load_environment_settings()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to a dictionary
        """
        retval = {}
        for key, value in self.__dict__.items():
            if key[0] == '_':
                continue
            retval[key] = value
        return retval

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__:
                setattr(self, key, value)


class Options(argparse.Namespace):
    """Options used by GameGenerator"""
    INI_FILENAME: Optional[str] = "bingo.ini"

    #pylint: disable=too-many-locals
    def __init__(self,
                 games_dest: str = "Bingo Games",
                 game_name_template: str = r'Game-{game_id}',
                 game_info_filename: str = "game-{game_id}.json",
                 game_id: str = "",
                 title: str = "",
                 clip_directory: str = 'Clips',
                 new_clips_dest: str = 'NewClips',
                 clip_start: str = "01:00",
                 clip_duration: int = 30,
                 colour_scheme: str = 'blue',
                 number_of_cards: int = 24,
                 include_artist: bool = True,
                 mode: GameMode = GameMode.BINGO,
                 create_index: bool = False,
                 page_order: bool = True,
                 columns: int = 5,
                 rows: int = 3,
                 bitrate: int = 256,
                 crossfade: int = 500,
                 mp3_engine: str = 'ffmpeg',
                 checkbox: bool = False,
                 cards_per_page: int = 0,
                 doc_per_page: bool = False,
                 secret_key: Optional[str] = None,
                 max_tickets_per_user: int = 2,
                 debug: bool = False,
                 create_superuser: bool = True,
                 database: Optional[DatabaseOptions] = None,
                 smtp: Optional[SmtpOptions] = None,
                 **kwargs
                 ) -> None:
        super().__init__()
        self.games_dest = games_dest
        self.game_name_template = game_name_template
        self.game_info_filename = game_info_filename
        self.game_id = game_id
        self.title = title
        self.clip_directory = clip_directory
        self.new_clips_dest = new_clips_dest
        self.clip_start = clip_start
        self.clip_duration = clip_duration
        self.colour_scheme = colour_scheme
        self.number_of_cards = number_of_cards
        self.include_artist = include_artist
        self.mode = mode
        self.create_index = create_index
        self.page_order = page_order
        self.columns = columns
        self.rows = rows
        self.bitrate = bitrate
        self.crossfade = crossfade
        self.mp3_engine = mp3_engine
        self.checkbox = checkbox
        self.cards_per_page = cards_per_page
        self.doc_per_page = doc_per_page
        self.secret_key = secret_key
        self.max_tickets_per_user = max_tickets_per_user
        self.debug = debug
        self.create_superuser = create_superuser
        if database is None:
            database = DatabaseOptions(**kwargs)
        self.database: DatabaseOptions = database
        if smtp is None:
            smtp = SmtpOptions(**kwargs)
        self.smtp: SmtpOptions = smtp
        self.__parser: Optional[argparse.ArgumentParser] = None

    def get_palette(self) -> Palette:
        """Return Palete for chosen colour scheme"""
        return Palette[self.colour_scheme.upper()]

    def set_palette(self, palette: Palette) -> None:
        """Set the colour palette name"""
        self.colour_scheme = palette.name.lower()

    palette = property(get_palette, set_palette)

    def clips(self) -> Path:
        """Return directory containing song clips"""
        # simple case - path is already absolute
        clip_dir = Path(self.clip_directory)
        if clip_dir.is_absolute():
            return clip_dir
        # try relative to current working directory
        filename = Path.cwd() / clip_dir
        if filename.exists():
            return filename
        # try relative to the top level of the source code
        basedir = Path(__file__).parents[1]
        return basedir / clip_dir

    def game_destination_dir(self, game_id: Optional[str] = None) -> Path:
        """Output directory for a Bingo game"""
        games_dest = Path(self.games_dest)
        if not games_dest.is_absolute():
            games_dest = Path.cwd() / games_dest
        if game_id is None:
            game_id = self.game_id
        dirname = self.game_name_template.format(game_id=game_id)
        return games_dest / dirname

    def mp3_output_name(self) -> Path:
        """Filename of MP3 file when generating a game"""
        filename = f'{self.game_id} Game Audio.mp3'
        return self.game_destination_dir() / filename

    def bingo_tickets_output_name(self, page: int = 0) -> Path:
        """Filename of document containing all Bingo tickets in a game"""
        if self.doc_per_page:
            if self.cards_per_page == 1:
                filename = f'{self.game_id} Bingo Ticket {page}.pdf'
            else:
                filename = (f'{self.game_id} Bingo Tickets - ' +
                            f'({self.number_of_cards} Tickets) page {page}.pdf')
        else:
            filename = (f'{self.game_id} Bingo Tickets - ' +
                        f'({self.number_of_cards} Tickets).pdf')
        return self.game_destination_dir() / filename

    def game_info_output_name(self) -> Path:
        """
        Filename of JSON file containing information about a generated game
        """
        filename = self.game_info_filename.format(game_id=self.game_id)
        return self.game_destination_dir() / filename

    def track_listing_output_name(self) -> Path:
        """Filename of document listing tracks in a game"""
        filename = f'{self.game_id} Track Listing.pdf'
        return self.game_destination_dir() / filename

    def ticket_results_output_name(self) -> Path:
        """Filename of document listing when each ticket in a game wins"""
        filename = f'{self.game_id} Ticket Results.pdf'
        return self.game_destination_dir() / filename

    def ticket_checker_output_name(self) -> Path:
        """Filename of file used by TicketChecker.py"""
        filename = "ticketTracks"
        return self.game_destination_dir() / filename

    def clip_destination_dir(self, album: str) -> Path:
        """Output directory when generating clips"""
        clips_dest = Path(self.new_clips_dest)
        if not clips_dest.is_absolute():
            clips_dest = Path.cwd() / clips_dest
        return clips_dest / album

    def songs_per_ticket(self) -> int:
        """number of songs on each Bingo ticket"""
        return self.columns * self.rows

    def email_settings(self) -> SmtpOptions:
        """
        Get the settings for sending emails
        """
        if self.smtp is None:
            self.smtp = SmtpOptions()
        return self.smtp

    def get_secret_key(self) -> str:
        """
        Get the secret key used by the server.
        The secret key is used for things like cookie generation
        """
        if self.secret_key is None:
            self.secret_key = secrets.token_urlsafe(32)
            self.save_ini_file()
        return self.secret_key

    def load_ini_file(self) -> bool:
        """
        Load ini file if available.
        The INI file is used to provide defaults that persist between
        sessions of running the app.
        """
        if self.INI_FILENAME is None:
            return False
        def apply_section(section, dest, fields):
            for key in section:
                if key not in fields:
                    continue
                value: Any = section[key]
                if isinstance(fields[key], bool):
                    value = value.lower() == 'true'
                elif isinstance(fields[key], GameMode):
                    try:
                        value = GameMode[value]
                    except KeyError:
                        print(f'Invalid GameMode: {value}')
                        continue
                elif isinstance(fields[key], int):
                    value = int(value)
                setattr(dest, key, value)

        basedir = Path(__file__).parents[1]
        ini_file = basedir / self.INI_FILENAME
        config = ConfigParser()
        if not ini_file.exists():
            return False
        config.read(str(ini_file))
        current = self.to_dict()
        section = config['musicbingo']
        apply_section(section, self, current)
        for field, cls in [('database', DatabaseOptions), ('smtp', SmtpOptions)]:
            try:
                section = config[field]
            except KeyError:
                section = None  # type: ignore
            if section is not None and len(section) > 0:
                if getattr(self, field, None) is None:
                    setattr(self, field, cls())
                    current[field] = getattr(self, field).to_dict()
                apply_section(section, getattr(self, field), current[field])
                getattr(self, field).load_environment_settings()
        return True

    def save_ini_file(self) -> None:
        """
        Save current settings as an INI file
        """
        if self.INI_FILENAME is None:
            return
        basedir = Path(__file__).parents[1]
        ini_file = basedir / self.INI_FILENAME
        config = ConfigParser()
        if ini_file.exists():
            config.read(str(ini_file))
        items = self.to_dict()
        try:
            section = config['musicbingo']
        except KeyError:
            config['musicbingo'] = {}
            section = config['musicbingo']
        for key, value in items.items():
            if value is None or key[0] == '_':
                continue
            if key in ['game_id', 'title', 'database', 'smtp']:
                continue
            if isinstance(value, GameMode):
                value = value.name
            section[key] = str(value)
        for field in ['database', 'smtp']:
            if getattr(self, field, None) is not None:
                try:
                    section = config[field]
                except KeyError:
                    config[field] = {}
                    section = config[field]
                for key, value in items[field].items():
                    if value is None or key[0] == '_':
                        continue
                    section[key] = str(value)
        with ini_file.open('w') as cfile:
            config.write(cfile)

    @classmethod
    def parse(cls, args: Sequence[str]) -> "Options":
        """parse command line into an Options object"""
        parser = cls.argument_parser()
        retval = cls()
        if not retval.load_ini_file():
            retval.save_ini_file()
        defaults = retval.to_dict()
        for key, value in defaults['database'].items():
            defaults[f'db{key}'] = value
        for key, value in defaults['smtp'].items():
            defaults[f'smtp{key}'] = value
        del defaults['smtp']
        parser.set_defaults(**defaults)
        result = parser.parse_args(args)
        for key, value in result.__dict__.items():
            if value is None or key in {'database', 'smtp'}:
                continue
            if key.startswith("database_"):
                retval.database.update(**{
                    key[len("database_"):]: value
                })
            elif key.startswith("smtp_"):
                retval.smtp.update(**{
                    key[len("database_"):]: value
                })
            elif key in result.__dict__:
                setattr(retval, key, value)
        retval.__parser = parser
        return retval

    def usage(self):
        """
        Display usage
        """
        self.__parser.print_help()

    @classmethod
    def argument_parser(cls, include_clip_directory=True) -> argparse.ArgumentParser:
        """
        Create argument parser
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--games", dest="games_dest", nargs='?',
            help="Destination directory for Bingo Games [%(default)s]")
        parser.add_argument(
            "--game_name_template", nargs='?',
            help="Template for Bingo Game directory [%(default)s]")
        parser.add_argument(
            "--game_info_filename", nargs='?',
            help="Filename remplate used to store a JSON file " +
            "containing all data of a game [%(default)s]")
        parser.add_argument(
            "--id", dest="game_id", nargs='?',
            help="ID to assign to the Bingo game [%(default)s]")
        parser.add_argument(
            "--title", dest="title", nargs='?',
            help="Title for the Bingo game [%(default)s]")
        parser.add_argument(
            "--new_clips", dest="new_clips_dest", nargs='?',
            help="Directory to store new song clips [%(default)s]")
        parser.add_argument(
            "--colour_scheme",
            choices=list(map(str.lower, Palette.colour_names())),
            help="Colour scheme to use for Bingo tickets [%(default)s]")
        parser.add_argument(
            "--cards", dest="number_of_cards", type=int,
            help="Quantity of Bingo tickets to create [%(default)d]")
        parser.add_argument(
            "--cards-per-page", dest="cards_per_page", type=int,
            help="Quantity of Bingo tickets to fit on each page [%(default)d] (0=auto)")
        parser.add_argument(
            "--checkbox", action="store_true",
            help="Add a checkbox to each cell")
        parser.add_argument(
            "--doc-per-page", dest="doc_per_page", action="store_true",
            help="Create each page as its own PDF document")
        parser.add_argument(
            "--no-artist", dest="include_artist", action="store_false",
            help="Exclude artist names from Bingo tickets [%(default)s]")
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument(
            "--bingo", dest="mode", action="store_const",
            const=GameMode.BINGO,
            help="Start in Bingo generation mode")
        modes.add_argument(
            "--clip", dest="mode", action="store_const",
            const=GameMode.CLIP,
            help="Start in clip generation mode")
        modes.add_argument(
            "--quiz", dest="mode", action="store_const",
            const=GameMode.QUIZ,
            help="Start in music quiz generation mode")
        parser.add_argument(
            "--create_index", action="store_true",
            help="Create an index of all songs")
        parser.add_argument(
            "--ticket-order", dest="page_order", action="store_false",
            help="Sort Bingo tickets in output by ticket number [%(default)s]")
        parser.add_argument(
            "--rows", type=int, choices=[2, 3, 4, 5],
            help="Number of rows for each Bingo ticket create [%(default)d]")
        parser.add_argument(
            "--columns", type=int, choices=[2, 3, 4, 5, 6, 7],
            help="Number of columns for each Bingo ticket create [%(default)d]")
        parser.add_argument(
            "--bitrate", type=int,
            help="Audio bitrate (in Kbps) [%(default)d]")
        parser.add_argument(
            "--crossfade", type=int,
            help="Set duration of cross fade between songs (in milliseconds). 0 = no crossfade")
        parser.add_argument(
            "--mp3-engine", dest="mp3_engine", nargs='?',
            help="MP3 engine to use when creating MP3 files [%(default)s]")
        parser.add_argument(
            "--no-create-superuser", action="store_false", dest="create_superuser",
            help="Don't create an admin account if database is empty")
        parser.add_argument(
            "--debug", action="store_true",
            help="Enable debug mode")
        DatabaseOptions.add_arguments(parser)
        SmtpOptions.add_arguments(parser)
        if include_clip_directory:
            parser.add_argument(
                "clip_directory", nargs='?',
                help="Directory to search for Songs [%(default)s]")
        defaults = cls().to_dict()
        for key, value in defaults['database'].items():
            defaults[f'db{key}'] = value
        del defaults['database']
        parser.set_defaults(**defaults)
        return parser

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None) -> Dict[str, Any]:
        """
        convert Options to a dictionary
        """
        retval = {
        }
        for key, value in self.__dict__.items():
            if key[0] == '_':
                continue
            if ((len(key) > 2 and key.startswith('db')) or
                (len(key) > 4 and key.startswith('smtp'))):
                continue
            if exclude is not None and key in exclude:
                continue
            if only is not None and key not in only:
                continue
            if key == 'database' and value is not None:
                value = cast(DatabaseOptions, value).to_dict()
            elif key == 'smtp' and value is not None:
                value = cast(SmtpOptions, value).to_dict()
            retval[key] = value
        return retval

    def to_kwargs(self, exclude: Optional[AbstractSet[str]] = None,
                  only: Optional[AbstractSet[str]] = None) -> Dict[str, Any]:
        """
        Convert options into a dictionary suitable to use as **kwargs in the
        Options constuctor
        """
        retval = self.to_dict(exclude=exclude, only=only)
        for section in ['database', 'smtp']:
            if section in retval and retval[section] is not None:
                for key, value in retval[section].items():
                    retval[f'{section}_{key}'] = value
                del retval[section]
        return retval
