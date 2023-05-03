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
import logging
import math
import random
import re
import secrets
import statistics
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, cast

from . import models
from .models.db import db_session
from .models.modelmixin import JsonObject
from .assets import Assets
from .bingoticket import BingoTicket
from .directory import Directory
from .docgen import documentgenerator as DG
from .docgen.colour import Colour
from .docgen.factory import DocumentFactory
from .docgen.sizes.dimension import Dimension
from .docgen.sizes.pagesize import PageSizeInterface, PageSizes
from .docgen.styles import (
    HorizontalAlignment, VerticalAlignment,
    ElementStyle, RowStyle, TableStyle, Padding)
from .duration import Duration
from .mp3.editor import MP3Editor, MP3FileWriter
from .options import GameMode, Options, PageSortOrder
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
        'track-cell': RowStyle(
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
        'results-cell': RowStyle(
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

    MIN_GENERATED_CARDS: int = 16  # min number of cards required by generator
    MIN_SONGS: int = 17  # 17 songs allows 136 combinations
    MAX_SONGS: int = len(PRIME_NUMBERS)
    DECAY_RATE: float = 0.65

    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 doc_gen: DG.DocumentGenerator,
                 progress: Progress) -> None:
        self.options = options
        self.mp3_editor = mp3_editor
        self.doc_gen = doc_gen
        self.progress = progress
        #self.game_songs: List[Song] = []
        self.used_fingerprints: Set[int] = set()
        self.log = logging.getLogger('generator')

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
            'cards_per_page', 'checkbox', 'columns', 'rows',
            'number_of_cards', 'doc_per_page', 'bitrate',
            'crossfade', 'include_artist'})
        opts['colour_scheme'] = self.options.colour_scheme.name.lower()
        opts['page_size'] = self.options.page_size.name.lower()
        game = cast(Optional[models.Game], models.Game.get(session, id=self.options.game_id))
        if game is None:
            game = models.Game(id=self.options.game_id,
                               title=self.options.title,
                               start=datetime.datetime.now(),
                               end=(datetime.datetime.now() + datetime.timedelta(days=100)),
                               options=opts)
            session.add(game)
        else:
            game.set(title=self.options.title,
                     start=datetime.datetime.now(),
                     end=(datetime.datetime.now() + datetime.timedelta(days=100)),
                     options=opts)
            # Clear out any old BingoTickets for this game, as they
            # will have been re-generated and the old ones are no
            # longer valid
            models.BingoTicket.delete_items(session, game=game)
            # Clear out any old tracks for this game, as the
            # track order will have changed when it was re-generated
            #session.execute(delete(models.Track).where(models.Track.game_pk=game.pk)
            models.Track.delete_items(session, game=game)
        if self.options.mode == GameMode.BINGO:
            self.progress.num_phases = 4
        else:
            self.progress.num_phases = 2
        self.progress.current_phase = 0
        tracks = self.generate_mp3(songs)
        if self.progress.abort:
            return
        self.progress.current_phase = 1
        db_tracks: List[models.Track] = []
        for track in tracks:
            song = track.song.model(session)
            assert song is not None
            db_tracks.append(track.save(game=game, song=song, session=session))
        session.flush()
        db_cards: List[models.BingoTicket] = []
        if self.options.mode != GameMode.BINGO:
            return
        self.progress.current_phase = 2
        cards = self.generate_all_cards(tracks)
        if self.progress.abort:
            return
        for card in cards:
            db_cards.append(card.save(game=game, session=session))
        self.progress.current_phase = 3
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
        if options.cards_per_page < 1 or options.cards_per_page > 6:
            raise ValueError(f'cards_per_page={options.cards_per_page}. ' +
                             'Must be between 1 and 6')
        min_songs = int(round(1.5 * options.songs_per_ticket() + 0.5))
        if num_songs < min_songs:
            raise ValueError(f'At least {min_songs} songs are required')
        if num_songs > cls.MAX_SONGS:
            raise ValueError(f'Maximum number of songs is {cls.MAX_SONGS}')
        if options.number_of_cards < Options.MIN_CARDS:
            raise ValueError(f'At least {Options.MIN_CARDS} tickets are required')
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
        return tracks

    # pylint: disable=too-many-statements
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
        if self.options.mode == GameMode.BINGO:
            output.append(countdown)
        tracks: List[Track] = []
        num_tracks = len(songs)
        for index, song in enumerate(songs, start=1):
            self.log.debug(r'song[%d] = %s', index, song)
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
                except KeyError as err:
                    self.log.error(r'%s', err)
                    print(err)
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
        self.progress.current_phase += 1
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

    def should_include_artist(self, track: Track) -> bool:
        """Check if the artist name should be shown"""
        return self.options.include_artist and not re.match(
            r'various\s+artist', track.artist, re.IGNORECASE)

    def render_bingo_ticket(self, filename: str, card: BingoTicket) -> None:
        """
        Convert a Bingo ticket into a PDF file
        """
        doc = DG.Document(
            pagesize=self.options.page_size,
            title=f'{self.options.game_id} - {self.options.title}',
            topMargin="0.15in",
            rightMargin="0.15in",
            bottomMargin="0.15in",
            leftMargin="0.15in")
        self.render_bingo_ticket_to_container(card, doc, False)
        self.doc_gen.render(filename, doc, Progress(), debug=self.options.debug)

    # pylint: disable=too-many-locals, too-many-branches
    def render_bingo_ticket_to_container(self, card: BingoTicket,
                                         dest: DG.Container, add_footer: bool,
                                         scale: float = 1.0) -> None:
        """
        Render a Bingo ticket into the specified Document.
        Each ticket has the Music Bingo logo followed by a
        table. If add_footer is True, the ticket number
        and game title is added as a table footer
        """
        logo = self.options.palette.logo_image(dest.width * 0.75, card.number)
        dest.append(logo)

        pstyle = self.TEXT_STYLES['ticket-cell'].scale(scale)
        id_style = self.TEXT_STYLES['ticket-id'].scale(scale)
        title_style = id_style.replace(
            'ticket-title', alignment=HorizontalAlignment.LEFT)

        ranges: List[Tuple[int, int]] = []
        for row_index in range(self.options.rows):
            ranges.append((row_index * self.options.columns,
                           (1 + row_index) * self.options.columns))

        data: List[DG.TableRow] = []
        for start, end in ranges:
            row = DG.TableRow([])
            for index in range(start, end):
                items: List[DG.TableCell] = [
                    DG.Paragraph(f'<b>{card.tracks[index].title}</b>',
                                 pstyle)
                ]
                if self.should_include_artist(card.tracks[index]):
                    items.append(
                        DG.Paragraph(card.tracks[index].artist, pstyle))
                if self.options.checkbox:
                    name = f'{card.fingerprint}_{index}'
                    cstyle = self.CHECKBOX_STYLE.replace(
                        f'checkbox{name}',
                        background=card.box_colour_style(len(row), len(data)),
                    ).scale(scale)
                    items.append(DG.Checkbox(
                        name=f'ticket_{name}',
                        text=card.tracks[index].title,
                        size=4,
                        borderColour='black',
                        style=cstyle))
                row.append(items)
            data.append(row)

        column_width = dest.width * 0.95 / float(self.options.columns)
        if self.options.columns > 5:
            column_width *= 5.0 / float(self.options.columns)
        row_height = dest.height - logo.height
        if add_footer:
            row_height -= Dimension(f'{title_style.font_size}pt') + Dimension('6pt')
        row_height = row_height // self.options.rows
        if self.options.debug:
            self.log.debug(r'table cell size: %s %s %s %s',
                           f'{column_width.value} {row_height.value}',
                           f'{column_width.value * self.options.columns}',
                           f'{row_height.value * self.options.rows}',
                           f'{dest.width.value} {dest.height.value}')

        tstyle = TableStyle(name='bingo-card',
                            borderColour=Colour('black'),
                            borderWidth=(2.0 * scale),
                            gridColour=Colour('black'),
                            gridWidth=(0.5 * scale),
                            verticalAlignment=VerticalAlignment.MIDDLE)
        footer: Optional[DG.TableRow] = None
        col_widths: List[Dimension] = [column_width] * self.options.columns
        row_heights: List[Dimension] = [row_height] * self.options.rows
        if add_footer:
            colspans: List[int] = [self.options.columns // 2]
            colspans.append(self.options.columns - colspans[0])
            tstyle.footer_style = RowStyle(name="footer", colspans=colspans)
            ticket_id = f"{self.options.game_id} / T{card.number}"
            footer = DG.TableRow([DG.Paragraph(self.options.title, title_style)])
            for _ in range(colspans[0] - 1):
                footer.append(DG.Paragraph('', title_style))
            footer.append(DG.Paragraph(ticket_id, id_style))
            for _ in range(colspans[1] - 1):
                footer.append(DG.Paragraph('', id_style))
            row_heights.append(Dimension(f'{title_style.font_size + 6}pt'))
        table = DG.Table(data, colWidths=col_widths, rowHeights=row_heights,
                         style=tstyle, footer=footer)
        for box_row in range(0, self.options.rows):
            for box_col in range(0, self.options.columns):
                table.style_cells(
                    DG.CellPos(col=box_col, row=box_row),
                    DG.CellPos(col=box_col, row=box_row),
                    background=card.box_colour_style(box_col, box_row))
        dest.append(table)

    def generate_track_listing(self, tracks: List[Track]) -> None:
        """generate a PDF version of the track order in the game"""
        assert len(tracks) > 0
        assert isinstance(self.options.page_size, PageSizes)
        doc = DG.Document(self.options.page_size,
                          topMargin="0.25in",
                          bottomMargin="0.25in",
                          leftMargin="0.35in",
                          rightMargin="0.35in",
                          title=f'{self.options.game_id} - {self.options.title}')

        scale = self.calculate_text_scale(doc, 1)
        doc.append(self.options.palette.logo_image(Dimension("6.2in") * scale, 1))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        doc.append(DG.Paragraph(
            f'Track Listing For Game Number: <b>{self.options.game_id}</b>',
            self.TEXT_STYLES['track-heading'].scale(scale)))

        doc.append(DG.Paragraph(
            self.options.title,
            self.TEXT_STYLES['track-title'].scale(scale)))

        cell_style = self.TEXT_STYLES['track-cell'].scale(scale)
        heading = DG.TableRow([
            DG.Paragraph('<b>Order</b>', cell_style),
            DG.Paragraph('<b>Title</b>', cell_style),
            DG.Paragraph('<b>Artist</b>', cell_style),
            DG.Paragraph('<b>Start Time</b>', cell_style),
        ])

        data: List[DG.TableRow] = []

        for index, song in enumerate(tracks, start=1):
            order = DG.Paragraph(f'<b>{index}</b>', cell_style)
            title = DG.Paragraph(song.title, cell_style)
            if self.should_include_artist(song):
                artist = DG.Paragraph(song.artist, cell_style)
            else:
                artist = DG.Paragraph('', cell_style)
            start = DG.Paragraph(Duration(song.start_time).format(), cell_style)
            data.append(DG.TableRow([order, title, artist, start]))

        col_widths: List[Dimension] = [
            Dimension("0.55in") * scale,
            Dimension("3.35in") * scale,
            Dimension("2.75in") * scale,
            Dimension("0.8in") * scale,
        ]

        hstyle = cast(RowStyle, cell_style.replace(
            name='track-table-heading',
            background=self.options.palette.title_bg))
        tstyle = TableStyle(
            name='track-table',
            borderColour=Colour('black'),
            borderWidth=1.0,
            gridColour=Colour('black'),
            gridWidth=0.5,
            verticalAlignment=VerticalAlignment.MIDDLE,
            headingStyle=hstyle)
        table = DG.Table(data, heading=heading, repeat_heading=True,
                         colWidths=col_widths, style=tstyle)
        doc.append(table)
        filename = str(self.options.track_listing_output_name())
        self.doc_gen.render(filename, doc, Progress(), debug=self.options.debug)

    def generate_card_results(self, tracks: List[Track],
                              cards: List[BingoTicket]):
        """generate PDF showing when each ticket wins"""
        doc = DG.Document(pagesize=self.options.page_size,
                          title=f'{self.options.game_id} - {self.options.title}',
                          topMargin="0.25in",
                          bottomMargin="0.25in",
                          rightMargin="0.25in",
                          leftMargin="0.25in")

        scale = self.calculate_text_scale(doc, 1)
        doc.append(self.options.palette.logo_image(Dimension("6.2in") * scale, 2))
        doc.append(DG.Spacer(width=0, height="0.05in"))

        doc.append(DG.Paragraph(
            f'Results For Game Number: <b>{self.options.game_id}</b>',
            self.TEXT_STYLES['results-heading'].scale(scale)))
        doc.append(DG.Paragraph(
            self.options.title,
            self.TEXT_STYLES['results-title'].scale(scale)))

        pstyle = self.TEXT_STYLES['results-cell'].scale(scale)
        heading = DG.TableRow([
            DG.Paragraph('<b>Ticket</b>', pstyle),
            DG.Paragraph('<b>Wins on or after track</b>', pstyle),
            DG.Paragraph('<b>Time</b>', pstyle),
        ])
        for row_num in range(self.options.rows):
            heading.append(DG.Paragraph(f'<b>Row {row_num + 1}</b>', pstyle))

        data: List[DG.TableRow] = []
        cards = copy.copy(cards)
        cards.sort(key=lambda card: card.number, reverse=False) # type: ignore
        for card in cards:
            song = tracks[card.wins_on_track - 1]
            row = DG.TableRow([
                DG.Paragraph(f'{card.number}', pstyle),
                DG.Paragraph(
                    f'Track {card.wins_on_track} - {song.title}', pstyle),
                DG.Paragraph(Duration(song.start_time).format(), pstyle),
            ])
            for num in card.rows_complete_on_track:
                row.append(DG.Paragraph(f'{num}', pstyle))
            data.append(row)

        title_width = 5.5 - 0.6 * self.options.rows
        col_widths: List[Dimension] = [
            Dimension("0.7in") * scale,
            Dimension(f"{title_width}in") * scale,
            Dimension("0.75in") * scale,
        ]
        col_widths += [Dimension("0.6in") * scale] * self.options.rows
        hstyle = cast(RowStyle, pstyle.replace(
            name='results-table-heading',
            background=self.options.palette.title_bg))
        tstyle = TableStyle(name='results-table',
                            borderColour=Colour('black'),
                            borderWidth=1.0,
                            gridColour=Colour('black'),
                            gridWidth=0.5,
                            verticalAlignment=VerticalAlignment.MIDDLE,
                            headingStyle=hstyle)
        table = DG.Table(data, heading=heading, repeat_heading=True,
                         colWidths=col_widths, style=tstyle)
        doc.append(table)
        filename = str(self.options.ticket_results_output_name())
        self.doc_gen.render(filename, doc, Progress(), debug=self.options.debug)

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
            if win_point == (len(tracks) - from_end):
                self.used_fingerprints.add(card.fingerprint)
                card.wins_on_track = win_point
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
        number_of_cards = max(self.options.number_of_cards, self.MIN_GENERATED_CARDS)
        num_on_last = number_of_cards * self.DECAY_RATE
        num_second_last = (number_of_cards - num_on_last) * self.DECAY_RATE
        num_third_last = (number_of_cards - num_on_last -
                          num_second_last) * self.DECAY_RATE
        num_fourth_last = ((number_of_cards - num_on_last -
                            num_second_last - num_third_last) *
                           self.DECAY_RATE)
        num_on_last = int(num_on_last)
        num_second_last = int(num_second_last)
        num_third_last = int(num_third_last)
        num_fourth_last = max(int(num_fourth_last), 1)
        amount_left = (number_of_cards - num_on_last -
                       num_second_last - num_third_last -
                       num_fourth_last)
        # number of "good" tickets that win before the last track
        amount_to_go = 4
        # offset from end of tracks when last "good" ticket wins
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
        good_cards = self.generate_winning_cards(tracks, amount_to_go, offset)
        increment: float = self.options.number_of_cards / float(amount_to_go)
        start_point: float = 0
        random.shuffle(good_cards)
        for card in good_cards:
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point + increment)))
            rand_point = int(math.ceil(rand_point))
            rand_point = min(rand_point, self.options.number_of_cards - 1)
            cards.insert(rand_point, card)
            start_point += increment
        if self.progress.abort:
            return cards
        while len(cards) > self.options.number_of_cards:
            worst_end: int = -1
            worst_index: int = 0
            for idx, card in enumerate(cards):
                #win_point = self.get_when_ticket_wins(tracks, card)
                if card.wins_on_track > worst_end:
                    worst_index = idx
                    worst_end = card.wins_on_track
            cards.pop(worst_index)
        for idx, card in enumerate(cards, start=1):
            card.number = idx
            card.compute_win_values(tracks)
        if self.options.cards_per_page != 1 or not self.options.doc_per_page:
            return self.sort_cards_by_page(cards)
        return cards

    def generate_winning_cards(self, tracks: List[Track], amount_to_go: int,
                               offset: int) -> List[BingoTicket]:
        """
        Create list of winning tickets
        """
        good_cards: List[BingoTicket] = []
        for idx in range(0, amount_to_go):
            self.progress.pct = 100.0 * (float(idx) / float(amount_to_go))
            good_cards += self.generate_at_point(tracks, 1, offset)
            offset += 1
        return good_cards

    def sort_cards_by_page(self, cards: List[BingoTicket]) -> List[BingoTicket]:
        """
        sort BingoTickets so that each ascending ticket number is on a
        different page.
        If sort_order == INTERLEAVE:
          BingoTickets 1 .. n will be on pages 1..n (where n is 1/3 of ticket total)
          BingoTickets n .. 2n will be on pages 1..n
          BingoTickets 2n .. 3n will be on pages 1..n
        """
        if self.options.sort_order == PageSortOrder.WINNER:
            cards.sort(key=lambda x: x.wins_on_track, reverse=False)  # type: ignore
            return cards
        if self.options.sort_order == PageSortOrder.NUMBER:
            cards.sort(key=lambda x: x.number, reverse=False)  # type: ignore
            return cards
        # PageSortOrder == INTERLEAVE
        buckets: Dict[int, List[BingoTicket]] = {}
        result = []
        flush_at = pow(self.options.cards_per_page, 2)
        for index, card in enumerate(cards):
            if (index % flush_at) == 0:
                for val in buckets.values():
                    result += val
                buckets = {}
            bkt = index % self.options.cards_per_page
            try:
                buckets[bkt].append(card)
            except KeyError:
                buckets[bkt] = [card]
        for val in buckets.values():
            result += val
        return result

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
        id_style = self.TEXT_STYLES['ticket-id']
        title_style = id_style.replace('ticket-title',
                                       alignment=HorizontalAlignment.CENTER)
        if self.options.debug:
            self.log.debug(r'cards_per_page=%d page_size=%s %fmm %fmm',
                  self.options.cards_per_page,
                  self.options.page_size, self.options.page_size.width().value,
                  self.options.page_size.height().value)
        page_size = cast(PageSizeInterface, self.options.page_size)
        if self.options.cards_per_page > 3:
            page_size = page_size.landscape()
        scale: float = 1.0
        for count, card in enumerate(cards, start=1):
            self.progress.text = f'Card {count}/{num_cards}'
            self.progress.pct = 100.0 * float(count) / float(num_cards)
            if doc is None:
                doc = DG.Document(
                    pagesize=page_size,
                    title=f'{self.options.game_id} - {self.options.title}',
                    topMargin="0.15in",
                    rightMargin="0.15in",
                    bottomMargin="0.15in",
                    leftMargin="0.15in")
            index0 = count - 1
            top, left, ticket_width, ticket_height = self.calculate_ticket_frame(
                index0, doc, self.options.cards_per_page)
            scale = self.calculate_text_scale(doc, self.options.cards_per_page)
            id_style = id_style.scale(scale)
            title_style = title_style.scale(scale)
            top += doc.top_margin
            left += doc.left_margin
            self.log.debug(r'frame[%d] id="t%s" top=%fmm left=%fmm width=%fmm height=%fmm',
                           count, card.number, top.value, left.value, ticket_width.value,
                           ticket_height.value)
            frame = DG.Container(cid=f't{card.number}', top=top, left=left,
                                 width=ticket_width, height=ticket_height)
            self.render_bingo_ticket_to_container(card, frame, True, scale=scale)
            doc.append(frame)
            if count % self.options.cards_per_page == 0:
                if self.options.doc_per_page:
                    filename = str(self.options.bingo_tickets_output_name(page))
                    self.doc_gen.render(filename, doc, Progress(), debug=self.options.debug)
                    doc = None
                else:
                    self.add_cut_here_lines(doc, self.options.cards_per_page)
                    doc.append(DG.PageBreak())
                page += 1

        if not self.options.doc_per_page:
            assert doc is not None
            filename = str(self.options.bingo_tickets_output_name())
            self.doc_gen.render(filename, doc, Progress(), debug=self.options.debug)

    def calculate_ticket_frame(self, index0: int, doc: DG.Document, cards_per_page: int):
        """
        Calculate the size and position of the container to hold the bingo ticket
        """
        if cards_per_page < 4:
            ticket_width = doc.available_width()
            ticket_height = doc.available_height() * 0.925 / max(2.3, cards_per_page)
            left = (doc.available_width() - ticket_width) // 2
            vmargin = (doc.available_height() - ticket_height * cards_per_page) // cards_per_page
            top = (ticket_height + vmargin) * int(index0 % cards_per_page)
            top += vmargin / 2.0
        else:
            ticket_rows = cards_per_page // 2
            ticket_width = doc.available_width() / 2.1
            if cards_per_page == 4:
                ticket_height = doc.available_height() * 0.9 / ticket_rows
            else:
                ticket_height = doc.available_height() * 0.925 / ticket_rows
            vmargin = (doc.available_height() - ticket_height * ticket_rows) // ticket_rows
            hmargin = (doc.available_width() - (ticket_width * 2)) // 2
            top = (ticket_height + vmargin) * ((index0 % cards_per_page) // 2)
            top += vmargin / 2.0
            left = (ticket_width + hmargin) * (index0 % 2) + hmargin / 2.0
            vspare = doc.available_height() - ((ticket_height + vmargin) * ticket_rows)
            top += vspare / 2.0
            hspare = doc.available_width() - ((ticket_width + hmargin) * 2.0)
            left += hspare / 2.0
        return (top, left, ticket_width, ticket_height)

    def calculate_text_scale(self, doc: DG.Document, cards_per_page: int) -> float:
        """
        Calcuate a scale factor to apply to all font sizes.
        Font sizes are defined based upon an A4 page size. When using other
        page sizes, the font sizes might need to be scaled.
        """
        scale = 1.0
        if cards_per_page == 4:
            scale = 3.4 / float(cards_per_page)
        elif cards_per_page > 4:
            scale = 3.7 / float(cards_per_page)
        if self.options.page_size != PageSizes.A4:
            ratio = doc.width / PageSizes.A4.width()
            if ratio.value <= 0.9:
                scale *= 1.05 * ratio.value
            elif ratio.value > 1.1:
                scale *= 0.875 * ratio.value
        self.log.debug(r'font_scale=%f', scale)
        return scale

    def add_cut_here_lines(self, doc: DG.Document, cards_per_page: int) -> None:
        """
        Add dashed lines to a page to indicate where to cut
        """
        # pylint: disable=invalid-name
        def add_line(name, x1, y1, x2, y2):
            doc.append(DG.OverlayLine(
                name, x1=x1, y1=y1, x2=x2, y2=y2,
                thickness="1px", colour=Colour('gray'), dash=[2, 2]))

        if cards_per_page in {2, 4}:
            pos = doc.height / 2.0
            add_line('hline', x1=doc.left_margin, y1=pos,
                     x2=(doc.width - doc.right_margin), y2=pos)
        if cards_per_page in {3, 6}:
            pos = doc.height / 3.0
            add_line('hline1', x1=doc.left_margin, y1=pos,
                     x2=(doc.width - doc.right_margin), y2=pos)
            pos *= 2.0
            add_line('hline2', x1=doc.left_margin, y1=pos,
                     x2=(doc.width - doc.right_margin), y2=pos)
        if cards_per_page > 3:
            pos = doc.width / 2
            add_line('vline', x1=pos, y1=doc.top_margin,
                     x2=pos, y2=(doc.height - doc.bottom_margin))

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
            random.shuffle(list_copy)
        return list_copy

    def get_when_ticket_wins(self, tracks: List[Track], ticket: BingoTicket) -> int:
        """
        get the point at which the given ticket will win, given the
        specified order
        """
        fingerprint: int = 1
        for count, track in enumerate(tracks, start=1):
            fingerprint *= track.prime
            if (fingerprint % ticket.fingerprint) == 0:
                self.log.debug('ticket %d wins at %d', ticket.number, count)
                return count
        raise ValueError(f'ticket {ticket.number} never wins')

    def save_game_info_json(self, game: models.Game, tracks: Iterable[models.Track],
                            cards: Iterable[models.BingoTicket]) -> None:
        """
        Saves the game info to game-{gameID}.json
        """
        db_package = {
            "BingoTickets": [dbc.to_dict(with_collections=True) for dbc in cards],
            "Games": [game.to_dict()],
        }
        db_dirs: Dict[int, models.Directory] = {}
        db_songs: List[JsonObject] = []
        db_tracks: List[JsonObject] = []
        for trk in tracks:
            db_dirs[trk.song.directory.pk] = trk.song.directory
            song = trk.song.to_dict(exclude={'artist', 'album'})
            song['album'] = trk.song.album.name if trk.song.album is not None else ''
            song['artist'] = trk.song.artist.name if trk.song.artist is not None else ''
            db_songs.append(song)
            db_tracks.append(trk.to_dict())
        for song_dir in list(db_dirs.values()):
            dbd = song_dir.parent
            while dbd is not None:
                db_dirs[dbd.pk] = dbd
                dbd = dbd.parent
        db_package["Directories"] = [item.to_dict() for item in db_dirs.values()]
        db_package["Songs"] = db_songs
        db_package["Tracks"] = db_tracks
        filename = self.options.game_info_output_name()
        with filename.open('wt', encoding='utf-8') as jsf:
            json.dump(db_package, jsf, sort_keys=True, indent=2, default=flatten)

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
    log_format = r"%(asctime)-15s:%(levelname)s:%(filename)s@%(lineno)d: %(message)s"
    logging.basicConfig(format=log_format)
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("pdfgen").setLevel(logging.DEBUG)
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
    print(f'Selected {len(songs)} songs')
    sys.stdout.flush()
    if len(songs) == 0:
        print('Error: failed to find any songs')
        return 1
    if options.title == '':
        options.title = Song.choose_collection_title(songs)
    mp3editor = MP3Factory.create_editor(options.mp3_editor)
    pdf = DocumentFactory.create_generator('pdf')
    gen = GameGenerator(options, mp3editor, pdf, progress)
    #pylint: disable=no-value-for-parameter
    gen.generate(songs)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
