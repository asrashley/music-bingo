"""
Mock implementation of MP3Parser interface
"""
from pathlib import Path
from typing import Dict

from musicbingo.song import Metadata
from musicbingo.mp3.parser import MP3Parser

class MockMP3Parser(MP3Parser):
    """
    Mock implementation of MP3Parser interface
    """
    def __init__(self, testcases: Dict[str, Metadata]) -> None:
        self.testcases: Dict[str, Metadata] = testcases

    def parse(self, filename: Path) -> Metadata:
        """Extract the metadata from an MP3 file"""
        try:
            return self.testcases[filename.name]
        except KeyError:
            raise IOError(f"File not found {filename.name}")
