"""
Provides a small number of classes to represent a document that
can be rendered by a DocumentGenerator.

Each Document is made up of one or more elements. An element can be:
- Paragraph
- Box
- Spacer
- Table
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Collection, Dict, Iterable, List, NamedTuple, Optional, Union, cast

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes.dimension import Dimension, RelaxedDimension
from musicbingo.docgen.sizes.pagesize import PageSizeInterface
from musicbingo.docgen.styles import ElementStyle, TableStyle
from musicbingo.progress import Progress


class Element(ABC):
    """base class for all document elements"""

    def __init__(self, style: Optional[ElementStyle]):
        if style is not None and not isinstance(style, ElementStyle):
            raise ValueError(f'Invalid style: {style}')
        self.style = style

    def as_dict(self) -> Dict[str, Any]:
        """convert element into a dictionary"""
        retval = {
            "_class_": self.__class__.__name__
        }
        for key, value in self.__dict__.items():
            if key[0] == '_' or value is None:
                continue
            if '_' in key:
                first, second = key.split('_')
                key = first + second.title()
            if callable(getattr(value, "as_dict", None)):
                value = value.as_dict()
            retval[key] = value
        return retval

class Checkbox(Element):
    """represents one clickable check box"""

    def __init__(self, name: str, text: str, size: RelaxedDimension,
                 style: ElementStyle,
                 borderColour: Optional[Union[Colour, str]] = None,
                 borderWidth: float = 1.0):
        super().__init__(style)
        self.name = name
        self.text = text
        self.size = Dimension(size)
        self.border_colour = borderColour
        self.border_width = borderWidth

    def __repr__(self) -> str:
        return (f'Checkbox(name={self.name}, text={self.text},' +
                f' size={self.size}, borderColour={self.border_colour}' +
                f' borderWidth={self.border_width}, style={self.style})')


class Image(Element):
    """represents one image"""

    def __init__(self, filename: Path, width: RelaxedDimension,
                 height: RelaxedDimension):
        super().__init__(None)
        if not isinstance(filename, Path):
            cls = type(filename)
            raise ValueError(f"Invalid filename class : {cls}")
        self.filename = filename
        self.width = Dimension(width)
        self.height = Dimension(height)

    def __repr__(self) -> str:
        return f'Image({self.filename}, {self.height}, {self.width})'


class Paragraph(Element):
    """represents one paragraph of text"""

    def __init__(self, text: str, style: ElementStyle):
        super().__init__(style)
        self.text = text

    def __repr__(self) -> str:
        return f'Paragraph("{self.text}", {self.style})'

class OverlayElement(Element):
    """
    Base class for elements that are outside the flow of
    other elements
    """
    def __init__(self,
                 x1: RelaxedDimension,
                 y1: RelaxedDimension,
                 style: ElementStyle):
        super().__init__(style)
        # pylint: disable=invalid-name
        self.x1 = Dimension(x1)
        # pylint: disable=invalid-name
        self.y1 = Dimension(y1)

class OverlayText(OverlayElement):
    """
    Represents a line of text that is outside of other element flows
    """

    def __init__(self,
                 x1: RelaxedDimension,
                 y1: RelaxedDimension,
                 style: ElementStyle,
                 text: str):
        """
        A line of text outside of element flow. The (x1, y1) value
        depends upon the horizontal alignment.
        (x1, y1) - start position
        style - style for text
        text - the text to draw
        """
        super().__init__(style=style, x1=x1, y1=y1)
        self.text = text

    def __repr__(self) -> str:
        assert self.style is not None
        items = [
            f'x1={self.x1}',
            f'y1={self.y1}',
            f'text="{self.text}"',
            f'style={self.style}'
        ]
        args = ', '.join(items)
        return f'OverlayText({args})'


class Spacer(Element):
    """represents gap between elements"""

    def __init__(self, width: RelaxedDimension, height: RelaxedDimension):
        super().__init__(None)
        self.width = Dimension(width)
        self.height = Dimension(height)

    def __repr__(self) -> str:
        return f'Spacer({self.height}, {self.width})'


class PageBreak(Element):
    """represents a forced page break in a document"""

    def __init__(self):
        super().__init__(None)

    def __repr__(self) -> str:
        return 'PageBreak()'


class HorizontalLine(Element):
    """
    Represents a horizontal line (a bit like a <hr /> tag)
    """

    def __init__(self, name: str, width: RelaxedDimension,
                 thickness: RelaxedDimension,
                 colour: Union[Colour, str],
                 dash: Optional[List[RelaxedDimension]] = None):
        """
        width - length of line
        thickness - thickness of line
        colour - colour of line
        dash - array of lengths used to specify length of each dash and the
               gap between each dash
        """
        super().__init__(ElementStyle(name=name, colour=colour))
        if not isinstance(name, str):
            raise ValueError(f"Invalid name: {name}")
        self.width = Dimension(width)
        self.thickness = Dimension(thickness)
        self.dash: Optional[List[Dimension]] = None
        if dash is not None:
            self.dash = [Dimension(w) for w in dash]

    def __repr__(self) -> str:
        assert self.style is not None
        items = [
            f'width={self.width}',
            f'thickness={self.thickness}'
            f'colour={self.style.colour}'
        ]
        if self.dash is not None:
            items.append(f'dash={self.dash}')
        return 'HorizontalLine({0})'.format(', '.join(items)) # pylint: disable=consider-using-f-string


class OverlayLine(OverlayElement):
    """
    Represents a line between points that is outside of other element flows
    """

    def __init__(self, name: str,
                 x1: RelaxedDimension,
                 y1: RelaxedDimension,
                 x2: RelaxedDimension,
                 y2: RelaxedDimension,
                 thickness: RelaxedDimension,
                 colour: Colour,
                 dash: Optional[List[RelaxedDimension]] = None):
        """
        name - name of element
        (x1, y1) - start position
        (x2, y2) - end position
        thickness - thickness of line
        colour - colour of line
        dash - array of lengths used to specify length of each dash and the
               gap between each dash
        """
        if not isinstance(name, str):
            raise ValueError(f"Invalid name: {name}")
        super().__init__(x1=x1, y1=y1,
                         style=ElementStyle(name=name, colour=colour))
        # pylint: disable=invalid-name
        self.x2 = Dimension(x2)
        # pylint: disable=invalid-name
        self.y2 = Dimension(y2)
        self.thickness = Dimension(thickness)
        self.dash: Optional[List[Dimension]] = None
        if dash is not None:
            self.dash = [Dimension(w) for w in dash]

    def __repr__(self) -> str:
        assert self.style is not None
        items = [
            f'x1={self.x1}',
            f'y1={self.y1}',
            f'x2={self.x2}',
            f'y2={self.y2}',
            f'thickness={self.thickness}'
            f'colour={self.style.colour}'
        ]
        if self.dash is not None:
            items.append(f'dash={self.dash}')
        args = ', '.join(items)
        return f'OverlayLine({args})'


class Box(Element):
    """represents a box filled the the specified colour"""

    def __init__(self, name: str, width: RelaxedDimension,
                 height: RelaxedDimension,
                 colour: Union[Colour, str]):
        super().__init__(ElementStyle(name=name, colour=colour))
        if not isinstance(name, str):
            raise ValueError(f"Invalid name: {name}")
        self.width = Dimension(width)
        self.height = Dimension(height)

    def __repr__(self) -> str:
        return f'Box({self.height}, {self.width}, {self.style})'


TableCell = Union[Checkbox, Paragraph, Collection]

class TableRow(Element):
    """
    Container for one row of a table
    """
    def __init__(self, cells: List[TableCell], style: Optional[ElementStyle] = None, **kwargs):
        super().__init__(style=style, **kwargs)
        self.cells = cells

    def append(self, item) -> None:
        """
        Append a cell to this row
        """
        self.cells.append(item)

    def __len__(self) -> int:
        return len(self.cells)


class CellPos(NamedTuple):
    """The position of one cell in the table"""
    col: int
    row: int


class CellStyleRule(NamedTuple):
    """Style rules to apply to one or more cells"""
    start: CellPos
    end: CellPos
    style: ElementStyle


class Table(Element):
    """
    Represents a table.
    Each table has one or more TableRows, an optional header and
    an optional footer. The whole table can be styled and each
    cell can be individually styled.
    """

    def __init__(self, data: List[TableRow],
                 style: TableStyle,
                 heading: Optional[TableRow] = None,
                 footer: Optional[TableRow] = None,
                 colWidths: Optional[Iterable[RelaxedDimension]] = None,
                 rowHeights: Optional[Iterable[RelaxedDimension]] = None,
                 repeat_heading: bool = False):
        super().__init__(style)
        if not isinstance(data, list):
            raise ValueError(f"Invalid data: {data}")
        if len(data) == 0:
            raise ValueError("Data cannot be an empty list")
        self.data = data
        self.heading = heading
        self.footer = footer
        self.repeat_heading = repeat_heading
        self.col_widths: Optional[List[Dimension]] = None
        if colWidths is not None:
            self.col_widths = list(map(Dimension, colWidths))
        self.row_heights: Optional[List[Dimension]] = None
        if rowHeights is not None:
            self.row_heights = list(map(Dimension, rowHeights))
        self._cell_styles: List[CellStyleRule] = []

    def style_cells(self, start: CellPos, end: CellPos,
                    style: Optional[ElementStyle] = None, **kwargs):
        """
        Apply styles to one or more cells.
        start - the first cell to style
        end - the last cell to style
        style - the styling to apply (optional)
        **kwargs - style properties to change
        """
        if style is None:
            try:
                name = kwargs['name']
                del kwargs['name']
            except KeyError:
                name = f'cells-{start.row}-{start.col}-{end.row}-{end.col}'
            style = ElementStyle(name, **kwargs)
        self._cell_styles.append(CellStyleRule(start, end, style))

    def __repr__(self):
        values = []
        for key, value in self.__dict__.items():
            if value is None:
                continue
            values.append(f'{key}={value}')
        return r'Table({0})'.format(',\n  '.join(values)) # pylint: disable=consider-using-f-string


class Container(Element):
    """
    A container for other elements
    """

    # pylint: disable=invalid-name
    def __init__(self, cid: str, top: RelaxedDimension, left: RelaxedDimension,
                 width: RelaxedDimension, height: RelaxedDimension,
                 style: Optional[ElementStyle] = None):
        super().__init__(style)
        self.cid = cid
        self.top = Dimension(top)
        self.left = Dimension(left)
        self.width = Dimension(width)
        self.height = Dimension(height)
        self._elements: List[Element] = []

    def append(self, element: Element):
        """
        append an element to this container
        """
        if not isinstance(element, Element):
            raise ValueError(f"Invalid element: {element}")
        self._elements.append(element)

    def as_dict(self) -> Dict[str, Any]:
        """
        convert container into a dictionary
        """
        retval = {
        }
        for key, value in self.__dict__.items():
            if key == '_elements':
                key = 'elements'
            if key[0] == '_' or value is None:
                continue
            if '_' in key:
                first, second = key.split('_')
                key = first + second.title()
            if isinstance(value, list):
                value = [cast(Element, elt).as_dict() for elt in value]
            elif isinstance(value, (Element, ElementStyle)):
                value = value.as_dict()
            retval[key] = value
        return retval

    def __str__(self) -> str:
        x2 = self.left + self.width
        y2 = self.top + self.height
        return f'"{self.cid}"=({self.left.value}, {self.top.value}) -> ({x2.value}, {y2.value})'


class Document(Container):
    """
    Represents a document containg one or more pages.
    Each page contains Elements that can be styled.
    """

    # pylint: disable=invalid-name
    def __init__(self, pagesize: PageSizeInterface,
                 topMargin: RelaxedDimension = Dimension.INCH,
                 bottomMargin: RelaxedDimension = Dimension.INCH,
                 leftMargin: RelaxedDimension = Dimension.INCH,
                 rightMargin: RelaxedDimension = Dimension.INCH,
                 title: Optional[str] = None):
        super().__init__(cid='document', top=0, left=0,
                         width=pagesize.width(), height=pagesize.height())
        self.pagesize = pagesize
        self.top_margin = Dimension(topMargin)
        self.bottom_margin = Dimension(bottomMargin)
        self.left_margin = Dimension(leftMargin)
        self.right_margin = Dimension(rightMargin)
        self.title = title

    def available_height(self) -> Dimension:
        """
        Get available height of this document, excluding margins
        """
        return self.height - self.top_margin - self.bottom_margin

    def available_width(self) -> Dimension:
        """
        Get available width of this document, excluding margins
        """
        return self.width - self.left_margin - self.right_margin

    def available_area(self) -> Container:
        """
        Create a container that covers the entire available area of a document page
        """
        return Container(cid=f'frame_{self.cid}',
                         top=self.top_margin,
                         left=self.left_margin,
                         width=self.available_width(),
                         height=self.available_height())


class DocumentGenerator(ABC):
    """
    Interface for translating a Document into a document file.
    """
    # pylint: disable=invalid-name
    @abstractmethod
    def render(self, filename: str, document: Document,
               progress: Progress, debug: bool = False, showBoundary: bool = False) -> None:
        """Render the given document"""
        raise NotImplementedError()
