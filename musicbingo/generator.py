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
import copy
import datetime
import json
import math
import random
import re
import secrets
from typing import Dict, List, Optional, Sequence, Set

from musicbingo.assets import Assets
from musicbingo.directory import Directory
from musicbingo.docgen import documentgenerator as DG
from musicbingo.docgen.colour import Colour
from musicbingo.docgen.factory import DocumentFactory
from musicbingo.docgen.sizes import PageSizes, Dimension
from musicbingo.docgen.styles import HorizontalAlignment, VerticalAlignment
from musicbingo.docgen.styles import ElementStyle, TableStyle, Padding
from musicbingo.mp3.editor import MP3Editor, MP3FileWriter
from musicbingo.options import GameMode, Options
from musicbingo.palette import Palette
from musicbingo.progress import Progress
from musicbingo.song import Duration, Metadata, Song

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

# pylint: disable=too-few-public-methods
class BingoTicket:
    """Represents a Bingo ticket with 15 songs"""

    NUM_SONGS: int = 15

    def __init__(self, palette: Palette, card_id: int = 0):
        self.palette = palette
        self.card_id = card_id
        self.card_tracks: List[Song] = []
        self.ticket_number: Optional[int] = None

    def box_colour_style(self, col: int, row: int) -> Colour:
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
        return colour
        #return ('BACKGROUND', (col, row), (col, row), colour)


# pylint: disable=too-many-instance-attributes
class GameGenerator:
    """
    All the functions used in generating the bingo tickets.
    """
    TEXT_STYLES = {
        'ticket-cell': ElementStyle(
            name='ticket-cell',
            colour='black',
            alignment=HorizontalAlignment.CENTER,
            fontSize=12,
            leading=12,
            padding=Padding(bottom=(4.0/72.0)),
        ),
        'track-heading': ElementStyle(
            name='track-heading',
            colour=Colour('black'),
            alignment=HorizontalAlignment.CENTER,
            fontSize=18,
            leading=18
        ),
        'track-cell': ElementStyle(
            name='track-cell',
            colour='black',
            alignment=HorizontalAlignment.CENTER,
            fontSize=10,
            leading=10
        ),
        'results-heading': ElementStyle(
            name='results-heading',
            colour='black',
            alignment=HorizontalAlignment.CENTER,
            fontSize=18,
            leading=18,
            padding=Padding(bottom="0.15in"),
        ),
        'results-cell': ElementStyle(
            name='results-cell',
            colour='black',
            alignment=HorizontalAlignment.CENTER,
            fontSize=10,
            leading=10
        ),
        'ticket-id': ElementStyle(
            name='ticket-id',
            colour='black',
            alignment=HorizontalAlignment.RIGHT,
            fontSize=10,
            leading=10,
            padding=Padding(top=1, bottom=2, right="6pt"),
        )
    }

    MIN_CARDS: int = 15 # minimum number of cards in a game
    MIN_SONGS: int = 17  # 17 songs allows 136 combinations
    MAX_SONGS: int = len(PRIME_NUMBERS)

    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 doc_gen: DG.DocumentGenerator,
                 progress: Progress) -> None:
        self.options = options
        self.mp3_editor = mp3_editor
        self.doc_gen = doc_gen
        self.progress = progress
        self.game_songs: List[Song] = []
        self.used_card_ids: Set[int] = set()

    def generate(self, songs: List[Song]) -> None:
        """
        Generate a bingo game.
        This function creates an MP3 file and PDF files.
        """
        self.check_options(self.options, songs)
        self.game_songs = songs
        if not self.assign_song_ids(self.game_songs):
            raise ValueError('Failed to assign song IDs - '+\
                             'maybe not enough tracks in the game?')
        dest_directory = self.options.game_destination_dir()
        if not dest_directory.exists():
            dest_directory.mkdir(parents=True)
        self.progress.num_phases = 4
        self.progress.current_phase = 1
        tracks = self.generate_mp3()
        self.progress.current_phase = 3
        if self.options.mode == GameMode.BINGO:
            cards = self.generate_all_cards(tracks)
            self.progress.current_phase = 4
            self.generate_tickets_pdf(cards)
            self.generate_ticket_tracks_file(cards)
            self.generate_card_results(tracks, cards)

    @classmethod
    def check_options(cls, options: Options, songs: Sequence[Song]):
        """
        Check that the given options and song list allow a game to be
        generated.
        """
        if options.game_id == '':
            raise ValueError("Game ID cannot be empty")
        num_songs = len(songs)
        if num_songs == 0:
            raise ValueError("Song list cannot be empty")
        if options.mode == GameMode.QUIZ:
            max_songs = len(Assets.QUIZ_COUNTDOWN_POSITIONS)
            if num_songs > max_songs:
                raise ValueError(f'Maximum number of songs for a quiz is {max_songs}')
            return
        if options.mode != GameMode.BINGO:
            raise ValueError(f'Invalid mode {options.mode}')
        if num_songs < cls.MIN_SONGS:
            raise ValueError(f'At least {cls.MIN_SONGS} songs are required')
        if num_songs > cls.MAX_SONGS:
            raise ValueError(f'Maximum number of songs is {cls.MAX_SONGS}')
        if options.number_of_cards < cls.MIN_CARDS:
            raise ValueError(f'At least {cls.MIN_CARDS} tickets are required')
        max_cards = cls.combinations(num_songs, BingoTicket.NUM_SONGS)
        if options.number_of_cards > max_cards:
            raise ValueError(f'{num_songs} songs only allows '+
                             f'{max_cards} cards to be generated')

    def generate_mp3(self) -> List[Song]:
        """
        Generate the mp3 for the game with the generated order of tracks.
        Returns a list of songs with the start_time metadata property
        of each song set to their positon in the output.
        """
        songs = self.gen_track_order()
        assert len(songs) > 0
        mp3_name = self.options.mp3_output_name()
        album: str = ''
        albums: Set[str] = set()
        for song in songs:
            if song.album:
                albums.add(song.album)
        if len(albums) == 1:
            album = list(albums)[0]
        with self.mp3_editor.create(
                mp3_name,
                metadata=Metadata(
                    title=f'Game {self.options.game_id}', artist='',
                    album=album),
                progress=self.progress) as output:
            tracks = self.append_songs(output, songs)
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
        transition = self.mp3_editor.use(Assets.transition())
        #transition = transition.normalize(0)
        if self.options.mode == GameMode.QUIZ:
            countdown = self.mp3_editor.use(Assets.quiz_countdown())
        else:
            countdown = self.mp3_editor.use(Assets.countdown())
        #countdown = countdown.normalize(headroom=0)
        if self.options.mode == GameMode.QUIZ:
            start, end = Assets.QUIZ_COUNTDOWN_POSITIONS['1']
            output.append(countdown.clip(start, end))
        else:
            output.append(countdown)
        tracks = []
        num_tracks = len(songs)
        for index, song in enumerate(songs, start=1):
            if index > 1:
                output.append(transition)
            cur_pos = output.duration
            next_track = self.mp3_editor.use(song) #.normalize(0)
            if self.options.mode == GameMode.QUIZ:
                try:
                    start, end = Assets.QUIZ_COUNTDOWN_POSITIONS[str(index)]
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
    def assign_song_ids(songs: Sequence[Song]) -> bool:
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
                    self.used_card_ids.add(card.card_id)

    def should_include_artist(self, track: Song) -> bool:
        """Check if the artist name should be shown"""
        return self.options.include_artist and not re.match(
            r'various\s+artist', track.artist, re.IGNORECASE)

    def render_bingo_ticket(self, card: BingoTicket, doc: DG.Document) -> None:
        """
        Render a Bingo ticket as flowable objects.
        Each ticket has the Music Bingo logo followed by a
        table.
        """
        doc.append(self.options.palette.logo_image("6.2in"))

        pstyle = self.TEXT_STYLES['ticket-cell']
        data: List[DG.TableRow] = []
        for start, end in ((0, 5), (5, 10), (10, 15)):
            row: DG.TableRow = []
            for index in range(start, end):
                items: List[DG.Paragraph] = [
                    DG.Paragraph(card.card_tracks[index].title, pstyle),
                ]
                if self.should_include_artist(card.card_tracks[index]):
                    items.append(
                        DG.Paragraph(f'<b>{card.card_tracks[index].artist}</b>',
                                     pstyle))
                row.append(items)
            data.append(row)

        column_width = Dimension("1.54in")
        row_height = Dimension("0.97in")

        tstyle = TableStyle(name='bingo-card',
                            borderColour=Colour('black'),
                            borderWidth=2.0,
                            gridColour=Colour('black'),
                            gridWidth=0.5,
                            verticalAlignment=VerticalAlignment.CENTER)
        col_widths: List[Dimension] = [column_width] * 5
        table = DG.Table(
            data,
            colWidths=col_widths,
            rowHeights=(row_height, row_height, row_height),
            style=tstyle)
        for box_row in range(0, 3):
            for box_col in range(0, 5):
                table.style_cells(
                    DG.CellPos(col=box_col, row=box_row),
                    DG.CellPos(col=box_col, row=box_row),
                    background=card.box_colour_style(box_col, box_row))
        #doc.append(DG.Spacer(width=0, height=0.1*INCH))
        doc.append(table)

    def generate_track_listing(self, tracks: List[Song]) -> None:
        """generate a PDF version of the track order in the game"""
        assert len(tracks) > 0
        doc = DG.Document(PageSizes.A4, topMargin="0.25in",
                          bottomMargin="0.25in",
                          leftMargin="0.35in", rightMargin="0.35in",
                          title=f'Track Listing for {self.options.game_id}')

        doc.append(self.options.palette.logo_image("6.2in"))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        hstyle = self.TEXT_STYLES['track-heading']
        title = DG.Paragraph(
            f'Track Listing For Game Number: <b>{self.options.game_id}</b>',
            hstyle)
        doc.append(title)

        doc.append(DG.Spacer(width=0, height="0.15in"))

        cell_style = self.TEXT_STYLES['track-cell']
        heading: DG.TableRow = [
            DG.Paragraph('<b>Order</b>', cell_style),
            DG.Paragraph('<b>Title</b>', cell_style),
            DG.Paragraph('<b>Artist</b>', cell_style),
            DG.Paragraph('<b>Start Time</b>', cell_style),
            DG.Paragraph('', cell_style),
        ]

        data: List[DG.TableRow] = []

        for index, song in enumerate(tracks, start=1):
            order = DG.Paragraph(f'<b>{index}</b>', cell_style)
            title = DG.Paragraph(song.title, cell_style)
            if self.should_include_artist(song):
                artist = DG.Paragraph(song.artist, cell_style)
            else:
                artist = DG.Paragraph('', cell_style)
            start = DG.Paragraph(Duration(song.start_time).format(), cell_style)
            end_box = DG.Paragraph('', cell_style)
            data.append([order, title, artist, start, end_box])

        col_widths = [Dimension("0.55in"),
                      Dimension("2.9in"),
                      Dimension("2.9in"),
                      Dimension("0.85in"),
                      Dimension("0.2in")]

        hstyle = cell_style.replace(
            name='track-table-heading',
            background=self.options.palette.title_bg)
        tstyle = TableStyle(
            name='track-table',
            borderColour=Colour('black'),
            borderWidth=1.0,
            gridColour=Colour('black'),
            gridWidth=0.5,
            verticalAlignment=VerticalAlignment.CENTER,
            headingStyle=hstyle)
        table = DG.Table(data, heading=heading, repeat_heading=True,
                         colWidths=col_widths, style=tstyle)
        doc.append(table)
        filename = str(self.options.track_listing_output_name())
        self.doc_gen.render(filename, doc, Progress())

    def generate_card_results(self, tracks: List[Song],
                              cards: List[BingoTicket]):
        """generate PDF showing when each ticket wins"""
        doc = DG.Document(pagesize=PageSizes.A4,
                          topMargin="0.25in",
                          bottomMargin="0.25in",
                          rightMargin="0.25in",
                          leftMargin="0.25in")

        doc.append(self.options.palette.logo_image("6.2in"))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        heading_style = self.TEXT_STYLES['results-heading']
        doc.append(
            DG.Paragraph(
                f'Results For Game Number: <b>{self.options.game_id}</b>',
                heading_style))

        pstyle = self.TEXT_STYLES['results-cell']
        heading: DG.TableRow = [
            DG.Paragraph('<b>Ticket Number</b>', pstyle),
            DG.Paragraph('<b>Wins after track</b>', pstyle),
            DG.Paragraph('<b>Start Time</b>', pstyle),
        ]
        data: List[DG.TableRow] = []

        cards = copy.copy(cards)
        cards.sort(key=lambda card: card.ticket_number, reverse=False)
        for card in cards:
            win_point = self.get_when_ticket_wins(tracks, card)
            song = tracks[win_point - 1]
            data.append([
                DG.Paragraph(f'{card.ticket_number}', pstyle),
                DG.Paragraph(
                    f'Track {win_point} - {song.title} ({song.artist})',
                    pstyle),
                DG.Paragraph(Duration(song.start_time).format(), pstyle)
            ])

        col_widths: List[Dimension] = [
            Dimension("0.75in"), Dimension("5.5in"), Dimension("0.85in"),
        ]
        hstyle = pstyle.replace(
            name='results-table-heading',
            background=self.options.palette.title_bg)
        tstyle = TableStyle(name='results-table',
                            borderColour=Colour('black'),
                            borderWidth=1.0,
                            gridColour=Colour('black'),
                            gridWidth=0.5,
                            verticalAlignment=VerticalAlignment.CENTER,
                            headingStyle=hstyle)
        table = DG.Table(data, heading=heading, repeat_heading=True,
                         colWidths=col_widths, style=tstyle)
        doc.append(table)
        filename = str(self.options.ticket_results_output_name())
        self.doc_gen.render(filename, doc, Progress())

    def generate_at_point(self, tracks: List[Song], amount: int,
                          from_end: int) -> List[BingoTicket]:
        """generate an 'amount' number of bingo tickets that will win
        at the specified amount from the end
        """
        count = 0
        cards = []
        while count < amount:
            card = BingoTicket(self.options.palette)
            self.select_songs_for_ticket(tracks, card,
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
        self.used_card_ids.clear()
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
        if self.options.page_order:
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
        doc = DG.Document(pagesize=PageSizes.A4,
                          topMargin="0.15in",
                          rightMargin="0.15in",
                          bottomMargin="0.15in",
                          leftMargin="0.15in")
        page = 1
        num_cards = len(cards)
        pstyle = self.TEXT_STYLES['ticket-id']
        for count, card in enumerate(cards, start=1):
            self.progress.text = f'Card {count}/{num_cards}'
            self.progress.pct = 100.0 * float(count) / float(num_cards)
            self.render_bingo_ticket(card, doc)
            ticket_id = f"{self.options.game_id} / T{card.ticket_number} / P{page}"
            ticket_id_para = DG.Paragraph(ticket_id, pstyle)
            if count % 3 != 0:
                doc.append(ticket_id_para)
                #doc.append(Box('hline', width=(10.0 * INCH), height=1.0,
                #width=PageSizes.A4.width(),
                doc.append(
                    DG.HorizontalLine('hline', width="100%", thickness="1px",
                                      colour=Colour('gray'), dash=[2, 2]))
                doc.append(DG.Spacer(width=0, height="0.08in"))
            else:
                doc.append(ticket_id_para)
                doc.append(DG.PageBreak())
                page += 1
        filename = str(self.options.bingo_tickets_output_name())
        self.doc_gen.render(filename, doc, Progress())

    def generate_ticket_tracks_file(self, cards: List[BingoTicket]) -> None:
        """store ticketTracks file used by TicketChecker.py"""
        filename = self.options.ticket_checker_output_name()
        with filename.open('wt') as ttf:
            for card in cards:
                ttf.write(f"{card.ticket_number}/{card.card_id}\n")

    def gen_track_order(self) -> List[Song]:
        """generate a random order of tracks for the game"""
        assert len(self.game_songs) > 0
        list_copy = copy.copy(self.game_songs)
        if not self.options.mode == GameMode.QUIZ:
            random.shuffle(list_copy, self.rand_float)
        return list_copy

    @staticmethod
    def rand_float() -> float:
        """generate a random number using the secrets library"""
        return float(secrets.randbelow(1000)) / 1000.0

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
        filename = self.options.game_info_output_name()
        clip_dir = str(self.options.clips())
        with filename.open('w') as jsf:
            marshalled: List[Dict] = []
            for track in tracks:
                track_dict = track.marshall(exclude=['ref_id', 'filename', 'index'])
                track_dict['filepath'] = str(track_dict['filepath'])
                # remove top level "Clips" directory to make filepath
                # relative to "Clips" directory
                if track_dict['filepath'].startswith(clip_dir):
                    track_dict['filepath'] = track_dict['filepath'][len(clip_dir)+1:]
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

def main(args: Sequence[str]) -> int:
    """used for testing game generation without needing to use the GUI"""
    #pylint: disable=import-outside-toplevel
    from musicbingo.mp3 import MP3Factory
    class TextProgress(Progress):
        """displays progress on console"""
        def on_change_total_percent(self, total_percentage: float) -> None:
            print('{0}: {1:0.3f}'.format(self._text, total_percentage))

    options = Options.parse(args)
    if options.game_id == '':
        options.game_id = datetime.date.today().strftime("%y-%m-%d")
    progress = TextProgress()
    mp3parser = MP3Factory.create_parser()
    mp3editor = MP3Factory.create_editor()
    pdf = DocumentFactory.create_generator('pdf')
    clips = Directory(None, 0, options.clips(), mp3parser, progress)
    clips.search()
    gen = GameGenerator(options, mp3editor, pdf, progress)
    gen.generate(clips.songs[:30])
    return 0

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
