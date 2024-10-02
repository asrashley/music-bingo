"""
Database model for a Bingo ticket
"""
from typing import AbstractSet, ClassVar, Iterable, List, Optional, cast, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Table, MetaData, text
from sqlalchemy.types import BigInteger, String, Integer, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import TextClause

from musicbingo.models.base import Base, mapper_registry
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap

from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .track import Track

if TYPE_CHECKING:
    from .game import Game
    from .user import User

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
    __migration_table: ClassVar[Table | None] = None
    __tablename__ = "BingoTicket_Track"
    __schema_version__ = 3

    bingoticket_pk: Mapped[int] = mapped_column(
        "bingoticket", Integer, ForeignKey('BingoTicket.pk'), primary_key=True, nullable=False)
    track_pk: Mapped[int] = mapped_column(
        "track", Integer, ForeignKey('Track.pk'), primary_key=True, nullable=False)
    # since v3
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, default=0)
    bingoticket: Mapped["BingoTicket"] = relationship("BingoTicket", back_populates="tracks")
    track: Mapped["Track"] = relationship("Track", back_populates="bingo_tickets")

    # pylint: disable=unused-argument, arguments-differ
    @classmethod
    def migrate_schema(cls, engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate database Schema
        """
        version, existing_columns, column_types = sver.get_table(cls.__tablename__)
        cmds: List[TextClause] = []
        if version < 3:
            if 'order' not in existing_columns:
                cmds.append(cls.add_column(engine, column_types, 'order'))
            else:
                sver.set_version(cls.__tablename__, 3)
        return cmds

    # pylint: disable=arguments-differ
    @classmethod
    def migrate_data(cls, session: DatabaseSession, sver: SchemaVersion) -> int:
        count: int = 0
        version: int = sver.get_version(cls.__tablename__)
        if version < 3:
            if BingoTicketTrack.__migration_table is None:
                # TODO: switch to using raw sql query
                metadata = MetaData()
                temp_tab = Table(BingoTicket.__tablename__, metadata,
                                 Column('pk', Integer, primary_key=True),
                                 Column('order', JSON, nullable=False, default=[]))
                BingoTicketTrack.__migration_table = temp_tab
                # mapper(TemporaryTicket, temp_tab)
                mapper_registry.map_imperatively(TemporaryTicket, temp_tab)
            for ticket in session.query(BingoTicketTrack.__migration_table):
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
        return count


class BingoTicket(Base, ModelMixin):  # type: ignore
    """
    Database model for a Bingo ticket
    """
    __plural__ = 'BingoTickets'
    __tablename__ = 'BingoTicket'
    __schema_version__ = 3

    pk: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_pk: Mapped[int] = mapped_column("user", Integer, ForeignKey("User.pk"), nullable=True)
    user: Mapped[Optional["User"]] = relationship('User', back_populates='bingo_tickets')
    game_pk: Mapped[int] = mapped_column("game", Integer, ForeignKey("Game.pk"), nullable=False)
    # game: Mapped["Game"] = relationship('Game', back_populates='bingo_tickets')
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    # backref="bingo_tickets",
    tracks: Mapped[list["BingoTicketTrack"]] = relationship("BingoTicketTrack",
                          back_populates="bingoticket",
                          innerjoin=True,
                          order_by="BingoTicketTrack.order",
                          cascade="all, delete-orphan")
    # calculated by multiplying the primes of each track on this ticket
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    checked: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False)  # bitmask of track order
    __table_args__ = (
        UniqueConstraint("game", "number"),
    )

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate database Schema
        """
        cmds: List[TextClause] = []
        this_tab = sver.get_table(cls.__tablename__)
        assoc_tab = sver.get_table(BingoTicketTrack.__tablename__)
        if ('order' in assoc_tab.existing_columns and
                'order' in this_tab.existing_columns):
            if sver.options.provider != 'sqlite':
                cmds.append(text(f"ALTER TABLE `{cls.__tablename__}` DROP COLUMN `order`"))
            else:
                print('===========================================')
                print('Warning: manual database migration required')
                print('===========================================')
        return cmds

    def get_tracks(self, session: DatabaseSession) -> List[Track]:
        """
        Get the tracks for this ticket
        """
        return [btt.track for btt in self.tracks]

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
            return super().to_dict(exclude=exclude, only=only)
        if exclude is None:
            exclude = set()
        trk_exclude = exclude | set({'tracks'})
        result = super().to_dict(exclude=trk_exclude, only=only)
        result["tracks"] = [btk.track_pk for btk in self.tracks]
        return result
