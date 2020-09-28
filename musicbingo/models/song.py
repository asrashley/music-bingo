"""
Database model for a song
"""

from pathlib import Path
from typing import AbstractSet, Dict, List, Optional, Tuple, cast

from sqlalchemy import Column, String, Integer, ForeignKey  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.event import listen  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.schema import UniqueConstraint  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap
from musicbingo.uuidmixin import UuidMixin

from .album import Album
from .artist import Artist
from .directory import Directory
from .schemaversion import SchemaVersion
from .session import DatabaseSession

class Song(Base, ModelMixin, UuidMixin):  # type: ignore
    """
    Database model for a song
    """
    __plural__ = 'Songs'
    __tablename__ = 'Song'
    __schema_version__ = 4

    pk = Column('pk', Integer, primary_key=True)
    directory_pk = Column('directory', Integer, ForeignKey('Directory.pk'),
                          nullable=False)
    directory = relationship("Directory", back_populates="songs")
    filename = Column(String(512), index=True, nullable=False)  # relative to directory
    title = Column(String(512), index=True, nullable=False)
    duration = Column(Integer, default=0, nullable=False)
    channels = Column(Integer, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    sample_width = Column(Integer, nullable=False)
    bitrate = Column(Integer, nullable=False)
    # UUID added in v3
    uuid = Column(String(22), index=True, nullable=True)
    tracks = relationship("Track", back_populates="song")
    # artist table added in v4
    artist_pk = Column('artist_pk', Integer, ForeignKey('Artist.pk'))
    artist = relationship("Artist", back_populates="songs")
    # album table added in v4
    album_pk = Column('album_pk', Integer, ForeignKey('Album.pk'))
    album = relationship("Album", back_populates="songs")
    __table_args__ = (
        UniqueConstraint("directory", "filename"),
    )

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        cmds: List[str] = []
        version, existing_columns, column_types = sver.get_table(cls.__tablename__)
        if version == 1:
            cmds.append(
                'INSERT INTO Artist (name) ' +
                'SELECT DISTINCT SongBase.artist ' +
                'FROM SongBase;')
            cmds.append(
                'INSERT INTO Album (name) ' +
                'SELECT DISTINCT SongBase.album ' +
                'FROM SongBase;')
            cmds.append(
                'INSERT INTO Song (pk, filename, title, artist_pk, duration, ' +
                'channels, sample_rate, sample_width, bitrate, album_pk, directory) ' +
                'SELECT sb.pk, sb.filename, sb.title, Artist.pk, sb.duration, sb.channels, ' +
                'sb.sample_rate, sb.sample_width, sb.bitrate, Album.pk, sb.directory ' +
                'FROM SongBase sb ' +
                'INNER JOIN Album ON Album.name = sb.album ' +
                'INNER JOIN Artist ON Artist.name = sb.artist ' +
                'WHERE sb.classtype = "Song"; ')
        elif version < 4:
            for name in ['uuid', 'album_pk', 'artist_pk']:
                if name not in existing_columns:
                    cmds.append(cls.add_column(engine, column_types, name))
            if 'album' in existing_columns and 'album_pk' not in existing_columns:
                cmds.append(
                    'INSERT INTO Album (name) ' +
                    'SELECT DISTINCT Song.album ' +
                    'FROM Song;')
                if sver.options.provider != 'sqlite':
                    cmds.append('UPDATE `Song` ' +
                                'INNER JOIN `Album` ON Song.album = Album.name ' +
                                'SET Song.album_pk=Album.pk;')
                    cmds.append('ALTER TABLE `Song` DROP COLUMN `album`')
                else:
                    cmds.append('UPDATE `Song` SET album_pk = ' +
                                '(SELECT pk FROM `Album` ' +
                                'WHERE Song.album=Album.name);')
            if 'artist' in existing_columns and 'artist_pk' not in existing_columns:
                cmds.append(
                    'INSERT INTO Artist (name) ' +
                    'SELECT DISTINCT Song.artist ' +
                    'FROM Song;')
                if sver.options.provider != 'sqlite':
                    cmds.append('UPDATE `Song` ' +
                                'INNER JOIN `Artist` ON Song.artist = Artist.name ' +
                                'SET Song.artist_pk=Artist.pk;')
                    cmds.append('ALTER TABLE `Song` DROP COLUMN `artist`')
                else:
                    cmds.append('UPDATE `Song` SET artist_pk = ' +
                                '(SELECT pk FROM `Artist` ' +
                                'WHERE Song.artist=Artist.name);')

        return cmds

    @classmethod
    def migrate_data(cls, session: DatabaseSession, sver: SchemaVersion) -> int:
        """
        Migrate data to allow model to work with the current Schema.
        """
        count: int = 0
        version = sver.get_version(cls.__tablename__)
        if version < 3:
            for song in session.query(cls):
                if song.uuid is None:
                    song.check_for_uuid()
                    count += 1
        return count

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None,
                with_collections: bool = False) -> JsonObject:
        """
        Convert this model into a dictionary
        :exclude: set of attributes to exclude
        :only: set of attributes to include
        """
        retval = super().to_dict(exclude=exclude, only=only,
                                 with_collections=with_collections)
        if 'uuid' in retval:
            # Use RFC4122 URN encoding in JSON files as the base85 encoded version
            # requires character escaping
            retval['uuid'] = self.str_to_uuid(self.uuid).urn
        return retval

    @classmethod
    def lookup(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> Optional["Song"]:
        """
        Try to get a Song from the database using the data in "item"
        """
        if 'pk' not in item:
            return cls.search_for_song(session, pk_maps, item)
        pk_map = pk_maps["Song"]
        song_pk = item['pk']
        #if song_pk in pk_map:
        song_pk = pk_map[song_pk]
        try:
            # print('song_pk', song_pk)
            # print(pk_map)
            song = cast(
                Optional["Song"],
                Song.get(session, pk=song_pk))
        except KeyError:
            song = None
        if song is None:
            song = cls.search_for_song(session, pk_maps, item)
        return song

    @classmethod
    def search_for_song(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                        item: JsonObject) -> Optional["Song"]:
        """
        Try to match this item to a song already in the database.
        """
        count, songs = cls.search_for_songs(session, pk_maps, item, False)
        if count > 0:
            return songs[0]
        return None

    # pylint: disable=too-many-branches
    @classmethod
    def search_for_songs(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                         item: JsonObject,
                         multiple: bool = True) -> Tuple[int, List["Song"]]:
        """
        Try to match this item to one or more songs already in the database.
        """
        try:
            filename = item['filename']
        except KeyError:
            return (0, [],)
        directory = item.get("directory", None)
        if directory is not None:
            directory = pk_maps["Directory"].get(directory, None)
        if directory is not None:
            if isinstance(directory, int):
                song = cast(
                    Optional[Song],
                    Song.get(session, directory_pk=directory, filename=filename))
            else:
                song = cast(
                    Optional[Song],
                    Song.get(session, directory=directory, filename=filename))
            if song is not None:
                return (1, [song],)
        try:
            title = item['title']
            artist = item['artist']
            album = item['album']
            if isinstance(album, list):
                # work-around for bug in some v1 gameTracks.json files
                album = album[0]
            if isinstance(album, str):
                album = Album.search_for_item(session, {'name': album})
            elif isinstance(album, int):
                album = Album.get(session, pk=pk_maps["Album"][album])
            if isinstance(artist, str):
                artist = Artist.search_for_item(session, {'name': artist})
            elif isinstance(artist, int):
                artist = Artist.get(session, pk=pk_maps["Artist"][artist])
        except KeyError:
            return (0, [],)
        # print((filename, title, artist, album))
        result = Song.search(session, filename=filename, title=title,
                             artist=artist, album=album)
        count = result.count()
        if multiple and count > 0:
            return (count, result,)
        if count == 1 and not multiple:
            return (count, [cast(Song, result.first())],)
        if count == 0:
            result = Song.search(session, filename=filename, title=title,
                                 artist=artist)
            count = result.count()
        if multiple and count > 0:
            return (count, result,)
        if count == 1 and not multiple:
            return (count, [cast(Song, result.first())],)
        if count > 1:
            result = result.filter_by(duration=item['duration'])
            count = result.count()
        return (count, result,)

    # pylint: disable=too-many-branches
    @classmethod
    def from_json(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                  src: Dict) -> Dict:
        """
        converts any fields in item to Python objects
        """
        columns = cls.attribute_names()
        columns += ['directory', 'artist', 'album']
        item = {}
        for key, value in src.items():
            if key in columns:
                if isinstance(value, list):
                    value = value[0]
                item[key] = value
        parent = None
        parent_pk = item.get('directory', None)
        if parent_pk is not None:
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
        if 'uuid' in item:
            item['uuid'] = cls.str_from_uuid(cls.str_to_uuid(item['uuid']))
        for field in ['filename', 'title', 'artist', 'album']:
            if (field in item and isinstance(item[field], str)
                    and len(item[field]) > 1):
                item[field] = cls.trim_string(item[field])
        if 'album' in item:
            if isinstance(item['album'], str):
                item['album'] = Album.search_for_item(
                    session, { 'name': item['album'] })
            else:
                album_pk = pk_maps["Album"][item['album']]
                item['album'] = Album.get(session, pk=album_pk)
        if 'artist' in item:
            if isinstance(item['artist'], str):
                item['artist'] = Artist.search_for_item(
                    session, { 'name': item['artist'] })
            else:
                art_pk = pk_maps["Artist"].get(item['artist'], None)
                if art_pk is not None:
                    item['artist'] = Artist.get(session, pk=art_pk)
        return item

    @staticmethod
    def trim_string(field: str) -> str:
        """
        Clean-up a field by checking for common characters that wrap it
        """
        if field[0] == '"' and field[-1] == '"':
            field = field[1:-1]
        if field[0] == '[' and field[-1] == ']':
            field = field[1:-1]
        if field[:2] == "u'" and field[-1] == "'":
            field = field[2:-1]
        return field

    def check_for_uuid(self):
        """
        add a UUID to this song if it doesn't have a UUID
        """
        if self.uuid is None:
            album = self.album.name if self.album is not None else ''
            artist = self.artist.name if self.artist is not None else ''
            self.uuid = self.create_uuid(
                filename=self.filename, title=self.title,
                artist=artist, duration=self.duration,
                sample_width=self.sample_width,
                channels=self.channels,
                sample_rate=self.sample_rate,
                bitrate=self.bitrate,
                album=album)

# pylint: disable=unused-argument
def check_song_for_uuid(mapper, connect, song):
    """
    add a UUID to song before saving if it doesn't have a UUID
    """
    song.check_for_uuid()

listen(Song, 'before_insert', check_song_for_uuid)
