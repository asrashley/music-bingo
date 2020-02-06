"""
page sizes
"""

from enum import Enum
import re
from typing import NamedTuple, Union, cast

INCH: float = 25.4

class Dimension:
    """
    Represents the length of something in real-world units
    """
    UNITS = {
        'in': INCH,
        'pt': INCH / 72.0,
        'px': INCH / 96.0,
        'cm': 10.0,
        'mm': 1.0
    }

    _re = re.compile(r'^([\d\.]+)\s*(\w+)$')

    def __init__(self, value: Union[float, str, "Dimension"]) -> None:
        if isinstance(value, str):
            if not value.endswith('%'):
                match = self._re.match(value)
                if match is None:
                    raise ValueError(f'Failed to parse "{value}"')
                value = float(match.group(1)) * self.UNITS[match.group(2)]
        elif isinstance(value, Dimension):
            value = cast(Dimension, value).value
        self.value: float = cast(float, value)

    def points(self) -> float:
        """Convert dimension into points (1/72nd of an inch)"""
        if not self.absolute:
            raise ValueError(self.value)
        return self.value / self.UNITS['pt']

    def points_or_relative(self) -> Union[float, str]:
        """
        Convert dimension into points unless relative, when the relative
        value is returned
        """
        if self.absolute:
            return self.value / self.UNITS['pt']
        return self.value

    @property
    def absolute(self) -> bool:
        """is this an absolute or relative dimension?"""
        return isinstance(self.value, (int, float))

    def __float__(self) -> float:
        if not self.absolute:
            raise ValueError('Cannot convert relative value "{self.value}"')
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dimension):
            return self.value == cast(Dimension, other).value
        if isinstance(other, (int, float)):
            return self.value == other
        if isinstance(other, str):
            return self.value == Dimension(other)
        raise NotImplementedError(f"Unable to compare {other} with {self}")

    def __truediv__(self, other: Union[float, str, "Dimension"]) -> "Dimension":
        if isinstance(other, Dimension):
            return Dimension(self.value / other.value)
        if isinstance(other, (int, float)):
            return Dimension(self.value / other)
        return Dimension(self.value / Dimension(other).value)

RelaxedDimension = Union[Dimension, float, str]

class Size(NamedTuple):
    """One standard page size (in mmm)"""
    width: int
    height: int

class PageSizes(Enum):
    """
    A collection of standardised page sizes (in mm).
    See https://simple.wikipedia.org/wiki/Paper_size#Paper_sizes_and_computer_printers
    """

    # International paper sizes
    A0 = Size(841, 1189)
    A1 = Size(594, 841)
    A2 = Size(420, 594)
    A3 = Size(297, 420)
    A4 = Size(210, 297)
    A5 = Size(148, 210)
    A6 = Size(105, 148)
    A7 = Size(74, 105)
    A8 = Size(52, 74)
    A9 = Size(37, 52)
    A10 = Size(26, 37)

    B0 = Size(1000, 1414)
    B1 = Size(707, 1000)
    B2 = Size(500, 707)
    B3 = Size(353, 500)
    B4 = Size(250, 353)
    B5 = Size(176, 250)
    B6 = Size(125, 176)
    B7 = Size(88, 125)
    B8 = Size(62, 88)
    B9 = Size(44, 62)
    B10 = Size(31, 44)

    C0 = Size(917, 1297)
    C1 = Size(648, 917)
    C2 = Size(458, 648)
    C3 = Size(324, 458)
    C4 = Size(229, 324)
    C5 = Size(162, 229)
    C6 = Size(114, 162)
    C7 = Size(81, 114)
    C8 = Size(57, 81)
    C9 = Size(40, 57)
    C10 = Size(28, 40)

    # US / Canada page sizes
    QUARTO = Size(203, 254)
    FOOLSCAP = Size(203, 330)
    EXECUTIVE = Size(182, 267)
    LETTER = Size(216, 279)
    LEGAL = Size(216, 356)
    LEDGER = Size(216, 356)
    POST = Size(394, 489)
    CROWN = Size(381, 508)

    def width(self) -> Dimension:
        """get width (in mm)"""
        #pylint: disable=no-member
        return Dimension(self.value.width)

    def height(self) -> Dimension:
        """get height (in mm)"""
        #pylint: disable=no-member
        return Dimension(self.value.height)
