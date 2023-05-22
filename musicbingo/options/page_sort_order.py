"""
Enum to control sorting of tickets when output
"""

# TODO: switch to StrEnum from Python 3.11
from enum import Enum
from typing import List

class PageSortOrder(Enum):
    """
    Enum to control sorting of tickets when output
    """
    NUMBER = 'number'
    INTERLEAVE = 'interleave'
    WINNER = 'winner'

    @classmethod
    def names(cls) -> List[str]:
        """get list of items in this enum"""
        return sorted(cls.__members__.keys()) # type: ignore
        # return sorted([item.value for item in cls]) # type: ignore

    @classmethod
    def from_string(cls, name: str) -> "PageSortOrder":
        """
        Convert name string into this enum
        """
        if name.startswith('PageSortOrder.'):
            name = name.split('.')[-1]
        try:
            return cls[name.upper()]  # type: ignore
        except KeyError:
            for item in cls:
                if item.value == name.lower():
                    return item
        raise ValueError(f'Unknown sort order: "{name}"')

    def __str__(self) -> str:
        return self.name

    def to_json(self) -> str:
        """
        Convert sort order name to a string.
        Used by utils.flatten()
        """
        return self.name.lower()
