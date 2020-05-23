import datetime
import typing

from sqlalchemy import Column, ForeignKey, Table  # type: ignore
from sqlalchemy.types import DateTime, String, Integer  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore
from sqlalchemy.schema import UniqueConstraint, CreateTable  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin, JsonObject
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

    @classmethod
    def migrate(cls, engine, mapper, version) -> typing.List[str]:
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
                'SELECT SongBase.pk, SongBase.number, SongBase.start_time, SongBase.game, Song.pk ' +
                'FROM SongBase ' +
                'INNER JOIN Song ON Song.filename = SongBase.filename AND ' +
                'Song.title = SongBase.title AND ' +
                'Song.artist = SongBase.artist ' +
                'WHERE SongBase.classtype = "Track"')
        return cmds

    @classmethod
    def import_json(cls, sess: ImportSession, items: typing.List[JsonObject]) -> None:
        """
        Try to import all of the tracks described in 'items'.
        Returns a map from the pk listed in 'items' to the
        primary key of each imported track.
        """
        pk_map: typing.Dict[int, int] = {}
        sess.set_map(cls.__name__, pk_map)
        for item in items:
            track = cls.lookup(sess, item)
            fields = cls.from_json(sess, item)
            if fields['song'] is None and 'filename' in fields:
                from .directory import Directory
                sess.log.warning('Failed to find song, adding it to lost+found directory: {0}'.format(item))
                lost = Directory.get(sess.session, name="lost+found")
                if lost is None:
                    lost = Directory(
                        name="lost+found",
                        title="lost & found",
                        artist="Orphaned songs")
                    sess.session.add(lost)
                song_fields = Song.from_json(sess, item)
                song_fields['directory'] = lost
                for field in list(fields.keys()) + ["bingo_tickets", "prime"]:
                    if field in song_fields:
                        del song_fields[field]
                fields['song'] = Song(**song_fields)
                sess.session.add(fields['song'])
            if fields['game'] is None:
                sess.log.error('Failed to find game for track: %s', fields)
                sess.log.debug('%s', item)
                continue
            if track is None:
                if 'pk' in fields:
                    del fields['pk']
                if fields['song'] is None:
                    print(item)
                    print(fields)
                assert fields['song'] is not None
                track = cls(**fields)
                sess.add(track)
            # else:
            #    for key, value in fields.items():
            #        if key != 'pk':
            #            setattr(track, key, value)
            sess.flush()
            if 'pk' in item:
                pk_map[item['pk']] = track.pk

    @classmethod
    def from_json(cls, sess: ImportSession, item: JsonObject) -> JsonObject:
        """
        converts any fields in item into a dictionary ready for use Track constructor
        """
        retval = {}
        for field in ['pk', 'number', 'start_time', 'game', 'song']:
            try:
                value = item[field]
                if field == 'start_time' and isinstance(value, str):
                    duration = typing.cast(datetime.timedelta, from_isodatetime(value))
                    value = round(duration.total_seconds() * 1000)
                elif field == 'song':
                    song = Song.lookup(sess, dict(pk=value))
                    if song is None:
                        song = Song.search_for_song(sess, item)
                    value = song
                retval[field] = value
            except KeyError as err:
                if field == 'song':
                    retval[field] = Song.search_for_song(sess, item)
        game_pk = item['game']
        # if game_pk in sess["Game"]:
        game_pk = sess["Game"][game_pk]
        retval['game'] = Game.get(sess.session, pk=game_pk)
        if 'prime' in item:
            retval['number'] = PRIME_NUMBERS.index(int(item['prime']))
        return retval

    @classmethod
    def lookup(cls, sess: ImportSession, item: JsonObject) -> typing.Optional["Track"]:
        """
        Check to see if 'item' references a track that is already in the database
        """
        if 'prime' in item:
            number = PRIME_NUMBERS.index(int(item['prime']))
        else:
            number = item['number']
        try:
            game_pk = item['game']
            # if game_pk in pk_maps["Game"]:
            game_pk = sess["Game"][game_pk]
            game = Game.get(sess.session, pk=game_pk)
        except KeyError as err:
            print("Track.lookup KeyError", err)
            return None
        if game is None:
            return None
        track = typing.cast(
            typing.Optional["Track"],
            Track.get(sess.session, game=game, number=number))
        # if track is None:
        #    try:
        #        track = Track.get(pk=item['pk'])
        #    except KeyError:
        #        track = None
        return track

    @property
    def prime(self) -> int:
        return PRIME_NUMBERS[self.number]
