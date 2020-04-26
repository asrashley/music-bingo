import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import composite_key, flush, select  # type: ignore

from musicbingo.models.db import db
from musicbingo.primes import PRIME_NUMBERS

from .bingoticket import BingoTicket
from .game import Game
from .song import Song

class Track(db.Entity):
    __plural__ = 'Tracks'

    pk = PrimaryKey(int, auto=True)
    number = Required(int, unsigned=True)
    bingo_tickets = Set(BingoTicket)
    start_time = Required(int, unsigned=True)
    game = Required(Game)
    song = Required(Song)
    composite_key(number, game)

    @classmethod
    def import_json(cls, items, options,
                     pk_maps: typing.Dict[typing.Type[db.Entity],
                                          typing.Dict[int, int]]) -> None:
        """
        Try to import all of the tracks described in 'items'.
        Returns a map from the pk listed in 'items' to the
        primary key of each imported track.
        """
        pk_map: typing.Dict[int, int] = {}
        pk_maps[cls] = pk_map
        for item in items:
            track = cls.lookup(item, pk_maps)
            fields = cls.from_json(item, pk_maps)
            if fields['song'] is None:
                print('Skipping track as failed to find song: {0}'.format(item))
                continue
            if track is None:
                #print(fields)
                track = cls(**fields)
            else:
                for key, value in fields.items():
                    if key != 'pk':
                        setattr(track, key, value)
            flush()
            if 'pk' in item:
                pk_map[item['pk']] = track.pk

    @classmethod
    def from_json(cls, item: typing.Dict[str, typing.Any], pk_maps) -> typing.Dict[str, typing.Any]:
        """
        converts any fields in item into a dictionary ready for use Track constructor
        """
        retval = {}
        for field in ['pk', 'number', 'start_time', 'game', 'song']:
            try:
                value = item[field]
                if field == 'start_time' and isinstance(value, str):
                    value = round(from_isodatetime(value).total_seconds() * 1000)
                if field == 'song':
                    song = Song.lookup(dict(pk=value), pk_maps)
                    if song is None:
                        print('map', value, pk_maps[Song].get(value, None))
                    value = song
                retval[field] = value
            except KeyError:
                if field == 'song':
                    retval[field] = Song.search_for_song(item)
        retval['game'] = Game.get(pk=item['game'])
        if 'prime' in item:
            retval['number'] = PRIME_NUMBERS.index(int(item['prime']))
        return retval

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Track"]:
        """
        Check to see if 'item' references a track that is already in the database
        """
        try:
            track = Track.get(pk=item['pk'])
        except KeyError:
            track = None
        if track is not None:
            return track
        if 'prime' in item:
            number = PRIME_NUMBERS.index(int(item['prime']))
        else:
            number = item['number']
        try:
            game = Game.get(pk=item['game'])
        except KeyError:
            return None
        return Track.get(number=number, game=game)



    @property
    def prime(self) -> int:
        return PRIME_NUMBERS[self.number]
