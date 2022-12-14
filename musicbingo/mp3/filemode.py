"""
Representation of MP3File open mode
"""

from enum import IntEnum

class FileMode(IntEnum):
    """file mode"""
    CLOSED = 0
    READ_ONLY = 1
    WRITE_ONLY = 2
