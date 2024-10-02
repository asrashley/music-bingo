"""
A mixin that is added to each model to provide a set of common
utility functions.
"""
from collections.abc import Iterable
from typing import AbstractSet, Dict, Optional, List, Tuple, cast

from sqlalchemy import select, text
from sqlalchemy.orm import class_mapper, ColumnProperty, RelationshipProperty
from sqlalchemy.orm.query import Query
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateColumn
from sqlalchemy.orm.dynamic import AppenderQuery
from sqlalchemy.sql.expression import TextClause

from musicbingo import utils
from musicbingo.json_object import JsonObject

from .base import Base
from .schemaversion import SchemaVersion
from .session import DatabaseSession

PrimaryKeyMap = Dict[str, Dict[int, int]]

class ModelMixin:
    """
    Mix-in used by all models to provide a set of common
    utility functions.
    """

    # pylint: disable=unused-argument
    @classmethod
    def add_column(cls, engine: Engine, column_types, name: str) -> TextClause:
        """
        Add a column to the table of this model
        :name: the name of the column to add
        """
        col_def: str = str(CreateColumn(getattr(cls, name)).compile(engine))
        default: str = ''
        if column_types[name].default and column_types[name].default.arg is not None:
            default = f'DEFAULT {column_types[name].default.arg}'
        elif ' NOT NULL' in col_def:
            col_def = col_def.replace(' NOT NULL', '')
        return text(f'ALTER TABLE {cls.__tablename__} ADD {col_def} {default}')  # type: ignore

    @classmethod
    def exists(cls, session: DatabaseSession, **kwargs) -> bool:
        """
        Check if the given object exists
        """
        return session.query(cls.pk).filter_by(**kwargs).scalar() is not None  # type: ignore

    @classmethod
    def get(cls, session: DatabaseSession, **kwargs) -> Optional["ModelMixin"]:
        """
        Get one object from a model, or None if not found
        """
        return session.query(cls).filter_by(**kwargs).one_or_none()

    @classmethod
    def search(cls, session: DatabaseSession, **kwargs) -> Query:
        """
        Search for all items in a model that match the fields specified
        in kwargs.
        For example Song.search(session, title="Hello")
        """
        return session.query(cls).filter_by(**kwargs)

    @classmethod
    def attribute_names(cls) -> List[str]:
        """
        Get all the fields of this table
        """
        return [prop.key for prop in class_mapper(cls).iterate_properties
                if isinstance(prop, ColumnProperty)]

    @classmethod
    def show(cls, session: DatabaseSession, max_width: int = 80) -> None:
        """
        Show all items in this table
        """
        def pad(value, width):
            value = value[:width]
            if len(value) < width:
                value += ' ' * (width - len(value))
            return value

        min_column_width = 3
        columns = cls.attribute_names()
        max_width = max(max_width, min_column_width * len(columns))
        widths: Dict[str, int] = {}
        for field in columns:
            widths[field] = len(field)
        for item in session.query(cls):
            for field in columns:
                value = str(getattr(item, field))
                widths[field] = max(widths[field], min(len(value), max_width))
        total_width: int = sum(widths.values())
        while total_width > max_width:
            longest: Tuple[str, int] = ('', 0)
            for field, value in widths.items(): # type: ignore
                if value > longest[1]: # type: ignore
                    longest = (field, value) # type: ignore
            widths[longest[0]] = max(min_column_width, (3 * longest[1]) // 4)
            total_width = sum(widths.values())
        line: str = '-' * (1 + total_width + len(columns) * 3)
        print(line)
        print(cls.__name__)
        print(line)
        print('| ' + (' | '.join([pad(col, widths[col]) for col in columns])) + ' |')
        print(line)
        for item in session.query(cls):
            values = []
            for col in columns:
                val = getattr(item, col)
                if isinstance(val, str):
                    val = utils.clean_string(val, ascii_only=True)
                else:
                    val = str(val)
                values.append(pad(val, widths[col]))
            print('| ' + (' | '.join(values)) + ' |')
        print(line)

    @classmethod
    def all(cls, session: DatabaseSession) -> Iterable["ModelMixin"]:
        """
        Return all items from this table
        """
        statement = select(cls)
        for row in session.execute(statement):
            yield row[0]

    @classmethod
    def total_items(cls, session: DatabaseSession) -> int:
        """
        Count of all items from this table
        """
        return session.query(cls).count()

    @classmethod
    def delete_items(cls, session: DatabaseSession, **kwargs) -> int:
        """
        Delete the selected items from this table
        """
        #Example: session.execute(delete(models.Track).where(models.Track.game_pk=game.pk)
        #session.execute(delete(cls).where(**kwargs))
        count = 0
        for item in cls.search(session, **kwargs):
            session.delete(item)
            count += 1
        session.flush()
        return count

    def set(self, **kwargs) -> None:
        """
        Set the given attributes on this object
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None,
                only: Optional[AbstractSet[str]] = None,
                with_collections: bool = False) -> JsonObject:
        """
        Convert this model into a dictionary
        :exclude: set of attributes to exclude
        :only: set of attributes to include
        """
        retval = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if only is not None and prop.key not in only:
                continue
            if exclude is not None and prop.key in exclude:
                continue
            if isinstance(prop, ColumnProperty):
                retval[prop.key] = getattr(self, prop.key)
            elif isinstance(prop, RelationshipProperty) and with_collections:
                value = getattr(self, prop.key)
                if value is not None:
                    if isinstance(value, (AppenderQuery, list)):
                        value = [v.pk for v in value]
                    elif isinstance(value, Base):
                        value = value.pk  # type: ignore
                retval[prop.key] = value
        # If the collection has been included in the output, remove the "xxx_pk" version
        # of the column.
        # If the collection has not been included, rename the "xxx_pk" version of the
        # column to "xxx".
        for prop in class_mapper(self.__class__).iterate_properties:
            if not isinstance(prop, RelationshipProperty):
                continue
            pk_name = f'{prop.key}_pk'
            if prop.key in retval and pk_name in retval:
                del retval[pk_name]
            elif pk_name in retval and prop.key not in retval:
                if exclude is None or prop.key not in exclude:
                    retval[prop.key] = retval[pk_name]
                del retval[pk_name]
        return retval

    @classmethod
    def migrate_schema(cls, engine: Engine, version: SchemaVersion) -> List[TextClause]:
        """
        Migrate the model from specified version to the latest version.
        Returns a list of SQL statements to modify the table.
        :version: The currently detected version of the model
        """
        raise NotImplementedError(f"migrate_schema must be implemented by {cls.__name__} model")

    @classmethod
    def migrate_data(cls, session: DatabaseSession, version: SchemaVersion) -> int:
        """
        Migrate data to allow model to work with the current Schema.
        Call *after* all tables have completed their migrate_schema() calls
        :version: The currently detected version of the model
        """
        return 0

class ArtistAlbumMixin:
    """
    Common methods used for both Album and Artist objects
    """
    @classmethod
    def search_for_item(cls, session: DatabaseSession,
                        item: JsonObject) -> Optional["ArtistAlbumMixin"]:
        """
        Try to match "item" to an object already in the database.
        """
        count, items = cls.search_for_items(session, item, False)
        if count > 0:
            return items[0]
        return None

    @classmethod
    def search_for_items(cls, session: DatabaseSession, item: JsonObject,
                         multiple: bool = True) -> Tuple[int, List]:
        """
        Try to match this item to one or more items already in the database.
        """
        if 'name' not in item:
            return (0, [],)
        result = cls.search(session, name=item['name']) # type: ignore
        count = result.count()
        if multiple and count > 0:
            return (count, result,)
        if count == 1 and not multiple:
            return (count, [cast(cls, result.first())],) # type: ignore
        if count == 0:
            result = session.query(cls).filter(
                cls.name.like(item['name'])) # type: ignore
            count = result.count()
        if count == 1 and not multiple:
            return (count, [cast(cls, result.first())],) # type: ignore
        return (count, result,)
