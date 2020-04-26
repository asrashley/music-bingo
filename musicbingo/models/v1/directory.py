import copy
import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import flush  # type: ignore

from musicbingo.models.db import db


class Directory(db.Entity): # type: ignore
    pk = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    songs = Set('Song')
    title = Required(str)
    artist = Optional(str)
    directories = Set('Directory', reverse='directory')
    directory = Optional('Directory', reverse='directories')

    @classmethod
    def import_json(cls, items, pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]])  -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in items:
            item = copy.copy(item)
            for field in ['directories', 'songs']:
                try:
                    del item[field]
                except KeyError:
                    pass
            directory = cls.lookup(item, pk_map)
            if item['directory']:
                item['directory'] = Directory.get(pk=item['directory'])
            if directory is None:
                directory = Directory(**item)
            else:
                for key, value in item.items():
                    if key not in ['pk', 'name']:
                        setattr(directory, key, value)
            flush()
            pk_map[item['pk']] = directory.pk
        for item in items:
            directory = cls.lookup(item, pk_map)
            if directory.directory is None and item['directory'] is not None:
                parent = Directory.get(pk=item['directory'])
                if parent is None and item['directory'] in pk_map:
                    parent = Directory.get(pk=pk_map[item['directory']])
                if parent is not None:
                    directory.directory = parent
                    flush()
        return pk_map

    @classmethod
    def lookup(cls, item, pk_map) -> typing.Optional["Directory"]:
        try:
            rv = Directory.get(pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None:
            rv = Directory.get(name=item['name'])
        return rv

