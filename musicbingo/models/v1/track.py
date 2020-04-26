import typing

from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import perm, composite_key, db_session, select  # type: ignore

from musicbingo.models.db import db, schema_version
from musicbingo.primes import PRIME_NUMBERS

from .bingoticket import BingoTicket
from .game import Game
from .songbase import SongBase

assert schema_version == 1

class Track(SongBase):
    __plural__ = 'Tracks'
    
    number = Required(int, unsigned=True)
    bingo_tickets = Set(BingoTicket)
    start_time = Required(int, unsigned=True)
    game = Required(Game)
    composite_key(number, game)

    @classmethod
    def from_json(cls, item, pk_maps):
        """
        converts any fields in item to Python objects
        """
        if isinstance(item['start_time'], str):
            item['start_time'] = round(from_isodatetime(item['start_time']).total_seconds() * 1000)
        item['game'] = Game.get(pk=item['game'])
        if 'prime' in item:
            item['number'] = PRIME_NUMBERS.index(int(item['prime']))
            del item['prime']

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Track"]:
        try:
            track = Track.get(pk=item['pk'])
        except KeyError:
            track = None
        if track is not None:
            return track
        try:
            game = Game.get(pk=item['game'])
            if game is not None:
                if 'prime' in item:
                    item['number'] = PRIME_NUMBERS.index(int(item['prime']))
                    del item['prime']
                track = Track.get(number=item['number'], game=game)
        except KeyError:
            track = None
        return track

    @property
    def prime(self) -> int:
        return PRIME_NUMBERS[self.number]
