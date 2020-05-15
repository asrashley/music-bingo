"""
class to represent a song
"""
from pathlib import Path
from typing import cast, Any, Iterable, List, Optional, Set, Tuple, Union

from .hasparent import HasParent
from .metadata import Metadata
from . import models

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

    SAFE_CHARS = set([' ', '_', '(', ')', ',', ])

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

    def to_dict(self, exclude: Optional[List[str]] = None) -> dict:
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

    def model(self, session) -> Optional[models.Song]:
        """
        get database model for this song
        """
        if self._parent is None:
            return None
        directory = self._parent.model(session)
        return cast(
            Optional[models.Song],
            models.Song.get(session, filename=self.filename, directory=directory))

    def save(self, session, commit: bool = False) -> models.Song:
        """
        save song to database
        """
        assert self._parent is not None
        args = self.to_dict(exclude=['fullpath', 'ref_id'])
        directory = self._parent.model(session)
        assert directory is not None
        db_song = self.model(session)
        if db_song is None:
            db_song = models.Song(directory=directory, **args)
            session.add(db_song)
        if commit:
            session.commit()
        return db_song

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
        return f"{self.title} - {self.artist} - {self.ref_id}"

    def __key(self):
        filename = self.filename
        if self._parent is not None:
            filename = str(self.fullpath)
        return (self.title, self.artist, filename, self.duration)

    def __eq__(self, other: object):
        return isinstance(other, Song) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())
