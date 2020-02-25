"""
Mock implementation of MP3Editor interface
"""
from typing import Dict, List, Optional, Union

from musicbingo.mp3.editor import MP3Editor, MP3File, MP3FileWriter
from musicbingo.progress import Progress

from .mock_base import MockBase

class MockMP3Editor(MP3Editor, MockBase):
    """
    Mock implementation of MP3Editor interface
    """
    def __init__(self):
        self.output: Dict[str, Dict] = {}
        self.played: List[Dict[str, Union[str, int]]] = []

    def play(self, mp3file: MP3File, progress: Progress) -> None:
        src: Dict[str, Union[str, int]] = {
            'filename': mp3file.filename.name
        }
        if mp3file.start is not None:
            src['start'] = mp3file.start
        if mp3file.end is not None:
            src['end'] = mp3file.end
        if mp3file.headroom is not None:
            src['headroom'] = mp3file.headroom
        self.played.append(src)

    def _generate(self, destination: MP3FileWriter, progress: Progress) -> None:
        """
        generate output file, combining all input files
        """
        num_files = float(len(destination._files))
        contents: List[Dict] = []
        metadata: Optional[Dict] = None
        if destination._metadata is not None:
            metadata = destination._metadata._asdict()
        for index, mp3file in enumerate(destination._files, 1):
            progress.pct = 100.0 * index / num_files
            progress.text = f'Adding {mp3file.filename.name}'
            src: Dict[str, Union[str, int]] = {
                'filename': mp3file.filename.name
            }
            if mp3file.start is not None:
                src['start'] = mp3file.start
            if mp3file.end is not None:
                src['end'] = mp3file.end
            if mp3file.headroom is not None:
                src['headroom'] = mp3file.headroom
            contents.append(src)
        results: Dict[str, Union[List, Optional[Dict]]] = {
            'contents': contents,
            'metadata': metadata,
        }
        self.output[destination.filename.name] = self.flatten(results)
