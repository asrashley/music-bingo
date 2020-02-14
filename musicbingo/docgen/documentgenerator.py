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
from typing import Collection, Iterable, List, NamedTuple, Optional, Union

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes import PageSizes, INCH, Dimension, RelaxedDimension
from musicbingo.docgen.styles import ElementStyle, TableStyle
from musicbingo.progress import Progress

class Element(ABC):
    """base class for all document elements"""
    def __init__(self, style: Optional[ElementStyle]):
        if style is not None and not isinstance(style, ElementStyle):
            raise ValueError(f'Invalid style: {style}')
        self.style = style

class Image(Element):
    """represents one image"""
    def __init__(self, filename: Path, width: RelaxedDimension,
                 height: RelaxedDimension):
        super(Image, self).__init__(None)
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
        super(Paragraph, self).__init__(style)
        self.text = text

    def __repr__(self) -> str:
        return f'Paragraph("{self.text}", {self.style})'

class Spacer(Element):
    """represents gap between elements"""
    def __init__(self, width: RelaxedDimension, height: RelaxedDimension):
        super(Spacer, self).__init__(None)
        self.width = Dimension(width)
        self.height = Dimension(height)

    def __repr__(self) -> str:
        return f'Spacer({self.height}, {self.width})'

class PageBreak(Element):
    """represents a forced page break in a document"""
    def __init__(self):
        super(PageBreak, self).__init__(None)

    def __repr__(self) -> str:
        return f'PageBreak()'


class HorizontalLine(Element):
    """
    Represents a horizontal line (a bit like a <hr /> tag)
    """
    def __init__(self, name: str, width: RelaxedDimension,
                 thickness: RelaxedDimension,
                 colour: Colour,
                 dash: Optional[List[RelaxedDimension]] = None):
        """
        width - length of line
        thickness - thickness of line
        colour - colour of line
        dash - array of lengths used to specify length of each dash and the
               gap between each dash
        """
        super(HorizontalLine, self).__init__(ElementStyle(name=name, colour=colour))
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
        return 'HorizontalLine({0})'.format(', '.join(items))


class Box(Element):
    """represents a box filled the the specified colour"""
    def __init__(self, name: str, width: RelaxedDimension,
                 height: RelaxedDimension, colour: Colour):
        super(Box, self).__init__(ElementStyle(name=name, colour=colour))
        if not isinstance(name, str):
            raise ValueError(f"Invalid name: {name}")
        self.width = Dimension(width)
        self.height = Dimension(height)

    def __repr__(self) -> str:
        return f'Box({self.height}, {self.width}, {self.style})'


TableCell = Union[Paragraph, Collection]
TableRow = List[TableCell]

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
        super(Table, self).__init__(style)
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
        return r'Table({0})'.format(',\n  '.join(values))

class Document:
    """
    Represents a document containg one or more pages.
    Each page contains Elements that can be styled.
    """
    def __init__(self, pagesize: PageSizes,
                 topMargin: RelaxedDimension = INCH,
                 bottomMargin: RelaxedDimension = INCH,
                 leftMargin: RelaxedDimension = INCH,
                 rightMargin: RelaxedDimension = INCH,
                 title: Optional[str] = None):
        self.pagesize = pagesize
        self.top_margin = Dimension(topMargin)
        self.bottom_margin = Dimension(bottomMargin)
        self.left_margin = Dimension(leftMargin)
        self.right_margin = Dimension(rightMargin)
        self.title = title
        self._elements: List[Element] = []


    def append(self, element: Element):
        """append an element to this document"""
        if not isinstance(element, Element):
            raise ValueError(f"Invalid element: {element}")
        self._elements.append(element)

class DocumentGenerator(ABC):
    """
    Interface for translating a Document into a document file.
    """
    @abstractmethod
    def render(self, filename: str, document: Document,
               progress: Progress) -> None:
        """Render the given document"""
        raise NotImplementedError()
