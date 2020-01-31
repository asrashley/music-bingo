#!/usr/bin/python3

"""
Music Bingo generator.

Music Bingo is a variation on normal bingo where the numbers are replaced
with songs which the players must listen out for. This program allows
users to generate their own games of Music Bingo using their own music
clips.

This app can also extract sections from MP3 files to allow clips to be
generated for use in a Bingo game.
"""

from __future__ import print_function
import enum
import copy
import json
import math
import os
import random
import re
import secrets
from typing import Any, Dict, List, NamedTuple, Optional, Set, cast
from typing import Union

from reportlab.lib.colors import Color, HexColor # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.lib.styles import ParagraphStyle # type: ignore
from reportlab.lib.pagesizes import A4, inch # type: ignore
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate # type: ignore
from reportlab.platypus import Table, Spacer, PageBreak # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_RIGHT # type: ignore

from musicbingo.mp3.editor import MP3Editor, MP3FileWriter
from musicbingo.assets import Assets
from musicbingo.directory import Directory
from musicbingo.progress import Progress
from musicbingo.song import Metadata, Song

# object types that can be passed to SimpleDocTemplate().build()
Flowable = Union[Image, Paragraph, Spacer, Table, PageBreak] # pylint: disable=invalid-name

# these prime numbers are here to avoid having to generate a list of
# prime number on start-up/when required
PRIME_NUMBERS = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013,
    1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091,
    1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181,
    1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277,
    1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361,
    1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451,
    1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531,
    1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609,
    1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699,
    1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789,
    1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889,
    1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997,
    1999, 2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063, 2069, 2081, 2083,
    2087, 2089, 2099, 2111, 2113, 2129, 2131, 2137, 2141, 2143, 2153, 2161,
    2179, 2203, 2207, 2213, 2221, 2237, 2239, 2243, 2251, 2267, 2269, 2273,
    2281, 2287, 2293, 2297, 2309, 2311, 2333, 2339, 2341, 2347, 2351, 2357,
    2371, 2377, 2381, 2383, 2389, 2393, 2399, 2411, 2417, 2423, 2437, 2441,
    2447, 2459, 2467, 2473, 2477, 2503, 2521, 2531, 2539, 2543, 2549, 2551,
    2557, 2579, 2591, 2593, 2609, 2617, 2621, 2633, 2647, 2657, 2659, 2663,
    2671, 2677, 2683, 2687, 2689, 2693, 2699, 2707, 2711, 2713, 2719, 2729,
    2731, 2741, 2749, 2753, 2767, 2777, 2789, 2791, 2797, 2801, 2803, 2819,
    2833, 2837, 2843, 2851, 2857, 2861, 2879, 2887, 2897, 2903, 2909, 2917,
    2927, 2939, 2953, 2957, 2963, 2969, 2971, 2999]

def format_duration(millis: int) -> str:
    """convert the time in milliseconds to a MM:SS form"""
    secs = millis // 1000
    seconds = secs % 60
    minutes = secs // 60
    return '{0:d}:{1:02d}'.format(minutes, seconds)

class ColourScheme(NamedTuple):
    """tuple representing one colour scheme"""
    box_normal_bg: HexColor
    box_alternate_bg: HexColor
    title_bg: HexColor
    logo: str
    colours: List[Color] = []

class Palette(enum.Enum):
    """Available colour schemes"""

    BLUE = ColourScheme(
        box_normal_bg=HexColor(0xF0F8FF),
        box_alternate_bg=HexColor(0xDAEDFF),
        title_bg=HexColor(0xa4d7ff),
        logo='logo_banner.jpg',
    )

    RED = ColourScheme(
        box_normal_bg=HexColor(0xFFF0F0),
        box_alternate_bg=HexColor(0xffdada),
        title_bg=HexColor(0xffa4a4),
        logo='logo_banner.jpg',
    )

    GREEN = ColourScheme(
        box_normal_bg=HexColor(0xf0fff0),
        box_alternate_bg=HexColor(0xd9ffd9),
        title_bg=HexColor(0xa4ffa4),
        logo='logo_banner.jpg',
    )

    ORANGE = ColourScheme(
        box_normal_bg=HexColor(0xfff7f0),
        box_alternate_bg=HexColor(0xffecd9),
        title_bg=HexColor(0xffd1a3),
        logo='logo_banner.jpg',
    )

    PURPLE = ColourScheme(
        box_normal_bg=HexColor(0xf8f0ff),
        box_alternate_bg=HexColor(0xeed9ff),
        title_bg=HexColor(0xd5a3ff),
        logo='logo_banner.jpg',
    )

    YELLOW = ColourScheme(
        box_normal_bg=HexColor(0xfffff0),
        box_alternate_bg=HexColor(0xfeffd9),
        title_bg=HexColor(0xfdffa3),
        logo='logo_banner.jpg',
    )

    GREY = ColourScheme(
        box_normal_bg=HexColor(0xf1f1f1),
        box_alternate_bg=HexColor(0xd9d9d9),
        title_bg=HexColor(0xbfbfbf),
        logo='logo_banner.jpg',
    )

    PRIDE = ColourScheme(
        box_normal_bg=HexColor(0xf1f1f1),
        box_alternate_bg=HexColor(0xd9d9d9),
        title_bg=HexColor(0xbfbfbf),
        colours=[
            Color(0.00, 0.00, 0.00, 0.25), # black
            Color(0.47, 0.31, 0.09, 0.25), # brown
            Color(0.94, 0.14, 0.14, 0.25), # red
            Color(0.93, 0.52, 0.13, 0.25), # orange
            Color(1.00, 0.90, 0.00, 0.25), # yellow
            Color(0.07, 0.62, 0.04, 0.25), # green
            Color(0.02, 0.27, 0.70, 0.25), # blue
            Color(0.76, 0.18, 0.86, 0.25), # purple
        ],
        logo='pride_logo_banner.png',
    )

    @classmethod
    def colour_names(cls):
        """get list of available colour names"""
        colours = [e.name for e in list(cls)]
        colours.sort()
        return colours

    def logo_filename(self):
        """filename of the Music Bingo logo"""
        #pylint: disable=no-member
        return Assets.get_data_filename(self.value.logo)

    @property
    def box_normal_bg(self):
        """primary background colour for a Bingo square"""
        #pylint: disable=no-member
        return self.value.box_normal_bg

    @property
    def box_alternate_bg(self):
        """alternate background colour for a Bingo square"""
        #pylint: disable=no-member
        return self.value.box_alternate_bg

    @property
    def title_bg(self) -> HexColor:
        """background colour for title row"""
        #pylint: disable=no-member
        return self.value.title_bg

    @property
    def colours(self) -> List[Color]:
        """list of colours for each Bingo square"""
        #pylint: disable=no-member
        return self.value.colours

# pylint: disable=too-few-public-methods
class BingoTicket:
    """Represents a Bingo ticket with 15 songs"""

    NUM_SONGS: int = 15

    def __init__(self, palette: Palette, card_id: int = 0):
        self.palette = palette
        self.card_id = card_id
        self.card_tracks: List[Song] = []
        self.ticket_number: Optional[int] = None

    def box_colour_style(self, col: int, row: int) -> Color:
        """Get the background colour for a given bingo ticket"""
        if self.palette.colours:
            colour = self.palette.colours[(col + row*5) %
                                          len(self.palette.colours)]
        else:
            # if col & row are both even or both odd, use box_alternate_bg
            if (((col & 1) == 0 and (row & 1) == 0) or
                    ((col & 1) == 1 and (row & 1) == 1)):
                colour = self.palette.box_alternate_bg
            else:
                colour = self.palette.box_normal_bg
        return ('BACKGROUND', (col, row), (col, row), colour)


# pylint: disable=too-few-public-methods
class Mp3Order:
    """represents the order of the tracks within the final mp3"""
    def __init__(self, items):
        self.items = items
        #self.winPoint = None
        #self.amountAtWinPoint = None
        #self.amountAfterWinPoint = None
        #self.winPoints = None

class Options(NamedTuple):
    """Options used by GameGenerator"""
    destination: str  # destination directory
    game_id: str
    palette: Palette
    number_of_cards: int
    include_artist: bool = True
    quiz_mode: bool = False

# pylint: disable=too-many-instance-attributes
class GameGenerator:
    """
    All the functions used in generating the bingo tickets.
    """
    GAME_DIRECTORY = "./Bingo Games"
    GAME_TRACKS_FILENAME = "gameTracks.json"
    CREATE_INDEX = False
    PAGE_ORDER = True
    # pylint: disable=bad-whitespace
    COUNTDOWN_POSITIONS = {
        '10': (   0,   880),
        '9':  ( 880,  2000),
        '8':  (2000,  2800),
        '7':  (2800,  3880),
        '6':  (3880,  5000),
        '5':  (5000,  5920),
        '4':  (5920,  6920),
        '3':  (6920,  7920),
        '2':  (7920,  8880),
        '1':  (8880,  9920),
        '0':  (9920, 10920)
    }


    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 progress: Progress) -> None:
        self.options = options
        self.editor = mp3_editor
        self.progress = progress
        self.game_songs: List[Song] = []
        self.used_card_ids: List[int] = []

    def generate(self, songs: List[Song]) -> None:
        """
        Generate a bingo game.
        This function creates an MP3 file and PDF files.
        """
        self.game_songs = songs
        if not self.assign_song_ids(self.game_songs):
            raise ValueError('Failed to assign song IDs - '+\
                             'maybe not enough tracks in the game?')
        self.progress.num_phases = 4
        self.progress.current_phase = 1
        tracks = self.generate_mp3()
        self.progress.current_phase = 3
        if not self.options.quiz_mode:
            cards = self.generate_all_cards(tracks)
            self.progress.current_phase = 4
            self.generate_tickets_pdf(cards)
            self.generate_ticket_tracks_file(cards)
            self.generate_card_results(tracks, cards)

    def generate_mp3(self) -> List[Song]:
        """
        Generate the mp3 for the game with the generated order of tracks.
        Returns a list of songs with the start_time metadata property
        of each song set to their positon in the output.
        """
        song_order = Mp3Order(self.gen_track_order())
        mp3_name = os.path.join(self.options.destination,
                                self.options.game_id + " Game Audio.mp3")
        album: str = ''
        albums: Set[str] = set()
        for song in song_order.items:
            if song.album:
                albums.add(song.album)
        if len(albums) == 1:
            album = list(albums)[0]
        with self.editor.create(
                mp3_name,
                metadata=Metadata(
                    title=f'Game {self.options.game_id}', artist='',
                    album=album),
                progress=self.progress) as output:
            tracks = self.append_songs(output, song_order.items)
        self.save_game_tracks_json(tracks)
        return tracks

    ##lint: disable=too-many-statements
    def append_songs(self, output: MP3FileWriter,
                     songs: List[Song]) -> List[Song]:
        """
        Append all of the songs to the specified output.
        Returns a new song list with the start_time metadata property
        of each song set to their positon in the output.
        """
        transition = self.editor.use(Assets.transition())
        #transition = transition.normalize(0)
        if self.options.quiz_mode:
            countdown = self.editor.use(Assets.quiz_countdown())
        else:
            countdown = self.editor.use(Assets.countdown())
        #countdown = countdown.normalize(headroom=0)
        if self.options.quiz_mode:
            start, end = self.COUNTDOWN_POSITIONS['1']
            output.append(countdown.clip(start, end))
        else:
            output.append(countdown)
        tracks = []
        num_tracks = len(songs)
        for index, song in enumerate(songs, start=1):
            if index > 1:
                output.append(transition)
            cur_pos = output.duration
            next_track = self.editor.use(song) #.normalize(0)
            if self.options.quiz_mode:
                try:
                    start, end = self.COUNTDOWN_POSITIONS[str(index)]
                    number = countdown.clip(start, end)
                except KeyError:
                    break
                output.append(number)
                output.append(transition)
            output.append(next_track)
            song_with_pos = song.marshall(exclude=["ref_id"])
            song_with_pos['start_time'] = cur_pos.format()
            metadata = Metadata(**song_with_pos)
            tracks.append(Song(song._parent, song.ref_id, metadata))
            self.progress.text = f'Adding track {index}/{num_tracks}'
            self.progress.pct = 100.0 * float(index) / float(num_tracks)

        output.append(transition)
        self.progress.text = 'Generating MP3 file'
        self.progress.current_phase = 2
        output.generate()
        self.progress.text = 'MP3 Generated, creating track listing PDF'
        self.generate_track_listing(tracks)
        self.progress.text = 'MP3 and Track listing PDF generated'
        self.progress.pct = 100.0
        return tracks

    @staticmethod
    def assign_song_ids(songs: List[Song]) -> bool:
        """assigns prime numbers to all of the songs in the game.
        Returns True if successfull and false if there are too many
        songs.
        """
        if len(songs) > len(PRIME_NUMBERS):
            print("Exceeded the {0} song limit".format(len(PRIME_NUMBERS)))
            return False
        for index, song in enumerate(songs):
            song.song_id = PRIME_NUMBERS[index]
        return True

    def select_songs_for_ticket(self, songs: List[Song],
                                card: BingoTicket, num_tracks: int) -> None:
        """select the songs for a bingo ticket ensuring that it is unique"""
        valid_card = False
        picked_indices: Set[int] = set()
        card.card_tracks = []
        card.card_id = 1
        while not valid_card:
            valid_index = False
            index = 0
            while not valid_index:
                index = secrets.randbelow(len(songs))
                valid_index = index not in picked_indices
            card.card_tracks.append(songs[index])
            card.card_id = card.card_id * songs[index].song_id
            picked_indices.add(index)
            if len(card.card_tracks) == num_tracks:
                valid_card = True
                if card.card_id in self.used_card_ids:
                    valid_card = False
                    picked_indices = set()
                    card.card_tracks = []
                    card.card_id = 1
                if valid_card:
                    self.used_card_ids.append(card.card_id)

    def should_include_artist(self, track: Song) -> bool:
        """Check if the artist name should be shown"""
        return self.options.include_artist and not re.match(
            r'various\s+artist', track.artist, re.IGNORECASE)

    def render_bingo_ticket(self, card: BingoTicket) -> List[Any]:
        """render a bingo ticket PDF Table"""
        img = Image(self.options.palette.logo_filename())
        img.drawHeight = 6.2 * inch * img.drawHeight / img.drawWidth
        img.drawWidth = 6.2 * inch

        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_CENTER
        pstyle.fontSize = 12
        pstyle.leading = 12

        para_gap = ParagraphStyle('test')
        para_gap.textColor = 'black'
        para_gap.alignment = TA_CENTER
        para_gap.fontSize = 4
        para_gap.leading = 4

        data = []
        for start,end in ((0, 5), (5, 10), (10, 15)):
            row = []
            for index in range(start, end):
                items = [
                    Paragraph(card.card_tracks[index].title, pstyle),
                    Paragraph('', para_gap),
                ]
                if self.should_include_artist(card.card_tracks[index]):
                    items.append(
                        Paragraph(f'<b>{card.card_tracks[index].artist}</b>',
                                  pstyle))
                row.append(items)
            data.append(row)

        column_width = 1.54*inch
        row_height = 1.0*inch

        table=Table(
            data,
            colWidths=(column_width, column_width, column_width, column_width, column_width),
            rowHeights=(row_height, row_height, row_height),
            style=[('BOX',(0,0),(-1,-1),2,colors.black),
                   ('GRID',(0,0),(-1,-1),0.5,colors.black),
                   ('VALIGN',(0,0),(-1,-1),'CENTER'),
                   card.box_colour_style(1,0),
                   card.box_colour_style(3,0),
                   card.box_colour_style(0,1),
                   card.box_colour_style(2,1),
                   card.box_colour_style(4,1),
                   card.box_colour_style(1,2),
                   card.box_colour_style(3,2),
                   ('PADDINGTOP', (0, 0), (-1, -1), 0),
                   ('PADDINGLEFT', (0, 0), (-1, -1), 0),
                   ('PADDINGRIGHT', (0, 0), (-1, -1), 0),
                   ('PADDINGBOTTOM', (0, 0), (-1, -1), 0),
                   card.box_colour_style(0,0),
                   card.box_colour_style(2,0),
                   card.box_colour_style(4,0),
                   card.box_colour_style(1,1),
                   card.box_colour_style(3,1),
                   card.box_colour_style(0,2),
                   card.box_colour_style(2,2),
                   card.box_colour_style(4,2)])
        return [img, Spacer(width=0, height=0.1*inch), table]

    def generate_track_listing(self, tracks: List[Song]) -> None:
        """generate a PDF version of the track order in the game"""
        doc = SimpleDocTemplate(os.path.join(self.options.destination,
                                             self.options.game_id+" Track Listing.pdf"),
                                pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements: List[Flowable] = []
        img = Image(self.options.palette.logo_filename())
        img.drawHeight = 6.2*inch * img.drawHeight / img.drawWidth
        img.drawWidth = 6.2*inch

        elements.append(img)
        elements.append(Spacer(width=0, height=0.05*inch))

        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_CENTER
        pstyle.fontSize = 18
        pstyle.leading = 18

        title = Paragraph(
            f'Track Listing For Game Number: <b>{self.options.game_id}</b>', pstyle)
        elements.append(title)

        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_CENTER
        pstyle.fontSize = 10
        pstyle.leading = 10

        elements.append(Spacer(width=0, height=0.15*inch))

        data = [[
            Paragraph('<b>Order</b>',pstyle),
            Paragraph('<b>Title</b>',pstyle),
            Paragraph('<b>Artist</b>',pstyle),
            Paragraph('<b>Start Time</b>',pstyle),
            Paragraph('',pstyle),
        ]]

        for index, song in enumerate(tracks, start=1):
            order = Paragraph(f'<b>{index}</b>',pstyle)
            title = Paragraph(song.title, pstyle)
            if self.should_include_artist(song):
                artist = Paragraph(song.artist, pstyle)
            else:
                artist = Paragraph('', pstyle)
            start = Paragraph(song.start_time, pstyle)
            end_box = Paragraph('',pstyle)
            data.append([order, title, artist, start, end_box])

        table=Table(data,
                    style=[('BOX',(0,0),(-1,-1),1,colors.black),
                           ('GRID',(0,0),(-1,-1),0.5,colors.black),
                           ('VALIGN',(0,0),(-1,-1),'CENTER'),
                           ('BACKGROUND', (0, 0), (4, 0),
                            self.options.palette.title_bg)])
        table._argW[0] = 0.55*inch
        table._argW[1] = 3.1*inch
        table._argW[2] = 3.1*inch
        table._argW[3] = 0.85*inch
        table._argW[4] = 0.3*inch
        elements.append(table)
        doc.build(elements)

    def generate_card_results(self, tracks: List[Song],
                              cards: List[BingoTicket]):
        """generate PDF showing when each ticket wins"""
        doc = SimpleDocTemplate(
            os.path.join(self.options.destination,
                         f"{self.options.game_id} Ticket Results.pdf"),
            pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements: List[Flowable] = []

        img = Image(self.options.palette.logo_filename())
        img.drawHeight = 6.2*inch * img.drawHeight / img.drawWidth
        img.drawWidth = 6.2*inch
        elements.append(img)

        elements.append(Spacer(width=0, height=0.05*inch))

        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_CENTER
        pstyle.fontSize = 18
        pstyle.leading = 18

        elements.append(
            Paragraph(f'Results For Game Number: <b>{self.options.game_id}</b>',
                      pstyle))
        elements.append(Spacer(width=0, height=0.15*inch))

        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_CENTER
        pstyle.fontSize = 10
        pstyle.leading = 10

        data = [[
            Paragraph('<b>Ticket Number</b>',pstyle),
            Paragraph('<b>Wins after track</b>',pstyle),
            Paragraph('<b>Start Time</b>',pstyle),
        ]]

        cards = copy.copy(cards)
        cards.sort(key=lambda card: card.ticket_number, reverse=False)
        for card in cards:
            win_point = self.get_when_ticket_wins(tracks, card)
            song = tracks[win_point - 1]
            data.append([
                Paragraph(f'{card.ticket_number}', pstyle),
                Paragraph(f'Track {win_point} - {song.title} ({song.artist})',
                          pstyle),
                Paragraph(song.start_time, pstyle)
            ])

        table=Table(data,
                    style=[('BOX',(0,0),(-1,-1),1,colors.black),
                           ('GRID',(0,0),(-1,-1),0.5,colors.black),
                           ('VALIGN',(0,0),(-1,-1),'CENTER'),
                           ('BACKGROUND', (0, 0), (4, 0),
                            self.options.palette.title_bg)])
        table._argW[0] = 0.75 * inch
        table._argW[1] = 5.5  * inch
        table._argW[2] = 0.8  * inch
        elements.append(table)
        doc.build(elements)

    def generate_at_point(self, tracks: List[Song], amount: int,
                          from_end: int) -> List[BingoTicket]:
        """generate an 'amount' number of bingo tickets that will win
        at the specified amount from the end
        """
        count = 0
        cards = []
        while count < amount:
            card = BingoTicket(self.options.palette)
            self.select_songs_for_ticket(self.game_songs, card,
                                         BingoTicket.NUM_SONGS)
            win_point = self.get_when_ticket_wins(tracks, card)
            if win_point != (len(tracks) - from_end):
                self.used_card_ids.remove(card.card_id)
            else:
                cards.append(card)
                count = count + 1
        return cards

    @staticmethod
    def randrange(start, end):
        """a version of random.randrange() that uses a better random number generator.
        This version of randrange() uses the secrets library for a better source of
        entropy.
        """
        return start + secrets.randbelow(end - start)

    def generate_all_cards(self, tracks: List[Song]) -> List[BingoTicket]:
        """generate all the bingo tickets in the game"""
        self.progress.text = 'Calculating cards'
        self.progress.pct = 0.0
        self.used_card_ids = [] # Could assign this from file (for printing more)
        cards: List[BingoTicket] = []
        decay_rate = 0.65
        num_on_last = self.options.number_of_cards * decay_rate
        num_second_last = (self.options.number_of_cards-num_on_last) * decay_rate
        num_third_last = (self.options.number_of_cards - num_on_last -
                          num_second_last) * decay_rate
        num_fourth_last = ((self.options.number_of_cards - num_on_last -
                            num_second_last - num_third_last) *
                           decay_rate)
        num_on_last = int(num_on_last)
        num_second_last = int(num_second_last)
        num_third_last = int(num_third_last)
        num_fourth_last = max(int(num_fourth_last), 1)
        amount_left = (self.options.number_of_cards - num_on_last -
                       num_second_last - num_third_last -
                       num_fourth_last)
        amount_to_go = 4
        offset = 4
        if num_fourth_last in [0, 1]:
            offset = 3
            num_fourth_last = 0
            num_on_last += 1
        if amount_left < amount_to_go or amount_left > amount_to_go:
            num_on_last = num_on_last - (amount_to_go - amount_left)
        cards += self.generate_at_point(tracks, num_on_last, 0)
        if num_second_last != 0:
            self.insert_random_cards(tracks, cards, 1, num_second_last, num_on_last)
        if num_third_last != 0:
            self.insert_random_cards(tracks, cards, 2, num_third_last, num_on_last)
        if num_fourth_last != 0:
            self.insert_random_cards(tracks, cards, 3, num_fourth_last, num_on_last)
        good_cards = []
        for idx in range(0, amount_to_go):
            self.progress.pct = 100.0 * (float(idx) / float(amount_to_go))
            card = self.generate_at_point(tracks, 1, offset)[0]
            good_cards.append(card)
            offset += 1
        increment: float = self.options.number_of_cards / float(amount_to_go)
        start_point: float = 0
        random.shuffle(good_cards)
        for card in good_cards:
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point+increment)))
            rand_point = int(math.ceil(rand_point))
            rand_point = min(rand_point, self.options.number_of_cards - 1)
            cards.insert(rand_point, card)
            start_point += increment
        for idx, card in enumerate(cards, start=1):
            card.ticket_number = idx
        if self.PAGE_ORDER:
            return self.sort_cards_by_page(cards)
        return cards

    def sort_cards_by_page(self, cards: List[BingoTicket]) -> List[BingoTicket]:
        """sort BingoTickets so that each ascending ticket number is on a
        different page.
        BingoTickets 1 .. n will be on pages 1..n (where n is 1/3 of ticket total)
        BingoTickets n .. 2n will be on pages 1..n
        BingoTickets 2n .. 3n will be on pages 1..n
        """
        noc3c = int(math.ceil(self.options.number_of_cards/3))
        noc3f = int(math.floor(self.options.number_of_cards/3))
        first_third = cards[0:noc3c]
        second_third = cards[noc3c: noc3c + noc3f]
        third_third = cards[noc3c+noc3f : len(cards)]
        cards = []
        while len(first_third) > 0:
            cards.append(first_third.pop(0))
            if len(second_third) > 0:
                cards.append(second_third.pop(0))
            if len(third_third) > 0:
                cards.append(third_third.pop(0))
        return cards

    def insert_random_cards(self, tracks: List[Song], cards: List[BingoTicket],
                            point: int, num_cards: int, num_on_last: int) -> None:
        """add cards at a random position in the card list.
        Adds num_cards Bingo Tickets at position "point" from the end of the list
        """
        increment: float = (len(cards) + num_cards) / float(num_cards)
        start_point: float = 0
        for _ in range(0, num_cards):
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point+increment)))
            rand_point = int(math.ceil(rand_point))
            if rand_point >= (num_on_last + num_cards):
                rand_point = num_on_last + num_cards - 1
            cards.insert(
                rand_point,
                self.generate_at_point(tracks, 1, point)[0])
            start_point = start_point + increment

    def generate_tickets_pdf(self, cards: List[BingoTicket]) -> None:
        """generate a PDF file containing all the Bingo tickets"""
        name = (f'{self.options.game_id} Bingo Tickets - ' +
                f'({self.options.number_of_cards} Tickets).pdf')
        doc = SimpleDocTemplate(os.path.join(self.options.destination, name),
                                pagesize=A4)
        doc.topMargin = 0
        doc.bottomMargin = 0
        # container for the 'Flowable' objects
        elements: List[Flowable] = []
        page = 1
        num_cards = len(cards)
        pstyle = ParagraphStyle('test')
        pstyle.textColor = 'black'
        pstyle.alignment = TA_RIGHT
        pstyle.fontSize = 12
        pstyle.leading = 12
        for count, card in enumerate(cards, start=1):
            self.progress.text = f'Card {count}/{num_cards}'
            self.progress.pct = 100.0 * float(count) / float(num_cards)
            elements += self.render_bingo_ticket(card)
            ticket_id = f"{self.options.game_id} / T{card.ticket_number} / P{page}"
            ticket_id_para = Paragraph(ticket_id, pstyle)
            if count % 3 != 0:
                elements.append(Spacer(width=0, height=0.01*inch))
                elements.append(ticket_id_para)
                elements.append(Spacer(width=0, height=0.06*inch))
                data = [[""]]
                table=Table(
                    data, colWidths=(10.0*inch), rowHeights=(0.0),
                    style=[("LINEBELOW", (0,0), (-1,-1), 1, colors.black)])
                elements.append(table)
                elements.append(Spacer(width=0, height=0.08*inch))
            else:
                elements.append(Spacer(width=0, height=0.01*inch))
                elements.append(ticket_id_para)
                elements.append(PageBreak())
                page += 1
        # write the document to disk
        doc.build(elements)

    def generate_ticket_tracks_file(self, cards: List[BingoTicket]) -> None:
        """store ticketTracks file used by TicketChecker.py"""
        filename = os.path.join(self.options.destination, "ticketTracks")
        with open(filename, 'wt') as ttf:
            for card in cards:
                ttf.write(f"{card.ticket_number}/{card.card_id}\n")

    def gen_track_order(self) -> List[Song]:
        """generate a random order of tracks for the game"""
        def rand_float() -> float:
            return float(secrets.randbelow(1000)) / 1000.0
        list_copy = copy.copy(self.game_songs)
        if not self.options.quiz_mode:
            random.shuffle(list_copy, rand_float)
        return list_copy

    @staticmethod
    def get_when_ticket_wins(tracks: List[Song], ticket: BingoTicket) -> int:
        """get the point at which the given ticket will win, given the
        specified order"""
        last_song = -1
        card_track_ids = {track.ref_id for track in ticket.card_tracks}

        for count, song in enumerate(tracks, start=1):
            if song.ref_id in card_track_ids:
                last_song = count
                card_track_ids.remove(song.ref_id)
            if not card_track_ids:
                break
        if card_track_ids:
            raise ValueError(f'ticket never wins, missing {card_track_ids}')
        return last_song

    def save_game_tracks_json(self, tracks: List[Song]) -> None:
        """saves the track listing to gameTracks.json"""
        filename = os.path.join(self.options.destination,
                                self.GAME_TRACKS_FILENAME)
        clip_dir = tracks[0]._parent
        assert clip_dir is not None
        while clip_dir._parent:
            clip_dir = clip_dir._parent
        clip_dir = cast(Directory, clip_dir)
        with open(filename, 'w') as jsf:
            marshalled: List[Dict] = []
            for track in tracks:
                track_dict = track.marshall(exclude=['ref_id', 'filename', 'index'])
                if track_dict['filepath'].startswith(clip_dir.directory):
                    track_dict['filepath'] = track_dict['filepath'][len(clip_dir.directory)+1:]
                marshalled.append(track_dict)
            json.dump(marshalled, jsf, sort_keys=True, indent=2)

    @staticmethod
    def combinations(total: int, select: int) -> int:
        """calculate combinations
        Calculates the number of combinations of selecting 'select' items
        from 'total' items
        """
        if select > total:
            return 0
        return int(math.factorial(total)/(math.factorial(select)*math.factorial(total-select)))
