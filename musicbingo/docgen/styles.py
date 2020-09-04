"""
Classes for representing the styling that can be applied to document elements
"""

from __future__ import print_function
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Union

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes import Dimension, RelaxedDimension


class HorizontalAlignment(Enum):
    """Horizontal alignment"""
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 4


class VerticalAlignment(Enum):
    """Vertical alignment"""
    TOP = 0
    CENTER = 1
    BOTTOM = 2


class PaddingIter(Iterator[Dimension]):
    """Iterator for dimensions of the Padding class"""

    def __init__(self, pad: "Padding"):
        self.items: List[Dimension] = [pad.top, pad.right, pad.bottom, pad.left]
        self.pos = 0

    def __iter__(self) -> Iterator[Dimension]:
        return self

    def __next__(self) -> Dimension:
        if self.pos > 3:
            raise StopIteration()
        self.pos += 1
        return self.items[self.pos - 1]


class Padding:
    """padding around an Element"""

    def __init__(self, top: RelaxedDimension = 0,
                 right: RelaxedDimension = 0,
                 bottom: RelaxedDimension = 0,
                 left: RelaxedDimension = 0):
        self.top = Dimension(top)
        self.right = Dimension(right)
        self.bottom = Dimension(bottom)
        self.left = Dimension(left)

    def __repr__(self) -> str:
        return f'Padding({self.top}, {self.right}, {self.bottom}, {self.left}'

    def __len__(self) -> int:
        return 4

    def __iter__(self) -> Iterator[Dimension]:
        return PaddingIter(self)


class ElementStyle:
    """Styles that can be applied to any element"""

    def __init__(
            self, name: str,
            background: Optional[Union[Colour, str]] = None,
            colour: Optional[Union[Colour, str]] = None,
            alignment: HorizontalAlignment = HorizontalAlignment.LEFT,
            fontSize: int = 10,
            leading: int = 12,
            padding: Optional[Padding] = None):
        self.name = name
        self.background: Optional[Colour] = None
        if background is not None:
            self.background = Colour(background)
        self.colour: Optional[Colour] = None
        if colour is not None:
            self.colour = Colour(colour)
        self.alignment = alignment
        self.font_size = fontSize
        self.leading = leading
        self.padding = padding

    def replace(self, name: str, **kwargs) -> "ElementStyle":
        """duplicate this style, replacing the given properties"""
        new_items = self.as_dict()
        new_items.update(kwargs)
        new_items['name'] = name
        return type(self)(**new_items)

    def as_dict(self) -> Dict[str, Any]:
        """convert styles into a dictionary"""
        retval: Dict[str, Any] = {
            'name': self.name
        }
        for key, value in self.__dict__.items():
            if key == 'name' or value is None:
                continue
            if '_' in key:
                first, second = key.split('_')
                key = first + second.title()
            retval[key] = value
        return retval

    def __repr__(self):
        values: List[str] = []
        for key, value in self.as_dict().items():
            values.append(f'{key}={value}')
        return r'Style({0})'.format(', '.join(values))


class TableStyle(ElementStyle):
    """Styles that are only applicable to a Table"""

    def __init__(
            self,
            gridColour: Optional[Union[Colour, str]] = None,
            gridWidth: float = 0.5,
            borderColour: Optional[Union[Colour, str]] = None,
            borderWidth: float = 1.0,
            verticalAlignment: VerticalAlignment = VerticalAlignment.BOTTOM,
            headingStyle: Optional[ElementStyle] = None,
            footerStyle: Optional[ElementStyle] = None,
            **kwargs):
        super().__init__(**kwargs)
        self.grid_colour: Optional[Colour] = None
        if gridColour is not None:
            self.grid_colour = Colour(gridColour)
        self.grid_width = gridWidth
        self.border_colour: Optional[Colour] = None
        if borderColour:
            self.border_colour = Colour(borderColour)
        self.border_width = borderWidth
        self.vertical_align = verticalAlignment
        if not isinstance(self.vertical_align, VerticalAlignment):
            raise ValueError(f'Invalid verticalAlignment: {self.vertical_align}')
        self.heading_style = headingStyle
        self.footer_style = footerStyle
