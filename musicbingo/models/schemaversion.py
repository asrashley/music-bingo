"""
Database model for a user of the app
"""
from typing import Dict, List, Set, NamedTuple

from sqlalchemy.engine.interfaces import ReflectedColumn

from musicbingo.options import DatabaseOptions
from .base import Base

class TableInformation(NamedTuple):
    """
    Holds version information about one table
    """
    version: int
    existing_columns: Set[str]
    column_types: dict[str, ReflectedColumn]

class SchemaVersion:
    """
    Holder to schema information for all tables
    """

    column_types: Dict[str, Dict]
    existing_columns: Dict[str, Set[str]]
    options: DatabaseOptions
    versions: dict[str, int]

    def __init__(self, tables: List[type[Base]], options: DatabaseOptions) -> None:
        self.options = options
        self.versions = {}
        self.existing_columns = {}
        self.column_types = {}
        for table in tables:
            self.column_types[table.__tablename__] = {}
            self.existing_columns[table.__tablename__] = set()
            self.versions[table.__tablename__] = 0

    def set_version(self, table_name: str, version: int) -> None:
        """
        Set version information for a table
        """
        self.versions[table_name] = version

    def set_existing_columns(self, table_name, existing_columns: Set[str]) -> None:
        """
        Set version information for a table
        """
        self.existing_columns[table_name] = existing_columns

    def set_column_types(self, table_name: str, columns: dict[str, ReflectedColumn]) -> None:
        """
        set column definitions for a table
        """
        column_types: dict[str, ReflectedColumn] = {}
        for key, col in columns.items():
            column_types[key] = col
        self.column_types[table_name] = column_types

    def get_version(self, table_name) -> int:
        """
        get version of a table
        """
        return self.versions[table_name]

    def get_table(self, table_name) -> TableInformation:
        """
        Get information on one table
        """
        return TableInformation(self.versions[table_name],
                                self.existing_columns[table_name],
                                self.column_types[table_name])

    def __repr__(self) -> str:
        versions = []
        for key, value in self.versions.items():
            versions.append(f'{key}={value}')
        return 'SchemaVersion(' + ','.join(versions) + ')'

    def show(self) -> None:
        """
        Show full Schema version information
        """
        for name,version in self.versions.items():
            print(name)
            print(f'  Version: {version}')
            print('  Columns: {0}'.format(self.existing_columns.get(name))) # pylint: disable=consider-using-f-string
