"""
Interface for playing MP3 files
"""
from abc import ABC, abstractmethod

from musicbingo.progress import Progress

from .mp3file import MP3File
from .uses_mixin import UsesMP3Mixin

class MP3Player(UsesMP3Mixin, ABC):
    """Interface for playing MP3 files"""

    @abstractmethod
    def play(self, mp3file: MP3File, progress: Progress) -> None:
        """play the specified MP3 file"""
        raise NotImplementedError()
