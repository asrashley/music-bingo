"""
utility functions to hold the names of the "Extra-Files" assets
used by musicbingo.
"""
from typing import Tuple
from pathlib import Path
import sys

from .duration import Duration
from .metadata import Metadata


class MP3Asset(Metadata):
    """used to create arguments for MP3File class"""

    def __init__(self, fullpath: Path, duration: int, sample_rate: int):
        super().__init__(title=fullpath.name,
                         artist='', duration=Duration(duration),
                         sample_width=16, bitrate=256, channels=2,
                         sample_rate=sample_rate)
        self.fullpath = fullpath


class Assets:
    """names of each asset in the "Extra-Files" directory"""
    ASSET_DIRECTORY = 'Extra-Files'
    TRANSITION = ('transition-{rate}.mp3', 1008)
    START_COUNTDOWN = ('start-{rate}.mp3', 9048)
    QUIZ_COUNTDOWN = ('countdown-{rate}.mp3', 10998)
    # pylint: disable=bad-whitespace
    QUIZ_COUNTDOWN_POSITIONS = {
        '10': (0, 880),
        '9': (880, 2000),
        '8': (2000, 2800),
        '7': (2800, 3880),
        '6': (3880, 5000),
        '5': (5000, 5920),
        '4': (5920, 6920),
        '3': (6920, 7920),
        '2': (7920, 8880),
        '1': (8880, 9920),
        '0': (9920, 10920)
    }

    @classmethod
    def icon_file(cls) -> Path:
        """Icon used by gui"""
        if sys.platform.startswith('win'):
            return cls.get_data_filename('Icon.ico')
        return cls.get_data_filename('Icon.gif')

    @classmethod
    def transition(cls, sample_rate: int) -> MP3Asset:
        """Sound effect that is placed between clips"""
        return cls.get_file_and_duration(cls.TRANSITION, sample_rate)

    @classmethod
    def countdown(cls, sample_rate: int) -> MP3Asset:
        """MP3 file that gives a 5,4,3,2,1 countdown"""
        return cls.get_file_and_duration(cls.START_COUNTDOWN, sample_rate)

    @classmethod
    def quiz_countdown(cls, sample_rate: int) -> MP3Asset:
        """MP3 file that gives a 10, 9, .. 2,1 countdown"""
        # note: there is only a 44100Hz version of the countdown audio
        sample_rate = 44100
        return cls.get_file_and_duration(cls.QUIZ_COUNTDOWN, sample_rate)

    @classmethod
    def get_data_filename(cls, filename: str) -> Path:
        """Return full path to file in "Extra-Files" directory"""
        extra_files = Path.cwd() / cls.ASSET_DIRECTORY
        if not extra_files.exists():
            # try relative to the top level of the source code
            basedir = Path(__file__).parents[1]
            extra_files = basedir / cls.ASSET_DIRECTORY
        if not extra_files.is_dir():
            raise IOError(f'Failed to find location of {cls.ASSET_DIRECTORY}')
        return extra_files / filename

    @classmethod
    def get_schema_filename(cls, filename: str) -> Path:
        """
        Return full path to JSON Schema file in "Extra-Files/schemas" directory
        """
        extra_files = Path.cwd() / cls.ASSET_DIRECTORY
        if not extra_files.exists():
            # try relative to the top level of the source code
            basedir = Path(__file__).parents[1]
            extra_files = basedir / cls.ASSET_DIRECTORY
        if not extra_files.is_dir():
            raise IOError(f'Failed to find location of {cls.ASSET_DIRECTORY}')
        return extra_files / "schemas" / filename

    @classmethod
    def get_file_and_duration(cls, item: Tuple[str, int], sample_rate: int) -> MP3Asset:
        """return filename and duration (in milliseconds)"""
        name, dur = item
        if sample_rate not in [48000, 44100]:
            sample_rate = 48000
        name = name.format(rate=sample_rate)
        return MP3Asset(cls.get_data_filename(name), dur, sample_rate)
