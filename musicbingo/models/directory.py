import copy
from pathlib import Path
import typing

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func  # type: ignore
from sqlalchemy.orm import relationship, backref  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap


class Directory(Base, ModelMixin):  # type: ignore
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
    songs = relationship("Song", back_populates="directory")

    @classmethod
    def migrate(cls, engine, mapper, version) -> typing.List[str]:
        return []

    @classmethod
    def search_for_directory(cls, session: Session, item: JsonObject) -> typing.Optional["Directory"]:
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
            artist = item['artist']
            title = item['title']
        except KeyError:
            return None
        return session.query(Directory).filter_by(title=title, artist=artist).one_or_none()
