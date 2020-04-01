"""
class to represent the metadata associated with a Song
"""

import re
from typing import Any, Dict, Optional, Set

from .duration import Duration


#pylint: disable=too-many-instance-attributes
class Metadata:
    """Data about a song"""

    FEAT_RE = re.compile(r'[\[(](feat[.\w]*|ft\.?)[)\]]', re.IGNORECASE)
    DROP_RE = re.compile(r'\s*[\[(](clean|[\w\s]+ ' +
                         r'(edit|mix|remix)|edit|explicit|remastered[ \d]*|' +
                         r'live|main title|mono|([\d\w"]+ single|album|single)' +
                         r' version)[)\]]\s*', re.IGNORECASE)

    def __init__(self,
                 title: str,  # the title of the Song
                 artist: str,  # the artist credited with the song
                 duration: Duration,  # duration of song (in milliseconds)
                 sample_width: int,  # bits per sample (e.g. 16)
                 channels: int,  # number of audio channels (e.g. 2)
                 sample_rate: int,  # samples per second (e.g. 44100)
                 bitrate: int,  # bitrate, in kilobits per second
                 album: str = '',  # the artist credited with the song
                 song_id: int = 0,  # a prime number used during game generation
                 start_time: int = 0  # position of song in playlist (in milliseconds)
                 ):
        self.title = self._correct_title(title.split('[')[0])
        self.artist = self._correct_title(artist)
        self.duration = duration
        self.sample_width = sample_width
        self.channels = channels
        self.sample_rate = sample_rate
        self.bitrate = bitrate
        self.album = album
        self.song_id = song_id
        self.start_time = start_time

    def as_dict(self, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
        """convert metadata into a dictionary"""
        retval: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None or key[0] == '_':
                continue
            if exclude is not None and key in exclude:
                continue
            retval[key] = value
        return retval

    def _correct_title(self, title: str) -> str:
        """Try to remove 'cruft' from title or artist.
        Tries to remove things like '(radio edit)' or '(single version)'
        from song titles, as they are not useful and can make the text
        too long to fit within a Bingo square
        """
        title = re.sub(self.DROP_RE, '', title)
        return re.sub(self.FEAT_RE, 'ft.', title)
