"""MP3 parsing functions and classes"""

from abc import ABC, abstractmethod

from musicbingo.song import Metadata

class MP3Parser(ABC):
    """Interface for the MP3 parsing functions"""

    @abstractmethod
    def parse(self, directory: str, filename: str) -> Metadata:
        """Extract the metadata from an MP3 file"""
        raise NotImplementedError()
