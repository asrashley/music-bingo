"""
Database model for one track in a game
"""
import datetime
from typing import AbstractSet, Optional, List, cast, TYPE_CHECKING

from sqlalchemy import ForeignKey, text
from sqlalchemy.types import Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import TextClause

from musicbingo.primes import PRIME_NUMBERS
from musicbingo.utils import from_isodatetime

from .base import Base
from .game import Game
from .modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from .schemaversion import SchemaVersion
from .session import DatabaseSession
from .song import Song

if TYPE_CHECKING:
    from .bingoticket import BingoTicketTrack

class Track(Base, ModelMixin):
    """
    Database model for one track in a game
    """
    __plural__ = 'Tracks'
    __tablename__ = 'Track'
    __schema_version__ = 2

    pk: Mapped[int] = mapped_column('pk', Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[int] = mapped_column(Integer, nullable=False)
    game_pk: Mapped[int] = mapped_column("game", Integer, ForeignKey('Game.pk'), nullable=False)
    song_pk: Mapped[int] = mapped_column("song", Integer, ForeignKey("Song.pk"), nullable=False)
    song: Mapped["Song"] = relationship("Song", back_populates="tracks")
    # game: Mapped["Game"] = relationship("Game", back_populates="tracks")
    bingo_tickets: Mapped[list["BingoTicketTrack"]] = relationship(
        "BingoTicketTrack", back_populates="track", lazy='dynamic')
    __table_args__ = (
        UniqueConstraint("number", "game"),
    )

    # pylint: disable=unused-argument, arguments-differ
    @classmethod
    def migrate_schema(cls, engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate database schema
        """
        cmds: List[TextClause] = []
        if sver.get_version(cls.__tablename__) == 1:
            cmds.append(text(
                'INSERT INTO Track (pk, number, start_time, game, song) ' +
                'SELECT SongBase.pk, SongBase.number, ' +
                'SongBase.start_time, SongBase.game, Song.pk ' +
                'FROM SongBase ' +
                'INNER JOIN Artist ON Artist.name = SongBase.artist '+
                'INNER JOIN Song ON Song.filename = SongBase.filename AND ' +
                'Song.title = SongBase.title AND Song.artist_pk = Artist.pk ' +
                'WHERE SongBase.classtype = "Track"'))
        return cmds

    @classmethod
    def from_json(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                  item: JsonObject) -> JsonObject:
        """
        Converts any fields in item into a dictionary ready for use
        by Track constructor
        """
        retval = {}
        for field in ['pk', 'number', 'start_time', 'game', 'song']:
            try:
                value = item[field]
                if field == 'start_time' and isinstance(value, str):
                    duration = cast(datetime.timedelta, from_isodatetime(value))
                    value = round(duration.total_seconds() * 1000)
                elif field == 'song':
                    song = Song.lookup(session, pk_maps, {'pk': value})
                    if song is None:
                        song = Song.search_for_song(session, pk_maps, item)
                    value = song
                retval[field] = value
            except KeyError:
                if field == 'song':
                    retval[field] = Song.search_for_song(session, pk_maps, item)
        game_pk = item['game']
        game_pk = pk_maps["Game"][game_pk]
        retval['game'] = Game.get(session, pk=game_pk)
        if 'prime' in item:
            retval['number'] = PRIME_NUMBERS.index(int(item['prime']))
        return retval

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None,
                with_collections: bool = False) -> JsonObject:
        if (not with_collections or
                (only is not None and 'bingo_tickets' not in only) or
                (exclude is not None and 'bingo_tickets' in exclude)):
            return super().to_dict(exclude=exclude, only=only)
        if exclude is None:
            exclude = set()
        trk_exclude = exclude | set({'bingo_tickets'})
        result = super().to_dict(exclude=trk_exclude, only=only)
        result["bingo_tickets"] = [btk.bingoticket_pk for btk in self.bingo_tickets]
        return result

    @classmethod
    def lookup(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> Optional["Track"]:
        """
        Check to see if 'item' references a track that is already in the database
        """
        if 'prime' in item:
            number = PRIME_NUMBERS.index(int(item['prime']))
        else:
            number = item['number']
        try:
            game_pk = item['game']
            game_pk = pk_maps["Game"][game_pk]
            game = Game.get(session, pk=game_pk)
        except KeyError as err:
            print("Track.lookup KeyError", err)
            return None
        if game is None:
            return None
        track = cast(
            Optional["Track"],
            Track.get(session, game=game, number=number))
        # if track is None:
        #    try:
        #        track = Track.get(pk=item['pk'])
        #    except KeyError:
        #        track = None
        return track

    @property
    def prime(self) -> int:
        """
        Get the prime number assigned to this track
        """
        # pylint: disable=invalid-sequence-index
        return PRIME_NUMBERS[cast(int, self.number)]
