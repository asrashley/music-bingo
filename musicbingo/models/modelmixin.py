"""
A mixin that is added to each model to provide a set of common
utility functions.
"""

from typing import cast, AbstractSet, Any, Dict, Optional, List

from sqlalchemy import DDL, MetaData, Table, sql  # type: ignore
from sqlalchemy.orm import class_mapper, ColumnProperty, RelationshipProperty  # type: ignore
from sqlalchemy.orm.collections import InstrumentedList  # type: ignore
from sqlalchemy.schema import CreateColumn  # type: ignore
from sqlalchemy.orm.query import Query  # type: ignore
from sqlalchemy.orm.dynamic import AppenderQuery  # type: ignore
from sqlalchemy.orm.session import Session  # type: ignore

from .base import Base

JsonObject = Dict[str, Any]
PrimaryKeyMap = Dict[str, Dict[int, int]]

class ModelMixin:
    @classmethod
    def add_column(cls, engine, column_types, name: str) -> str:
        db_col = column_types[name]
        col_def = CreateColumn(getattr(cls, name)).compile(engine)
        return 'ALTER TABLE {0} ADD {1}'.format(cls.__tablename__, col_def)  # type: ignore

    @classmethod
    def exists(cls, session: Session, **kwargs) -> bool:
        """
        Check if the given object exists
        """
        return session.query(cls.pk).filter_by(**kwargs).scalar() is not None  # type: ignore

    @classmethod
    def get(cls, session: Session, **kwargs) -> Optional["ModelMixin"]:
        """
        Get one object from a model, or None if not found
        """
        return session.query(cls).filter_by(**kwargs).one_or_none()

    @classmethod
    def search(cls, session: Session, **kwargs) -> Query:
        """
        Search for all items in a model that match the fields specified
        in kwargs.
        For example Song.search(session, title="Hello")
        """
        return session.query(cls).filter_by(**kwargs)

    @classmethod
    def attribute_names(cls):
        return [prop.key for prop in class_mapper(cls).iterate_properties
                if isinstance(prop, ColumnProperty)]

    @classmethod
    def show(cls, session: Session) -> None:
        def pad(value, width):
            value = value[:width]
            if len(value) < width:
                value += ' ' * (width - len(value))
            return value

        columns = cls.attribute_names()
        max_width = 20
        widths = {}
        for field in columns:
            widths[field] = len(field)
        for item in session.query(cls):
            for field in columns:
                value = str(getattr(item, field))
                widths[field] = max(widths[field], min(len(value), max_width))
        line = '-' * (1 + sum(widths.values()) + len(columns) * 3)
        print(line)
        print(cls.__name__)
        print(line)
        print('| ' + (' | '.join([pad(col, widths[col]) for col in columns])) + ' |')
        print(line)
        for item in session.query(cls):
            values = []
            for col in columns:
                values.append(pad(str(getattr(item, col)), widths[col]))
            print('| ' + (' | '.join(values)) + ' |')
        print(line)

    @classmethod
    def all(cls, session: Session):
        """
        Return all items from this table
        """
        return session.query(cls)

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
            elif exclude is not None and prop.key in exclude:
                continue
            #print(prop.key, type(prop))
            if isinstance(prop, ColumnProperty):
                retval[prop.key] = getattr(self, prop.key)
            elif isinstance(prop, RelationshipProperty) and with_collections:
                value = getattr(self, prop.key)
                #print('value', type(value))
                if value is not None:
                    if isinstance(value, (AppenderQuery, list)):
                        value = [v.pk for v in value]
                    elif isinstance(value, Base):
                        value = value.pk
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
                retval[prop.key] = retval[pk_name]
                del retval[pk_name]
        return retval

    @classmethod
    def migrate_schema(cls, engine, existing_columns, column_types, version) -> List[str]:
        """
        Migrate the model from specified version to the latest version.
        Returns a list of SQL statements to modify the table.
        :version: The currently detected version of the model
        """
        raise NotImplementedError(f"migrate_schema must be implemented by {cls.__name__} model")

    @classmethod
    def migrate_data(cls, session: Session, version: int) -> int:
        """
        Migrate data to allow model to work with the current Schema.
        Call *after* all tables have completed their migrate_schema() calls
        :version: The currently detected version of the model
        """
        return 0
