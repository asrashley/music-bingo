"""
Container for options used by both Bingo Game and clip generation
"""
import argparse
from configparser import ConfigParser, SectionProxy
from enum import Enum, IntEnum
from pathlib import Path
import secrets
from typing import (
    cast, AbstractSet, Any, Dict, List, Optional,
    Sequence, Set, Union
)

from musicbingo.palette import Palette
from musicbingo.docgen.sizes.pagesize import PageSizes
from musicbingo.json_object import JsonObject

from .database import DatabaseOptions
from .enum_wrapper import EnumWrapper
from .extra import ExtraOptions
from .game_mode import GameMode
from .option_field import OptionField, TypeConvert
from .page_sort_order import PageSortOrder
from .privacy import PrivacyOptions
from .smtp import SmtpOptions

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
        OptionField('sort_order', EnumWrapper[PageSortOrder](PageSortOrder),
                    'How to Sort tickets on generated pages',
                    PageSortOrder.INTERLEAVE.value, None, None, PageSortOrder.names()),
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

    #pylint: disable=too-many-locals,too-many-statements, too-many-positional-arguments
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
                 sort_order: PageSortOrder = PageSortOrder.INTERLEAVE,
                 page_order: Optional[bool] = None,
                 columns: int = 5,
                 rows: int = 3,
                 bitrate: int = 256,
                 crossfade: int = 500,
                 mp3_editor: Optional[str] = None,
                 mp3_player: Optional[str] = None,
                 checkbox: bool = False,
                 cards_per_page: int = 3,
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
        self.sort_order = sort_order
        if page_order is not None:
            if page_order is True:
                self.sort_order = PageSortOrder.INTERLEAVE
            elif page_order is False:
                self.sort_order = PageSortOrder.NUMBER
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
        if self.cards_per_page < 1 or self.cards_per_page > 6:
            self.cards_per_page = 3
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
            elif isinstance(fields[dest_key], (Enum, IntEnum)):
                try:
                    value = type(fields[dest_key]).from_string(value)
                except KeyError:
                    print(f'Invalid {dest_key}: {value}')
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
            elif isinstance(fields[dest_key], PageSortOrder):
                try:
                    value = PageSortOrder.from_string(value)
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
