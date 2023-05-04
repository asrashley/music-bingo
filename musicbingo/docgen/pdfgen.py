"""
A DocumentGenerator that will produce PDF files.

It uses the reportlab library to produce the PDF documents.
"""
import logging
from typing import (
    Any, Callable, Iterable, List, Mapping, Optional,
    Tuple, Type, Union, cast,
)

from reportlab import platypus, lib  # type: ignore
from reportlab.pdfgen.canvas import Canvas  # type: ignore

from musicbingo.progress import Progress
from musicbingo.tests.mixin import TestCaseMixin
from musicbingo.docgen.colour import Colour
from musicbingo.docgen import documentgenerator as DG
from musicbingo.docgen.styles import HorizontalAlignment, Padding, RowStyle, TableStyle
from musicbingo.docgen.sizes.dimension import Dimension

class InteractiveCheckBox(platypus.Flowable):
    """class to implement a PDF checkbox"""

    def __init__(self, checkbox: DG.Checkbox):
        platypus.Flowable.__init__(self)
        self.box = checkbox

    def draw(self) -> None:
        """draw this check box"""
        self.canv.saveState()
        form = self.canv.acroForm
        assert self.box.style is not None
        fill_color = PDFGenerator.translate_colour(self.box.style.background)
        text_color = PDFGenerator.translate_colour(self.box.style.colour)
        form.checkbox(checked=False,
                      buttonStyle='check',
                      name=self.box.name,
                      tooltip=self.box.text,
                      relative=True,
                      y=-self.box.size.points(),
                      x=0,
                      size=self.box.size.points(),
                      forceBorder=False,
                      borderWidth=self.box.border_width,
                      fillColor=fill_color,
                      textColor=text_color)
        self.canv.restoreState()


class FixedElement:
    """
    Base class for all overlay elements
    """
    pass


class FixedLine(FixedElement):
    """
    class to implement an OverlayLine
    """

    def __init__(self, line: DG.OverlayLine):
        super().__init__()
        self.line = line

    # pylint: disable=unused-argument
    def draw(self, canv: Canvas, doc: platypus.BaseDocTemplate) -> None:
        """draw this line box"""
        assert self.line.style is not None
        colour = PDFGenerator.translate_colour(self.line.style.colour)
        canv.saveState()
        canv.setLineWidth(self.line.thickness.points())
        if self.line.dash is not None:
            dash = [cast(Dimension, w).points() for w in self.line.dash]
            canv.setDash(dash)
        canv.setStrokeColor(colour)
        canv.line(self.line.x1.points(), self.line.y1.points(),
                       self.line.x2.points(), self.line.y2.points())
        canv.restoreState()

class FixedText(FixedElement):
    """
    class to implement an OverlayText
    """

    def __init__(self, txt: DG.OverlayText):
        super().__init__()
        self.text = txt

    # pylint: disable=unused-argument
    def draw(self, canv: Canvas, doc: platypus.BaseDocTemplate) -> None:
        """
        draw this text
        """
        assert self.text.style is not None
        colour = PDFGenerator.translate_colour(self.text.style.colour)
        canv.saveState()
        canv.setStrokeColor(colour)
        for font in canv.getAvailableFonts():
            print(f'font="{font}"')
        canv.setFontSize(
            size=self.text.style.font_size,
            leading=self.text.style.leading)
        if self.text.style.alignment == HorizontalAlignment.LEFT:
            canv.drawString(self.text.x1.points(), self.text.y1.points(),
                            self.text.text)
        elif self.text.style.alignment == HorizontalAlignment.RIGHT:
            canv.drawRightString(self.text.x1.points(), self.text.y1.points(),
                                 self.text.text)
        else:
            canv.drawCentredString(self.text.x1.points(), self.text.y1.points(),
                                   self.text.text)
        canv.restoreState()


class OnPageComplete:
    """
    Class called when a page has been completed. It is used to draw the
    overlay lines once the rest of the page has been rendered.
    """
    def __init__(self) -> None:
        self.lines: List[FixedLine] = []

    def on_page(self, canvas: Canvas, document: platypus.BaseDocTemplate) -> None:
        """
        called when page rendering has completed
        """
        for line in self.lines:
            line.draw(canvas, document)

    def append(self, line: FixedLine) -> None:
        """
        add an overlay line
        """
        self.lines.append(line)


class DocumentState(TestCaseMixin):
    """
    Used to store the state while rendering a document
    """
    def __init__(self, doc: DG.Document, show_boundary: bool = False, debug: bool = False):
        self.doc = doc
        self.templates: List[platypus.PageTemplate] = []
        self.current_template: Optional[platypus.PageTemplate] = None
        self.elements: List[platypus.Flowable] = []
        self.page_complete: Optional[OnPageComplete] = None
        self.log = logging.getLogger('pdfgen')
        self.show_boundary = show_boundary
        self.debug = debug

    def add_frame(self, container: DG.Container) -> None:
        """
        Add a container to this page, using a platypus frame
        """
        if self.current_template is None:
            page = len(self.templates) + 1
            pagesize = (self.doc.pagesize.width().points(),
                        self.doc.pagesize.height().points())
            if self.page_complete is None:
                self.page_complete = OnPageComplete()
            self.current_template = platypus.PageTemplate(
                id=f'page{page}',
                pagesize=pagesize,
                frames=[],
                onPage=self.page_complete.on_page)
            self.log.debug('page %s width=%fpt height=%fpt',
                           page, pagesize[0], pagesize[1])
        if self.debug:
            self.log.debug('add_frame doc=%s container=%s', self.doc, container)
            self.assertGreaterThanOrEqual(container.top.value, self.doc.top_margin.value)
            self.assertGreaterThanOrEqual(container.left.value, self.doc.left_margin.value)
            self.assertLessThanOrEqual(container.height.value, self.doc.available_height().value)
            self.assertLessThanOrEqual(container.width.value, self.doc.available_width().value)
            self.assertGreaterThanOrEqual(container.left.value, self.doc.left_margin.value)
            self.assertLessThanOrEqual(
                cast(float, container.top.value) + cast(float, container.height.value),
                cast(float, self.doc.height.value) - cast(float, self.doc.bottom_margin.value))
        # pylint: disable=invalid-name
        y1 = self.doc.pagesize.height() - container.top - container.height
        if self.debug:
            self.assertGreaterThanOrEqual(y1.value, 0)
            self.assertLessThanOrEqual(cast(float, y1.value) + cast(float, container.height.value),
                                       self.doc.height.value)
        y1_pt = y1.points()
        if self.debug:
            self.assertGreaterThanOrEqual(container.top.value, self.doc.top_margin.value)
            self.assertGreaterThanOrEqual(container.left.value, self.doc.left_margin.value)
            self.assertLessThan(y1_pt, self.doc.height.points())
            self.assertLessThanOrEqual(y1_pt + container.height.points(), self.doc.height.points())
        frame = platypus.Frame(
            container.left.points(),
            y1_pt,
            container.width.points(),
            container.height.points(),
            id=container.cid, leftPadding=0, bottomPadding=0,
            rightPadding=0, topPadding=0,
            showBoundary=self.show_boundary,
            _debug=self.debug)
        self.log.debug(r'frame id="%s" x1=%fpt y1=%fpt width=%fpt height=%fpt x2=%fpt y2=%fpt',
                       frame.id, frame._x1, frame._y1, frame._width, frame._height,
                       frame._x1 + frame._width, frame._y1 + frame._height)
        self.current_template.frames.append(frame)

    def page_end(self, add_next=True) -> Optional[platypus.NextPageTemplate]:
        """
        Called when a page is complete, to create the frames for the page
        """
        while (self.elements and
               isinstance(self.elements[-1], (
                   platypus.CurrentFrameFlowable, platypus.doctemplate._FrameBreak))):
            # need to remove previous CurrentFrameFlowable if moving to a new page, to
            # avoid a blank page being created
            self.elements.pop()
        self.page_complete = None
        if self.current_template is None:
            return None
        self.log.debug('page_end template=%s frames=%s',
                       self.current_template.id,
                       [f.id for f in self.current_template.frames])
        self.templates.append(self.current_template)
        self.current_template = None
        if add_next:
            page = len(self.templates) + 1
            self.log.debug('adding NextPageTemplate "page%s"', page)
            return platypus.NextPageTemplate(f'page{page}')
        return None

    def append_overlay(self, elt: DG.OverlayElement) -> None:
        """
        Add an overlay element to this page
        """
        if self.page_complete is None:
            self.page_complete = OnPageComplete()
        if isinstance(elt, DG.OverlayLine):
            self.page_complete.append(FixedLine(elt))
        elif isinstance(elt, DG.OverlayText):
            self.page_complete.append(FixedText(elt))


# function prototype for each render_something() function
# pylint: disable=invalid-name, line-too-long
RENDER_FUNC = Callable[[Union[DG.Element, Iterable[DG.Element]], DocumentState], List[platypus.Flowable]]

class PDFGenerator(DG.DocumentGenerator):
    """
    Converts a Document into a PDF file.
    """

    ALIGNMENTS: Mapping[int, Any]  = {
        HorizontalAlignment.LEFT.value: lib.enums.TA_LEFT,
        HorizontalAlignment.RIGHT.value: lib.enums.TA_RIGHT,
        HorizontalAlignment.CENTER.value: lib.enums.TA_CENTER,
        HorizontalAlignment.JUSTIFY.value: lib.enums.TA_JUSTIFY,
    }

    def __init__(self) -> None:
        self.renderers: Mapping[Union[Type[DG.Element], List[DG.Element]], RENDER_FUNC] = {
            DG.Box: cast(RENDER_FUNC, self.render_box),
            DG.Checkbox: cast(RENDER_FUNC, self.render_checkbox),
            DG.Container: cast(RENDER_FUNC, self.render_container),
            DG.HorizontalLine: cast(RENDER_FUNC, self.render_horiz_line),
            DG.Image: cast(RENDER_FUNC, self.render_image),
            DG.OverlayLine: cast(RENDER_FUNC, self.render_overlay_line),
            DG.OverlayText: cast(RENDER_FUNC, self.render_overlay_text),
            DG.PageBreak: cast(RENDER_FUNC, self.render_page_break),
            DG.Paragraph: cast(RENDER_FUNC, self.render_paragraph),
            DG.Spacer: cast(RENDER_FUNC, self.render_spacer),
            DG.Table: cast(RENDER_FUNC, self.render_table),
            DG.TableRow: cast(RENDER_FUNC, self.render_table_row),
            cast(List[DG.Element], list): cast(RENDER_FUNC, self.render_list),
        }

    # pylint: disable=invalid-name
    def render(self, filename: str, document: DG.Document,
               progress: Progress, debug: bool = False, showBoundary: bool = False) -> None:
        """
        Renders the given document as a PDF file
        """
        num_elts = float(len(document._elements))
        state = DocumentState(document, show_boundary=showBoundary, debug=debug)
        doc = self.render_document(filename, document)
        for index, elt in enumerate(document._elements):
            progress.pct = 100.0 * float(index) / num_elts
            state.elements += self.renderers[type(elt)](elt, state)
        #state.page_end(False)
        if not state.templates:
            state.add_frame(document.available_area())
        state.page_end(False)
        while (state.elements and
               isinstance(state.elements[-1], (platypus.NextPageTemplate, platypus.PageBreak))):
            state.elements.pop()
        state.log.debug('addPageTemplates(%s)', [t.id for t in state.templates])
        doc.addPageTemplates(state.templates)
        state.log.debug('doc.build %s %d', filename, len(state.elements))
        doc.build(state.elements)
        progress.pct = 100.0

    @staticmethod
    def render_document(filename: str,
                        document: DG.Document) -> platypus.BaseDocTemplate:
        """
        Create a platypus document from a Document
        """
        # pagesize is a tuple of (width, height)
        # see reportlab.lib.pagesizes for detains
        pagesize = (document.pagesize.width().points(),
                    document.pagesize.height().points())
        # print('render_document', filename)
        return platypus.BaseDocTemplate(
            filename,
            _debug=True,
            pagesize=pagesize,
            topMargin=(document.top_margin.points()),
            bottomMargin=(document.bottom_margin.points()),
            leftMargin=(document.left_margin.points()),
            rightMargin=(document.right_margin.points()),
            title=document.title)

    def render_table_row(self, row: DG.TableRow,
                         state: DocumentState) -> List[platypus.Flowable]:
        """Translate one table row into Platypus objects"""
        result: List[platypus.Flowable] = []
        for elt in row.cells:
            # print(f'render_table_row {type(elt)}')
            result.append(self.renderers[type(elt)](elt, state))  # type: ignore
            # print(f'render_table_row {type(elt)} = {type(result[-1])}')
        return result

    def render_list(self, items: List[DG.Element],
                    state: DocumentState) -> List[platypus.Flowable]:
        """Translate one table row into Platypus objects"""
        result: List[platypus.Flowable] = []
        for elt in items:
            result += self.renderers[type(elt)](elt, state)
        return result

    # pylint: disable=unused-argument
    @staticmethod
    def render_image(img: DG.Image, state: DocumentState) -> List[platypus.Flowable]:
        """Convert an Image in to a Platypus version"""
        return [platypus.Image(str(img.filename), height=img.height.points(),
                              width=img.width.points())]

    @staticmethod
    def render_overlay_line(line: DG.OverlayLine, state: DocumentState) -> List[platypus.Flowable]:
        """
        Convert an OverlayLine into a Platypus version
        """
        state.append_overlay(line)
        return []

    @staticmethod
    def render_overlay_text(txt: DG.OverlayText, state: DocumentState) -> List[platypus.Flowable]:
        """
        Convert an OverlayText into a Platypus version
        """
        state.append_overlay(txt)
        return []

    #pylint: disable=unused-argument
    @staticmethod
    def render_page_break(pg_break: DG.PageBreak, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a PageBreak in to a Platypus version"""
        return [state.page_end(), platypus.PageBreak()]

    def render_paragraph(self, para: DG.Paragraph, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a Paragraph in to a Platypus version"""
        assert isinstance(para, DG.Paragraph)
        assert para.style is not None
        pstyle = self.translate_element_style(para.style)
        return [platypus.Paragraph(para.text, pstyle)]

    @staticmethod
    def render_spacer(spacer: DG.Spacer, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a Spacer in to a Platypus version"""
        return [platypus.Spacer(width=spacer.width.points(),
                               height=spacer.height.points())]

    def render_box(self, box: DG.Box, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a Box in to a Platypus Table"""
        data = [[""]]
        assert box.style is not None
        assert box.style.colour is not None
        return [platypus.Table(
            data, colWidths=[box.width.points()],
            rowHeights=[box.height.points()],
            style=[("LINEBELOW", (0, 0), (-1, -1), 1,
                    self.translate_colour(box.style.colour))])]

    @staticmethod
    def render_checkbox(box: DG.Checkbox, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a Checkbox in to a Platypus checkbox"""
        return [InteractiveCheckBox(box)]

    def render_horiz_line(self, line: DG.HorizontalLine,
                          state: DocumentState) -> List[platypus.Flowable]:
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
        return [platypus.HRFlowable(
            width=line.width.points_or_relative(),
            thickness=line.thickness.points_or_relative(),
            color=self.translate_colour(line.style.colour),
            spaceBefore=space_before,
            spaceAfter=space_after,
            dash=dash,
        )]

    def render_table(self, table: DG.Table, state: DocumentState) -> List[platypus.Flowable]:
        """Convert a Table in to a Platypus version"""
        data: List[List[platypus.Paragraph]] = []
        num_cols = max(len(row) for row in table.data)
        repeat_rows = 0
        first_row = 0
        last_row = len(table.data)
        if table.heading is not None:
            data.append(self.render_table_row(table.heading, state))
            first_row = 1
            last_row += 1
            if table.repeat_heading:
                repeat_rows = 1
        for row in table.data:
            data.append(self.render_table_row(row, state))
        if table.footer is not None:
            assert isinstance(table.footer, DG.TableRow)
            data.append(self.render_table_row(table.footer, state))
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
        return [platypus.Table(data, repeatRows=repeat_rows,
                              colWidths=col_widths,
                              rowHeights=row_heights, style=tstyles)]

    def render_container(self, container: DG.Container,
                         state: DocumentState) -> List[platypus.Flowable]:
        """
        Convert a Container into a Reportlab frame
        """
        state.add_frame(container)
        elements: List[platypus.Flowable] = []
        # print(f'render_container: CurrentFrameFlowable({container.cid})')
        elements.append(platypus.CurrentFrameFlowable(container.cid))
        for elt in container._elements:
            elements += self.renderers[type(elt)](elt, state)
        elements.append(platypus.FrameBreak())
        return elements

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
            alignment=self.ALIGNMENTS[style.alignment.value],
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
            if table.footer is None or style.footer_grid:
                result.append(('BOX', (0, 0), (-1, -1), style.border_width,
                               self.translate_colour(style.border_colour)))
            else:
                result.append(('BOX', (0, 0), (-1, last_row - 1), style.border_width,
                               self.translate_colour(style.border_colour)))
        if style.grid_colour is not None:
            if table.footer is None or style.footer_grid:
                result.append(('GRID', (0, 0), (-1, -1), style.grid_width,
                               self.translate_colour(style.grid_colour)))
            else:
                result.append(('GRID', (0, 0), (-1, -2), style.grid_width,
                               self.translate_colour(style.grid_colour)))
        align = style.vertical_alignment.name
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
            value = getattr(style, prop, None)
            pvalue = None if parent is None else getattr(parent, prop, None)
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
        if need_cmd("colspans"):
            col = 0
            for span in cast(List[int], cast(RowStyle, style).colspans):
                result.append(('SPAN', (col, start[1]), (col + span - 1, end[1])))
                col += span
        return result
