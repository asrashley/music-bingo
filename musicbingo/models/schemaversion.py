"""
Database model for a user of the app
"""
from collections import namedtuple
from typing import Dict, List, Set

from musicbingo.options import DatabaseOptions
from .base import Base

TableInformation = namedtuple('TableInformation',
                              ['version', 'existing_columns', 'column_types'])

class SchemaVersion:
    """
    Holder to schema information for all tables
    """
    def __init__(self, tables: List[Base], options: DatabaseOptions):
        self.options = options
        self.versions = {}
        self.existing_columns: Dict[str, Set[str]] = {}
        self.column_types: Dict[str, Dict] = {}
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

    def set_column_types(self, table_name, columns: Dict) -> None:
        """
        set column definitions for a table
        """
        column_types = {}
        for col in columns:
            column_types[col.key] = col
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
