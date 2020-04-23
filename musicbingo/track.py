"""
class to represent one Song within a game.
"""

import datetime
from typing import Optional, cast

from . import models
from .directory import Directory
from .primes import PRIME_NUMBERS
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

    def model(self, game: models.Game) -> Optional[models.Track]:
        """
        get database model for this track
        """
        number = PRIME_NUMBERS.index(self.prime)
        return models.Track.get(game=game, number=number)

    def save(self, game: models.Game) -> models.Track:
        """
        save track to database
        """
        args = self.to_dict(exclude=['ref_id', 'prime'])
        args['number'] = PRIME_NUMBERS.index(self.prime)
        trk = models.Track.get(game=game, number=args['number'])
        if trk is None:
            trk = models.Track(game=game, **args)
        else:
            trk.set(**args)
        return trk
