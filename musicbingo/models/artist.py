"""
Database model for an artist
"""

from typing import Dict, List, Optional, Tuple, cast

from sqlalchemy import Column, String, Integer  # type: ignore
from sqlalchemy.engine import Engine  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from musicbingo.models.base import Base
from musicbingo.models.modelmixin import ModelMixin, JsonObject, PrimaryKeyMap

from .schemaversion import SchemaVersion
from .session import DatabaseSession

class Artist(Base, ModelMixin):  # type: ignore
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
            return cls.search_for_artist(session, pk_maps, item)
        pk_map = pk_maps["Artist"]
        try:
            art_pk = pk_map[item['pk']]
            artist = cast(
                Optional["Artist"],
                Artist.get(session, pk=art_pk))
        except KeyError:
            artist = None
        if artist is None:
            artist = cls.search_for_artist(session, pk_maps, item)
        return artist

    @classmethod
    def search_for_artist(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                          item: JsonObject) -> Optional["Artist"]:
        """
        Try to match this item to an artist already in the database.
        """
        count, artists = cls.search_for_artists(session, pk_maps, item, False)
        if count > 0:
            return artists[0]
        return None

    @classmethod
    def search_for_artists(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                           item: JsonObject,
                           multiple: bool = True) -> Tuple[int, List["Artist"]]:
        """
        Try to match this item to one or more artists already in the database.
        """
        if 'name' not in item:
            return (0, [],)
        result = cls.search(session, name=item['name'])
        count = result.count()
        if multiple and count > 0:
            return (count, result,)
        if count == 1 and not multiple:
            return (count, [cast(cls, result.first())],) # type: ignore
        if count == 0:
            result = session.query(cls).filter(cls.name.like(item['name']))
            count = result.count()
        if count == 1 and not multiple:
            return (count, [cast(cls, result.first())],) # type: ignore
        return (count, result,)

    @classmethod
    def from_json(cls, session: DatabaseSession, pk_maps: PrimaryKeyMap,
                  src: Dict) -> Dict:
        """
        converts any fields in item to Python objects
        """
        columns = cls.attribute_names()
        item = {}
        for key, value in src.items():
            if key in columns:
                if isinstance(value, list):
                    value = value[0]
                item[key] = value
        if 'songs' in item:
            del item['songs']
        if 'name' in item and len(item['name']) > 1:
            if item['name'][0] == '"' and item['name'][-1] == '"':
                item['name'] = item['name'][1:-1]
            if item['name'][0] == '[' and item['name'][-1] == ']':
                item['name'] = item['name'][1:-1]
            if item['name'][:2] == "u'" and item['name'][-1] == "'":
                item['name'] = item['name'][2:-1]
        return item
