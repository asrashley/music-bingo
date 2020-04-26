from datetime import datetime, timedelta
import typing


from pony.orm import PrimaryKey, Required, Optional, Set # type: ignore
from pony.orm import flush  # type: ignore

from musicbingo.models.db import db
from musicbingo.utils import from_isodatetime, parse_date, make_naive_utc

#from .bingoticket import BingoTicket

class Game(db.Entity): # type: ignore
    __plural__ = 'Games'

    pk = PrimaryKey(int, auto=True)
    bingo_tickets = Set('BingoTicket')
    id = Required(str, 64, unique=True)
    title = Required(str)
    start = Required(datetime, unique=True)
    end = Required(datetime)
    tracks = Set('Track')

    @classmethod
    def import_json(cls, items, options,
                    pk_maps: typing.Dict[typing.Type[db.Entity], typing.Dict[int, int]]) -> None:
        pk_map: Dict[int, int] = {}
        pk_maps[cls] = pk_map
        for item in items:
            game = cls.lookup(item, pk_maps)
            for field in ['start', 'end']:
                item[field] = parse_date(item[field])
                # Pony doesn't work correctly with timezone aware datetime
                # see: https://github.com/ponyorm/pony/issues/434
                item[field] = make_naive_utc(item[field])
            for field in ['bingo_tickets', 'tracks', 'options']:
                try:
                    del item[field]
                except KeyError:
                    pass
            if game is None:
                game = Game(**item)
            else:
                for key, value in item.items():
                    if key != 'pk':
                        setattr(game, key, value)
            flush()
            pk_map[item['pk']] = game.pk

    @classmethod
    def lookup(cls, item, pk_maps) -> typing.Optional["Game"]:
        try:
            game = Game.get(pk=item['pk'])
        except KeyError:
            game = None
        if game is None:
            game = Game.get(id=item['id'])
        return game
