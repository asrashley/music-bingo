import copy
from pathlib import Path
import typing

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func # type: ignore
from sqlalchemy.orm import relationship, backref # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.importsession import ImportSession
from musicbingo.models.modelmixin import ModelMixin, JsonObject

class Directory(Base, ModelMixin): # type: ignore
    __plural__ = 'Directories'
    __tablename__ = 'Directory'
    __schema_version__ = 2

    pk = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    parent_pk = Column('directory', Integer, ForeignKey('Directory.pk'),
        nullable=True)
    parent = relationship("Directory", remote_side=[pk], backref="directories")
    songs = relationship("Song", back_populates = "directory")

    @classmethod
    def migrate(cls, engine, mapper, version) -> typing.List[str]:
        return []

    @classmethod
    def import_json(cls, sess: ImportSession, items: typing.List[typing.Dict[str, typing.Any]]) -> None:
        pk_map: typing.Dict[int, int] = {}
        sess.set_map(cls.__name__, pk_map)
        skipped = []
        for item in items:
            fields = cls.from_json(sess, item)
            directory = cls.lookup(sess, fields)
            try:
                pk = fields['pk']
                del fields['pk']
            except KeyError:
                pk = None
            if directory is None:
                #print(fields)
                directory = Directory(**fields)
                if sess.options.exists:
                    if not directory.absolute_path(sess.options).exists():
                        print(f'Skipping missing directory: "{directory.name}"')
                        skipped.append(item)
                        continue
                sess.add(directory)
            else:
                for key, value in fields.items():
                    if key not in ['pk', 'name']:
                        setattr(directory, key, value)
            sess.commit()
            if pk is not None:
                pk_map[pk] = directory.pk
        for item in items:
            directory = cls.lookup(sess, item)
            if directory is None:
                continue
            parent_pk = item.get('Parent', None)
            if parent_pk is None:
                parent_pk = item.get('Directory', None)
            if directory.parent is None and parent_pk is not None:
                parent = Directory.get(sess.session, pk=parent_pk)
                if parent is None and parent_pk in pk_map:
                    parent = Directory.get(sess.session, pk=pk_map[parent_pk])
                if parent is not None:
                    directory.directory = parent
                    sess.commit()
        for item in skipped:
            directory = cls.search_for_directory(sess.session, item)
            if directory is not None:
                pk_map[item['pk']] = directory.pk

    @classmethod
    def from_json(cls, sess: ImportSession, item: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        converts any fields in item into a dictionary ready for use Track constructor
        """
        retval = {}
        for field, value in item.items():
            if field not in ['directories', 'songs', 'directory', 'parent']:
                retval[field] = value
        clipdir = str(sess.options.clips())
        if retval['name'].startswith(clipdir):
            retval['name'] = retval['name'][len(clipdir):]
        if retval['name'] == "":
            retval['name'] = "."
        parent = item.get('parent', None)
        if parent is None:
            parent = item.get('directory', None)
        if parent is not None:
            retval['parent'] = cls.lookup(sess, dict(pk=parent))
        return retval

    @classmethod
    def lookup(cls, sess: ImportSession, item: JsonObject) -> typing.Optional["Directory"]:
        """
        Check if this directory is already in the database
        """
        pk_map = sess["Directory"]
        try:
            rv = Directory.get(sess.session, pk=item['pk'])
            if rv is None and item['pk'] in pk_map:
                rv = Directory.get(sess.session, pk=pk_map[item['pk']])
        except KeyError:
            rv = None
        if rv is None and 'name' in item:
            clipdir = str(sess.options.clips())
            name = item['name']
            if name.startswith(clipdir):
                name = name[len(clipdir):]
            if name == "":
                name = "."
            rv = Directory.get(sess.session, name=name)
        return typing.cast(typing.Optional[Directory], rv)

    @classmethod
    def search_for_directory(cls, session, item: JsonObject) -> typing.Optional["Directory"]:
        """
        Try to match this item to a directory already in the database.
        """
        if 'name' in item:
            directory = typing.cast(
                typing.Optional["Directory"],
                Directory.get(session, name=item['name']))
            if directory is not None:
                return directory
        try:
            title = item['title']
            artist = item['artist']
        except KeyError:
            return None
        result = select(directory for directory in Directory # type: ignore
                        if directory.title == title
                        and directory.artist == artist)
        count = result.count()
        if count == 1:
            return result.first()
        return None

    #def absolute_path(self, options) -> Path:
    #    """
    #    Get the absolute path of this directory
    #    """
    #    if self.directory is None:
    #        pdir = options.clips()
    #    else:
    #        pdir = self.directory.absolute_path(options)
    #    return pdir.joinpath(self.name)
