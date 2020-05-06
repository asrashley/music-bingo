import copy
from pathlib import Path
import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import flush, select # type: ignore

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
                    pk_maps: typing.Dict[str, typing.Dict[int, int]]) -> None:
        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls.__name__] = pk_map
        skipped = []
        for item in items:
            fields = cls.from_json(item, options, pk_maps)
            directory = cls.lookup(fields, options, pk_map)
            try:
                pk = fields['pk']
                del fields['pk']
            except KeyError:
                pk = None
            if directory is None:
                #print(fields)
                directory = Directory(**fields)
                if options.exists:
                    if not directory.absolute_path(options).exists():
                        print(f'Skipping missing directory: "{directory.name}"')
                        directory.delete()
                        skipped.append(item)
                        continue
            else:
                for key, value in fields.items():
                    if key not in ['name']:
                        setattr(directory, key, value)
            flush()
            if pk is not None:
                pk_map[pk] = directory.pk
        for item in items:
            directory = cls.lookup(item, options, pk_map)
            if directory is None:
                continue
            if directory.directory is None and item['directory'] is not None:
                parent = Directory.get(pk=item['directory'])
                if parent is None and item['directory'] in pk_map:
                    parent = Directory.get(pk=pk_map[item['directory']])
                if parent is not None:
                    directory.directory = parent
                    flush()
        for item in skipped:
            directory = cls.search_for_directory(item)
            if directory is not None:
                pk_map[item['pk']] = directory.pk

    @classmethod
    def from_json(cls, item: typing.Dict[str, typing.Any], options, pk_map) -> typing.Dict[str, typing.Any]:
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
        if item.get('directory', None) is not None:
            retval['directory'] = cls.lookup(dict(pk=item['directory']), options, pk_map)
        return retval

    @classmethod
    def lookup(cls, item, options, pk_map) -> typing.Optional["Directory"]:
        """
        Check if this directory is already in the database
        """
        try:
            rv = Directory.get(pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None and 'name' in item:
            clipdir = str(options.clips())
            name = item['name']
            if name.startswith(clipdir):
                name = name[len(clipdir):]
            if name == "":
                name = "."
            rv = Directory.get(name=name)
        return rv

    @classmethod
    def search_for_directory(cls, item: typing.Dict[str, typing.Any]
        ) -> typing.Optional["Directory"]:
        """
        Try to match this item to a directory already in the database.
        """
        if 'name' in item:
            directory = Directory.get(name=item['name'])
            if directory is not None:
                return directory
        try:
            title = item['title']
            artist = item['artist']
        except KeyError:
            return None
        result = select(directory for directory in Directory # type: ignore
                        if directory.title == title
                        and directory.artist == artist)
        count = result.count()
        if count == 1:
            return result.first()
        return None

    def absolute_path(self, options) -> Path:
        """
        Get the absolute path of this directory
        """
        if self.directory is None:
            pdir = options.clips()
        else:
            pdir = self.directory.absolute_path(options)
        return pdir.joinpath(self.name)
