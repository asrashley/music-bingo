"""
classes to represent a song and the metadata associated with it
"""

import re
from typing import List, NamedTuple, Optional, SupportsInt

class Duration(SupportsInt):
    """Duration of a song (in milliseconds)"""
    def __init__(self, value) -> None:
        if isinstance(value, str):
            value = self.parse(value)
        self._value = value

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return self.format()

    def __add__(self, dur: "Duration") -> "Duration":
        return Duration(int(self) + int(dur))

    def __iadd__(self, dur: "Duration") -> "Duration":
        self._value += int(dur)
        return self

    def __floordiv__(self, other: int) -> int:
        return self._value // other

    @staticmethod
    def parse(time_str: str) -> "Duration":
        """Convert string in the form MM:SS to milliseconds"""
        parts = time_str.split(':')
        parts.reverse()
        secs = 0
        while parts:
            secs = (60*secs) + int(parts.pop(), 10)
        return Duration(secs * 1000)

    def format(self) -> str:
        """convert the time in milliseconds to a MM:SS form"""
        secs: int = self._value // 1000
        seconds = secs % 60
        minutes = secs // 60
        return '{0:d}:{1:02d}'.format(minutes, seconds)

class Metadata(NamedTuple):
    """the title of the Song"""
    title: str
    """the artist credited with the song"""
    artist: str
    """the artist credited with the song"""
    album: str = ''
    """a prime number used during game generation"""
    song_id: int = 0
    """duration of song (in milliseconds)"""
    duration: Duration = Duration(0)
    """position of song in playlist (in milliseconds)"""
    start_time: int = 0
    """filename of the MP3 file (name without path)"""
    filename: str = ''
    """location of the MP3 file (name with path)"""
    filepath: str = ''

class HasParent:
    """interface used for classes that have a parent-child relationship"""
    def __init__(self, parent: Optional["HasParent"]):
        self._parent = parent

#pylint: disable=too-many-instance-attributes
class Song(HasParent):
    """
    Represents one Song.
    'Song' objects are objects which possess a title,  artist,
    and a filepath to the file
    Arguments:
    parent   -- Directory that contains this song
    ref_id   -- unique ID for referring to the track in a list
    title    -- the title of the Song
    artist   -- the artist credited with the song
    song_id  -- a prime number used during game generation (optional)
    duration -- duration of song (in milliseconds)
    filepath -- location of the MP3 file
    """
    FEAT_RE = re.compile(r'[\[(](feat[.\w]*|ft\.?)[)\]]', re.IGNORECASE)
    DROP_RE = re.compile(r'\s*[\[(](clean|[\w\s]+ ' +
                         r'(edit|mix|remix)|edit|explicit|remastered[ \d]*|' +
                         r'live|main title|mono|([\d\w"]+ single|album|single)' +
                         r' version)[)\]]\s*', re.IGNORECASE)

    def __init__(self, parent: Optional[HasParent], ref_id: int,
                 metadata: Metadata) -> None:
        super(Song, self).__init__(parent)
        self.ref_id = ref_id
        self.title: str = ''
        self.artist: str = ''
        self.album: str = ''
        self.song_id: int = 0
        self.duration: int = 0
        self.start_time: int = 0
        self.filename: str = ''
        self.filepath: str = ''
        for key, value in metadata._asdict().items():
            setattr(self, key, value)
        self.title = self._correct_title(self.title.split('[')[0])
        self.artist = self._correct_title(self.artist)

    def _correct_title(self, title: str) -> str:
        """Try to remove 'cruft' from title or artist.
        Tries to remove things like '(radio edit)' or '(single version)'
        from song titles, as they are not useful and can make the text
        too long to fit within a Bingo square
        """
        title = re.sub(self.DROP_RE, '', title)
        return re.sub(self.FEAT_RE, 'ft.', title)

    def find(self, ref_id: int) -> Optional["Song"]:
        """Find a Song by its ref_id"""
        if self.ref_id == ref_id:
            return self
        return None

    def marshall(self, exclude: Optional[List[str]] = None) -> dict:
        """Convert attributes of this object to a dictionary"""
        retval = {}
        if exclude is None:
            exclude = []
        for key, value in self.__dict__.items():
            if key[0] == '_' or key in exclude or value is None:
                continue
            retval[key] = value
        return retval

    @staticmethod
    def clean(text: str) -> str:
        """remove all non-ascii characters from a string"""
        if not isinstance(text, str):
            text = text.decode('utf-8')
        return ''.join(filter(lambda c: c.isalnum(), list(text)))


    def __len__(self):
        return 1

    def __str__(self):
        if self.song_id is not None:
            song_id = f' song_id={self.song_id}'
        else:
            song_id = ''
        return f"{self.title} - {self.artist} - ref={self.ref_id}{song_id}"

    def __key(self):
        return (self.title, self.artist, self.filepath, self.duration)

    def __eq__(self, other: object):
        return isinstance(other, Song) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())
