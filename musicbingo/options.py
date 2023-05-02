"""
Container for options used by both Bingo Game and clip generation
"""
from abc import ABC, abstractmethod
import argparse
from configparser import ConfigParser, SectionProxy
from enum import IntEnum, auto
import json
from pathlib import Path
import os
import secrets
from typing import (
    cast, AbstractSet, Any, Callable, Dict, Generic, List,
    Optional, NamedTuple, Sequence, Set, TypeVar, Union
)
import urllib

from musicbingo.palette import Palette
from musicbingo.docgen.sizes.pagesize import PageSizes
from musicbingo.json_object import JsonObject

EnumType = TypeVar('EnumType') # pylint: disable=invalid-name

class EnumWrapper(Generic[EnumType]):
    """
    Interface for a TypeConvert that has helper functions
    """

    def __init__(self, enum_type):
        self.type = enum_type

    def names(self) -> List[str]:
        """
        Get all of the key names of this enum, sorted alphabetically
        """
        try:
            return self.type.names()
        except AttributeError:
            return sorted(self.type.__members__.keys()) # type: ignore

    def __call__(self, name: Union[str, EnumType]) -> EnumType:
        """
        Convert a string to this enum
        """
        if isinstance(name, self.type):
            return name
        return self.type[name.upper()]  # type: ignore

class GameMode(IntEnum):
    """Enumeration of game operating modes"""
    BINGO = auto()
    QUIZ = auto()
    CLIP = auto()

    @classmethod
    def names(cls) -> List[str]:
        """get list of items in this enum"""
        return sorted(cls.__members__.keys()) # type: ignore

    @classmethod
    def from_string(cls, name: str) -> "GameMode":
        """
        Convert name string into this enum
        """
        return cls[name.upper()]  # type: ignore


# pylint: disable=invalid-name
TypeConvert = Union[Callable[[str], Any], argparse.FileType]


class OptionField(NamedTuple):
    """
    Tuple used to describe each option
    """
    name: str
    ftype: TypeConvert
    help: str
    default: Any
    min_value: Optional[int]
    max_value: Optional[int]
    choices: Optional[List[Any]]


class ExtraOptions(ABC):
    """
    Base class for additional option sections
    """
    OPTIONS: List[OptionField] = []
    LONG_PREFIX: str = ""
    SHORT_PREFIX: str = ""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        adds command line options for database settings
        """
        # pylint: disable=no-member
        group = parser.add_argument_group(title=cls.LONG_PREFIX,  # type: ignore
                                          description=cls.DESCRIPTION)  # type: ignore
        for opt in cls.OPTIONS:
            try:
                ftype = opt.ftype.from_string  # type: ignore
            except AttributeError:
                ftype = opt.ftype
            group.add_argument(
                f"--{cls.SHORT_PREFIX}-{opt.name}",  # type: ignore
                dest=f"{cls.SHORT_PREFIX}_{opt.name}",  # type: ignore
                nargs='?',
                help=f'{opt.help}  [%(default)s]',
                type=cast(TypeConvert, ftype))

    def load_environment_settings(self):
        """
        Check environment for database settings
        """
        # pylint: disable=no-member
        for opt in self.OPTIONS:
            try:
                env = (self.SHORT_PREFIX + opt.name).upper()
                value = opt.ftype(os.environ[env])
                setattr(self, opt.name, value)
            except ValueError as err:
                print(f'Failed to parse {env}: {err}')
            except KeyError:
                pass

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

    @abstractmethod
    def update(self, **kwargs) -> bool:
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


class SmtpOptions(ExtraOptions):
    """
    Options for sending emails
    """
    DESCRIPTION = "Email server connection options"
    SHORT_PREFIX = "smtp"
    LONG_PREFIX = "smtp"
    OPTIONS: List[OptionField] = [
        OptionField('port', int, 'SMTP port', 25, 1, 65535, None),
        OptionField('server', str, 'server hostname', 'localhost', None, None, None),
        OptionField('sender', str, 'email address to use for sending',
                    None, None, None, None),
        OptionField('reply_to', str, 'email address to use as "reply to" address',
                    None, None, None, None),
        OptionField('username', str, 'username to use to authenticate',
                    None, None, None, None),
        OptionField('password', str, 'password to use to authenticate',
                    None, None, None, None),
        OptionField('starttls', bool, 'use STARTTLS rather than SSL',
                    None, None, None, None),
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

    def update(self, **kwargs) -> bool:
        changed = False
        for key, value in kwargs.items():
            if key in self.__dict__ and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)
        return changed


class PrivacyOptions(ExtraOptions):
    """
    Options for setting privacy policy
    """
    DESCRIPTION = "Privacy policy options"
    SHORT_PREFIX = "privacy"
    LONG_PREFIX = "privacy"

    OPTIONS: List[OptionField] = [
        OptionField('name', str, 'Company Name', '', None, None, None),
        OptionField('email', str, 'Company Email', '', None, None, None),
        OptionField('address', str, 'Company Address', '', None, None, None),
        OptionField('data_center', str, 'Data Center', '', None, None, None),
        OptionField('ico', str, 'Information Commissioner URL', '', None, None, None),
    ]

    def __init__(self,
                 privacy_name: str = "",
                 privacy_email: str = "",
                 privacy_address: str = "",
                 privacy_data_center: str = '',
                 privacy_ico: str = "",
                 **_,
                 ):
        self.name = privacy_name
        self.email = privacy_email
        self.address = privacy_address
        self.data_center = privacy_data_center
        self.ico = privacy_ico
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

    def update(self, **kwargs) -> bool:
        changed = False
        for key, value in kwargs.items():
            if key in self.__dict__ and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)
        return changed


class Options(argparse.Namespace):
    """Options used by GameGenerator"""
    MIN_CARDS: int = 10  # minimum number of cards in a game
    INI_FILENAME: Optional[str] = "bingo.ini"
    OPTIONS: List[OptionField] = [
        OptionField('games_dest', str, 'Bingo Game destination directory',
                    'Bingo Games', None, None, None),
        OptionField('game_name_template', str, 'Template for game IDs',
                    r'Game-{game_id}', None, None, None),
        OptionField('game_info_filename', str, 'Template for game info JSON file',
                    r'game-{game_id}.json', None, None, None),
        OptionField('game_id', str, 'Game ID', '', None, None, None),
        OptionField('title', str, 'Game Title', '', None, None, None),
        OptionField('clip_directory', str, 'Directory containing clips',
                    'Clips', None, None, None),
        OptionField('new_clips_dest', str, 'Directory for new clips',
                    'NewClips', None, None, None),
        OptionField('clip_start', str, 'Clip start time',
                    '01:00', None, None, None),
        OptionField('clip_duration', int, 'Clip duration (seconds)', 30, 1, 120, None),
        OptionField('colour_scheme', EnumWrapper[Palette](Palette),
                    'Colour scheme', 'blue', None, None, Palette.names()),
        OptionField('number_of_cards', int, 'Number of cards', 24, MIN_CARDS, 100, None),
        OptionField('include_artist', bool, 'Include artist on Bingo card?',
                    True, None, None, None),
        OptionField('mode', EnumWrapper[GameMode](GameMode), 'GUI mode',
                    GameMode.BINGO, None, None, GameMode.names()),
        OptionField('create_index', bool, 'Create a song index file?', False, None, None, None),
        OptionField('page_order', bool,
                    'Sort tickets by number on generated pages', True, None, None, None),
        OptionField('page_size', EnumWrapper[PageSizes](PageSizes),
                    'Size of page', 'a4', None, None, PageSizes.names()),
        OptionField('columns', int, 'Columns per Bingo ticket', 5, 3, 7, None),
        OptionField('rows', int, 'Rows per Bingo ticket', 3, 3, 5, None),
        OptionField('bitrate', int, 'Audio bitrate (KBit/sec)', 256, 64, 512, None),
        OptionField('crossfade', int, 'Audio cross-fade (milliseconds)', 500, 0, 2000, None),
        OptionField('mp3_editor', str, 'MP3 editor engine', None, None, None, None),
        OptionField('mp3_player', str, 'MP3 player engine', None, None, None, None),
        OptionField('checkbox', bool, 'Add a checkbox to each Bingo ticket cell?',
                    False, None, None, None),
        OptionField('cards_per_page', int, 'Bingo cards per page', 3, 1, 6,
                    [1, 2, 3, 4, 6]),
        OptionField('doc_per_page', bool, 'Put each page in its own PDF document?',
                    False, None, None, None),
        OptionField('max_tickets_per_user', int, 'Maximum tickets per user', 2, 1, 100, None),
        OptionField('debug', bool, 'Enable debug', False, None, None, None),
        OptionField('create_superuser', bool, 'Create a super user account?',
                    True, None, None, None),
    ]
    EXTRA_OPTIONS: List[ExtraOptions] = [
        cast(ExtraOptions, DatabaseOptions),
        cast(ExtraOptions, PrivacyOptions),
        cast(ExtraOptions, SmtpOptions),
    ]
    EXTRA_OPTIONS_NAMES: List[str] = [e.LONG_PREFIX for e in EXTRA_OPTIONS]

    #pylint: disable=too-many-locals
    def __init__(self,
                 games_dest: str = "Bingo Games",
                 game_name_template: str = r'Game-{game_id}',
                 game_info_filename: str = r'game-{game_id}.json',
                 game_id: str = "",
                 title: str = "",
                 clip_directory: str = 'Clips',
                 new_clips_dest: str = 'NewClips',
                 clip_start: str = '01:00',
                 clip_duration: int = 30,
                 colour_scheme: Union[Palette,str] = 'blue',
                 number_of_cards: int = 24,
                 include_artist: bool = True,
                 mode: GameMode = GameMode.BINGO,
                 create_index: bool = False,
                 page_order: bool = True,
                 columns: int = 5,
                 rows: int = 3,
                 bitrate: int = 256,
                 crossfade: int = 500,
                 mp3_editor: Optional[str] = None,
                 mp3_player: Optional[str] = None,
                 checkbox: bool = False,
                 cards_per_page: int = 0,
                 doc_per_page: bool = False,
                 page_size: Union[PageSizes, str] = 'a4',
                 secret_key: Optional[str] = None,
                 max_tickets_per_user: int = 2,
                 debug: bool = False,
                 create_superuser: bool = True,
                 database: Optional[DatabaseOptions] = None,
                 smtp: Optional[SmtpOptions] = None,
                 privacy: Optional[PrivacyOptions] = None,
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
        if isinstance(colour_scheme, str):
            self.colour_scheme: Palette = Palette.from_string(colour_scheme)
        else:
            self.colour_scheme = colour_scheme
        self.number_of_cards = number_of_cards
        self.include_artist = include_artist
        self.mode = mode
        self.create_index = create_index
        self.page_order = page_order
        if isinstance(page_size, str):
            self.page_size: PageSizes = PageSizes.from_string(page_size)
        else:
            self.page_size = page_size
        self.columns = columns
        self.rows = rows
        self.bitrate = bitrate
        self.crossfade = crossfade
        self.mp3_editor = mp3_editor
        self.mp3_player = mp3_player
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
        if privacy is None:
            privacy = PrivacyOptions(**kwargs)
        self.privacy: PrivacyOptions = privacy
        self.__parser: Optional[argparse.ArgumentParser] = None

    def get_palette(self) -> Palette:
        """Return Palete for chosen colour scheme"""
        return self.colour_scheme

    def set_palette(self, palette: Palette) -> None:
        """Set the colour palette name"""
        self.colour_scheme = palette # .name.lower()

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
        album = album.replace(':', '-')
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
        basedir = Path(__file__).parents[1]
        ini_file = basedir / self.INI_FILENAME
        config = ConfigParser()
        if not ini_file.exists():
            return False
        config.read(str(ini_file))
        current = self.to_dict()
        section = config['musicbingo']
        self.apply_section(section, self, current)
        for cls in self.EXTRA_OPTIONS:
            field: str = cls.LONG_PREFIX
            try:
                section = config[field]
            except KeyError:
                continue
            if len(section) == 0:
                continue
            if getattr(self, field, None) is None:
                setattr(self, field, cls()) # type: ignore
                current[field] = getattr(self, field).to_dict()
            self.apply_section(section, getattr(self, field), current[field])
            getattr(self, field).load_environment_settings()
        return True

    @staticmethod
    def apply_section(section: SectionProxy, dest: Any, fields: JsonObject) -> None:
        """
        Takes the fields from section and sets attributes in dest.
        Used to copy data from a settings section into this options object
        """
        for key in section:
            dest_key = key
            # setting was renamed from mp3_engine to mp3_editor
            if key == 'mp3_engine':
                dest_key = 'mp3_editor'
            if dest_key not in fields:
                continue
            value: Any = section[key]
            if isinstance(fields[dest_key], bool):
                value = value.lower() == 'true'
            elif isinstance(fields[dest_key], GameMode):
                try:
                    value = GameMode.from_string(value)
                except KeyError:
                    print(f'Invalid GameMode: {value}')
                    continue
            elif isinstance(fields[dest_key], Palette):
                try:
                    value = Palette.from_string(value)
                except KeyError:
                    print(f'Invalid colour palette: {value}')
                    continue
            elif isinstance(fields[dest_key], PageSizes):
                try:
                    value = PageSizes.from_string(value)
                except KeyError:
                    print(f'Invalid page size: {value}')
                    continue
            elif isinstance(fields[dest_key], int):
                value = int(value)
            setattr(dest, dest_key, value)

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
        skip_items: Set[str] = set(self.EXTRA_OPTIONS_NAMES)
        skip_items.add('game_id')
        skip_items.add('jsonfile')
        skip_items.add('tables')
        skip_items.add('title')
        for key, value in items.items():
            if value is None or key[0] == '_':
                continue
            if key in skip_items:
                continue
            if isinstance(value, (GameMode, Palette, PageSizes)):
                value = value.name
            section[key] = str(value)
        for ext_opt in self.EXTRA_OPTIONS:
            field = ext_opt.LONG_PREFIX
            if getattr(self, field, None) is None:
                continue
            try:
                section = config[field]
            except KeyError:
                config[field] = {}
                section = config[field]
            for key, value in items[field].items():
                if value is None or key[0] == '_':
                    continue
                section[key] = str(value)
        with ini_file.open('w', encoding='utf-8') as cfile:
            config.write(cfile)

    @classmethod
    def parse(cls, args: Sequence[str]) -> "Options":
        """
        parse command line into an Options object
        """
        parser = cls.argument_parser()
        retval = cls()
        if not retval.load_ini_file():
            retval.save_ini_file()
        defaults = retval.to_dict()
        extra_option_names: Set[str] = set()
        for ext_cls in cls.EXTRA_OPTIONS:
            extra_option_names.add(ext_cls.LONG_PREFIX)
            for key, value in defaults[ext_cls.LONG_PREFIX].items():
                defaults[f'{ext_cls.SHORT_PREFIX}_{key}'] = value
            del defaults[ext_cls.LONG_PREFIX]
        parser.set_defaults(**defaults)
        result = parser.parse_args(args)
        changed = False
        for key, value in result.__dict__.items():
            if value is None or key in extra_option_names:
                continue
            found = False
            for ext_cls in cls.EXTRA_OPTIONS:
                prefix = f'{ext_cls.SHORT_PREFIX}_'
                if key.startswith(prefix):
                    found = True
                    eopt = cast(ExtraOptions, getattr(retval, ext_cls.LONG_PREFIX))
                    assert eopt is not None
                    changed |= eopt.update(**({
                        key[len(prefix):]: value
                    }))
            if not found and getattr(retval, key, None) != value:
                setattr(retval, key, value)
                changed = True
        if changed:
            retval.save_ini_file()
        retval.__parser = parser  # pylint: disable=unused-private-member
        return retval

    def usage(self):
        """
        Display usage
        """
        if self.__parser is None:
            parser = self.argument_parser()
            parser.print_help()
        else:
            self.__parser.print_help()

    @classmethod
    def argument_parser(cls, include_clip_directory=True) -> argparse.ArgumentParser:
        """
        Create argument parser
        """
        parser = argparse.ArgumentParser()
        name_map = {
            'games_dest': 'games',
            'game_id': 'id',
            'new_clips_dest': 'new-clips',
            'number_of_cards': 'cards',
            'include_artist': 'no-artist',
            'page_order': 'no-sort-cards',
            'create_superuser': 'no-create-superuser',
        }
        for opt in cls.OPTIONS:
            if opt.name == 'mode':
                continue
            try:
                ftype = opt.ftype.from_string  # type: ignore
            except AttributeError:
                ftype = opt.ftype
            choices_help = ''
            choices: Optional[List[Any]] = None
            if opt.choices is not None:
                values = ','.join(map(str, opt.choices))
                choices_help = f'({values}) '
                if opt.ftype in {int, str}:
                    choices = opt.choices
            try:
                arg = name_map[opt.name]
            except KeyError:
                arg = opt.name.replace('_', '-')
            if ftype == bool:
                if opt.default:
                    action="store_false"
                else:
                    action="store_true"
                parser.add_argument(
                    f"--{arg}",
                    dest=f"{opt.name}",
                    action=action,
                    help=f'{opt.help} {choices_help}[%(default)s]')
            else:
                parser.add_argument(
                    f"--{arg}",
                    dest=f"{opt.name}",
                    nargs='?',
                    choices=choices,
                    help=f'{opt.help} {choices_help}[%(default)s]',
                    type=cast(TypeConvert, ftype))
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
        for ext_cls in cls.EXTRA_OPTIONS:
            ext_cls.add_arguments(parser)
        if include_clip_directory:
            parser.add_argument(
                "clip_directory", nargs='?',
                help="Directory to search for Songs [%(default)s]")
        defaults = cls().to_dict()
        for ext_cls in cls.EXTRA_OPTIONS:
            for key, value in defaults[ext_cls.LONG_PREFIX].items():
                defaults[f'{ext_cls.SHORT_PREFIX}_{key}'] = value
            del defaults[ext_cls.LONG_PREFIX]
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
            for ext_cls in self.EXTRA_OPTIONS:
                if key == ext_cls.LONG_PREFIX and value is not None:
                    value = cast(ExtraOptions, value).to_dict()
            retval[key] = value
        return retval

    def to_kwargs(self, exclude: Optional[AbstractSet[str]] = None,
                  only: Optional[AbstractSet[str]] = None) -> Dict[str, Any]:
        """
        Convert options into a dictionary suitable to use as **kwargs in the
        Options constuctor
        """
        retval = self.to_dict(exclude=exclude, only=only)
        for section in self.EXTRA_OPTIONS_NAMES:
            if section in retval and retval[section] is not None:
                for key, value in retval[section].items():
                    retval[f'{section}_{key}'] = value
                del retval[section]
        return retval

    def update(self, **kwargs) -> None:
        """
        Update these settings using supplied arguments
        """
        for opt in self.OPTIONS:
            if opt.name not in kwargs:
                continue
            value = opt.ftype(kwargs[opt.name])
            setattr(self, opt.name, value)
        for name in self.EXTRA_OPTIONS_NAMES:
            if name in kwargs:
                ext_opt = cast(ExtraOptions, getattr(self, name))
                ext_opt.update(**kwargs[name])

    @classmethod
    def get_field(cls, name: str) -> OptionField:
        """
        Get the OptionField for the given setting
        """
        for opt in cls.OPTIONS:
            if name == opt.name:
                return opt
        raise KeyError(f'{name} field not found')
