"""
Represents a Bingo ticket with a songs for each
row and column.
"""

from typing import cast, AbstractSet, Any, Dict, List, Optional

from . import models
from .docgen.colour import Colour
from .palette import Palette
from .track import Track

# pylint: disable=too-few-public-methods

class BingoTicket:
    """Represents a Bingo ticket with 15 songs"""

    def __init__(self, palette: Palette, columns: int, fingerprint: int = 0,
                 number: Optional[int] = None, tracks: Optional[List[Track]] = None):
        self.palette = palette
        self.columns = columns  # number of columns
        self.fingerprint = fingerprint
        self.tracks: List[Track] = []
        self.number = number
        self.wins_on_track: int = 0
        self.rows_complete_on_track: List[int] = []
        if tracks is not None:
            self.fingerprint = 0
            self.tracks = tracks
            for trk in tracks:
                self.fingerprint *= trk.prime

    def compute_win_values(self, tracks: List[Track]) -> None:
        """
        Calculate when the ticket is complete and when each row is
        complete.
        """
        self.wins_on_track = 0
        fingerprint: int = 1
        row_fingerprints: List[int] = []
        for idx, track in enumerate(self.tracks):
            fingerprint *= track.prime
            if ((idx + 1) % self.columns) == 0:
                row_fingerprints.append(fingerprint)
                fingerprint = 1
        self.rows_complete_on_track = [0] * len(row_fingerprints)
        for tnum, track in enumerate(tracks):
            fingerprint *= track.prime
            for idx, row in enumerate(row_fingerprints):
                if self.rows_complete_on_track[idx] != 0:
                    continue
                if (fingerprint % row) == 0:
                    self.rows_complete_on_track[idx] = tnum + 1
            if self.wins_on_track == 0 and (fingerprint % self.fingerprint) == 0:
                self.wins_on_track = tnum + 1

    def box_colour_style(self, col: int, row: int) -> Colour:
        """Get the background colour for a given bingo ticket"""
        if self.palette.colours:
            colour = self.palette.colours[(col + row * self.columns) %
                                          len(self.palette.colours)]
        else:
            # if col & row are both even or both odd, use box_alternate_bg
            if (((col & 1) == 0 and (row & 1) == 0) or
                    ((col & 1) == 1 and (row & 1) == 1)):
                colour = self.palette.box_alternate_bg
            else:
                colour = self.palette.box_normal_bg
        return colour

    def to_dict(self, exclude: Optional[AbstractSet[str]] = None) -> Dict[str, Any]:
        """
        return this ticket as a dictionary
        """
        retval: Dict[str, Any] = {}
        if exclude is None:
            exclude = set({'palette', 'columns'})
        for key, value in self.__dict__.items():
            if value is None or key[0] == '_':
                continue
            if key in exclude:
                continue
            retval[key] = value
        return retval

    def model(self, session, game: models.Game) -> Optional[models.BingoTicket]:
        """
        Get the database model for this Bingo ticket
        """
        return cast(
            Optional[models.BingoTicket],
            models.BingoTicket.get(session, game_pk=game.pk, number=self.number))

    def save(self, session, game: models.Game, flush: bool = False) -> models.BingoTicket:
        """
        save ticket to database
        """
        tracks: List[models.Track] = []
        for track in self.tracks:
            mdl = track.model(session=session, game=game)
            assert mdl is not None
            tracks.append(mdl)
        retval = models.BingoTicket(game=game,
                                    checked=0,
                                    number=self.number,
                                    fingerprint=str(self.fingerprint))
        retval.set_tracks(session, tracks)
        session.add(retval)
        if flush:
            session.flush()
        return retval
