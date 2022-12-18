"""factory method for creating an MP3 engine"""

from typing import Dict, Generic, List, Optional, Tuple, Type, TypeVar

from musicbingo.mp3.editor import MP3Editor
from musicbingo.mp3.mockeditor import MockEditor
from musicbingo.mp3.parser import MP3Parser
from musicbingo.mp3.player import MP3Player

ETYPE = TypeVar('ETYPE')

class MP3Feature(Generic[ETYPE]):
    """
    Holds state about one MP3 feature (editor, player, parser)
    """
    def __init__(self, engines: Optional[Dict[str, ETYPE]] = None):
        self.engines: Dict[str, ETYPE] = {}
        if engines is not None:
            self.engines = engines
        self.errors: List[Tuple[str, str]] = []
        self.default_engine: Optional[str] = None

    def available_engines(self) -> List[str]:
        """
        Get list of available MP3 engines
        """
        return sorted([k.lower() for k in self.engines])

    def get_engine(self, engine: Optional[str] = None) -> ETYPE:
        """
        Get an MP3 engine class.
        If engine==None, this will pick the default
        """
        if engine is None:
            if self.default_engine is None:
                raise NotImplementedError('Failed to find any MP3 editors')
            engine = self.default_engine
        engine = engine.lower()
        try:
            return self.engines[engine]
        except KeyError as err:
            raise NotImplementedError(f'Unknown engine {engine}') from err


class MP3Factory:
    """Class for creating MP3Editor and MP3Parser instances"""

    PROBE_DONE = False
    EDITOR = MP3Feature[Type[MP3Editor]]({'mock': MockEditor})
    PARSER = MP3Feature[Type[MP3Parser]]()
    PLAYER = MP3Feature[Type[MP3Player]]()

    @classmethod
    def available_editors(cls) -> List[str]:
        """
        Get list of available MP3 engines
        """
        cls._auto_probe()
        return sorted([k.lower() for k in cls.EDITOR.engines])

    @classmethod
    def available_parsers(cls) -> List[str]:
        """
        Get list of available MP3 parsers
        """
        cls._auto_probe()
        return cls.PARSER.available_engines()

    @classmethod
    def available_players(cls) -> List[str]:
        """
        Get list of available MP3 players
        """
        cls._auto_probe()
        return cls.PLAYER.available_engines()

    @classmethod
    def create_editor(cls, editor: Optional[str] = None) -> MP3Editor:
        """
        Create an MP3Editor.
        If editor==None, the factory will pick one that is supported.
        """
        cls._auto_probe()
        engine = cls.EDITOR.get_engine(editor)
        return engine()

    @classmethod
    def create_parser(cls, parser: Optional[str] = None) -> MP3Parser:
        """
        Create an MP3Parser.
        If parser==None, the factory will pick the first one that
        is supported.
        """
        cls._auto_probe()
        return cls.PARSER.get_engine(parser)()

    @classmethod
    def create_player(cls, player: Optional[str] = None) -> MP3Player:
        """
        Create an MP3Player.
        If player == None, the factory will pick the first one that
        is supported.
        """
        cls._auto_probe()
        return cls.PLAYER.get_engine(player)()

    @classmethod
    def _auto_probe(cls) -> None:
        """
        Try to detect all of the available parsers and editors
        """

        if cls.PROBE_DONE:
            return
        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.mutagenparser import MutagenParser
            cls.PARSER.engines['mutagen'] = MutagenParser
            cls.PARSER.default_engine = 'mutagen'
        except ImportError as mutagenparser_err:
            cls.PARSER.errors.append(('mutagen', str(mutagenparser_err)))

        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.pydubeditor import PydubEditor
            cls.EDITOR.engines['pydub'] = PydubEditor
            cls.EDITOR.default_engine = 'pydub'
            if PydubEditor.is_playback_supported():
                cls.PLAYER.engines['pydub'] = PydubEditor
                cls.PLAYER.default_engine = 'pydub'
        except ImportError as pydubeditor_err:
            cls.EDITOR.errors.append(('pydub', str(pydubeditor_err)))
        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.ffmpegeditor import FfmpegEditor
            if FfmpegEditor.is_encoding_supported():
                cls.EDITOR.engines['ffmpeg'] = FfmpegEditor
                cls.EDITOR.default_engine = 'ffmpeg'
            if FfmpegEditor.is_playback_supported():
                cls.PLAYER.engines['ffmpeg'] = FfmpegEditor
                if cls.PLAYER.default_engine is None:
                    cls.PLAYER.default_engine = 'ffmpeg'
        except ImportError as ffmpegeditor_err:
            cls.EDITOR.errors.append(('ffmpeg', str(ffmpegeditor_err)))
            cls.PLAYER.errors.append(('ffmpeg', str(ffmpegeditor_err)))

        cls.PROBE_DONE = True
