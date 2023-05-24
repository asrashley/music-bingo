"""
Interface definition for a database session
"""

from typing import Protocol

class DatabaseSession(Protocol):
    """
    Interface to abstract away from sqlalchemy session
    """

    def add(self, model) -> None:
        """Add item to database"""

    def commit(self) -> None:
        """Commit changes to database"""

    def close(self) -> None:
        """Close database session"""

    def delete(self, model) -> None:
        """Remove item from database"""

    def flush(self) -> None:
        """Flush changes to database, but can still be rolled back"""

    def query(self, *args):
        """start database query"""

    def rollback(self) -> None:
        """Revert changes to database in this session"""
