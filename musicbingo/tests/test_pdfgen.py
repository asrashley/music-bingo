"""
tests of the PDF generator
"""

#pylint: disable=too-many-locals

import os
from pathlib import Path
import shutil
import tempfile
from typing import Collection, Iterable, List, Tuple, cast
import unittest
from unittest import mock

from reportlab import platypus, lib  # type: ignore

from musicbingo.docgen import documentgenerator as DG
from musicbingo.docgen.colour import Colour, CSS_COLOUR_NAMES
from musicbingo.docgen.pdfgen import PDFGenerator
from musicbingo.docgen.sizes import Dimension, PageSizes
from musicbingo.docgen.styles import HorizontalAlignment, VerticalAlignment
from musicbingo.docgen.styles import Padding, ElementStyle


class TestPDFGenerator(unittest.TestCase):
    """tests of the PDF generator"""

    def setUp(self):
        """called before each test"""
        self.tmpdir = tempfile.mkdtemp()
        self.basedir = Path(__file__).parents[2]
        #self.basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.extra_files = Path(self.basedir) / "Extra-Files"

    def tearDown(self):
        """called after each test"""
        # pylint: disable=broad-except
        try:
            shutil.rmtree(self.tmpdir)
        except (Exception) as ex:
            print(ex)

    #pylint: disable=no-member
    def test_render_empty_document(self):
        """test rendering DG.Document to a reportlab document"""
        tmpfile = os.path.join(self.tmpdir, "test.pdf")
        dg_doc = DG.Document(pagesize=PageSizes.A4, topMargin=0.0,
                             bottomMargin=0.0, leftMargin=10,
                             rightMargin=20,
                             title="Empty document")
        pdfgen = PDFGenerator()
        pdf_doc = pdfgen.render_document(tmpfile, dg_doc)
        self.assertEqual(pdf_doc.topMargin, 0)
        self.assertEqual(pdf_doc.bottomMargin, 0)
        self.assertAlmostEqual(pdf_doc.leftMargin, Dimension(10).points())
        self.assertAlmostEqual(pdf_doc.rightMargin, Dimension(20).points())
        self.assertAlmostEqual(pdf_doc.pagesize[0],
                               PageSizes.A4.width().points())
        self.assertAlmostEqual(pdf_doc.pagesize[1],
                               PageSizes.A4.height().points())
        self.assertEqual(pdf_doc.title, dg_doc.title)

    def test_render_image(self):
        """test rendering DG.Image to a reportlab image"""
        filename, width, height = ('logo_banner.jpg', 7370 / 50.0,
                                   558 / 50.0)
        ext_filename = self.extra_files / filename
        dg_img = DG.Image(ext_filename, width=width, height=height)
        pdfgen = PDFGenerator()
        pdf_img = pdfgen.render_image(dg_img)
        self.assertEqual(pdf_img.filename, str(dg_img.filename))
        self.assertAlmostEqual(pdf_img.drawWidth, Dimension(width).points())
        self.assertAlmostEqual(pdf_img.drawHeight, Dimension(height).points())

    def test_render_horiz_line(self):
        """test rendering DG.HorizontalLine to a reportlab line"""
        dg_line = DG.HorizontalLine(name='hr', width="5in", colour='blue',
                                    thickness=2)
        pdfgen = PDFGenerator()
        pdf_line = pdfgen.render_horiz_line(dg_line)
        self.assertAlmostEqual(pdf_line.width, Dimension("5in").points())
        self.assertAlmostEqual(pdf_line.lineWidth, Dimension(2).points())

    def test_render_paragraph(self):
        """test rendering DG.Paragraph to a reportlab paragraph"""
        pstyle = DG.ElementStyle(
            name='test-paragraph',
            colour=Colour('blue'),
            background='yellow',
            fontSize=12,
            leading=16,
            padding=Padding(top="1mm", right="6pt", left="12px",
                            bottom="0.1in"),
        )
        dg_para = DG.Paragraph('A test paragraph', pstyle)
        pdfgen = PDFGenerator()
        pdf_para = pdfgen.render_paragraph(dg_para)
        self.assertParagraphEqual(dg_para, pdf_para)

    @mock.patch('musicbingo.docgen.pdfgen.platypus.Table', autospec=True)
    def test_render_results_table(self, mock_table):
        """
        Test converting a documentgenerator Table to a reportlab table.
        This test uses example data from the ticket results table
        """
        cstyle = DG.ElementStyle(
            name='results-cell',
            colour=Colour('black'),
            alignment=HorizontalAlignment.CENTER,
            fontSize=10,
            leading=10)
        heading: DG.TableRow = [
            DG.Paragraph('<b>Ticket Number</b>', cstyle),
            DG.Paragraph('<b>Wins after track</b>', cstyle),
            DG.Paragraph('<b>Start Time</b>', cstyle),
        ]
        data: List[DG.TableRow] = [
            [
                DG.Paragraph('1', cstyle),
                DG.Paragraph('2', cstyle),
                DG.Paragraph('3:45', cstyle),
            ],
            [
                DG.Paragraph('2', cstyle),
                DG.Paragraph('3', cstyle),
                DG.Paragraph('4:45', cstyle),
            ],
            [
                DG.Paragraph('3', cstyle),
                DG.Paragraph('1', cstyle),
                DG.Paragraph('1:45', cstyle),
            ],
        ]
        hstyle = DG.ElementStyle(
            name='heading',
            fontSize=12,
            background=Colour('blue'))
        col_widths: List[Dimension] = list(map(Dimension, [20, 125, 20]))
        tstyle = DG.TableStyle(name='test-table',
                               borderColour=Colour('black'),
                               borderWidth=1.0,
                               gridColour=Colour('black'),
                               gridWidth=0.5,
                               alignment=HorizontalAlignment.LEFT,
                               verticalAlignment=VerticalAlignment.CENTER,
                               headingStyle=hstyle)

        dg_table = DG.Table(data, heading=heading, repeat_heading=True,
                            colWidths=col_widths, style=tstyle)
        pdfgen = PDFGenerator()
        expected_styles = [
            # table styles:
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 1, lib.colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), tstyle.font_size),
            ('GRID', (0, 0), (-1, -1), 0.5, lib.colors.black),
            ('LEADING', (0, 0), (-1, -1), tstyle.leading),
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
            # heading row styles:
            ('BACKGROUND', (0, 0), (2, 0), lib.colors.blue),
            ('FONTSIZE', (0, 0), (2, 0), hstyle.font_size),
        ]
        pdf_styles = pdfgen.translate_table_style(
            dg_table, first_row=1, last_row=(len(data) + 1), num_cols=3)
        self.assertStyleListsEqual(expected_styles, pdf_styles)
        pdfgen.render_table(dg_table)
        _, args, kwargs = mock_table.mock_calls[0]

        self.assertListsEqual([heading] + data, args[0])
        self.assertStyleListsEqual(expected_styles, kwargs['style'])
        for dg_col, pdf_col in zip(col_widths, kwargs['colWidths']):
            self.assertAlmostEqual(dg_col.points(), pdf_col)

    @mock.patch('musicbingo.docgen.pdfgen.platypus.Table', autospec=True)
    def test_render_bingo_ticket_table(self, mock_table):
        """
        Test converting a documentgenerator Table to a reportlab table.
        This test uses example data from the Bingo ticket generator
        """
        cstyle = DG.ElementStyle('ticket-cell',
                                 colour='black',
                                 alignment=HorizontalAlignment.CENTER,
                                 fontSize=12,
                                 leading=12,
                                 padding=Padding(bottom=4))

        data: List[DG.TableRow] = []
        for start, end in ((0, 5), (5, 10), (10, 15)):
            row: DG.TableRow = []
            for index in range(start, end):
                items: List[DG.TableCell] = [
                    DG.Paragraph(f'Title {index}', cstyle),
                    DG.Paragraph(f'<b>Artist {index}</b>', cstyle),
                ]
                row.append(items)
            data.append(row)

        column_width = Dimension("1.54in")
        row_height = Dimension("1.0in")
        col_widths = (column_width, column_width, column_width, column_width, column_width)
        row_heights = (row_height, row_height, row_height)

        tstyle = DG.TableStyle(name='bingo-ticket',
                               borderColour=Colour('black'),
                               borderWidth=1.0,
                               colour='black',
                               gridColour=Colour('black'),
                               gridWidth=0.5,
                               padding=Padding(0, 0, 0, 0),
                               alignment=HorizontalAlignment.CENTER,
                               verticalAlignment=VerticalAlignment.CENTER)

        dg_table = DG.Table(data, colWidths=col_widths, rowHeights=row_heights,
                            style=tstyle)
        box_colours: List[Colour] = []
        for name, value in CSS_COLOUR_NAMES.items():
            if name == 'black':
                continue
            box_colours.append(Colour(value))
        expected_styles = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1.0, lib.colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('FONTSIZE', (0, 0), (-1, -1), tstyle.font_size),
            ('GRID', (0, 0), (-1, -1), 0.5, lib.colors.black),
            ('LEADING', (0, 0), (-1, -1), tstyle.leading),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TEXTCOLOR', (0, 0), (-1, -1), lib.colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]
        index = 0
        for box_row in range(0, 3):
            for box_col in range(0, 5):
                box_style = DG.ElementStyle(
                    name=f'bingo-cell-r{box_row}-c{box_col}',
                    alignment=HorizontalAlignment.CENTER,
                    background=box_colours[index % len(box_colours)])
                dg_table.style_cells(DG.CellPos(col=box_col, row=box_row),
                                     DG.CellPos(col=box_col, row=box_row),
                                     box_style)
                expected_styles.append((
                    'BACKGROUND',
                    (box_col, box_row),
                    (box_col, box_row),
                    lib.colors.HexColor(box_style.background.css()),
                ))
                index += 1

        pdfgen = PDFGenerator()
        pdf_styles = pdfgen.translate_table_style(
            dg_table, first_row=0, last_row=len(data), num_cols=5)
        self.assertStyleListsEqual(expected_styles, pdf_styles)
        pdfgen.render_table(dg_table)
        _, args, kwargs = mock_table.mock_calls[0]
        self.assertListsEqual(data, args[0])
        self.assertStyleListsEqual(expected_styles, kwargs['style'])
        for dg_col, pdf_col in zip(col_widths, kwargs['colWidths']):
            self.assertAlmostEqual(dg_col.points(), pdf_col)
        for dg_row, pdf_row in zip(row_heights, kwargs['rowHeights']):
            self.assertAlmostEqual(dg_row.points(), pdf_row)

    @mock.patch('musicbingo.docgen.pdfgen.platypus.Table', autospec=True)
    def test_render_box(self, mock_table):
        """test rendering DG.Box to a reportlab table"""
        dg_box = DG.Box('test-box', width="10in", height=0, colour='black')
        pdfgen = PDFGenerator()
        pdfgen.render_box(dg_box)
        _, args, kwargs = mock_table.mock_calls[0]
        col_width = Dimension("10.0in").points()
        expected_styles = [
            ("LINEBELOW", (0, 0), (-1, -1), 1, lib.colors.black)
        ]
        self.assertEqual(len(args), 1)  # one positonal argument (data)
        self.assertEqual(len(args[0]), 1)  # data has one row
        self.assertEqual(len(args[0][0]), 1)  # row has one cell
        self.assertEqual(args[0][0][0], "")
        self.assertStyleListsEqual(expected_styles, kwargs['style'])
        self.assertEqual(len(kwargs['colWidths']), 1)
        self.assertAlmostEqual(col_width, kwargs['colWidths'][0])
        self.assertEqual(len(kwargs['rowHeights']), 1)
        self.assertAlmostEqual(0.0, kwargs['rowHeights'][0])

    def test_translate_style(self):
        """
        test translating DG.ElementStyle to a reportlab paragraph style
        """
        dg_style = DG.ElementStyle(
            name='test-style',
            colour=Colour('blue'),
            background='white',
            alignment=HorizontalAlignment.RIGHT,
            fontSize=16,
            leading=18,
            padding=Padding(bottom=7),
        )
        self.assertEqual(dg_style.alignment, HorizontalAlignment.RIGHT)
        self.assertEqual(dg_style.colour, Colour('blue'))
        self.assertEqual(dg_style.background, Colour('white'))
        self.assertEqual(dg_style.font_size, 16)
        self.assertEqual(dg_style.leading, 18)
        self.assertEqual(dg_style.padding.top, 0)
        self.assertEqual(dg_style.padding.right, 0)
        self.assertEqual(dg_style.padding.bottom, 7)
        self.assertEqual(dg_style.padding.left, 0)
        pdfgen = PDFGenerator()
        pdf_style = pdfgen.translate_element_style(dg_style)
        self.assertStylesEqual(dg_style, pdf_style)

    #pylint: disable=invalid-name
    def assertListsEqual(self, expected: Collection, actual: Collection) -> None:
        """
        check that both lists are equal after rendering
        """
        self.assertIsInstance(expected, list)
        self.assertIsInstance(actual, list)
        self.assertEqual(len(expected), len(actual))
        for e_item, a_item in zip(expected, actual):
            if isinstance(e_item, list):
                self.assertIsInstance(a_item, list)
                self.assertListsEqual(e_item, a_item)
                continue
            self.assertIsInstance(e_item, DG.Paragraph)
            self.assertParagraphEqual(cast(DG.Paragraph, e_item), a_item)

    def assertStylesEqual(self, dg_style: DG.ElementStyle,
                          pdf_style: lib.styles.ParagraphStyle) -> None:
        """
        check that both styles are equal after rendering
        """
        self.assertEqual(pdf_style.name, dg_style.name)
        if dg_style.colour is not None:
            pdf_col = lib.colors.HexColor(dg_style.colour.css())
            self.assertEqual(pdf_style.textColor, pdf_col)
        if dg_style.background is not None:
            pdf_col = lib.colors.HexColor(dg_style.background.css())
            self.assertEqual(pdf_style.backColor, pdf_col)
        self.assertEqual(pdf_style.fontSize, dg_style.font_size)
        self.assertEqual(pdf_style.leading, dg_style.leading)
        if dg_style.padding is not None:
            self.assertAlmostEqual(pdf_style.spaceAfter,
                                   dg_style.padding.bottom.points())
            self.assertAlmostEqual(pdf_style.spaceBefore,
                                   dg_style.padding.top.points())
            self.assertAlmostEqual(pdf_style.leftIndent,
                                   dg_style.padding.left.points())
            self.assertAlmostEqual(pdf_style.rightIndent,
                                   dg_style.padding.right.points())
        else:
            self.assertEqual(pdf_style.spaceAfter, 0)
            self.assertEqual(pdf_style.spaceBefore, 0)
            self.assertEqual(pdf_style.leftIndent, 0)
            self.assertEqual(pdf_style.rightIndent, 0)
        self.assertEqual(pdf_style.alignment,
                         PDFGenerator.ALIGNMENTS[dg_style.alignment])

    def assertParagraphEqual(self, dg_para: DG.Paragraph,
                             pdf_para: platypus.Paragraph) -> None:
        """
        check that both paragraphs are equal after rendering
        """
        self.assertEqual(pdf_para.text, dg_para.text)
        self.assertIsNotNone(dg_para.style)
        self.assertIsNotNone(pdf_para.style)
        self.assertStylesEqual(cast(ElementStyle, dg_para.style),
                               pdf_para.style)

    def assertStyleListsEqual(self, expected: Iterable[Tuple],
                              actual: Iterable[Tuple]) -> None:
        """
        check that both table styles are equal after rendering
        """
        self.assertIsInstance(expected, list)
        self.assertIsInstance(actual, list)
        todo = set(expected)
        for item in actual:
            try:
                todo.remove(item)
                continue
            except KeyError:
                if item[0] not in ['BACKGROUND', 'TEXTCOLOR']:
                    raise
            cmd, start, end, colour = item
            for candidate in todo:
                if candidate[0] != cmd:
                    continue
                if len(candidate) != 4:
                    continue
                if start != candidate[1] or end != candidate[2]:
                    continue
                self.assertAlmostEqual(colour.red, candidate[3].red)
                self.assertAlmostEqual(colour.green, candidate[3].green)
                self.assertAlmostEqual(colour.blue, candidate[3].blue)
                self.assertAlmostEqual(colour.alpha, candidate[3].alpha)
                todo.remove(candidate)
                break
        self.assertEqual(len(todo), 0,
                         f'Expected items {todo} not found')


if __name__ == '__main__':
    unittest.main()
