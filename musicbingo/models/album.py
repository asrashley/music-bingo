"""
Database model for an album
"""

from typing import Dict, List, Optional, cast, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.expression import TextClause

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import (
    ArtistAlbumMixin, JsonObject, PrimaryKeyMap, ModelMixin
)
from musicbingo.utils import clean_string

from .schemaversion import SchemaVersion
from .session import DatabaseSession

if TYPE_CHECKING:
    from .song import Song

class Album(Base, ArtistAlbumMixin, ModelMixin):  # type: ignore
    """
    Database model for an album
    """
    __plural__ = 'Albums'
    __tablename__ = 'Album'
    __schema_version__ = 1

    pk: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(512), index=True, unique=True)
    songs: Mapped[list["Song"]] = relationship("Song", back_populates="album")

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[TextClause]:
        """
        Migrate database Schema
        """
        cmds: List[TextClause] = []
        return cmds

    @classmethod
    def lookup(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> Optional["Album"]:
        """
        Try to get an Album from the database using the data in "item"
        """
        if 'pk' not in item:
            return cast(Optional[Album],
                        cls.search_for_item(session, item))
        pk_map = pk_maps["Album"]
        try:
            art_pk = pk_map[item['pk']]
            album = cast(
                Optional["Album"],
                Album.get(session, pk=art_pk))
        except KeyError:
            album = None
        if album is None:
            album = cast(Optional[Album],
                         cls.search_for_item(session, item))
        return album

    @classmethod
    def from_json(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                  src: Dict) -> Dict:
        """
        converts any fields in item to Python objects
        """
        columns = cls.attribute_names()
        item = {}
        for key, value in src.items():
            if key in columns and key != 'songs':
                if isinstance(value, list):
                    value = value[0]
                if isinstance(value, str):
                    item[key] = clean_string(value)
                else:
                    item[key] = value
        return item
