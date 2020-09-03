"""factory method for creating an MP3 engine"""

from typing import Dict, List, Optional, Type

from musicbingo.mp3.editor import MP3Editor
from musicbingo.mp3.parser import MP3Parser

PARSERS: List[Type[MP3Parser]] = []
EDITORS: Dict[str, Type[MP3Editor]] = {}
DEFAULT_EDITOR: Optional[str] = None

try:
    from musicbingo.mp3.mutagenparser import MutagenParser
    PARSERS.append(MutagenParser)
except ImportError as err:
    print(err)

try:
    from musicbingo.mp3.pydubeditor import PydubEditor
    EDITORS['pydub'] = PydubEditor
    DEFAULT_EDITOR = 'pydub'
except ImportError as err:
    print(err)

try:
    from musicbingo.mp3.ffmpegeditor import FfmpegEditor
    EDITORS['ffmpeg'] = FfmpegEditor
    DEFAULT_EDITOR = 'ffmpeg'
except ImportError as err:
    print(err)


class MP3Factory:
    """Class for creating MP3Editor and MP3Parser instances"""

    @classmethod
    def create_editor(cls, editor: Optional[str] = None) -> MP3Editor:
        """
        Create an MP3Editor.
        If editor==None, the factory will pick one that is supported.
        """
        if editor is None:
            if DEFAULT_EDITOR is None:
                raise NotImplementedError('Failed to find any MP3 editor')
            editor = DEFAULT_EDITOR
        editor = editor.lower()
        try:
            return EDITORS[editor]()
        except KeyError as err:
            raise NotImplementedError(f'Unknown editor {editor}') from err

    @classmethod
    def create_parser(cls, parser: Optional[str] = None) -> MP3Parser:
        """
        Create an MP3Parser.
        If parser==None, the factory will pick the first one that
        is supported.
        """
        parser_class: Optional[Type[MP3Parser]] = None
        if parser is None:
            parser_class = PARSERS[0]
        else:
            parser = parser.lower()
            for pcls in PARSERS:
                if pcls.__name__.lower() == parser:
                    parser_class = pcls
                    break
        if parser_class is None:
            raise NotImplementedError(f'Unknown parser {parser}')
        return parser_class()
