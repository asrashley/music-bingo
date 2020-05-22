import copy
from pathlib import Path
import typing

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore
from sqlalchemy.schema import UniqueConstraint, CreateTable  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin, JsonObject
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
    artist = Column(String)
    duration = Column(Integer, default=0, nullable=False)
    channels = Column(Integer, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    sample_width = Column(Integer, nullable=False)
    bitrate = Column(Integer, nullable=False)
    album = Column(String, nullable=True)
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
    def import_json(cls, sess: ImportSession, items: typing.List[JsonObject]) -> None:
        pk_map: typing.Dict[int, int] = {}
        sess.set_map(cls.__name__, pk_map)
        skipped = []
        for item in items:
            fields = cls.from_json(sess, item)
            #song = cls.lookup(fields, pk_maps)
            song = cls.search_for_song(sess, fields)
            skip = False
            if fields['directory'] is None:
                print('Failed to find parent {0} for song: "{1}"'.format(
                    item.get('directory', None), fields['filename']))
                skip = True
            elif sess.options.exists == True:
                dirname = fields['directory'].absolute_path(sess.options)
                filename = dirname.joinpath(fields['filename'])
                if not filename.exists():
                    skip = True
            if skip:
                alternative = cls.search_for_song(sess, item)
                if alternative:
                    pk_map[item['pk']] = alternative.pk
                else:
                    skipped.append(item)
                continue
            pk = None
            if 'pk' in fields:
                pk = fields['pk']
                del fields['pk']
            if song is None:
                song = cls(**fields)
                sess.add(song)
            else:
                for key, value in fields.items():
                    if key not in ['filename']:
                        setattr(song, key, value)
            sess.commit()
            if pk is not None:
                pk_map[pk] = song.pk
        for item in skipped:
            alternative = cls.search_for_song(sess, item)
            if alternative:
                print('Found alternative for {0} missing song {1}'.format(
                    alternative.pk, item))
                pk_map[item['pk']] = alternative.pk
            else:
                print('Failed to find an alterative for Song: {0}'.format(item))
                print('Adding the Song anyway')
                lost = Directory.get(sess.session, name="lost+found")
                if lost is None:
                    lost = Directory(
                        name="lost+found",
                        title="lost & found",
                        artist="Orphaned songs")
                    sess.session.add(lost)
                fields = cls.from_json(sess, item)
                if 'directory' not in fields or fields['directory'] is None:
                    fields['directory'] = lost
                song = cls(**fields)
                if 'pk' in item:
                    pk_map[item['pk']] = song.pk
                sess.commit()

    @classmethod
    def lookup(cls, sess: ImportSession, item: JsonObject) -> typing.Optional["Song"]:
        if 'pk' not in item:
            return cls.search_for_song(sess, item)
        song_pk = item['pk']
        pk_map = sess["Song"]
        if song_pk in pk_map:
            song_pk = pk_map[song_pk]
        try:
            song = typing.cast(
                typing.Optional["Song"],
                Song.get(sess.session, pk=song_pk))
        except KeyError:
            song = None
        if song is None:
            song = cls.search_for_song(sess, item)
        return song

    @classmethod
    def search_for_song(cls, sess: ImportSession,
                        item: JsonObject) -> typing.Optional["Song"]:
        """
        Try to match this item to a song already in the database.
        """
        try:
            filename = item['filename']
        except KeyError:
            return None
        directory = item.get("directory", None)
        if directory is not None and directory in sess["Directory"]:
            directory = sess["Directory"][directory]
        if directory is not None:
            if isinstance(directory, int):
                song = typing.cast(
                    typing.Optional[Song],
                    Song.get(sess.session, directory_pk=directory, filename=filename))
            else:
                song = typing.cast(
                    typing.Optional[Song],
                    Song.get(sess.session, directory=directory, filename=filename))
            #print("song.get", directory_pk, filename, song)
            if song is not None:
                return song
        try:
            title = item['title']
            artist = item['artist']
            album = item['album']
        except KeyError:
            return None
        result = Song.search(sess.session, filename=filename, title=title,
                             artist=artist, album=album)
        count = result.count()
        if count == 1:
            return result.first()
        if count == 0:
            result = Song.search(sess.session, filename=filename, title=title,
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
    def from_json(cls, sess: ImportSession, src: typing.Dict) -> typing.Dict:
        """
        converts any fields in item to Python objects
        """
        columns = cls.attribute_names()
        columns.append('directory')
        item = {}
        #copy.copy(item)
        for key, value in src.items():
            if key in columns:
                item[key] = value
        parent = None
        parent_pk = item.get('directory', None)
        if parent_pk is not None and parent_pk in sess["Directory"]:
            parent_pk = sess["Directory"][parent_pk]
        if parent_pk is not None:
            parent = Directory.get(sess.session, pk=parent_pk)
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
