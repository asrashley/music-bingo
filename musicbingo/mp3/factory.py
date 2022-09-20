"""factory method for creating an MP3 engine"""

from typing import Dict, List, Optional, Tuple, Type

from musicbingo.mp3.editor import MP3Editor
from musicbingo.mp3.mockeditor import MockEditor
from musicbingo.mp3.parser import MP3Parser

class MP3Factory:
    """Class for creating MP3Editor and MP3Parser instances"""

    PROBE_DONE = False
    PARSERS: Dict[str, Type[MP3Parser]] = {}
    PARSER_ERRORS: List[Tuple[str, str]] = []
    DEFAULT_PARSER: Optional[str] = None
    EDITORS: Dict[str, Type[MP3Editor]] = {
        'mock': MockEditor
    }
    EDITOR_ERRORS: List[Tuple[str, str]] = []
    DEFAULT_EDITOR: Optional[str] = None

    @classmethod
    def available_editors(cls) -> List[str]:
        """
        Get list of available MP3 engines
        """
        cls._auto_probe()
        return sorted([k.lower() for k in cls.EDITORS])

    @classmethod
    def available_parsers(cls) -> List[str]:
        """
        Get list of available MP3 parsers
        """
        cls._auto_probe()
        return sorted([k.lower() for k in cls.PARSERS])

    @classmethod
    def create_editor(cls, editor: Optional[str] = None) -> MP3Editor:
        """
        Create an MP3Editor.
        If editor==None, the factory will pick one that is supported.
        """
        cls._auto_probe()
        if editor is None:
            if cls.DEFAULT_EDITOR is None:
                raise NotImplementedError('Failed to find any MP3 editors')
            editor = cls.DEFAULT_EDITOR
        editor = editor.lower()
        try:
            return cls.EDITORS[editor]()
        except KeyError as err:
            raise NotImplementedError(f'Unknown editor {editor}') from err

    @classmethod
    def create_parser(cls, parser: Optional[str] = None) -> MP3Parser:
        """
        Create an MP3Parser.
        If parser==None, the factory will pick the first one that
        is supported.
        """
        cls._auto_probe()
        if parser is None:
            if cls.DEFAULT_PARSER is None:
                raise NotImplementedError('Failed to find any MP3 parsers')
            parser = cls.DEFAULT_PARSER
        parser = parser.lower()
        try:
            return cls.PARSERS[parser]()
        except KeyError as err:
            raise NotImplementedError(f'Unknown parser {parser}') from err

    @classmethod
    def _auto_probe(cls):
        """
        Try to detect all of the available parsers and editors
        """

        if cls.PROBE_DONE:
            return
        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.mutagenparser import MutagenParser
            cls.PARSERS['mutagen'] = MutagenParser
            cls.DEFAULT_PARSER = 'mutagen'
        except ImportError as mutagenparser_err:
            cls.PARSER_ERRORS.append(('mutagen', str(mutagenparser_err)))

        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.pydubeditor import PydubEditor
            cls.EDITORS['pydub'] = PydubEditor
            cls.DEFAULT_EDITOR = 'pydub'
        except ImportError as pydubeditor_err:
            cls.EDITOR_ERRORS.append(('pydub', str(pydubeditor_err)))

        try:
            # pylint: disable=import-outside-toplevel
            from musicbingo.mp3.ffmpegeditor import FfmpegEditor
            cls.EDITORS['ffmpeg'] = FfmpegEditor
            cls.DEFAULT_EDITOR = 'ffmpeg'
        except ImportError as ffmpegeditor_err:
            cls.EDITOR_ERRORS.append(('ffmpeg', str(ffmpegeditor_err)))

        cls.PROBE_DONE = True
