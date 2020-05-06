import copy
from pathlib import Path
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
                    pk_maps: typing.Dict[str, typing.Dict[int, int]]) -> None:
        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls.__name__] = pk_map
        skipped = []
        for item in items:
            fields = cls.from_json(item, pk_maps)
            #song = cls.lookup(fields, pk_maps)
            song = cls.search_for_song(fields, pk_maps)
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
                alternative = cls.search_for_song(item, pk_maps)
                if alternative:
                    pk_map[item['pk']] = alternative.pk
                else:
                    skipped.append(item)
                continue
            if song is None:
                #print(fields)
                if 'pk' in fields:
                    del fields['pk']
                song = cls(**fields)
            else:
                #print(fields)
                #print(song.to_dict())
                for key, value in fields.items():
                    if key not in ['pk', 'filename']:
                        setattr(song, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = song.pk
        for item in skipped:
            alternative = cls.search_for_song(item, pk_maps)
            if alternative:
                print('Found alternative for {0} missing song {1}'.format(
                    alternative.pk, item))
                pk_map[item['pk']] = alternative.pk
            else:
                print('Failed to find an alterative for Song: {0}'.format(item))
                print('Adding the Song anyway')
                lost = Directory.get(name="lost+found")
                if lost is None:
                    lost = Directory(name="lost+found", title="lost & found", artist="Orphaned songs")
                fields = cls.from_json(item, pk_maps)
                if 'directory' not in fields or fields['directory'] is None:
                    fields['directory'] = lost
                song = cls(**fields)
                if 'pk' in item:
                    pk_map[item['pk']] = song.pk
                flush()

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Song"]:
        song_pk = item['pk']
        if song_pk in pk_maps["Song"]:
            song_pk = pk_maps["Song"][song_pk]
        try:
            song = Song.get(pk=song_pk) #, filename=item['filename'])
        except KeyError:
            song = None
        return song

    @classmethod
    def search_for_song(cls, item: typing.Dict[str, typing.Any], pk_maps) -> typing.Optional["Song"]:
        """
        Try to match this item to a song already in the database.
        """
        try:
            filename = item['filename']
        except KeyError:
            return None
        directory_pk = item.get("directory", None)
        if directory_pk is not None and directory_pk in pk_maps["Directory"]:
            directory_pk = pk_maps["Directory"][directory_pk]
        if directory_pk is not None:
            song = Song.get(directory=directory_pk, filename=filename)
            if song is not None:
                return song
        try:
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
        parent = None
        parent_pk = item.get('directory', None)
        if parent_pk is not None and parent_pk in pk_maps["Directory"]:
            parent_pk = pk_maps["Directory"][parent_pk]
        if parent_pk is not None:
            parent = Directory.get(pk=parent_pk)
        item['directory'] = parent
        if 'classtype' in item:
            del item['classtype']
        if 'fullpath' in item:
            if 'filename' not in item:
                item['filename'] = Path(item['fullpath']).name
            del item['fullpath']
        if 'tracks' in item:
            del item['tracks']
        for field in ['filename', 'title', 'artist', 'album']:
            if field in item and len(item[field]) > 1:
                if item[field][0] == '"' and item[field][-1] == '"':
                    item[field] = item[field][1:-1]
        return item
