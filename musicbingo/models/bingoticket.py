"""
Database model for a Bingo ticket
"""
from random import shuffle
import typing

from sqlalchemy import Column, ForeignKey  # type: ignore
from sqlalchemy.types import BigInteger, String, Integer, JSON  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore
from sqlalchemy.schema import UniqueConstraint  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap

from .user import User
from .track import Track

class BingoTicket(Base, ModelMixin):  # type: ignore
    """
    Database model for a Bingo ticket
    """
    __plural__ = 'BingoTickets'
    __tablename__ = 'BingoTicket'
    __schema_version__ = 2

    pk = Column(Integer, primary_key=True)
    user_pk = Column("user", Integer, ForeignKey("User.pk"), nullable=True)
    user = relationship('User', back_populates='bingo_tickets')
    game_pk = Column("game", Integer, ForeignKey("Game.pk"), nullable=False)
    number = Column(Integer, nullable=False)
    tracks = relationship('Track',
                          secondary="BingoTicket_Track",
                          backref="bingo_tickets",
                          order_by=BingoTicketTrack.order)
    # calculated by multiplying the primes of each track on this ticket
    fingerprint = Column(String, nullable=False)
    #order = Column(JSON, nullable=False, default=[])  # List[int] - order of tracks by pk
    checked = Column(BigInteger, default=0, nullable=False)  # bitmask of track order
    __table_args__ = (
        UniqueConstraint("game", "number"),
    )

    # pylint: disable=unused-argument
    @classmethod
    def migrate(cls, engine, columns, version) -> typing.List[str]:
        """
        Migrate database Schema
        """
        return []

    def set_tracks(self, tracks: typing.Iterable["Track"]) -> None:
        """
        Set the tracks for this bingo ticket, including setting their order
        """
        for idx, track in tracks:
            card_track = BingoTicketTrack(bingoticket_pk=self.pk,

    def tracks_in_order(self) -> typing.List["Track"]:
        """
        Get the list of tracks, in the order they appear on the ticket
        """
        # if not self.order:
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
        # pylint:used-before-assignment
        tracks: typing.List[Track] = []
        for tpk in self.order:
            if tpk in tk_map:
                tracks.append(tk_map[tpk])
        return tracks

    @classmethod
    def lookup(cls, session: Session, pk_maps: PrimaryKeyMap, item: JsonObject) -> typing.Optional["BingoTicket"]:
        """
        Check to see if 'item' references a BingoTicket that is already in the database
        """
        try:
            pk = item['pk']
            if item['pk'] is not None:
                pk = pk_maps["Game"][pk]
            ticket = typing.cast(
                typing.Optional["BingoTicket"],
                BingoTicket.get(session, pk=pk))
        except KeyError:
            ticket = None
        if ticket is not None:
            return ticket
        try:
            ticket = typing.cast(
                typing.Optional["BingoTicket"],
                BingoTicket.get(session, game_pk=item['game'], number=item['number']))
        except KeyError:
            ticket = None
        return ticket

class BingoTicketTrack(Base):
    __tablename__ = "BingoTicket_Track"
    __schema_version__ = 3
    bingoticket_pk = Column(
        "bingoticket",
        Integer,
        ForeignKey('BingoTicket.pk'),
        primary_key=True),
    track_pk = Column("track", Integer, ForeignKey('Track.pk'), primary_key=True)
    # since v3
    order = Column("order", Integer, nullable=False, default=0)
    bingoticket = relationship(BingoTicket, backref=backref("bingoticket_assoc"))
    track = relationship(Track, backref=backref("track_assoc"))

    # pylint: disable=unused-argument
    @classmethod
    def migrate_schema(cls, engine, columns, version) -> typing.List[str]:
        """
        Migrate database Schema
        """
        cmds: typing.List[str] = []
        if version < 3:
            col_def = CreateColumn(getattr(cls, 'order')).compile(engine)
            cmds.append('ALTER TABLE {0} ADD {1}'.format(bingoticket_track.__tablename__, col_def))
        return cmds
