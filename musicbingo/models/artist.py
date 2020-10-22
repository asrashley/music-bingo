"""
Database model for an artist
"""

from typing import Dict, List, Optional, cast

from sqlalchemy import Column, String, Integer  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import (
    ArtistAlbumMixin, JsonObject, PrimaryKeyMap, ModelMixin
)
from musicbingo.utils import clean_string

from .schemaversion import SchemaVersion
from .session import DatabaseSession

class Artist(Base, ArtistAlbumMixin, ModelMixin):  # type: ignore
    """
    Database model for an artist
    """
    __plural__ = 'Artists'
    __tablename__ = 'Artist'
    __schema_version__ = 1

    pk = Column('pk', Integer, primary_key=True)
    name = Column(String(512), index=True, unique=True)
    songs = relationship("Song", back_populates="artist")

    # pylint: disable=unused-argument,arguments-differ
    @classmethod
    def migrate_schema(cls, engine: Engine, sver: SchemaVersion) -> List[str]:
        """
        Migrate database Schema
        """
        cmds: List[str] = []
        #version, existing_columns, column_types = sver.get_table("Song")
        #print(existing_columns)
        return cmds

    @classmethod
    def lookup(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
               item: JsonObject) -> Optional["Artist"]:
        """
        Try to get an Artist from the database using the data in "item"
        """
        if 'pk' not in item:
            return cast(Optional[Artist],
                        cls.search_for_item(session, item))
        pk_map = pk_maps["Artist"]
        try:
            art_pk = pk_map[item['pk']]
            artist = cast(
                Optional["Artist"],
                Artist.get(session, pk=art_pk))
        except KeyError:
            artist = None
        if artist is None:
            artist = cast(Optional[Artist],
                          cls.search_for_item(session, item))
        return artist

    @classmethod
    def from_json(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                  src: Dict) -> Dict:
        """
        converts any fields in item to Python objects
        """
        columns = set(cls.attribute_names())
        item = {}
        for key, value in src.items():
            if key in columns:
                if isinstance(value, list):
                    value = value[0]
                item[key] = value
        if 'songs' in item:
            del item['songs']
        if 'name' in item:
            item['name'] = clean_string(item['name'])
        return item
