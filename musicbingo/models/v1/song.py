import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore

from musicbingo.models.db import db, schema_version
from .directory import Directory
from .songbase import SongBase

assert schema_version == 1

class Song(SongBase):
    __plural__ = 'Songs'

    directory = Required(Directory)
    composite_key(directory, SongBase.filename)

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Song"]:
        try:
            song = Song.get(pk=item['pk'])
        except KeyError:
            song = None
        return song

    @classmethod
    def from_json(cls, item, pk_maps):
        """
        converts any fields in item to Python objects
        """
        parent = Directory.get(pk=item['directory'])
        if parent is None and item['directory'] in pk_maps["Directory"]:
            parent = Directory.get(pk=pk_maps["Directory"][item['directory']])
        item['directory'] = parent
