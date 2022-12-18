"""
Mixin for classes that make use of MP3 files
"""
from typing import Union

from musicbingo.assets import MP3Asset
from musicbingo.song import Song

from .filemode import FileMode
from .mp3file import MP3File

class UsesMP3Mixin:
    """Mixin for classes that make use of MP3 files"""

    def use(self, item: Union[Song, MP3Asset]) -> MP3File:
        """
        Create an MP3File object from a song or an asset.
        """
        return MP3File(item.fullpath, FileMode.READ_ONLY, start=0,
                       end=int(item.duration), metadata=item)
