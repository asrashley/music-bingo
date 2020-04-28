import copy
from pathlib import Path
import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import flush  # type: ignore

from musicbingo.models.db import db

class Directory(db.Entity): # type: ignore
    __plural__ = 'Directories'
    
    pk = PrimaryKey(int, auto=True)
    name = Required(str, unique=True, index=True)
    songs = Set('Song')
    title = Required(str)
    artist = Optional(str)
    directories = Set('Directory', reverse='directory')
    directory = Optional('Directory', reverse='directories')

    @classmethod
    def import_json(cls, items, options,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]])  -> typing.Dict[int, int]:
        pk_map: Dict[int, int] = {}
        for item in items:
            item = cls.from_json(item, options, pk_maps)
            directory = cls.lookup(item, options, pk_map)
            if item.get('directory', None):
                item['directory'] = Directory.get(pk=item['directory'])
            if directory is None:
                #print(item)
                directory = Directory(**item)
            else:
                for key, value in item.items():
                    if key not in ['pk', 'name']:
                        setattr(directory, key, value)
            flush()
            pk_map[item['pk']] = directory.pk
        for item in items:
            directory = cls.lookup(item, options, pk_map)
            if directory.directory is None and item['directory'] is not None:
                parent = Directory.get(pk=item['directory'])
                if parent is None and item['directory'] in pk_map:
                    parent = Directory.get(pk=pk_map[item['directory']])
                if parent is not None:
                    directory.directory = parent
                    flush()
        return pk_map
    
    @classmethod
    def from_json(cls, item: typing.Dict[str, typing.Any], options, pk_maps) -> typing.Dict[str, typing.Any]:
        """
        converts any fields in item into a dictionary ready for use Track constructor
        """
        retval = {}
        for field, value in item.items():
            if field not in ['directories', 'songs']:
                retval[field] = value
        clipdir = str(options.clips())
        if retval['name'].startswith(clipdir):
            retval['name'] = retval['name'][len(clipdir):]
        if retval['name'] == "":
            retval['name'] = "."
        return retval

    @classmethod
    def lookup(cls, item, options, pk_map) -> typing.Optional["Directory"]:
        try:
            rv = Directory.get(pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None:
            clipdir = str(options.clips())
            name = item['name']
            if name.startswith(clipdir):
                name = name[len(clipdir):]
            if name == "":
                name = "."
            rv = Directory.get(name=name)
        return rv

    def absolute_path(self, options) -> Path:
        """
        Get the absolute path of this directory
        """
        if self.directory is None:
            pdir = options.clips()
        else:
            pdir = self.directory.absolute_path(options)
        return pdir.joinpath(self.name)