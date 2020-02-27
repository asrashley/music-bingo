"""
classes to represent a song and the metadata associated with it
"""

from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

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

    def as_dict(self) -> Dict[str, Any]:
        """convert metadata into a dictionary"""
        retval: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is None:
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


class HasParent:
    """interface used for classes that have a parent-child relationship"""
    def __init__(self, filename: str, parent: Optional["HasParent"] = None):
        self._parent = parent
        self.filename = filename
        self._fullpath: Optional[Path] = None

    def get_fullpath(self) -> Optional[Path]:
        """return absolute name of this object"""
        if self._fullpath is None and self._parent is not None:
            if self._parent.fullpath is None:
                return None
            self._fullpath = self._parent.fullpath / self.filename
        return self._fullpath

    def set_fullpath(self, path: Union[Path, str]) -> None:
        """set absolute path of this song"""
        if isinstance(path, str):
            path = Path(path)
        self._fullpath = path

    fullpath = property(get_fullpath, set_fullpath)


# pylint: disable=too-many-instance-attributes
class Song(Metadata, HasParent):
    """
    Represents one Song.
    'Song' objects are objects which possess a title,  artist,
    and a fullpath to the file
    Arguments:
    :parent: Directory that contains this song
    :ref_id: unique ID for referring to the track in a list
    """

    def __init__(self, filename: str, parent: Optional[HasParent], ref_id: int,
                 **kwargs) -> None:
        HasParent.__init__(self, filename=filename, parent=parent)
        Metadata.__init__(self, **kwargs)
        self.ref_id = ref_id

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

    def pick(self, props: Iterable[str]) -> Tuple:
        """select "props" attributes from this Song"""
        items = [getattr(self, name) for name in props]
        return tuple(items)

    SAFE_CHARS = set([' ', '_', '(', ')', ',', ])

    @staticmethod
    def clean(text: str) -> str:
        """remove all non-ascii characters from a string"""
        if not isinstance(text, str):
            text = text.decode('utf-8')
        return ''.join(filter(lambda c: c.isalnum() or c in Song.SAFE_CHARS,
                              list(text)))

    @staticmethod
    def choose_collection_title(songs: Iterable["Song"]) -> str:
        """
        Try to find a suitable title for a collection of songs.
        """
        folders: Set[str] = set()
        parents: Set[str] = set()
        for song in songs:
            if song._parent is not None:
                folders.add(song._parent.filename)
                if (song._parent._parent is not None and
                        song._parent._parent._parent is not None):
                    parents.add(song._parent._parent.filename)
        if len(folders) == 1:
            return folders.pop()
        if len(parents) == 1:
            return parents.pop()
        return ''

    def __len__(self):
        return 1

    def __str__(self):
        if self.song_id is not None:
            song_id = f' song_id={self.song_id}'
        else:
            song_id = ''
        return f"{self.title} - {self.artist} - ref={self.ref_id}{song_id}"

    def __key(self):
        filename = self.filename
        if self._parent is not None:
            filename = str(self.fullpath)
        return (self.title, self.artist, filename, self.duration)

    def __eq__(self, other: object):
        return isinstance(other, Song) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())
