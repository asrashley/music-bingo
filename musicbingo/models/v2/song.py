import copy
import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import composite_key, flush, select  # type: ignore

from musicbingo.models.db import db
from .directory import Directory

class Song(db.Entity): # type: ignore
    __plural__ = 'Songs'

    pk = PrimaryKey(int, auto=True)
    directory = Required(Directory)
    filename = Required(str, index=True)  # relative to directory
    title = Required(str, index=True)
    artist = Optional(str)
    duration = Required(int, default=0, unsigned=True)
    channels = Required(int, unsigned=True)
    sample_rate = Required(int, unsigned=True)
    sample_width = Required(int, unsigned=True)
    bitrate = Required(int, unsigned=True)
    album = Optional(str)
    tracks = Set('Track')
    composite_key(directory, filename)

    @classmethod
    def import_json(cls, items, options,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> None:
        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls] = pk_map
        skipped = []
        for item in items:
            song = cls.lookup(item, pk_maps)
            fields = cls.from_json(item, pk_maps)
            skip = False
            if fields['directory'] is None:
                print('Failed to find parent {0} for song: "{1}"'.format(
                    item.get('directory',None), fields['filename']))
                skip = True
            elif options.exists == True:
                dirname = fields['directory'].absolute_path(options)
                filename = dirname.joinpath(fields['filename'])
                if not filename.exists():
                    skip = True
            if skip:
                alternative = cls.search_for_song(item)
                if alternative:
                    pk_map[item['pk']] = alternative.pk
                else:
                    skipped.append(item)
                print('Skipping song "{0}" (alternative = {1})'.format(
                    filename, pk_map.get(item['pk'], "none")))
                continue
            if song is None:
                song = cls(**fields)
            else:
                for key, value in fields.items():
                    if key != 'pk':
                        setattr(song, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = song.pk
        for item in skipped:
            alternative = cls.search_for_song(item)
            if alternative:
                print('Found alternative for {0} missing song {1}'.format(
                    alternative.pk, item))
                pk_map[item['pk']] = alternative.pk
            else:
                print('Failed to find an alterative for Song: {0}'.format(item))
                print('Adding the Song anyway')
                fields = cls.from_json(item, pk_maps)
                song = cls(**fields)
                if 'pk' in item:
                    pk_map[item['pk']] = song.pk
                flush()

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Song"]:
        if 'pk' not in item:
            return cls.search_for_song(item)
        try:
            song = Song.get(pk=item['pk'])
        except KeyError:
            song = None
        if song is None and Song in pk_maps and item['pk'] in pk_maps[Song]:
            song = Song.get(pk=pk_maps[Song][item['pk']])
        if song is None:
            song = cls.search_for_song(item)
        return song

    @classmethod
    def search_for_song(cls, item: typing.Dict[str, typing.Any]) -> typing.Optional["Song"]:
        """
        Try to match this item to a song already in the database.
        """
        try:
            filename = item['filename']
            title = item['title']
            artist = item['artist']
            album = item['album']
        except KeyError:
            return None
        result = select(song for song in Song # type: ignore
                        if song.filename == filename
                        and song.title == title
                        and song.artist == artist
                        and song.album == album)
        count = result.count()
        if count == 1:
            return result.first()
        if count == 0:
            result = select(song for song in Song # type: ignore
                            if song.filename == filename
                            and song.title == title
                            and song.artist == artist)
            count = result.count()
        if count == 1:
            return result.first()
        if count > 1:
            result = result.filter(lambda song: song.duration == item['duration'])
            count = result.count()
        if count > 0:
            return result.first()
        return None

    @classmethod
    def from_json(cls, item: typing.Dict, pk_maps) -> typing.Dict:
        """
        converts any fields in item to Python objects
        """
        item = copy.copy(item)
        parent = Directory.get(pk=item['directory'])
        if parent is None and item['directory'] in pk_maps[Directory]:
            parent = Directory.get(pk=pk_maps[Directory][item['directory']])
        item['directory'] = parent
        if 'classtype' in item:
            del item['classtype']
        if 'tracks' in item:
            del item['tracks']
        for field in ['filename', 'title', 'artist', 'album']:
            if field in item and len(item[field]) > 1:
                if item[field][0] == '"' and item[field][-1] == '"':
                    item[field] = item[field][1:-1]
        return item
