from random import shuffle
import typing

from sqlalchemy import Column, ForeignKey, func # type: ignore
from sqlalchemy.types import BigInteger, DateTime, String, Integer, JSON # type: ignore
from sqlalchemy.orm import relationship, backref # type: ignore
from sqlalchemy.schema import UniqueConstraint # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin, JsonObject

from .user import User
from .track import bingoticket_track

if typing.TYPE_CHECKING:
    from musicbingo.models.game import Game
    from musicbingo.models.track import Track

class BingoTicket(Base, ModelMixin): # type: ignore
    __plural__ = 'BingoTickets'
    __tablename__ = 'BingoTicket'
    __schema_version__ = 2

    pk = Column(Integer, primary_key=True)
    user_pk = Column("user", Integer, ForeignKey("User.pk"), nullable=True)
    user = relationship('User', back_populates='bingo_tickets')
    game_pk = Column("game", Integer, ForeignKey("Game.pk"), nullable=False)
    game = relationship('Game', back_populates='bingo_tickets')
    number = Column(Integer, nullable=False)
    tracks = relationship('Track', secondary=bingoticket_track, back_populates="bingo_tickets")
    fingerprint = Column(String, nullable=False)  # calculated by multiplying the primes of each track on this ticket
    order = Column(JSON, nullable=False, default=[]) # List[int] - order of tracks by pk
    checked = Column(BigInteger, default=0, nullable=False) # bitmask of track order
    __table_args__ = (
        UniqueConstraint("game", "number"),
    )

    @classmethod
    def migrate(cls, engine, columns, version) -> typing.List[str]:
        return []

    def tracks_in_order(self) -> typing.List["Track"]:
        """
        Get the list of tracks, in the order they appear on the ticket
        """
        #if not self.order:
        #    self.order = list(select(track.pk for track in self.tracks).random(len(self.tracks)))
        tk_map = {}
        for trck in self.tracks:
            tk_map[trck.pk] = trck
            if self.order and trck.pk not in self.order:
                self.order.append(trck.pk)
        if not self.order:
            order = list(tk_map.keys())
            shuffle(order)
            self.order = order
        elif None in self.order:
            # work-around for bug that did not wait for Track.pk to be
            # calculated when generating order
            self.order = list(filter(lambda item: item is not None, self.order))
        tracks: typing.List[Track] = []
        for tpk in self.order:
            if tpk in tk_map:
                tracks.append(tk_map[tpk])
        return tracks

    @classmethod
    def import_json(cls, sess: ImportSession, items: typing.List[JsonObject]) -> None:
        from musicbingo.models import Game, Track

        pk_map: typing.Dict[int, int] = {}
        sess.set_map("BingoTicket", pk_map)
        for item in items:
            ticket = cls.lookup(sess, item)
            try:
                game_pk = item['game']
                game_pk = sess["Game"][game_pk]
            except KeyError as err:
                print('Warning: failed to find primary key for game {game} for ticket {pk}'.format(**item))
                print(err)
                continue
            game = Game.get(sess.session, pk=game_pk)
            if not game:
                print('Warning: failed to find game {game} for ticket {pk}'.format(**item))
                continue
            user = None
            if item['user']:
                try:
                    user_pk = sess['User'][item['user']]
                except KeyError:
                    user_pk = item['user']
                user = User.get(sess.session, pk=user_pk)
                if not user:
                    print('Warning: failed to find user {user} for ticket {pk} in game {game}'.format(**item))
            tracks = []
            # The database field "order" has the list of Track primary keys.
            # The JSON representation of BingoTicket should have a property called
            # "tracks" which is an ordered list of Track.pk. If the JSON
            # file has an "order" property, it can be used as a fallback.
            if 'order' in item and 'tracks' not in item:
                item['tracks'] = item['order']
            for trk in item['tracks']:
                if trk in sess["Track"]:
                    trk = sess["Track"][trk]
                if trk in sess["Track"]:
                    trk = sess["Track"][trk]
                track = Track.get(sess.session, pk=trk)
                if not track:
                    print('Warning: failed to find track {trk} for ticket {pk} in game {game}'.format(trk=trk, **item))
                else:
                    tracks.append(track)
            item['game'] = game
            item['user'] = user
            item['tracks'] = tracks
            if 'order' not in item:
                item['order'] = [t.pk for t in item['tracks']]
            try:
                pk = item['pk']
                del item['pk']
            except KeyError:
                pk = None
            if ticket is None:
                ticket = BingoTicket(**item)
                sess.add(ticket)
            else:
                for key, value in item.items():
                    if key not in ['pk']:
                        setattr(ticket, key, value)
            sess.commit()
            if pk is not None:
                pk_map[pk] = ticket.pk

    @classmethod
    def lookup(cls, sess: ImportSession, item: JsonObject) -> typing.Optional["BingoTicket"]:
        """
        Check to see if 'item' references a BingoTicket that is already in the database
        """
        try:
            pk = item['pk']
            if item['pk'] in sess["Game"]:
                pk = sess["Game"][pk]
            ticket = typing.cast(
                typing.Optional["BingoTicket"],
                BingoTicket.get(sess.session, pk=pk))
        except KeyError:
            ticket = None
        if ticket is not None:
            return ticket
        try:
            ticket = typing.cast(
                typing.Optional["BingoTicket"],
                BingoTicket.get(sess.session, game_pk=item['game'], number=item['number']))
        except KeyError:
            ticket = None
        return ticket
