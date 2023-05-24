"""
Interface definition for a database query
"""
from typing import Any, Protocol

class DatabaseQuery(Protocol):
    """
    Interface to abstract away from sqlalchemy query
    """

    def count(self) -> int:
        """Get number of matching items"""

    def first(self) -> Any:
        """Get first matching item"""

    def filter_by(self, *args, **kwargs) -> "DatabaseQuery":
        """Filter this query"""
