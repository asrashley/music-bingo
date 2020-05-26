"""
Database model for one track in a game
"""
import datetime
import typing

from sqlalchemy import Column, ForeignKey, Table  # type: ignore
from sqlalchemy.types import Integer  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore
from sqlalchemy.schema import UniqueConstraint  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from musicbingo.primes import PRIME_NUMBERS
from musicbingo.utils import from_isodatetime

from .game import Game
from .song import Song

bingoticket_track = Table("BingoTicket_Track", Base.metadata,
                          Column(
                              "bingoticket",
                              Integer,
                              ForeignKey('BingoTicket.pk'),
                              primary_key=True),
                          Column("track", Integer, ForeignKey('Track.pk'), primary_key=True)
                          )


class Track(Base, ModelMixin):
    """
    Database model for one track in a game
    """
    __plural__ = 'Tracks'
    __tablename__ = 'Track'
    __schema_version__ = 2

    pk = Column('pk', Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    bingo_tickets = relationship(
        "BingoTicket",
        secondary=bingoticket_track,
        back_populates="tracks")
    start_time = Column(Integer, nullable=False)
    game_pk = Column("game", Integer, ForeignKey('Game.pk'), nullable=False)
    song_pk = Column("song", Integer, ForeignKey("Song.pk"), nullable=False)
    song = relationship("Song", back_populates="tracks")
    __table_args__ = (
        UniqueConstraint("number", "game"),
    )

    # pylint: disable=unused-argument
    @classmethod
    def migrate(cls, engine, mapper, version) -> typing.List[str]:
        """
        Migrate database schema
        """
        cmds: typing.List[str] = []
        if version == 1:
            #columns = []
            # for name, value in mapper.attrs.items():
            #    columns.append('"{0}" {1}'.format(name, value.type))
            # cmd = [
            #    'CREATE TABLE "Track" (',
            #    ', '.join(columns),
            #    ')' ]
            #print(' '.join(cmd))
            # cmds.append(cmd)
            # cmds.append(CreateTable(Track).compile(engine))

            cmds.append(
                'INSERT INTO Track (pk, number, start_time, game, song) ' +
                'SELECT SongBase.pk, SongBase.number, ' +
                'SongBase.start_time, SongBase.game, Song.pk ' +
                'FROM SongBase ' +
                'INNER JOIN Song ON Song.filename = SongBase.filename AND ' +
                'Song.title = SongBase.title AND ' +
                'Song.artist = SongBase.artist ' +
                'WHERE SongBase.classtype = "Track"')
        return cmds

    @classmethod
    def from_json(cls, session: Session, pk_maps: PrimaryKeyMap,
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
                    duration = typing.cast(datetime.timedelta, from_isodatetime(value))
                    value = round(duration.total_seconds() * 1000)
                elif field == 'song':
                    song = Song.lookup(session, pk_maps, dict(pk=value))
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

    @classmethod
    def lookup(cls, session: Session, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> typing.Optional["Track"]:
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
        track = typing.cast(
            typing.Optional["Track"],
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
        return PRIME_NUMBERS[typing.cast(int, self.number)]
