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
                 number: Optional[int] = None):
        self.palette = palette
        self.columns = columns
        self.fingerprint = fingerprint
        self.tracks: List[Track] = []
        self.number = number

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
