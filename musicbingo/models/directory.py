"""
Database mode for directories
"""
from pathlib import PureWindowsPath
from typing import List, Optional, cast, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, text
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.expression import TextClause

from .base import Base
from .modelmixin import ModelMixin, JsonObject
from .schemaversion import SchemaVersion
from .session import DatabaseSession

if TYPE_CHECKING:
    from .song import Song

class Directory(Base, ModelMixin):  # type: ignore
    """
    Database mode for directories
    """
    __plural__ = 'Directories'
    __tablename__ = 'Directory'
    __schema_version__ = 4

    pk: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    parent_pk: Mapped[int] = mapped_column(
        'directory', Integer, ForeignKey('Directory.pk'), nullable=True)
    parent: Mapped[Optional["Directory"]] = relationship(
        "Directory", remote_side=[pk], backref="directories")
    songs: Mapped[list["Song"]] = relationship("Song", back_populates="directory")

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate database Schema
        """
        cmds: List[TextClause] = []
        version, existing_columns, _ = sver.get_table(cls.__tablename__)
        if version < 4:
            if 'artist' in existing_columns and sver.options.provider != 'sqlite':
                cmds.append(text('ALTER TABLE `Directory` DROP COLUMN `artist`'))
        return cmds

    @classmethod
    def migrate_data(cls, session: DatabaseSession, sver: SchemaVersion) -> int:
        """
        Migrate data to allow model to work with the current Schema.
        """
        count: int = 0
        for subdir in session.query(cls).filter(cls.name.like('_:\\_')):
            subdir.name = PureWindowsPath(subdir.name).as_posix()
            count += 1
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
            title = item['title']
        except KeyError:
            return None
        return session.query(Directory).filter_by(title=title).one_or_none()
