"""
class to represent one Song within a game.
"""

from typing import Optional, cast

from . import models
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

    def model(self, game: models.Game, session) -> Optional[models.Track]:
        """
        get database model for this track
        """
        number = PRIME_NUMBERS.index(self.prime)
        return cast(
            Optional[models.Track],
            models.Track.get(session, game=game, number=number))

    def save(self, game: models.Game, song: models.Song, session,
             flush: bool = False) -> models.Track:
        """
        save track to database
        """
        number = PRIME_NUMBERS.index(self.prime)
        trk = models.Track.get(session, game_pk=game.pk, number=number)
        if trk is None:
            trk = models.Track(game=game, song=song, number=number,
                               start_time=self.start_time)
            session.add(trk)
        else:
            trk.set(start_time=self.start_time, song=song)
        if flush:
            session.flush()
        assert trk is not None
        return cast(models.Track, trk)
