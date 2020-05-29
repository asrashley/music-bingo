"""
Database model for a Bingo ticket
"""
from typing import AbstractSet, Iterable, List, Optional, cast

from sqlalchemy import Column, ForeignKey, Table, MetaData  # type: ignore
from sqlalchemy.types import BigInteger, String, Integer, JSON  # type: ignore
from sqlalchemy.orm import mapper, relationship  # type: ignore
from sqlalchemy.schema import CreateColumn, UniqueConstraint  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap

from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .track import Track

class TemporaryTicket:
    """
    Used when migrating from v2 to v3 of BingoTicketTrack
    """
    def __init__(self, pk, order):
        self.pk = pk
        self.order = order

class BingoTicketTrack(Base, ModelMixin):
    """
    Many-to-many association table for BingoTicket and Track
    """
    __tablename__ = "BingoTicket_Track"
    __schema_version__ = 3

    bingoticket_pk = Column("bingoticket", Integer, ForeignKey('BingoTicket.pk'),
                            primary_key=True)
    track_pk = Column("track", Integer, ForeignKey('Track.pk'), primary_key=True)
    # since v3
    order = Column("order", Integer, nullable=False, default=0)
    bingoticket = relationship("BingoTicket", back_populates="tracks")
    track = relationship("Track", back_populates="bingo_tickets")

    # pylint: disable=unused-argument
    @classmethod
    def migrate_schema(cls, engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        version, existing_columns, column_types = sver.get_table(cls.__tablename__)
        cmds: List[str] = []
        if version < 3:
            if 'order' not in existing_columns:
                cmds.append(cls.add_column(engine, column_types, 'order'))
            else:
                sver.set_version(cls.__tablename__, 3)
        return cmds

    @classmethod
    def migrate_data(cls, session: DatabaseSession, sver: SchemaVersion) -> int:
        count: int = 0
        version = sver.get_version(cls.__tablename__)
        if version < 3:
            if BingoTicketTrack._migration_table is None:
                # TODO: switch to using raw sql query
                metadata = MetaData()
                temp_tab = Table(BingoTicket.__tablename__, metadata,
                                 Column('pk', Integer, primary_key=True),
                                 Column('order', JSON, nullable=False, default=[]),
                )
                mapper(TemporaryTicket, temp_tab) #, non_primary=True)
                BingoTicketTrack._migration_table = temp_tab
            for ticket in session.query(BingoTicketTrack._migration_table):
                if not ticket.order:
                    # order = session.query(Ticket.pk).filter_by()
                    continue
                for idx, track_pk in enumerate(ticket.order):
                    if not track_pk:
                        continue
                    ticket_track = session.query(BingoTicketTrack).filter_by(
                        bingoticket_pk=ticket.pk, track_pk=track_pk).one_or_none()
                    if ticket_track:
                        ticket_track.order = idx
                        count += 1
            count = 1
        return count

BingoTicketTrack._migration_table = None

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
    tracks = relationship("BingoTicketTrack",
                          back_populates="bingoticket",
                          innerjoin=True,
                          order_by="BingoTicketTrack.order")
    # calculated by multiplying the primes of each track on this ticket
    fingerprint = Column(String, nullable=False)
    checked = Column(BigInteger, default=0, nullable=False)  # bitmask of track order
    __table_args__ = (
        UniqueConstraint("game", "number"),
    )

    # pylint: disable=unused-argument
    @classmethod
    def migrate_schema(cls, engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        return []

    def set_tracks(self, session, tracks: Iterable[Track]) -> None:
        """
        Set the tracks for this bingo ticket, including setting their order
        """
        for idx, track in enumerate(tracks):
            card_track = None
            if self.pk:
                card_track = session.query(
                    BingoTicketTrack).filter_by(bingoticket_pk=self.pk,
                                                track=track)
            if card_track is not None:
                card_track.order = idx
            else:
                card_track = BingoTicketTrack(bingoticket=self,
                                              track=track,
                                              order=idx)
                session.add(card_track)

    @classmethod
    def lookup(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> Optional["BingoTicket"]:
        """
        Check to see if 'item' references a BingoTicket that is already in the database
        """
        try:
            pk = item['pk']
            if item['pk'] is not None:
                pk = pk_maps["Game"][pk]
            ticket = cast(
                Optional["BingoTicket"],
                BingoTicket.get(session, pk=pk))
        except KeyError:
            ticket = None
        if ticket is not None:
            return ticket
        try:
            ticket = cast(
                Optional["BingoTicket"],
                BingoTicket.get(session, game_pk=item['game'], number=item['number']))
        except KeyError:
            ticket = None
        return ticket

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None,
                with_collections: bool = False) -> JsonObject:
        """
        convert Bingo Ticket to a dictionary
        """
        if (not with_collections or
                (only is not None and 'tracks' not in only) or
                (exclude is not None and 'tracks' in exclude)):
            return super(BingoTicket, self).to_dict(exclude=exclude, only=only)
        if exclude is None:
            exclude = set()
        trk_exclude = exclude | set({'tracks'})
        result = super(BingoTicket, self).to_dict(exclude=trk_exclude, only=only)
        result["tracks"] = [btk.track_pk for btk in self.tracks]
        return result
