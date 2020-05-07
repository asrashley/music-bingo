import datetime
import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import composite_key, flush, select  # type: ignore

from musicbingo.models.db import db
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.utils import from_isodatetime

from .game import Game
from .song import Song

class Track(db.Entity):
    __plural__ = 'Tracks'

    pk = PrimaryKey(int, auto=True)
    number = Required(int, unsigned=True)
    bingo_tickets = Set("BingoTicket")
    start_time = Required(int, unsigned=True)
    game = Required(Game)
    song = Required(Song)
    composite_key(number, game)

    @classmethod
    def import_json(cls, items, options,
                    pk_maps: typing.Dict[str, typing.Dict[int, int]]) -> None:
        """
        Try to import all of the tracks described in 'items'.
        Returns a map from the pk listed in 'items' to the
        primary key of each imported track.
        """
        pk_map: typing.Dict[int, int] = {}
        pk_maps["Track"] = pk_map
        for item in items:
            track = cls.lookup(item, pk_maps)
            fields = cls.from_json(item, pk_maps)
            if fields['song'] is None and 'filename' in fields:
                from .directory import Directory
                print('Failed to find song, adding it to lost+found directory: {0}'.format(item))
                lost = Directory.get(name="lost+found")
                if lost is None:
                    lost = Directory(name="lost+found", title="lost & found", artist="Orphaned songs")
                song_fields = Song.from_json(item, pk_maps)
                song_fields['directory'] = lost
                for field in list(fields.keys()) + ["bingo_tickets", "prime"]:
                    if field in song_fields:
                        del song_fields[field]
                fields['song'] = Song(**song_fields)
            if fields['game'] is None:
                print('Failed to find game for track', fields)
                print(item)
                continue
            if track is None:
                if 'pk' in fields:
                    del fields['pk']
                track = cls(**fields)
            #else:
            #    for key, value in fields.items():
            #        if key != 'pk':
            #            setattr(track, key, value)
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
                    duration = typing.cast(datetime.timedelta, from_isodatetime(value))
                    value = round(duration.total_seconds() * 1000)
                if field == 'song':
                    song = Song.lookup(dict(pk=value), pk_maps)
                    if song is None:
                        song = Song.search_for_song(item, pk_maps)
                    value = song
                retval[field] = value
            except KeyError as err:
                if field == 'song':
                    retval[field] = Song.search_for_song(item, pk_maps)
        game_pk = item['game']
        if game_pk in pk_maps["Game"]:
            game_pk = pk_maps["Game"][game_pk]
        retval['game'] = Game.get(pk=game_pk)
        if 'prime' in item:
            retval['number'] = PRIME_NUMBERS.index(int(item['prime']))
        return retval

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Track"]:
        """
        Check to see if 'item' references a track that is already in the database
        """
        if 'prime' in item:
            number = PRIME_NUMBERS.index(int(item['prime']))
        else:
            number = item['number']
        try:
            game_pk = item['game']
            #if game_pk in pk_maps["Game"]:
            game_pk = pk_maps["Game"][game_pk]
            game = Game.get(pk=game_pk)
        except KeyError as err:
            print("Track.lookup KeyError", err)
            return None
        if game is None:
            return None
        track = Track.get(game=game, number=number)
        #if track is None:
        #    try:
        #        track = Track.get(pk=item['pk'])
        #    except KeyError:
        #        track = None
        return track

    @property
    def prime(self) -> int:
        return PRIME_NUMBERS[self.number]
