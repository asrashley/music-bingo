"""
Enumeration of game operating modes
"""
from enum import IntEnum, auto
from typing import List

class GameMode(IntEnum):
    """Enumeration of game operating modes"""
    BINGO = auto()
    QUIZ = auto()
    CLIP = auto()

    @classmethod
    def names(cls) -> List[str]:
        """get list of items in this enum"""
        return sorted(cls.__members__.keys()) # type: ignore

    @classmethod
    def from_string(cls, name: str) -> "GameMode":
        """
        Convert name string into this enum
        """
        return cls[name.upper()]  # type: ignore
