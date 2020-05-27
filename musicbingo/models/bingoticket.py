"""
Database model for a Bingo ticket
"""
from random import shuffle
import typing

from sqlalchemy import Column, ForeignKey, Table, MetaData  # type: ignore
from sqlalchemy.types import BigInteger, String, Integer, JSON  # type: ignore
from sqlalchemy.orm import mapper, relationship, backref  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore
from sqlalchemy.schema import UniqueConstraint  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap

from .user import User
from .track import Track

class TemporaryTicket:
    """
    Used when migrating from v2 to v3 of BingoTicketTrack
    """
    def __init__(self, pk, order):
        self.pk = pk
        self.order = order

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
    # bingoticket = relationship(BingoTicket, backref=backref("bingoticket_assoc"))
    # track = relationship(Track, backref=backref("track_assoc"))

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

class BingoTicket(Base, ModelMixin):  # type: ignore
    """
    Database model for a Bingo ticket
    """
    __plural__ = 'BingoTickets'
    __tablename__ = 'BingoTicket'
    __schema_version__ = 3

    pk = Column(Integer, primary_key=True)
    user_pk = Column("user", Integer, ForeignKey("User.pk"), nullable=True)
    user = relationship('User', back_populates='bingo_tickets')
    game_pk = Column("game", Integer, ForeignKey("Game.pk"), nullable=False)
    number = Column(Integer, nullable=False)
    # backref="bingo_tickets",
    tracks = relationship(Track,
                          secondary=BingoTicketTrack,
                          back_populates="bingo_tickets",
                          order_by=BingoTicketTrack.order)
    # calculated by multiplying the primes of each track on this ticket
    fingerprint = Column(String, nullable=False)
    checked = Column(BigInteger, default=0, nullable=False)  # bitmask of track order
    __table_args__ = (
        UniqueConstraint("game", "number"),
    )

    # pylint: disable=unused-argument
    @classmethod
    def migrate_schema(cls, engine, existing_columns, column_types, version) -> typing.List[str]:
        """
        Migrate database Schema
        """
        return []

    @classmethod
    def migrate_data(cls, session: Session, version: int) -> int:
        count: int = 0
        if version < 3:
            #metadata = MetaData()
            #temp_tab = Table(cls.__tablename__, metadata,
            #                 Column('pk', Integer, primary_key=True),
            #                 Column('order', JSON, nullable=False, default=[]),
            #)
            #mapper(TemporaryTicket, temp_tab)
            #for ticket in session.query(temp_tab):
            #    if not ticket.order:
            #        continue
            #    for idx, track_pk in enumerate(ticket.order):
            #        if not track_pk:
            #            continue
            #        ticket_track = session.query(BingoTicketTrack).filter_by(
            #            bingoticket_pk=ticket.pk, track_pk=track_pk).one_or_none()
            #        if ticket_track:
            #            ticket_track.order = idx
            #            count += 1
            count = 1
        return count


    def set_tracks(self, tracks: typing.Iterable[Track]) -> None:
        """
        Set the tracks for this bingo ticket, including setting their order
        """
        for idx, track in tracks:
            card_track = BingoTicketTrack(bingoticket_pk=self.pk,
                                          track=track,
                                          order=idx)

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
