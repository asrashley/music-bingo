import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import flush  # type: ignore

from musicbingo.models.db import db, schema_version

assert schema_version == 1

class SongBase(db.Entity): # type: ignore
    pk = PrimaryKey(int, auto=True)
    filename = Required(str)  # relative to directory
    title = Required(str)
    artist = Optional(str)
    duration = Required(int, default=0, unsigned=True)
    channels = Required(int, unsigned=True)
    sample_rate = Required(int, unsigned=True)
    sample_width = Required(int, unsigned=True)
    bitrate = Required(int, unsigned=True)
    album = Optional(str)

    @classmethod
    def import_json(cls, items,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> None:
        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls] = pk_map
        for item in items:
            song = cls.lookup(item, pk_maps)
            for key in list(item.keys()):
                value = item[key]
                if isinstance(value, (list, dict)) or key == 'classtype':
                    del item[key]
            cls.from_json(item, pk_maps)
            if song is None:
                song = cls(**item)
            else:
                for key, value in item.items():
                    if key != 'pk':
                        setattr(song, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = song.pk
