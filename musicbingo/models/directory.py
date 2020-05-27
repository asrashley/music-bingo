"""
Database mode for directories
"""
import typing

from sqlalchemy import Column, String, Integer, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject


class Directory(Base, ModelMixin):  # type: ignore
    """
    Database mode for directories
    """
    __plural__ = 'Directories'
    __tablename__ = 'Directory'
    __schema_version__ = 2

    pk = Column(Integer, primary_key=True)
    name = Column(String(512), unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    parent_pk = Column('directory', Integer, ForeignKey('Directory.pk'),
                       nullable=True)
    parent = relationship("Directory", remote_side=[pk], backref="directories")
    songs = relationship("Song", back_populates="directory")

    # pylint: disable=unused-argument
    @classmethod
    def migrate_schema(cls, engine, existing_columns, column_types,
                       version) -> typing.List[str]:
        """
        Migrate database Schema
        """
        return []

    @classmethod
    def search_for_directory(cls, session: Session,
                             item: JsonObject) -> typing.Optional["Directory"]:
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
