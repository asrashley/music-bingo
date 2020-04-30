"""
Represents a Bingo ticket with a songs for each
row and column.
"""

from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from . import models
from .docgen.colour import Colour
from .options import Options

# pylint: disable=too-few-public-methods
class BingoTicket:
    """Represents a Bingo ticket with 15 songs"""

    def __init__(self, options: Options, fingerprint: int = 0,
                 number: Optional[int] = None):
        self.options = options
        self.fingerprint = fingerprint
        self.tracks: List[Track] = []
        self.number = number

    def box_colour_style(self, col: int, row: int) -> Colour:
        """Get the background colour for a given bingo ticket"""
        palette = self.options.palette
        if palette.colours:
            colour = palette.colours[(col + row * self.options.columns) %
                                     len(palette.colours)]
        else:
            # if col & row are both even or both odd, use box_alternate_bg
            if (((col & 1) == 0 and (row & 1) == 0) or
                    ((col & 1) == 1 and (row & 1) == 1)):
                colour = palette.box_alternate_bg
            else:
                colour = palette.box_normal_bg
        return colour

    def to_dict(self, exclude: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        return this ticket as a dictionary
        """
        retval: Dict[str, Any] = {}
        if exclude is None:
            exclude = set({'options'})
        for key, value in self.__dict__.items():
            if value is None or key[0] == '_':
                continue
            if key in exclude:
                continue
            retval[key] = value
        return retval

    def save(self, game: models.Game, commit=False) -> models.BingoTicket:
        """
        save ticket to database
        """
        args = self.to_dict(exclude={'options', 'tracks', 'fingerprint'})
        tracks: List[models.Track] = []
        order: List[int] = []
        for track in self.tracks:
            mdl = track.save(game, commit=True)
            tracks.append(mdl)
            order.append(mdl.pk)
        retval = models.BingoTicket(game=game, tracks=tracks, order=order,
                               fingerprint=str(self.fingerprint), **args)
        if commit:
            models.flush()
        return retval

