import copy
from pathlib import Path
import typing

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore
from sqlalchemy.schema import UniqueConstraint, CreateTable  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from .directory import Directory


class Song(Base, ModelMixin):  # type: ignore
    __plural__ = 'Songs'
    __tablename__ = 'Song'
    __schema_version__ = 2

    pk = Column('pk', Integer, primary_key=True)
    directory_pk = Column('directory', Integer, ForeignKey('Directory.pk'),
                          nullable=False)
    directory = relationship("Directory", back_populates="songs")
    filename = Column(String, index=True, nullable=False)  # relative to directory
    title = Column(String, index=True, nullable=False)
    artist = Column(String, index=True)
    duration = Column(Integer, default=0, nullable=False)
    channels = Column(Integer, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    sample_width = Column(Integer, nullable=False)
    bitrate = Column(Integer, nullable=False)
    album = Column(String, index=True, nullable=True)
    tracks = relationship("Track", back_populates="song")
    __table_args__ = (
        UniqueConstraint("directory", "filename"),
    )

    @classmethod
    def migrate(cls, engine, columns, version) -> typing.List[str]:
        cmds: typing.List[str] = []
        if version == 1:
            #columns = []
            # for name, value in columns.items():
            #    columns.append('"{0}" {1}'.format(name, value.type))
            #cmd = CreateTable(Song).compile(engine)

            # cmd = [
            #    'CREATE TABLE IF NOT EXISTS "Song" (',
            #    ', '.join(columns),
            #    ')' ]
            #print(' '.join(cmd))
            # cmds.append(cmd)

            cmds.append(
                'INSERT INTO Song (pk, filename, title, artist, duration, ' +
                'channels, sample_rate, sample_width, bitrate, album, directory) ' +
                'SELECT pk, filename, title, artist, duration, channels, ' +
                'sample_rate, sample_width, bitrate, album, directory ' +
                'FROM SongBase ' +
                'WHERE classtype = "Song"; ')
        return cmds

    @classmethod
    def lookup(cls, session: Session, pk_maps: PrimaryKeyMap, item: JsonObject) -> typing.Optional["Song"]:
        if 'pk' not in item:
            return cls.search_for_song(session, pk_maps, item)
        song_pk = item['pk']
        pk_map = pk_maps["Song"]
        if song_pk in pk_map:
            song_pk = pk_map[song_pk]
        try:
            song = typing.cast(
                typing.Optional["Song"],
                Song.get(session, pk=song_pk))
        except KeyError:
            song = None
        if song is None:
            song = cls.search_for_song(session, pk_maps, item)
        return song

    @classmethod
    def search_for_song(cls, session: Session, pk_maps: PrimaryKeyMap,
                        item: JsonObject) -> typing.Optional["Song"]:
        """
        Try to match this item to a song already in the database.
        """
        try:
            filename = item['filename']
        except KeyError:
            return None
        directory = item.get("directory", None)
        if directory is not None:
            directory = pk_maps["Directory"].get(directory, None)
        if directory is not None:
            if isinstance(directory, int):
                song = typing.cast(
                    typing.Optional[Song],
                    Song.get(session, directory_pk=directory, filename=filename))
            else:
                song = typing.cast(
                    typing.Optional[Song],
                    Song.get(session, directory=directory, filename=filename))
            if song is not None:
                return song
        try:
            title = item['title']
            artist = item['artist']
            album = item['album']
            if isinstance(album, list):
                # work-around for bug in some v1 gameTracks.json files
                album = album[0]
        except KeyError:
            return None
        result = Song.search(session, filename=filename, title=title,
                             artist=artist, album=album)
        count = result.count()
        if count == 1:
            return result.first()
        if count == 0:
            result = Song.search(session, filename=filename, title=title,
                                 artist=artist)
            count = result.count()
        if count == 1:
            return result.first()
        if count > 1:
            result = result.filter_by(duration=item['duration'])
            count = result.count()
        if count > 0:
            return result.first()
        return None

    @classmethod
    def from_json(cls, session: Session, pk_maps: PrimaryKeyMap, src: typing.Dict) -> typing.Dict:
        """
        converts any fields in item to Python objects
        """
        columns = cls.attribute_names()
        columns.append('directory')
        item = {}
        #copy.copy(item)
        for key, value in src.items():
            if key in columns:
                if isinstance(value, list):
                    value = value[0]
                item[key] = value
        parent = None
        parent_pk = item.get('directory', None)
        if parent_pk is not None: # and parent_pk in pk_maps["Directory"]:
            parent_pk = pk_maps["Directory"].get(parent_pk, None)
        if parent_pk is not None:
            parent = Directory.get(session, pk=parent_pk)
        item['directory'] = parent
        if 'classtype' in item:
            del item['classtype']
        if 'fullpath' in item:
            if 'filename' not in item:
                item['filename'] = Path(item['fullpath']).name
            del item['fullpath']
        if 'tracks' in item:
            del item['tracks']
        for field in ['filename', 'title', 'artist', 'album']:
            if field in item and len(item[field]) > 1:
                if item[field][0] == '"' and item[field][-1] == '"':
                    item[field] = item[field][1:-1]
        return item
