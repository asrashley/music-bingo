"""
class to represent one Song within a game.
"""

import datetime
from typing import Optional, cast

from . import models
from .directory import Directory
from .primes import PRIME_NUMBERS
from .song import Song

class Track:
    """
    The Track class represents one Song within a game.
    """
    def __init__(self, song: Song,
                 prime: int,  # a prime number used during game generation
                 start_time: int   # position of song in playlist (in milliseconds)
                ):
        self.song = song
        self.prime = prime
        self.start_time = start_time

    def __getattr__(self, name):
        return getattr(self.song, name)

    def model(self, game: models.Game) -> Optional[models.Track]:
        """
        get database model for this track
        """
        number = PRIME_NUMBERS.index(self.prime)
        return models.Track.get(game=game, number=number)

    def save(self, game: models.Game, commit: bool = False) -> models.Track:
        """
        save track to database
        """
        song = self.song.model()
        if song is None:
            song = self.song.save(commit=commit)
        number = PRIME_NUMBERS.index(self.prime)
        trk = models.Track.get(game=game, number=number)
        if trk is None:
            trk = models.Track(game=game, song=song, number=number,
                start_time=self.start_time)
        else:
            trk.set(start_time=self.start_time, song=song)
        if commit:
            models.flush()
        return trk
