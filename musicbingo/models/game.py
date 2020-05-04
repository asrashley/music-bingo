from datetime import datetime, timedelta
import typing

from sqlalchemy import Column, ForeignKey, func # type: ignore
from sqlalchemy.types import DateTime, String, Integer, JSON # type: ignore
from sqlalchemy.orm import relationship, backref # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin, JsonObject
from musicbingo.utils import from_isodatetime, parse_date, make_naive_utc

class Game(Base, ModelMixin): # type: ignore
    __plural__ = 'Games'
    __tablename__ = 'Game'
    __schema_version__ = 3

    pk = Column(Integer, primary_key=True)
    bingo_tickets = relationship("BingoTicket", back_populates="game")
    id = Column(String(64), unique=True, nullable=False)
    title = Column(String, nullable=False)
    start = Column(DateTime, unique=True, nullable=False)
    end = Column(DateTime, nullable=False)
    tracks = relationship("Track", back_populates="game")
    # since 3
    options = Column(JSON, nullable=True)


    @classmethod
    def migrate(cls, conn, columns, version) -> typing.List[str]:
        if version < 3:
            return([cls.add_column(conn, columns, 'options')])
        return []

    @classmethod
    def import_json(cls, sess: ImportSession, items: typing.List[JsonObject]) -> None:
        pk_map: typing.Dict[int, int] = {}
        sess.set_map(cls.__name__, pk_map)
        games = {}
        for item in items:
            game = cls.lookup(sess, item)
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
            try:
                pk = item['pk']
                del item['pk']
            except KeyError:
                pk = None
            if game is None:
                game = Game(**item)
                sess.add(game)
            else:
                for key, value in item.items():
                    setattr(game, key, value)
            if pk is not None:
                games[pk] = game
        sess.commit()
        for pk, game in games.items():
            pk_map[pk] = game.pk

    @classmethod
    def lookup(cls, sess: ImportSession, item: JsonObject) -> typing.Optional["Game"]:
        game = Game.get(sess.session, id=item['id'])
        if game is None:
            try:
                game = Game.get(sess.session, pk=item['pk'])
            except KeyError:
                game = None
        return typing.cast(typing.Optional["Game"], game)
