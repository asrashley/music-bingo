"""
class to represent one Song within a game.
"""

import datetime
from typing import Optional, cast

from . import models
from .directory import Directory
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
        return models.Track.get(game=game, prime=str(self.prime))

    def save(self, game: models.Game) -> models.Track:
        """
        save track to database
        """
        args = self.to_dict(exclude=['ref_id', 'prime', 'start_time'])
        args['start_time'] = datetime.timedelta(milliseconds=self.start_time)
        args['number'] = str(self.prime)
        #db_dir = cast(Directory, self._parent).model()
        trk = models.Track.get(game=game, prime=str(self.prime))
        if trk is None:
            trk = models.Track(game=game, **args)
        else:
            trk.set(**args)
        return trk
