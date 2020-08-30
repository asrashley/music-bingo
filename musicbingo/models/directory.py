"""
Database mode for directories
"""
from typing import List, Optional, cast

from sqlalchemy import Column, String, Integer, ForeignKey  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
# from sqlalchemy.event import listen  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from .base import Base
from .modelmixin import ModelMixin, JsonObject
from .schemaversion import SchemaVersion
from .session import DatabaseSession

class Directory(Base, ModelMixin):  # type: ignore
    """
    Database mode for directories
    """
    __plural__ = 'Directories'
    __tablename__ = 'Directory'
    __schema_version__ = 3

    pk = Column(Integer, primary_key=True)
    name = Column(String(512), unique=True, index=True, nullable=False)
    title = Column(String(512), nullable=False)
    artist = Column(String(512), nullable=True)
    parent_pk = Column('directory', Integer, ForeignKey('Directory.pk'),
                       nullable=True)
    parent = relationship("Directory", remote_side=[pk], backref="directories")
    songs = relationship("Song", back_populates="directory")

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        cmds: List[str] = []
        return cmds

    @classmethod
    def migrate_data(cls, session: DatabaseSession, sver: SchemaVersion) -> int:
        """
        Migrate data to allow model to work with the current Schema.
        """
        count: int = 0
        return count

    @classmethod
    def search_for_directory(cls, session: DatabaseSession,
                             item: JsonObject) -> Optional["Directory"]:
        """
        Try to match this item to a directory already in the database.
        """
        if 'name' in item:
            directory = cast(
                Optional["Directory"],
                Directory.get(session, name=item['name']))
            if directory is not None:
                return directory
        try:
            artist = item['artist']
            title = item['title']
        except KeyError:
            return None
        return session.query(Directory).filter_by(title=title, artist=artist).one_or_none()
