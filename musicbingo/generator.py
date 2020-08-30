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
import statistics
import sys
from typing import Iterable, List, Optional, Sequence, Set, Tuple

from . import models
from .models.db import db_session
from .models.modelmixin import JsonObject
from .assets import Assets
from .bingoticket import BingoTicket
from .directory import Directory
from .docgen import documentgenerator as DG
from .docgen.colour import Colour
from .docgen.factory import DocumentFactory
from .docgen.sizes import PageSizes, Dimension
from .docgen.styles import HorizontalAlignment, VerticalAlignment
from .docgen.styles import ElementStyle, TableStyle, Padding
from .duration import Duration
from .mp3.editor import MP3Editor, MP3FileWriter
from .options import GameMode, Options
from .primes import PRIME_NUMBERS
from .progress import Progress, TextProgress
from .metadata import Metadata
from .song import Song
from .track import Track
from .utils import flatten


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
            padding=Padding(bottom=(4.0 / 72.0)),
        ),
        'track-heading': ElementStyle(
            name='track-heading',
            colour=Colour('black'),
            alignment=HorizontalAlignment.CENTER,
            fontSize=18,
            leading=18,
            padding=Padding(bottom="3pt"),
        ),
        'track-title': ElementStyle(
            name='track-title',
            colour=Colour('black'),
            alignment=HorizontalAlignment.CENTER,
            fontSize=14,
            leading=14,
            padding=Padding(bottom="10pt"),
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
            padding=Padding(bottom="3pt"),
        ),
        'results-title': ElementStyle(
            name='results-title',
            colour='black',
            alignment=HorizontalAlignment.CENTER,
            fontSize=14,
            leading=14,
            padding=Padding(bottom="10pt"),
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
        )
    }
    CHECKBOX_STYLE = ElementStyle(
        name='checkbox-style',
        colour='black',
    )

    MIN_CARDS: int = 15  # minimum number of cards in a game
    MIN_SONGS: int = 17  # 17 songs allows 136 combinations
    MAX_SONGS: int = len(PRIME_NUMBERS)

    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 doc_gen: DG.DocumentGenerator,
                 progress: Progress) -> None:
        self.options = options
        self.mp3_editor = mp3_editor
        self.doc_gen = doc_gen
        self.progress = progress
        #self.game_songs: List[Song] = []
        self.used_fingerprints: Set[int] = set()

    @db_session
    def generate(self, songs: List[Song], session) -> None:
        """
        Generate a bingo game.
        This function creates an MP3 file and PDF files.
        """
        self.check_options(self.options, songs)
        # self.game_songs = self.create_tracks(songs):
        #    raise ValueError('Failed to assign song IDs - '+\
        #                    'maybe not enough tracks in the game?')
        dest_directory = self.options.game_destination_dir()
        if not dest_directory.exists():
            dest_directory.mkdir(parents=True)
        opts = self.options.to_dict(only={
            'cards_per_page', 'checkbox', 'colour_scheme', 'columns', 'rows',
            'number_of_cards', 'doc_per_page', 'cards_per_page', 'bitrate',
            'crossfade', 'include_artist'})
        game = models.Game(id=self.options.game_id,
                           title=self.options.title,
                           start=datetime.datetime.now(),
                           end=(datetime.datetime.now() + datetime.timedelta(days=100)),
                           options=opts,
                           )
        session.add(game)
        self.progress.num_phases = 4
        self.progress.current_phase = 1
        tracks = self.generate_mp3(songs)
        if self.progress.abort:
            return
        db_tracks: List[models.Track] = []
        for track in tracks:
            song = track.song.model(session)
            assert song is not None
            db_tracks.append(track.save(game=game, song=song, session=session))
        session.flush()
        self.progress.current_phase = 3
        db_cards: List[models.BingoTicket] = []
        if self.options.mode == GameMode.BINGO:
            cards = self.generate_all_cards(tracks)
            if self.progress.abort:
                return
            for card in cards:
                db_cards.append(card.save(game=game, session=session))
            self.progress.current_phase = 4
            self.generate_tickets_pdf(cards)
            if self.progress.abort:
                return
            self.generate_ticket_tracks_file(cards)
            if self.progress.abort:
                return
            session.flush()
            self.generate_card_results(tracks, cards)
            self.save_game_info_json(game, db_tracks, db_cards)

    @classmethod
    def check_options(cls, options: Options, songs: Sequence[Song]):
        """
        Check that the given options and song list allow a game to be
        generated.
        """
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
        if options.game_id == '':
            raise ValueError("Game ID cannot be empty")
        min_songs = int(round(1.5 * options.songs_per_ticket() + 0.5))
        if num_songs < min_songs:
            raise ValueError(f'At least {min_songs} songs are required')
        if num_songs > cls.MAX_SONGS:
            raise ValueError(f'Maximum number of songs is {cls.MAX_SONGS}')
        if options.number_of_cards < cls.MIN_CARDS:
            raise ValueError(f'At least {cls.MIN_CARDS} tickets are required')
        max_cards = cls.combinations(num_songs, options.songs_per_ticket())
        if options.number_of_cards > max_cards:
            raise ValueError(f'{num_songs} songs only allows ' +
                             f'{max_cards} cards to be generated')

    def generate_mp3(self, songs: Sequence[Song]) -> List[Track]:
        """
        Generate the mp3 for the game with the generated order of tracks.
        Returns a list of songs with the start_time metadata property
        of each song set to their positon in the output.
        """
        songs = self.gen_track_order(songs)
        mp3_name = self.options.mp3_output_name()
        album: str = ''
        albums: Set[str] = set()
        channels: List[int] = []
        sample_width: List[int] = []
        sample_rate: List[int] = []
        for song in songs:
            channels.append(song.channels)
            sample_width.append(song.sample_width)
            sample_rate.append(song.sample_rate)
            if song.album:
                albums.add(song.album)
        if len(albums) == 1:
            album = list(albums)[0]
        metadata = Metadata(
            title=f'{self.options.game_id} - {self.options.title}',
            artist='',
            album=album,
            channels=int(statistics.median(channels)),
            sample_rate=int(statistics.median(sample_rate)),
            sample_width=int(statistics.median(sample_width)),
            bitrate=self.options.bitrate,
            duration=Duration(0),
        )
        with self.mp3_editor.create(mp3_name, metadata=metadata,
                                    progress=self.progress) as output:
            tracks = self.append_songs(output, songs)
        # self.save_game_tracks_json(tracks)
        return tracks

    ##lint: disable=too-many-statements
    def append_songs(self, output: MP3FileWriter,
                     songs: List[Song]) -> List[Track]:
        """
        Append all of the songs to the specified output.
        Returns a new song list with the start_time metadata property
        of each song set to their positon in the output.
        """
        sample_rate = output.metadata.sample_rate
        transition = self.mp3_editor.use(Assets.transition(sample_rate))
        if self.options.mode == GameMode.QUIZ:
            countdown = self.mp3_editor.use(Assets.quiz_countdown(sample_rate))
        else:
            countdown = self.mp3_editor.use(Assets.countdown(sample_rate))
        overlap: Optional[Duration] = None
        if self.options.crossfade > 0:
            overlap = Duration(self.options.crossfade)
        if self.options.mode == GameMode.QUIZ:
            start, end = Assets.QUIZ_COUNTDOWN_POSITIONS['1']
            output.append(countdown.clip(start, end))
        else:
            output.append(countdown)
        tracks: List[Track] = []
        num_tracks = len(songs)
        for index, song in enumerate(songs, start=1):
            if self.progress.abort:
                return tracks
            if index > 1:
                output.append(transition, overlap=overlap)
            cur_pos = output.duration
            next_track = self.mp3_editor.use(song)
            if self.options.mode == GameMode.QUIZ:
                try:
                    start, end = Assets.QUIZ_COUNTDOWN_POSITIONS[str(index)]
                    number = countdown.clip(start, end)
                except KeyError:
                    break
                output.append(number)
                output.append(transition)
            output.append(next_track, overlap=overlap)
            tracks.append(
                Track(song=song, prime=PRIME_NUMBERS[index - 1],
                      start_time=int(cur_pos)))
            self.progress.text = f'Adding track {index}/{num_tracks}'
            self.progress.pct = 100.0 * float(index) / float(num_tracks)
        output.append(transition, overlap=overlap)
        if self.options.crossfade > 0:
            # if we need to re-encode the stream anyway, might as well also
            # do loudness normalisation
            output.normalize(1)
        self.progress.text = 'Generating MP3 file'
        self.progress.current_phase = 2
        output.generate()
        if self.progress.abort:
            return tracks
        self.progress.text = 'MP3 Generated, creating track listing PDF'
        self.generate_track_listing(tracks)
        self.progress.text = 'MP3 and Track listing PDF generated'
        self.progress.pct = 100.0
        return tracks

    def select_songs_for_ticket(self, songs: List[Track],
                                card: BingoTicket, num_tracks: int) -> None:
        """select the songs for a bingo ticket ensuring that it is unique"""
        valid_card = False
        picked_indices: Set[int] = set()
        card.tracks = []
        card.fingerprint = 1
        while not valid_card and not self.progress.abort:
            valid_index = False
            index = 0
            while not valid_index:
                index = secrets.randbelow(len(songs))
                valid_index = index not in picked_indices
            card.tracks.append(songs[index])
            card.fingerprint = card.fingerprint * songs[index].prime
            picked_indices.add(index)
            if len(card.tracks) == num_tracks:
                valid_card = True
                if card.fingerprint in self.used_fingerprints:
                    valid_card = False
                    picked_indices = set()
                    card.tracks = []
                    card.fingerprint = 1
                if valid_card:
                    self.used_fingerprints.add(card.fingerprint)

    def should_include_artist(self, track: Track) -> bool:
        """Check if the artist name should be shown"""
        return self.options.include_artist and not re.match(
            r'various\s+artist', track.artist, re.IGNORECASE)

    def render_bingo_ticket(self, filename: str, card: BingoTicket) -> None:
        """
        Convert a Bingo ticket into a PDF file
        """
        doc = DG.Document(
            pagesize=PageSizes.A4,
            title=f'{self.options.game_id} - {self.options.title}',
            topMargin="0.15in",
            rightMargin="0.15in",
            bottomMargin="0.15in",
            leftMargin="0.15in")
        self.render_bingo_ticket_to_document(card, doc)
        self.doc_gen.render(filename, doc, Progress())

    def render_bingo_ticket_to_document(self, card: BingoTicket,
                                        doc: DG.Document) -> None:
        """
        Render a Bingo ticket into the specified Document.
        Each ticket has the Music Bingo logo followed by a
        table.
        """
        doc.append(self.options.palette.logo_image("6.2in"))

        pstyle = self.TEXT_STYLES['ticket-cell']
        ranges: List[Tuple[int, int]] = []
        for row_index in range(self.options.rows):
            ranges.append((row_index * self.options.columns,
                           (1 + row_index) * self.options.columns))
        data: List[DG.TableRow] = []
        for start, end in ranges:
            row: DG.TableRow = []
            for index in range(start, end):
                items: List[DG.Element] = [
                    DG.Paragraph(card.tracks[index].title, pstyle)
                ]
                if self.should_include_artist(card.tracks[index]):
                    items.append(
                        DG.Paragraph(f'<b>{card.tracks[index].artist}</b>',
                                     pstyle))
                if self.options.checkbox:
                    name = f'{card.fingerprint}_{index}'
                    cstyle = self.CHECKBOX_STYLE.replace(
                        f'checkbox{name}',
                        background=card.box_colour_style(len(row), len(data)),
                    )
                    items.append(DG.Checkbox(
                        name=f'ticket_{name}',
                        text=card.tracks[index].title,
                        size=4,
                        borderColour='black',
                        style=cstyle))
                row.append(items)
            data.append(row)

        column_width = Dimension("1.54in")
        if self.options.columns > 5:
            column_width *= 5.0 / float(self.options.columns)
        row_height = Dimension("0.97in")

        tstyle = TableStyle(name='bingo-card',
                            borderColour=Colour('black'),
                            borderWidth=2.0,
                            gridColour=Colour('black'),
                            gridWidth=0.5,
                            verticalAlignment=VerticalAlignment.CENTER)
        col_widths: List[Dimension] = [column_width] * self.options.columns
        row_heights: List[Dimension] = [row_height] * self.options.rows
        table = DG.Table(data, colWidths=col_widths, rowHeights=row_heights,
                         style=tstyle)
        for box_row in range(0, self.options.rows):
            for box_col in range(0, self.options.columns):
                table.style_cells(
                    DG.CellPos(col=box_col, row=box_row),
                    DG.CellPos(col=box_col, row=box_row),
                    background=card.box_colour_style(box_col, box_row))
        doc.append(table)

    def generate_track_listing(self, tracks: List[Track]) -> None:
        """generate a PDF version of the track order in the game"""
        assert len(tracks) > 0
        doc = DG.Document(PageSizes.A4, topMargin="0.25in",
                          bottomMargin="0.25in",
                          leftMargin="0.35in", rightMargin="0.35in",
                          title=f'{self.options.game_id} - {self.options.title}')

        doc.append(self.options.palette.logo_image("6.2in"))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        doc.append(DG.Paragraph(
            f'Track Listing For Game Number: <b>{self.options.game_id}</b>',
            self.TEXT_STYLES['track-heading']))

        doc.append(DG.Paragraph(
            self.options.title,
            self.TEXT_STYLES['track-title']))

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

    def generate_card_results(self, tracks: List[Track],
                              cards: List[BingoTicket]):
        """generate PDF showing when each ticket wins"""
        doc = DG.Document(pagesize=PageSizes.A4,
                          title=f'{self.options.game_id} - {self.options.title}',
                          topMargin="0.25in",
                          bottomMargin="0.25in",
                          rightMargin="0.25in",
                          leftMargin="0.25in")

        doc.append(self.options.palette.logo_image("6.2in"))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        doc.append(DG.Paragraph(
            f'Results For Game Number: <b>{self.options.game_id}</b>',
            self.TEXT_STYLES['results-heading']))
        doc.append(DG.Paragraph(
            self.options.title,
            self.TEXT_STYLES['results-title']))

        pstyle = self.TEXT_STYLES['results-cell']
        heading: DG.TableRow = [
            DG.Paragraph('<b>Ticket Number</b>', pstyle),
            DG.Paragraph('<b>Wins after track</b>', pstyle),
            DG.Paragraph('<b>Start Time</b>', pstyle),
        ]
        data: List[DG.TableRow] = []

        cards = copy.copy(cards)
        cards.sort(key=lambda card: card.number, reverse=False)
        for card in cards:
            win_point = self.get_when_ticket_wins(tracks, card)
            song = tracks[win_point - 1]
            data.append([
                DG.Paragraph(f'{card.number}', pstyle),
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

    def generate_at_point(self, tracks: List[Track], amount: int,
                          from_end: int) -> List[BingoTicket]:
        """generate an 'amount' number of bingo tickets that will win
        at the specified amount from the end
        """
        count = 0
        cards: List[BingoTicket] = []
        while count < amount:
            card = BingoTicket(palette=self.options.palette,
                               columns=self.options.columns)
            self.select_songs_for_ticket(tracks, card,
                                         self.options.songs_per_ticket())
            if self.progress.abort:
                return cards
            win_point = self.get_when_ticket_wins(tracks, card)
            if win_point != (len(tracks) - from_end):
                self.used_fingerprints.remove(card.fingerprint)
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

    def generate_all_cards(self, tracks: List[Track]) -> List[BingoTicket]:
        """generate all the bingo tickets in the game"""
        self.progress.text = 'Calculating cards'
        self.progress.pct = 0.0
        self.used_fingerprints.clear()
        cards: List[BingoTicket] = []
        decay_rate = 0.65
        num_on_last = self.options.number_of_cards * decay_rate
        num_second_last = (self.options.number_of_cards - num_on_last) * decay_rate
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
        good_cards: List[BingoTicket] = []
        for idx in range(0, amount_to_go):
            if self.progress.abort:
                return cards
            self.progress.pct = 100.0 * (float(idx) / float(amount_to_go))
            good_cards += self.generate_at_point(tracks, 1, offset)
            offset += 1
        increment: float = self.options.number_of_cards / float(amount_to_go)
        start_point: float = 0
        random.shuffle(good_cards)
        for card in good_cards:
            if self.progress.abort:
                return cards
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point + increment)))
            rand_point = int(math.ceil(rand_point))
            rand_point = min(rand_point, self.options.number_of_cards - 1)
            cards.insert(rand_point, card)
            start_point += increment
        for idx, card in enumerate(cards, start=1):
            card.number = idx
        if self.options.page_order:
            if self.options.cards_per_page != 1 or not self.options.doc_per_page:
                return self.sort_cards_by_page(cards)
        return cards

    def sort_cards_by_page(self, cards: List[BingoTicket]) -> List[BingoTicket]:
        """sort BingoTickets so that each ascending ticket number is on a
        different page.
        BingoTickets 1 .. n will be on pages 1..n (where n is 1/3 of ticket total)
        BingoTickets n .. 2n will be on pages 1..n
        BingoTickets 2n .. 3n will be on pages 1..n
        """
        noc3c = int(math.ceil(self.options.number_of_cards / 3))
        noc3f = int(math.floor(self.options.number_of_cards / 3))
        first_third = cards[0:noc3c]
        second_third = cards[noc3c: noc3c + noc3f]
        third_third = cards[noc3c + noc3f: len(cards)]
        cards = []
        while len(first_third) > 0:
            cards.append(first_third.pop(0))
            if len(second_third) > 0:
                cards.append(second_third.pop(0))
            if len(third_third) > 0:
                cards.append(third_third.pop(0))
        return cards

    def insert_random_cards(self, tracks: List[Track], cards: List[BingoTicket],
                            point: int, num_cards: int, num_on_last: int) -> None:
        """add cards at a random position in the card list.
        Adds num_cards Bingo Tickets at position "point" from the end of the list
        """
        increment: float = (len(cards) + num_cards) / float(num_cards)
        start_point: float = 0
        for _ in range(0, num_cards):
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point + increment)))
            rand_point = int(math.ceil(rand_point))
            if rand_point >= (num_on_last + num_cards):
                rand_point = num_on_last + num_cards - 1
            cards.insert(
                rand_point,
                self.generate_at_point(tracks, 1, point)[0])
            start_point = start_point + increment

    def generate_tickets_pdf(self, cards: List[BingoTicket]) -> None:
        """generate a PDF file containing all the Bingo tickets"""
        doc: Optional[DG.Document] = None
        page: int = 1
        num_cards: int = len(cards)
        cards_per_page: int = 3
        if self.options.rows == 2:
            cards_per_page = 4
        elif self.options.rows > 3:
            cards_per_page = 2
        if self.options.cards_per_page > 0:
            cards_per_page = self.options.cards_per_page
        id_style = self.TEXT_STYLES['ticket-id']
        title_style = id_style.replace('ticket-title',
                                       alignment=HorizontalAlignment.LEFT)

        for count, card in enumerate(cards, start=1):
            self.progress.text = f'Card {count}/{num_cards}'
            self.progress.pct = 100.0 * float(count) / float(num_cards)
            if doc is None:
                doc = DG.Document(
                    pagesize=PageSizes.A4,
                    title=f'{self.options.game_id} - {self.options.title}',
                    topMargin="0.15in",
                    rightMargin="0.15in",
                    bottomMargin="0.15in",
                    leftMargin="0.15in")
            self.render_bingo_ticket_to_document(card, doc)
            ticket_id = f"{self.options.game_id} / T{card.number} / P{page}"
            if self.options.cards_per_page == 1 and self.options.doc_per_page:
                ticket_id = f"{self.options.game_id} / T{card.number}"
            data: List[DG.TableRow] = [[
                DG.Paragraph(self.options.title, title_style),
                DG.Paragraph(ticket_id, id_style),
            ]]
            tstyle = TableStyle(name='ticket-id',
                                borderWidth=0,
                                gridWidth=0,
                                verticalAlignment=VerticalAlignment.CENTER)
            table = DG.Table(
                data,
                colWidths=[Dimension(80), Dimension(80)],
                rowHeights=[Dimension('16pt')],
                style=tstyle)
            doc.append(table)
            if count % cards_per_page != 0:
                doc.append(
                    DG.HorizontalLine('hline', width="100%", thickness="1px",
                                      colour=Colour('gray'), dash=[2, 2]))
                doc.append(DG.Spacer(width=0, height="0.08in"))
            else:
                if self.options.doc_per_page:
                    filename = str(self.options.bingo_tickets_output_name(page))
                    self.doc_gen.render(filename, doc, Progress())
                    doc = None
                else:
                    doc.append(DG.PageBreak())
                page += 1

        if not self.options.doc_per_page:
            assert doc is not None
            filename = str(self.options.bingo_tickets_output_name())
            self.doc_gen.render(filename, doc, Progress())

    def generate_ticket_tracks_file(self, cards: List[BingoTicket]) -> None:
        """store ticketTracks file used by TicketChecker.py"""
        filename = self.options.ticket_checker_output_name()
        with filename.open('wt') as ttf:
            for card in cards:
                ttf.write(f"{card.number}/{card.fingerprint}\n")

    def gen_track_order(self, songs: Sequence[Song]) -> List[Song]:
        """generate a random order of songs for the game"""
        assert len(songs) > 0
        list_copy = copy.copy(list(songs))
        if not self.options.mode == GameMode.QUIZ:
            random.shuffle(list_copy, self.rand_float)
        return list_copy

    @staticmethod
    def rand_float() -> float:
        """generate a random number using the secrets library"""
        return float(secrets.randbelow(1000)) / 1000.0

    @staticmethod
    def get_when_ticket_wins(tracks: List[Track], ticket: BingoTicket) -> int:
        """get the point at which the given ticket will win, given the
        specified order"""
        last_song = -1
        card_track_ids = {track.ref_id for track in ticket.tracks}

        for count, song in enumerate(tracks, start=1):
            if song.ref_id in card_track_ids:
                last_song = count
                card_track_ids.remove(song.ref_id)
            if not card_track_ids:
                break
        if card_track_ids:
            raise ValueError(f'ticket never wins, missing {card_track_ids}')
        return last_song

    def save_game_info_json(self, game: models.Game, tracks: Iterable[models.Track],
                            cards: Iterable[models.BingoTicket]) -> None:
        """
        Saves the game info to game-{gameID}.json
        """
        db_package = {
            "BingoTickets": [dbc.to_dict(with_collections=True) for dbc in cards],
            "Games": [game.to_dict()],
        }
        db_tracks: List[JsonObject] = []
        for trk in tracks:
            item = trk.song.to_dict(exclude={'uuid'})
            item.update(trk.to_dict())
            db_tracks.append(item)
        db_package["Tracks"] = db_tracks
        # db_package["Games"][0]["options"] = self.options.to_dict(
        #     only=['cards_per_page', 'checkbox', 'colour_scheme', 'columns', 'rows',
        #          'number_of_cards', 'doc_per_page', 'cards_per_page', 'bitrate',
        #          'crossfade', 'include_artist'])
        db_package = flatten(db_package)
        filename = self.options.game_info_output_name()
        with filename.open('w') as jsf:
            json.dump(db_package, jsf, sort_keys=True, indent=2)

    @staticmethod
    def combinations(total: int, select: int) -> int:
        """calculate combinations
        Calculates the number of combinations of selecting 'select' items
        from 'total' items
        """
        if select > total:
            return 0
        return int(math.factorial(total) / (math.factorial(select) *
                                            math.factorial(total - select)))


def main(args: Sequence[str]) -> int:
    """used for testing game generation without needing to use the GUI"""
    # pylint: disable=import-outside-toplevel
    from musicbingo.mp3 import MP3Factory

    options = Options.parse(args)
    assert options.database is not None
    models.db.DatabaseConnection.bind(options.database)
    if options.game_id == '':
        options.game_id = datetime.date.today().strftime("%y-%m-%d")
    progress = TextProgress()
    mp3parser = MP3Factory.create_parser()
    clips = Directory(None, options.clips())
    progress = TextProgress()
    clips.search(mp3parser, progress)
    sys.stdout.write('\n')
    sys.stdout.flush()
    num_songs = options.columns * options.rows * 2
    songs = clips.songs[:num_songs]
    if len(songs) < num_songs:
        for subdir in clips.subdirectories:
            todo = num_songs - len(songs)
            if todo < 1:
                break
            songs += subdir.songs[:todo]
    print('Selected {0} songs'.format(len(songs)))
    sys.stdout.flush()
    if len(songs) == 0:
        print('Error: failed to find any songs')
        return 1
    if options.title == '':
        options.title = Song.choose_collection_title(songs)
    mp3editor = MP3Factory.create_editor(options.mp3_engine)
    pdf = DocumentFactory.create_generator('pdf')
    gen = GameGenerator(options, mp3editor, pdf, progress)
    #pylint: disable=no-value-for-parameter
    gen.generate(songs)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
