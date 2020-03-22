"""
Container for options used by both Bingo Game and clip generation
"""
from __future__ import print_function
import argparse
from enum import IntEnum, auto
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from musicbingo.palette import Palette

class GameMode(IntEnum):
    """Enumeration of game operating modes"""
    BINGO = auto()
    QUIZ = auto()
    CLIP = auto()

class Options(argparse.Namespace):
    """Options used by GameGenerator"""
    #pylint: disable=too-many-locals
    def __init__(self,
                 games_dest: str = "Bingo Games",
                 game_name_template: str = r'Game-{game_id}',
                 game_tracks_filename: str = "gameTracks.json",
                 game_id: str = "",
                 title: str = "",
                 clip_directory: str = 'Clips',
                 new_clips_dest: str = 'NewClips',
                 clip_start: str = "01:00",
                 clip_duration: int = 30,
                 colour_scheme: str = 'blue',
                 number_of_cards: int = 24,
                 include_artist: bool = True,
                 mode: GameMode = GameMode.BINGO,
                 create_index: bool = False,
                 page_order: bool = True,
                 columns: int = 5,
                 rows: int = 3,
                 bitrate: int = 256,
                 crossfade: int = 500,
                 mp3_engine: str = 'ffmpeg',
                 checkbox: bool = False,
                 cards_per_page: int = 0,
                 doc_per_page: bool = False,
                 ) -> None:
        super(Options, self).__init__()
        self.games_dest = games_dest
        self.game_name_template = game_name_template
        self.game_tracks_filename = game_tracks_filename
        self.game_id = game_id
        self.title = title
        self.clip_directory = clip_directory
        self.new_clips_dest = new_clips_dest
        self.clip_start = clip_start
        self.clip_duration = clip_duration
        self.colour_scheme = colour_scheme
        self.number_of_cards = number_of_cards
        self.include_artist = include_artist
        self.mode = mode
        self.create_index = create_index
        self.page_order = page_order
        self.columns = columns
        self.rows = rows
        self.bitrate = bitrate
        self.crossfade = crossfade
        self.mp3_engine = mp3_engine
        self.checkbox = checkbox
        self.cards_per_page = cards_per_page
        self.doc_per_page = doc_per_page

    def get_palette(self) -> Palette:
        """Return Palete for chosen colour scheme"""
        return Palette[self.colour_scheme.upper()]

    def set_palette(self, palette: Palette) -> None:
        """Set the colour palette name"""
        self.colour_scheme = palette.name.lower()

    palette = property(get_palette, set_palette)

    def clips(self) -> Path:
        """Return directory containing song clips"""
        # simple case - path is already absolute
        clip_dir = Path(self.clip_directory)
        if clip_dir.is_absolute():
            return clip_dir
        # try relative to current working directory
        filename = Path.cwd() / clip_dir
        if filename.exists():
            return filename
        # try relative to the top level of the source code
        basedir = Path(__file__).parents[1]
        return basedir / clip_dir

    def game_destination_dir(self, game_id: Optional[str] = None) -> Path:
        """Output directory for a Bingo game"""
        games_dest = Path(self.games_dest)
        if not games_dest.is_absolute():
            games_dest = Path.cwd() / games_dest
        if game_id is None:
            game_id = self.game_id
        dirname = self.game_name_template.format(game_id=game_id)
        return games_dest / dirname

    def mp3_output_name(self) -> Path:
        """Filename of MP3 file when generating a game"""
        filename = f'{self.game_id} Game Audio.mp3'
        return self.game_destination_dir() / filename

    def bingo_tickets_output_name(self, page: int = 0) -> Path:
        """Filename of document containing all Bingo tickets in a game"""
        if self.doc_per_page:
            if self.cards_per_page == 1:
                filename = f'{self.game_id} Bingo Ticket {page}.pdf'
            else:
                filename = (f'{self.game_id} Bingo Tickets - ' +
                            f'({self.number_of_cards} Tickets) page {page}.pdf')
        else:
            filename = (f'{self.game_id} Bingo Tickets - ' +
                        f'({self.number_of_cards} Tickets).pdf')
        return self.game_destination_dir() / filename

    def game_info_output_name(self) -> Path:
        """
        Filename of JSON file containing information about a generated game
        """
        filename = self.game_tracks_filename.format(game_id=self.game_id)
        return self.game_destination_dir() / filename

    def track_listing_output_name(self) -> Path:
        """Filename of document listing tracks in a game"""
        filename = f'{self.game_id} Track Listing.pdf'
        return self.game_destination_dir() / filename

    def ticket_results_output_name(self) -> Path:
        """Filename of document listing when each ticket in a game wins"""
        filename = f'{self.game_id} Ticket Results.pdf'
        return self.game_destination_dir() / filename

    def ticket_checker_output_name(self) -> Path:
        """Filename of file used by TicketChecker.py"""
        filename = "ticketTracks"
        return self.game_destination_dir() / filename

    def clip_destination_dir(self, album: str) -> Path:
        """Output directory when generating clips"""
        clips_dest = Path(self.new_clips_dest)
        if not clips_dest.is_absolute():
            clips_dest = Path.cwd() / clips_dest
        return clips_dest / album

    def songs_per_ticket(self) -> int:
        """number of songs on each Bingo ticket"""
        return self.columns * self.rows

    @classmethod
    def parse(cls, args: Sequence[str]) -> "Options":
        """parse command line into an Options object"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--games", dest="games_dest", nargs='?',
            help="Destination directory for Bingo Games [%(default)s]")
        parser.add_argument(
            "--game_name_template", nargs='?',
            help="Template for Bingo Game directory [%(default)s]")
        parser.add_argument(
            "--game_tracks_filename", nargs='?',
            help="Filename to store track listing of a game [%(default)s]")
        parser.add_argument(
            "--id", dest="game_id", nargs='?',
            help="ID to assign to the Bingo game [%(default)s]")
        parser.add_argument(
            "--title", dest="title", nargs='?',
            help="Title for the Bingo game [%(default)s]")
        parser.add_argument(
            "--new_clips", dest="new_clips_dest", nargs='?',
            help="Directory to store new song clips [%(default)s]")
        parser.add_argument(
            "--colour_scheme",
            choices=list(map(str.lower, Palette.colour_names())),
            help="Colour scheme to use for Bingo tickets [%(default)s]")
        parser.add_argument(
            "--cards", dest="number_of_cards", type=int,
            help="Quantity of Bingo tickets to create [%(default)d]")
        parser.add_argument(
            "--cards-per-page", dest="cards_per_page", type=int,
            help="Quantity of Bingo tickets to fit on each page [%(default)d] (0=auto)")
        parser.add_argument(
            "--checkbox", action="store_true",
            help="Add a checkbox to each cell")
        parser.add_argument(
            "--doc-per-page", dest="doc_per_page", action="store_true",
            help="Create each page as its own PDF document")
        parser.add_argument(
            "--no-artist", dest="include_artist", action="store_false",
            help="Exclude artist names from Bingo tickets [%(default)s]")
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument(
            "--bingo", dest="mode", action="store_const",
            const=GameMode.BINGO,
            help="Start in Bingo generation mode")
        modes.add_argument(
            "--clip", dest="mode", action="store_const",
            const=GameMode.CLIP,
            help="Start in clip generation mode")
        modes.add_argument(
            "--quiz", dest="mode", action="store_const",
            const=GameMode.QUIZ,
            help="Start in music quiz generation mode")
        parser.add_argument(
            "--create_index", action="store_true",
            help="Create an index of all songs")
        parser.add_argument(
            "--ticket-order", dest="page_order", action="store_false",
            help="Sort Bingo tickets in output by ticket number [%(default)s]")
        parser.add_argument(
            "--rows", type=int, choices=[2, 3, 4, 5],
            help="Number of rows for each Bingo ticket create [%(default)d]")
        parser.add_argument(
            "--columns", type=int, choices=[2, 3, 4, 5, 6, 7],
            help="Number of columns for each Bingo ticket create [%(default)d]")
        parser.add_argument(
            "--bitrate", type=int,
            help="Audio bitrate (in Kbps) [%(default)d]")
        parser.add_argument(
            "--crossfade", type=int,
            help="Set duration of cross fade between songs (in milliseconds). 0 = no crossfade")
        parser.add_argument(
            "clip_directory", nargs='?',
            help="Directory to search for Songs [%(default)s]")
        parser.add_argument(
            "--mp3-engine", dest="mp3_engine", nargs='?',
            help="MP3 engine to use when creating MP3 files [%(default)s]")
        result = Options()
        parser.set_defaults(**result._asdict())
        parser.parse_args(args, namespace=result) # type: ignore
        return result

    def _asdict(self) -> Dict[str, Any]:
        """convert Options to a dictionary"""
        retval = {
        }
        for key, value in self.__dict__.items():
            if value is None:
                continue
            retval[key] = value
        return retval
