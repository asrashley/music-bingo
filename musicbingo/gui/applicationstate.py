"""
Enumeration of GUI application state
"""
from enum import IntEnum, auto

class ApplicationState(IntEnum):
    """Enumeration of GUI application state"""
    IDLE = auto()
    GENERATING_GAME = auto()
    GAME_GENERATED = auto()
    SONG_PLAYING = auto()
