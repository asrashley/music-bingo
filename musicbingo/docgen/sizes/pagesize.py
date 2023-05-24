"""
Document page sizes
"""

from enum import Enum
from typing import List, NamedTuple, Protocol

from .dimension import Dimension

class Size(NamedTuple):
    """One standard page size (in mmm)"""
    width: int
    height: int


class PageSizeInterface(Protocol):
    """
    Interface for functions provided by both _NonEnumPageSize and PageSizes
    """

    def width(self) -> Dimension:
        """get width (in mm)"""

    def height(self) -> Dimension:
        """get height (in mm)"""

    def landscape(self) -> "PageSizeInterface":
        """Returns landscape orientation of page"""

    def to_json(self) -> str:
        """convert page size into a JSON compatible version"""

class _NonEnumPageSize(PageSizeInterface):
    def __init__(self, name, width, height):
        self.name = name
        self._width = width
        self._height = height

    def width(self) -> Dimension:
        """get width (in mm)"""
        return Dimension(self._width)

    def height(self) -> Dimension:
        """get height (in mm)"""
        return Dimension(self._height)

    def landscape(self) -> PageSizeInterface:
        """Returns landscape orientation of page"""
        if self._width < self._height:
            return _NonEnumPageSize(f'landscape_{self.name}', width=self._height,
                                    height=self._width)
        return _NonEnumPageSize(self.name, width=self._width, height=self._height)

    def to_json(self) -> str:
        """convert page size into a JSON compatible version"""
        return self.name

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
        assert isinstance(self.value, Size)
        return Dimension(self.value.width)

    def height(self) -> Dimension:
        """get height (in mm)"""
        #pylint: disable=no-member
        return Dimension(self.value.height)

    def landscape(self) -> PageSizeInterface:
        """
        Returns landscape orientation of page
        """
        if self.value.width < self.value.height:
            return _NonEnumPageSize(f'landscape_{self.name}', width=self.value.height,
                                    height=self.value.width)
        return _NonEnumPageSize(f'landscape_{self.name}', width=self.value.width,
                                height=self.value.height)

    @classmethod
    def names(cls) -> List[str]:
        """get list of items in this enum"""
        return sorted(cls.__members__.keys()) # type: ignore

    @classmethod
    def from_string(cls, name):
        """convert string into an enum value"""
        try:
            return cls[name.upper()]  # type: ignore
        except KeyError as err:
            raise ValueError(name) from err

    def __str__(self) -> str:
        return self.name

    def to_json(self) -> str:
        """convert page size into a JSON compatible version"""
        return self.name
