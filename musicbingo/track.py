"""
class to represent one Song within a game.
"""

from .song import Song

class Track(Song):
    """
    The Track class represents one Song within a game.
    """
    def __init__(self, prime: int,  # a prime number used during game generation
                 start_time: int,   # position of song in playlist (in milliseconds)
                 **kwargs):
        super(Track, self).__init__(**kwargs)
        self.prime = prime
        self.start_time = start_time
