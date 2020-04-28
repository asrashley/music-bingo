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
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> typing.Dict[int, int]:
        pk_map: typing.Dict[int, int] = {}
        for item in items:
            song = cls.lookup(item, pk_maps)
            item = cls.from_json(item, pk_maps)
            if song is None:
                if options.exists == True:
                    dirname = item['directory'].absolute_path(options)
                    filename = dirname.joinpath(item['filename'])
                    if not filename.exists():
                        alternative = cls.search_for_song(item)
                        if alternative:
                            pk_map[item['pk']] = alternative.pk
                        print('Song not found "{0}" (alternative = {1})'.format(
                              filename, pk_map.get(item['pk'], "none")))
                        print(f'    {item}')
                        continue
                song = cls(**item)
            else:
                for key, value in item.items():
                    if key != 'pk':
                        setattr(song, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = song.pk
        #print(pk_map)
        return pk_map

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
        Try to match this track to a song in the database. Only used when importing
        a JSON file that used the v1 database schema.
        """
        try:
            filename = item['filename'] 
            title = item['title'] 
            artist = item['artist']
            album = item['album']
        except KeyError:
            return None
        result = select(song for song in Song if song.filename == filename
                        and song.title == title
                        and song.artist == artist
                        and song.album == album)
        count = result.count()
        if count == 1:
            return result.first()
        if count == 0:
            result = select(song for song in Song if song.filename == filename
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
        if parent is None:
            print(pk_maps.keys())
        if parent is None and item['directory'] in pk_maps[Directory]:
            parent = Directory.get(pk=pk_maps[Directory][item['directory']])
        item['directory'] = parent
        if 'classtype' in item:
            del item['classtype']
        if 'tracks' in item:
            del item['tracks']
        return item


