"""MP3 parsing functions and classes"""

from abc import ABC, abstractmethod
from pathlib import Path

from musicbingo.song import Metadata


class MP3Parser(ABC):
    """Interface for the MP3 parsing functions"""

    @abstractmethod
    def parse(self, filename: Path) -> Metadata:
        """Extract the metadata from an MP3 file"""
        raise NotImplementedError()
