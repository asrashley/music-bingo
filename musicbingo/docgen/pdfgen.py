"""
A DocumentGenerator that will produce PDF files.

It uses the reportlab library to produce the PDF documents.
"""

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Type, Union, cast

from reportlab import platypus, lib # type: ignore

from musicbingo.progress import Progress
from musicbingo.docgen.colour import Colour
from musicbingo.docgen import documentgenerator as DG
from musicbingo.docgen.styles import HorizontalAlignment, Padding, TableStyle
from musicbingo.docgen.sizes import Dimension

# pylint: disable=invalid-name
Flowable = Union[platypus.Image, platypus.Paragraph, platypus.Spacer,
                 platypus.Table, platypus.PageBreak]

# function prototype for each render_something() function
RENDER_FUNC = Callable[[Union[DG.Element, Iterable]], Flowable]

class PDFGenerator(DG.DocumentGenerator):
    """
    Converts a Document into a PDF file.
    """

    ALIGNMENTS = {
        HorizontalAlignment.LEFT: lib.enums.TA_LEFT,
        HorizontalAlignment.RIGHT: lib.enums.TA_RIGHT,
        HorizontalAlignment.CENTER: lib.enums.TA_CENTER,
        HorizontalAlignment.JUSTIFY: lib.enums.TA_JUSTIFY,
    }

    def __init__(self):
        self.renderers: Dict[Type, RENDER_FUNC] = {
            DG.Box: self.render_box,
            DG.HorizontalLine: self.render_horiz_line,
            DG.Image: self.render_image,
            DG.PageBreak: self.render_page_break,
            DG.Paragraph: self.render_paragraph,
            DG.Spacer: self.render_spacer,
            DG.Table: self.render_table,
            list: self.render_table_row,
        }

    def render(self, filename: str, document: DG.Document,
               progress: Progress) -> None:
        """Renders the given document as a PDF file"""
        # pagesize is a tuple of (width, height)
        # see reportlab.lib.pagesizes for detains
        doc = self.render_document(filename, document)
        elements: List[Flowable] = []
        num_elts = float(len(document._elements))
        for index, elt in enumerate(document._elements):
            progress.pct = 100.0 * float(index) / num_elts
            elements.append(self.renderers[type(elt)](elt))
        doc.build(elements)
        progress.pct = 100.0

    @staticmethod
    def render_document(filename: str,
                        document: DG.Document) -> platypus.BaseDocTemplate:
        """Create a platypus document from a Document"""
        pagesize = (document.pagesize.width().points(),
                    document.pagesize.height().points())
        return platypus.SimpleDocTemplate(
            filename,
            pagesize=pagesize,
            topMargin=(document.top_margin.points()),
            bottomMargin=(document.bottom_margin.points()),
            leftMargin=(document.left_margin.points()),
            rightMargin=(document.right_margin.points()),
            title=document.title)

    def render_table_row(self, row: DG.TableRow) -> List[Flowable]:
        """Translate one table row into Platypus objects"""
        result: List[Flowable] = []
        for elt in row:
            result.append(self.renderers[type(elt)](elt))
        return result

    @staticmethod
    def render_image(img: DG.Image) -> Flowable:
        """Convert an Image in to a Platypus version"""
        return platypus.Image(str(img.filename), height=img.height.points(),
                              width=img.width.points())

    #pylint: disable=unused-argument
    @staticmethod
    def render_page_break(pg_break: DG.PageBreak) -> Flowable:
        """Convert a PageBreak in to a Platypus version"""
        return platypus.PageBreak()

    def render_paragraph(self, para: DG.Paragraph) -> Flowable:
        """Convert a Paragraph in to a Platypus version"""
        assert isinstance(para, DG.Paragraph)
        assert para.style is not None
        pstyle = self.translate_element_style(para.style)
        return platypus.Paragraph(para.text, pstyle)

    @staticmethod
    def render_spacer(spacer: DG.Spacer) -> Flowable:
        """Convert a Spacer in to a Platypus version"""
        return platypus.Spacer(width=spacer.width.points(),
                               height=spacer.height.points())

    def render_box(self, box: DG.Box) -> Flowable:
        """Convert a Box in to a Platypus Table"""
        data = [[""]]
        assert box.style is not None
        assert box.style.colour is not None
        return platypus.Table(
            data, colWidths=[box.width.points()],
            rowHeights=[box.height.points()],
            style=[("LINEBELOW", (0, 0), (-1, -1), 1,
                    self.translate_colour(box.style.colour))])

    def render_horiz_line(self, line: DG.HorizontalLine) -> Flowable:
        """Convert a HorizontalLine into a Platypus version"""
        space_before: float = 1
        space_after: float = 1
        dash: Optional[List[float]] = None
        assert line.style is not None
        if line.style.padding:
            space_before = line.style.padding.top.points()
            space_after = line.style.padding.bottom.points()
        if line.dash is not None:
            dash = [cast(Dimension, w).points() for w in line.dash]
        return platypus.HRFlowable(
            width=line.width.points_or_relative(),
            thickness=line.thickness.points_or_relative(),
            color=self.translate_colour(line.style.colour),
            spaceBefore=space_before,
            spaceAfter=space_after,
            dash=dash,
        )

    def render_table(self, table: DG.Table) -> Flowable:
        """Convert a Table in to a Platypus version"""
        data: List[List[platypus.Paragraph]] = []
        num_cols = max(len(row) for row in table.data)
        repeatRows = 0
        first_row = 0
        last_row = len(table.data)
        if table.heading is not None:
            data.append(self.render_table_row(table.heading))
            first_row = 1
            last_row += 1
            if table.repeat_heading:
                repeatRows = 1
        for row in table.data:
            data.append(self.render_table_row(row))
        if table.footer is not None:
            data.append(self.render_table_row(table.footer))
            last_row -= 1
        tstyles = self.translate_table_style(table, first_row, last_row,
                                             num_cols)
        col_widths: Optional[List[float]] = None
        if table.col_widths:
            col_widths = list(map(lambda width: width.points(),
                                  table.col_widths))
        row_heights: Optional[List[float]] = None
        if table.row_heights:
            row_heights = list(map(lambda height: height.points(),
                                   table.row_heights))
        assert len(table.data) == (last_row - first_row)
        return platypus.Table(data, repeatRows=repeatRows,
                              colWidths=col_widths,
                              rowHeights=row_heights, style=tstyles)

    def translate_element_style(self, style: DG.ElementStyle) -> lib.styles.ParagraphStyle:
        """Convert an ElementStyle into Reportlab version"""
        space_after: float = 0
        space_before: float = 0
        left_indent: float = 0
        right_indent: float = 0
        if style.padding:
            space_after = style.padding.bottom.points()
            space_before = style.padding.top.points()
            left_indent = style.padding.left.points()
            right_indent = style.padding.right.points()
        return lib.styles.ParagraphStyle(
            style.name,
            textColor=self.translate_colour(style.colour),
            backColor=self.translate_colour(style.background),
            alignment=self.ALIGNMENTS[style.alignment],
            fontSize=style.font_size,
            leading=style.leading,
            spaceAfter=space_after,
            spaceBefore=space_before,
            leftIndent=left_indent,
            rightIndent=right_indent,
        )

    @staticmethod
    def translate_colour(col: Optional[DG.Colour]) -> Optional[lib.colors.Color]:
        """
        convert a colour into reportlab version.
        Reportlab uses floating point values between 0.0 .. 1.0
        """
        if col is None:
            return None
        return lib.colors.Color(red=(col.red / float(Colour.MAX_VALUE)),
                                green=(col.green / float(Colour.MAX_VALUE)),
                                blue=(col.blue / float(Colour.MAX_VALUE)),
                                alpha=(col.alpha / float(Colour.MAX_VALUE)))

    def translate_table_style(self, table: DG.Table, first_row: int,
                              last_row: int, num_cols: int) -> List[Tuple]:
        """
        Produce Reportlab format table styling.
        Converts all of the styling information in a table to the
        list of style commands used by Reportlab tables.
        """
        if table.style is None:
            return []
        style = cast(TableStyle, table.style)
        result: List[Tuple] = self.translate_element_style_for_table(
            style, (0, 0), (-1, -1), None)
        if style.border_colour is not None:
            result.append(('BOX', (0, 0), (-1, -1), style.border_width,
                           self.translate_colour(style.border_colour)))
        if style.grid_colour is not None:
            result.append(('GRID', (0, 0), (-1, -1), style.grid_width,
                           self.translate_colour(style.grid_colour)))
        align = style.vertical_align.name
        result.append(('VALIGN', (0, 0), (-1, -1), align))
        if style.heading_style is not None and table.heading is not None:
            result += self.translate_element_style_for_table(
                style.heading_style, (0, 0), (num_cols - 1, 0),
                table.style)
        if style.footer_style is not None and table.footer is not None:
            result += self.translate_element_style_for_table(
                style.footer_style, (0, -1), (num_cols - 1, -1),
                table.style)
        for start, end, cstyle in table._cell_styles:
            start = DG.CellPos(col=start.col, row=(start.row + first_row))
            end = DG.CellPos(col=end.col, row=(end.row + first_row))
            result += self.translate_element_style_for_table(
                cstyle, start, end, table.style)
        return result

    def translate_element_style_for_table(
            self, style: DG.ElementStyle, start: Tuple[int, int],
            end: Tuple[int, int],
            parent: Optional[DG.ElementStyle]) -> List[Tuple]:
        """
        Translate ElementStyle rules into Reportlab table style commands.
        A style rule is only generated if a style property is present
        in "style" and is different from the value in "parent"
        """
        if style is None:
            return []

        def need_cmd(prop):
            value = getattr(style, prop)
            pvalue = None if parent is None else getattr(parent, prop)
            return value is not None and value != pvalue

        result: List[Tuple] = []
        if need_cmd("background"):
            result.append(('BACKGROUND', start, end,
                           self.translate_colour(style.background)))
        if need_cmd("colour"):
            result.append(('TEXTCOLOR', start, end,
                           self.translate_colour(style.colour)))
        if need_cmd("font_size") and style.font_size > 0:
            result.append(('FONTSIZE', start, end, style.font_size))
        if need_cmd("leading") and style.leading > 0:
            result.append(('LEADING', start, end, style.leading))
        if need_cmd("padding") and style.padding is not None:
            dflt = Padding(-1, -1, -1, -1)
            if parent is not None and parent.padding is not None:
                dflt = parent.padding
            if style.padding.top != dflt.top:
                result.append(('TOPPADDING', start, end,
                               style.padding.top.points()))
            if style.padding.right != dflt.right:
                result.append(('RIGHTPADDING', start, end,
                               style.padding.right.points()))
            if style.padding.bottom != dflt.bottom:
                result.append(('BOTTOMPADDING', start, end,
                               style.padding.bottom.points()))
            if style.padding.left != dflt.left:
                result.append(('LEFTPADDING', start, end,
                               style.padding.left.points()))
        if need_cmd("alignment"):
            result.append(('ALIGN', start, end, style.alignment.name))
        #print('****')
        #print(style)
        #print(result)
        #print('****')
        return result
