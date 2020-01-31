"""
utility functions to hold the names of the "Extra-Files" assets
used by musicbingo.
"""
from typing import NamedTuple, Tuple
import os
import sys

class MP3Asset(NamedTuple):
    """used to create arguments for MP3File class"""
    filename: str
    duration: int

class Assets:
    """names of each asset in the "Extra-Files" directory"""
    ASSET_DIRECTORY = 'Extra-Files'
    TRANSITION = ('TRANSITION.mp3', 1008)
    START_COUNTDOWN = ('START.mp3', 9048)
    QUIZ_COUNTDOWN = ('countdown.mp3', 10998)

    @classmethod
    def icon_file(cls) -> str:
        """Icon used by gui"""
        if sys.platform.startswith('win'):
            return cls.get_data_filename('Icon.ico')
        return cls.get_data_filename('Icon.gif')

    @classmethod
    def transition(cls) -> MP3Asset:
        """Sound effect that is placed between clips"""
        return cls.get_file_and_duration(cls.TRANSITION)

    @classmethod
    def countdown(cls) -> MP3Asset:
        """MP3 file that gives a 5,4,3,2,1 countdown"""
        return cls.get_file_and_duration(cls.START_COUNTDOWN)

    @classmethod
    def quiz_countdown(cls) -> MP3Asset:
        """MP3 file that gives a 10, 9, .. 2,1 countdown"""
        return cls.get_file_and_duration(cls.QUIZ_COUNTDOWN)

    @classmethod
    def get_data_filename(cls, filename: str) -> str:
        """Return full path to file in "Extra-Files" directory"""
        extra_files = os.path.join(os.getcwd(), cls.ASSET_DIRECTORY)
        return os.path.join(extra_files, filename)

    @classmethod
    def get_file_and_duration(cls, item: Tuple[str, int]) -> MP3Asset:
        """return filename and duration (in milliseconds)"""
        name, dur = item
        return MP3Asset(cls.get_data_filename(name), dur)
