"""factory method for creating an MP3 engine"""

from typing import List, Optional, Type

from musicbingo.mp3.editor import MP3Editor
from musicbingo.mp3.parser import MP3Parser

PARSERS: List[Type[MP3Parser]] = []
EDITORS: List[Type[MP3Editor]] = []

try:
    from musicbingo.mp3.mutagenparser import MutagenParser
    PARSERS.append(MutagenParser)
except ImportError as err:
    print(err)

try:
    from musicbingo.mp3.pydubeditor import PydubEditor
    EDITORS.append(PydubEditor)
except ImportError as err:
    print(err)

class MP3Factory:
    """Class for creating MP3Editor and MP3Parser instances"""

    @classmethod
    def create_editor(cls, editor: Optional[str] = None) -> MP3Editor:
        """
        Create an MP3Editor.
        If editor==None, the factory will pick the first one that
        is supported.
        """
        editor_class: Optional[Type[MP3Editor]] = None
        if editor is None:
            editor_class = EDITORS[0]
        else:
            editor = editor.lower()
            for ecls in EDITORS:
                if ecls.__name__.lower() == editor:
                    editor_class = ecls
                    break
        if editor_class is None:
            raise NotImplementedError(f'Unknown editor {editor}')
        return editor_class()

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
