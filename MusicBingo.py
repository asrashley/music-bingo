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
import hashlib
import copy
import csv
import datetime
import io
import json
import math
import os
import random
import re
import secrets
import stat
import sys
import threading
import traceback
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set
from typing import Tuple, Union
import tkinter as tk # pylint: disable=import-error
import tkinter.messagebox # pylint: disable=import-error
import tkinter.constants # pylint: disable=import-error
import tkinter.filedialog # pylint: disable=import-error
import tkinter.ttk # pylint: disable=import-error

from mutagen.easyid3 import EasyID3 # type: ignore
#from mutagen.mp3 import MP3

from pydub import AudioSegment # type: ignore

from reportlab.lib.colors import Color, HexColor # type: ignore
from reportlab.lib import colors # type: ignore
from reportlab.lib.styles import ParagraphStyle # type: ignore
from reportlab.lib.pagesizes import A4, inch # type: ignore
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate # type: ignore
from reportlab.platypus import Table, Spacer, PageBreak # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_RIGHT # type: ignore

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

def parse_time(time_str: str) -> int:
    """Convert MM:SS form to milliseconds"""
    parts = time_str.split(':')
    parts.reverse()
    secs = 0
    while parts:
        secs = (60*secs) + int(parts.pop(), 10)
    return secs * 1000

def get_data_filename(filename: str) -> str:
    """Return full path to file in "Extra-Files" directory"""
    extra_files = os.path.join(os.getcwd(), 'Extra-Files')
    return os.path.join(extra_files, filename)

class NotAnMP3Exception(Exception):
    """Exception raised when checking a file that's not an MP3 file"""

class InvalidMP3Exception(Exception):
    """Exception raised for an MP3 file that can't be used"""

class Metadata(NamedTuple):
    """the title of the Song"""
    title: str
    """the artist credited with the song"""
    artist: str
    """the artist credited with the song"""
    album: str = ''
    """a prime number used during game generation"""
    song_id: int = 0
    """duration of song (in milliseconds)"""
    duration: int = 0
    """position of song in playlist (in milliseconds)"""
    start_time: int = 0
    """filename of the MP3 file (name without path)"""
    filename: str = ''
    """location of the MP3 file (name with path)"""
    filepath: str = ''

class MP3Engine:
    """Interface for the MP3 parsing and editing functions"""

    #pylint: disable=no-self-use
    def parse(self, directory: str, filename: str) -> Metadata:
        """Extract the metadata from an MP3 file"""
        print(filename)
        abs_path = os.path.join(directory, filename)
        try:
            mp3_data = io.BytesIO(open(abs_path, 'rb').read())
        except IOError as err:
            raise InvalidMP3Exception(err)
        mp3info = EasyID3(mp3_data)
        artist = mp3info["artist"]
        title = mp3info["title"]
        if len(artist) == 0 or len(title) == 0:
            raise InvalidMP3Exception(
                f"File: {filename} does not both title and artist info")
        metadata = {
            "artist": artist[0],
            "title": title[0],
            "filepath": str(abs_path),
            "filename": str(filename),
        }
        try:
            metadata["album"] = str(mp3info["album"][0])
        except KeyError:
            head, tail = os.path.split(directory)
            metadata["album"] = tail if tail else head
        del mp3info
        mp3_data.seek(0)
        # duration is in milliseconds
        metadata["duration"] = len(AudioSegment.from_mp3(mp3_data))
        return Metadata(**metadata) # type: ignore

#pylint: disable=too-many-instance-attributes
class Song:
    """
    Represents one Song.
    'Song' objects are objects which possess a title,  artist,
    and a filepath to the file
    Arguments:
    ref_id   -- unique ID for referring to the track in a list
    title    -- the title of the Song
    artist   -- the artist credited with the song
    song_id  -- a prime number used during game generation (optional)
    duration -- duration of song (in milliseconds)
    filepath -- location of the MP3 file
    """
    FEAT_RE = re.compile(r'[\[(](feat[.\w]*|ft\.?)[)\]]', re.IGNORECASE)
    DROP_RE = re.compile(r'\s*[\[(](clean|[\w\s]+ ' +
                         r'(edit|mix|remix)|edit|explicit|remastered[ \d]*|' +
                         r'live|main title|mono|([\d\w"]+ single|album|single)' +
                         r' version)[)\]]\s*', re.IGNORECASE)

    def __init__(self, ref_id: int, metadata: Metadata):
        self.ref_id = ref_id
        self.title: str = ''
        self.artist: str = ''
        self.album: str = ''
        self.song_id: int = 0
        self.duration: int = 0
        self.start_time: int = 0
        self.filename: str = ''
        self.filepath: str = ''
        for key, value in metadata._asdict().items():
            setattr(self, key, value)
        self.title = self._correct_title(self.title.split('[')[0])
        self.artist = self._correct_title(self.artist)

    def _correct_title(self, title: str) -> str:
        """Try to remove 'cruft' from title or artist.
        Tries to remove things like '(radio edit)' or '(single version)'
        from song titles, as they are not useful and can make the text
        too long to fit within a Bingo square
        """
        title = re.sub(self.DROP_RE, '', title)
        return re.sub(self.FEAT_RE, 'ft.', title)

    def find(self, ref_id: int) -> Optional["Song"]:
        """Find a Song by its ref_id"""
        if self.ref_id == ref_id:
            return self
        return None

    def marshall(self, exclude: Optional[List[str]] = None) -> dict:
        """Convert attributes of this object to a dictionary"""
        retval = {}
        if exclude is None:
            exclude = []
        for key, value in self.__dict__.items():
            if key in exclude or value is None:
                continue
            retval[key] = value
        return retval

    def __len__(self):
        return 1

    def __str__(self):
        if self.song_id is not None:
            song_id = f' song_id={self.song_id}'
        else:
            song_id = ''
        return f"{self.title} - {self.artist} - ref={self.ref_id}{song_id}"

    def __key(self):
        return (self.title, self.artist, self.filepath, self.duration)

    def __eq__(self, other: Any):
        return isinstance(other, Song) and self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

ProgressCallback = Callable[[str, str, float], None]

class Directory:
    """Represents one directory full of mp3 files.
    It will parse reach mp3 file it finds to create Song objects.
    As this process is quite slow, it caches its results in a
    songs.json file.
    """

    maxFileSize = 32 * 1024 * 1024
    cache_filename = 'songs.json'

    def __init__(self, ref_id: int, directory: str):
        self.ref_id = ref_id
        self.directory = directory
        self.songs: List[Song] = []
        self.subdirectories: List[Directory] = []
        _, tail = os.path.split(directory)
        self.title: str = '[{0}]'.format(tail)
        self.artist: str = ''
        self.cache_hash: str = ''

    def search(self, engine: MP3Engine, progress: ProgressCallback,
               depth: int = 0, start_pct: float = 0.0) -> None:
        """Walk self.directory finding all songs and sub-directories."""
        if not os.path.isdir(self.directory):
            raise IOError(f'Directory "{self.directory}" does not exist')
        cache = {}
        try:
            with open(os.path.join(self.directory, self.cache_filename), 'r') as cfn:
                data = cfn.read()
            contents = json.loads(data)
            sha = hashlib.sha256()
            sha.update(data.encode('utf-8'))
            self.cache_hash = sha.hexdigest()
            for song in contents:
                cache[song['filename']] = song
            del data
            del contents
            del sha
        except IOError:
            pass
        folder_list = os.listdir(self.directory)
        divisor = math.pow(10, depth) * len(folder_list)
        for index, filename in enumerate(folder_list):
            pct = start_pct + (100.0 * index / divisor)
            progress(self.directory, filename, pct)
            try:
                self.songs.append(
                    self._check_file(engine, cache, filename, index, pct,
                                     depth, progress))
            except NotAnMP3Exception:
                pass
            except InvalidMP3Exception as err:
                print(sys.exc_info())
                print(f"Error inspecting file: {filename} - {err}")
        if self.songs:
            self.save_cache()

    def _check_file(self, engine: MP3Engine, cache: Dict[str, dict],
                    filename: str, index: int, start_pct: float,
                    depth: int, progress: ProgressCallback) -> Song:
        """Check one file to see if it an MP3 file or a directory.
        If it is a directory, a new Directory object is created for that
        directory. If it is an MP3 file, as new Song object is created
        """
        abs_path = os.path.join(self.directory, filename)
        stats = os.stat(abs_path)
        if stat.S_ISDIR(stats.st_mode):
            subdir = Directory(1000 * (self.ref_id + index), abs_path)
            subdir.search(engine, progress, depth + 1, start_pct)
            self.subdirectories.append(subdir)
        elif not stat.S_ISREG(stats.st_mode):
            raise NotAnMP3Exception("Not a regular file")
        if filename.lower()[-4:] != ".mp3":
            raise NotAnMP3Exception("Wrong file extension")
        if stats.st_size > self.maxFileSize:
            raise InvalidMP3Exception(f'{filename} is too large')
        try:
            mdata = cache[filename]
            try:
                mdata['filepath'] = os.path.join(self.directory,
                                                 mdata['filename'])
            except KeyError:
                pass
            try:
                mdata['song_id'] = mdata['songId']
                del mdata['songId']
            except KeyError:
                pass
            return Song(self.ref_id + index + 1, Metadata(**mdata))
        except KeyError:
            pass
        metadata = engine.parse(self.directory, filename)
        return Song(self.ref_id + index + 1, metadata)

    def find(self, ref_id: int) -> Optional[Song]:
        """Find a Song by its ref_id"""
        for song in self.songs:
            if song.ref_id == ref_id:
                return song
        for sub_dir in self.subdirectories:
            song2 = sub_dir.find(ref_id)
            if song2 is not None:
                return song2
        return None

    def add_to_tree_view(self, view: tkinter.ttk.Treeview, parent='', index_file=None) -> None:
        """Add this song to a TreeView widget"""
        for sub_dir in self.subdirectories:
            item_id = view.insert(parent, 'end', str(sub_dir.ref_id),
                                  values=(sub_dir.title, ''), open=False)
            sub_dir.add_to_tree_view(view, item_id, index_file=index_file)
        for song in self.songs:
            try:
                if index_file is not None:
                    index_file.writerow([song.artist, song.title, song.filepath])
            except UnicodeEncodeError:
                pass
            view.insert(parent, 'end', str(song.ref_id),
                        values=(song.title, song.artist))

    def total_length(self) -> int:
        """Returns total number of songs.
        Returns total of songs in this directory plus any subdirectories
        """
        total = len(self.songs)
        for sub_dir in self.subdirectories:
            total += len(sub_dir)
        return total

    def get_songs(self, ref_id: int) -> List[Song]:
        """Get all matching songs.
        Returns a list of all songs that match ref_id or all songs
        in a directory if its ref_id matches
        """
        song_list = []
        for sub_dir in self.subdirectories:
            for song in sub_dir.get_songs(ref_id):
                song_list.append(song)
        for song in self.songs:
            if ref_id in [song.ref_id, self.ref_id]:
                song_list.append(song)
        return song_list

    def sort(self, key, reverse=False):
        """Sort directories and songs within each directory"""
        self.subdirectories.sort(key=key, reverse=reverse)
        for sub_dir in self.subdirectories:
            sub_dir.sort(key=key, reverse=reverse)
        self.songs.sort(key=key, reverse=reverse)

    def save_cache(self):
        """Write contents of this directory to a cache file"""
        songs = [song.marshall(exclude=['filepath', 'ref_id', 'song_id']) for song in self.songs]
        js_str = json.dumps(songs, ensure_ascii=True)
        sha = hashlib.sha256()
        sha.update(js_str.encode('utf-8'))
        if self.cache_hash != sha.hexdigest():
            cfn = os.path.join(self.directory, self.cache_filename)
            with open(cfn, 'w') as cache_file:
                cache_file.write(js_str)

    def __len__(self):
        return len(self.songs) + len(self.subdirectories)

    def __getitem__(self, index):
        sub_len = len(self.subdirectories)
        if index < sub_len:
            return self.subdirectories[index]
        return self.songs[index - sub_len]

    def __repr__(self):
        return 'Directory({0}, {1}, {2})'.format(
            self.directory, str(self.subdirectories), str(self.songs))

# pylint: disable=too-few-public-methods
class BingoTicket:
    """Represents a Bingo ticket with 15 songs"""

    NUM_SONGS: int = 15

    def __init__(self, card_id: int = 0):
        self.card_id = card_id
        self.card_tracks: List[Song] = []
        self.ticket_number: Optional[int] = None

# pylint: disable=too-few-public-methods
class Mp3Order:
    """represents the order of the tracks within the final mp3"""
    def __init__(self, items):
        self.items = items
        #self.winPoint = None
        #self.amountAtWinPoint = None
        #self.amountAfterWinPoint = None
        #self.winPoints = None


class Progress:
    """represents the progress of a background thread"""
    def __init__(self, text: str, pct: float = 0.0, num_phases: int = 1) -> None:
        self.text = text
        self.pct = pct
        self.phase: Tuple[int, int] = (1, num_phases)


BANNER_COLOUR = "#222"
NORMAL_COLOUR = "#343434"
ALTERNATE_COLOUR = "#282828"
TYPEFACE = "Arial"

# pylint: disable=too-few-public-methods,too-many-instance-attributes
class Frames:
    """Container for tk frames used by MainApp"""
    def __init__(self, root_elt: tk.Tk):
        self.main = tk.Frame(root_elt, bg=NORMAL_COLOUR)
        self.left = tk.Frame(self.main, bg=BANNER_COLOUR)
        self.mid = tk.Frame(self.main, bg=NORMAL_COLOUR, padx=15)
        self.right = tk.Frame(self.main, bg=BANNER_COLOUR)
        self.song_list = tk.Frame(self.left)
        self.game_song_list = tk.Frame(self.right)
        self.game_button = tk.Frame(self.main, bg=ALTERNATE_COLOUR, pady=5)
        self.clip_button = tk.Frame(self.game_button, bg=ALTERNATE_COLOUR,
                                    pady=5)

# pylint: disable=too-few-public-methods
class Variables:
    """Container for tk variables used by MainApp"""
    def __init__(self):
        self.all_songs = tk.StringVar()
        self.colour = tk.StringVar()
        self.progress_pct = tk.DoubleVar()
        self.progress_text = tk.StringVar()
        self.new_clips_destination = tk.StringVar()
        self.new_clips_destination.set('./NewClips')


# pylint: disable=too-many-instance-attributes
class Buttons:
    """Container for tk buttons used by MainApp"""
    def __init__(self, app, frames: Frames):
        self.select_source_directory = tk.Button(
            frames.mid, text="Select Directory",
            command=app.ask_select_source_directory, bg="#63ff5f")
        self.add_song = tk.Button(frames.mid, text="Add Selected Songs",
                                  command=app.add_selected_songs_to_game, bg="#63ff5f")
        self.add_random_songs = tk.Button(
            frames.mid, text="Add 5 Random Songs",
            command=app.add_random_songs_to_game, bg="#18ff00")
        self.remove_song = tk.Button(
            frames.mid, text="Remove Selected Songs",
            command=app.remove_song_from_game, bg="#ff9090")
        self.remove_all_songs = tk.Button(frames.mid, text="Remove All Songs",
                                          command=app.remove_all_songs_from_game,
                                          bg="#ff5151")
        self.toggle_artist = tk.Button(
            frames.mid, text="Exclude Artist Names",
            command=app.toggle_exclude_artists, bg="#63ff5f")
        self.generate_cards = tk.Button(
            frames.game_button, text="Generate Bingo Game",
            command=app.generate_bingo_game, pady=0,
            font=(TYPEFACE, 18), bg="#00cc00")
        self.select_clip_directory = tk.Button(
            frames.clip_button, text="Select destination",
            command=app.ask_select_destination_directory, bg="#63ff5f")
        self.generate_clips = tk.Button(
            frames.clip_button, text="Generate clips",
            command=app.generate_clips, pady=0,
            font=(TYPEFACE, 18), bg="#00cc00")

    def disable(self):
        """disable all buttons"""
        self.add_song.config(state=tk.DISABLED)
        self.add_random_songs.config(state=tk.DISABLED)
        self.remove_song.config(state=tk.DISABLED)
        self.remove_all_songs.config(state=tk.DISABLED)
        self.toggle_artist.config(state=tk.DISABLED)
        self.generate_cards.config(state=tk.DISABLED)
        self.generate_clips.config(state=tk.DISABLED)

    def enable(self):
        """enable all buttons"""
        self.add_song.config(state=tk.NORMAL)
        self.add_random_songs.config(state=tk.NORMAL)
        self.remove_song.config(state=tk.NORMAL)
        self.remove_all_songs.config(state=tk.NORMAL)
        self.toggle_artist.config(state=tk.NORMAL)
        self.generate_cards.config(state=tk.NORMAL)
        self.generate_clips.config(state=tk.NORMAL)

class Labels:
    """Container for tk labels used by MainApp"""
    SONGS_REMAINING = "Available Songs = "

    def __init__(self, frames: Frames, variables: Variables):
        self.songs_remaining = tk.Label(
            frames.left, text=self.SONGS_REMAINING, padx=5, bg=BANNER_COLOUR,
            fg="#FFF", font=(TYPEFACE, 14))
        self.game_songs = tk.Label(frames.right, text="Songs In This Game:",
                                   padx=5, bg=BANNER_COLOUR, fg="#FFF",
                                   font=(TYPEFACE, 16))
        self.songs_in_game = tk.Label(
            frames.right, text="Songs In Game = 0", padx=5, bg=BANNER_COLOUR,
            fg="#FFF", font=(TYPEFACE, 14))
        self.previous_games_size = tk.Label(
            frames.mid, font=(TYPEFACE, 16),
            text="Previous\ngames:\n0 songs",
            bg=ALTERNATE_COLOUR, fg="#FFF", padx=6)
        self.bottom_banner = tk.Label(
            frames.game_button, textvariable=variables.progress_text,
            bg=BANNER_COLOUR, fg="#FFF",
            font=(TYPEFACE, 14), justify=tk.LEFT, anchor=tk.W)
        self.clip_dest = tk.Label(
            frames.clip_button, textvariable=variables.new_clips_destination,
            font=(TYPEFACE, 16), width=10, justify=tk.CENTER)

class BackgroundOperation(enum.Enum):
    """enumeration for the states of the background thread"""
    IDLE = enum.auto()
    GENERATING_CLIPS = enum.auto()
    GENERATING_GAME = enum.auto()
    SEARCHING_MUSIC = enum.auto()

# pylint: disable=too-many-instance-attributes
class MainApp:
    """The GUI of the program.
    It also contains all the functions used in generating the bingo tickets.
    """
    GAME_DIRECTORY = "./Bingo Games"
    GAME_PREFIX = "Game-"
    GAME_TRACKS_FILENAME = "gameTracks.json"
    QUIZ_MODE = False
    CREATE_INDEX = False
    PAGE_ORDER = True
    START_COUNTDOWN_FILENAME = 'countdown.mp3' if QUIZ_MODE else 'START.mp3'
    TRANSITION_FILENAME = 'TRANSITION.mp3'
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

    TICKET_COLOURS = {
        "BLUE": {
            "boxNorColour":   HexColor(0xF0F8FF),
            "boxAltColour":   HexColor(0xDAEDFF),
            "boxTitleColour": HexColor(0xa4d7ff),
            "logo"           : 'logo_banner.jpg',
        },
        "RED": {
            "boxNorColour":   HexColor(0xFFF0F0),
            "boxAltColour":   HexColor(0xffdada),
            "boxTitleColour": HexColor(0xffa4a4),
            "logo"           : 'logo_banner.jpg',
        },
        "GREEN": {
            "boxNorColour":   HexColor(0xf0fff0),
            "boxAltColour":   HexColor(0xd9ffd9),
            "boxTitleColour": HexColor(0xa4ffa4),
            "logo"           : 'logo_banner.jpg',
        },
        "ORANGE": {
            "boxNorColour":   HexColor(0xfff7f0),
            "boxAltColour":   HexColor(0xffecd9),
            "boxTitleColour": HexColor(0xffd1a3),
            "logo"           : 'logo_banner.jpg',
        },
        "PURPLE": {
            "boxNorColour" :   HexColor(0xf8f0ff),
            "boxAltColour" :   HexColor(0xeed9ff),
            "boxTitleColour" : HexColor(0xd5a3ff),
            "logo"           : 'logo_banner.jpg',
        },
        "YELLOW": {
            "boxNorColour" :   HexColor(0xfffff0),
            "boxAltColour" :   HexColor(0xfeffd9),
            "boxTitleColour" : HexColor(0xfdffa3),
            "logo"           : 'logo_banner.jpg',
        },
        "GREY": {
            "boxNorColour" :   HexColor(0xf1f1f1),
            "boxAltColour" :   HexColor(0xd9d9d9),
            "boxTitleColour" : HexColor(0xbfbfbf),
            "logo"           : 'logo_banner.jpg',
        },
        "PRIDE": {
            "boxNorColour" :   HexColor(0xf1f1f1),
            "boxAltColour" :   HexColor(0xd9d9d9),
            "boxTitleColour" : HexColor(0xbfbfbf),
            "colours"        : [
                Color(0.00, 0.00, 0.00, 0.25), # black
                Color(0.47, 0.31, 0.09, 0.25), # brown
                Color(0.94, 0.14, 0.14, 0.25), # red
                Color(0.93, 0.52, 0.13, 0.25), # orange
                Color(1.00, 0.90, 0.00, 0.25), # yellow
                Color(0.07, 0.62, 0.04, 0.25), # green
                Color(0.02, 0.27, 0.70, 0.25), # blue
                Color(0.76, 0.18, 0.86, 0.25), # purple
            ],
            "logo"           : 'pride_logo_banner.png',
        }
    }

    #pylint: disable=too-many-statements
    def __init__(self, root_elt: tk.Tk, clip_directory: Optional[str] = None):
        self.root = root_elt
        self._sort_by_title_option = True
        self.include_artist = True
        self.progress: Progress = Progress('')
        self.bg_thread = None
        self.game_id: str = ''
        self.clips: Directory = Directory(0, '')
        self.base_game_id: str = ''
        self.poll_id = None
        self.bg_status: BackgroundOperation = BackgroundOperation.IDLE
        self.dest_directory: str = ''
        self.palette = self.TICKET_COLOURS["BLUE"]
        self.number_of_cards = 0
        self.used_card_ids: List[int] = []
        self.variables = Variables()
        if clip_directory is not None:
            self.clip_directory = clip_directory
        else:
            self.clip_directory = './Clips'
        self.previous_games_songs: Set[int] = set() # uses hash of song
        self.base_game_id = datetime.date.today().strftime("%y-%m-%d")
        self.game_songs: List[Song] = []

        frames = Frames(root_elt)
        frames.main.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        frames.left.grid(row=0, column=0)
        frames.mid.grid(row=0, column=1)
        frames.right.grid(row=0, column=2)

        all_songs = tk.Label(frames.left,
                             textvariable=self.variables.all_songs,
                             padx=5, bg=BANNER_COLOUR, fg="#FFF",
                             font=(TYPEFACE, 16))
        all_songs.grid(row=0, column=0)

        frames.song_list.grid(row=1, column=0)

        self.buttons = Buttons(self, frames)
        self.labels = Labels(frames, self.variables)

        columns = ('title', 'artist')

        scrollbar = tk.Scrollbar(frames.song_list)

        self.song_list_tree = tkinter.ttk.Treeview(
            frames.song_list, columns=columns, height=20,
            yscrollcommand=scrollbar.set)
        self.song_list_tree.pack(side=tk.LEFT)

        self.song_list_tree.column('#0', width=20, anchor='center')
        self.song_list_tree.column('title', width=200, anchor='center')
        self.song_list_tree.heading('title', text='Title',
                                    command=self.sort_available_songs_by_title)
        self.song_list_tree.column('artist', width=200, anchor='center')
        self.song_list_tree.heading('artist', text='Artist',
                                    command=self.sort_available_songs_by_artist)
        self.labels.songs_remaining.grid(row=3, column=0)
        self.labels.songs_in_game.grid(row=3, column=0)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=self.song_list_tree.yview)

        self.labels.game_songs.grid(row=0, column=0)

        frames.game_song_list.grid(row=1, column=0)

        scrollbar = tk.Scrollbar(frames.game_song_list)

        columns = ('title', 'artist')
        self.game_songs_tree = tkinter.ttk.Treeview(
            frames.game_song_list, columns=columns, show="headings", height=20,
            yscrollcommand=scrollbar.set)
        self.game_songs_tree.pack(side=tk.LEFT)
        self.game_songs_tree.column('title', width=200, anchor='center')
        self.game_songs_tree.heading('title', text='Title',
                                     command=self.sort_game_list_by_title)
        self.game_songs_tree.column('artist', width=200, anchor='center')
        self.game_songs_tree.heading('artist', text='Artist',
                                     command=self.sort_game_list_by_artist)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=self.game_songs_tree.yview)

        self.buttons.select_source_directory.grid(row=0 , column=0, pady=0)

        padding = tk.Label(frames.mid, height=2, bg=NORMAL_COLOUR)
        padding.grid(row=1, column=0)

        self.buttons.add_song.grid(row=2, column=0, pady=10)
        self.buttons.add_random_songs.grid(row=3, column=0, pady=10)
        self.buttons.remove_song.grid(row=4, column=0, pady=10)
        self.buttons.remove_all_songs.grid(row=5, column=0, pady=10)
        self.buttons.toggle_artist.grid(row=6, column=0, pady=10)

        self.labels.previous_games_size.grid(row=7, column=0, pady=10)

        frames.game_button.grid(row=1, column=0, columnspan=3)

        colour_label = tk.Label(frames.game_button, font=(TYPEFACE, 16),
                                text="Ticket Colour:", bg=ALTERNATE_COLOUR,
                                fg="#FFF", padx=6)
        colour_label.grid(row=0, column=1)

        colour_combo = tkinter.ttk.Combobox(
            frames.game_button, textvariable=self.variables.colour,
            state='readonly', font=(TYPEFACE, 16),
            width=8, justify=tk.CENTER)
        colours = list(self.TICKET_COLOURS.keys())
        colours.sort()
        colour_combo['values'] = tuple(colours)
        colour_combo.current(0)
        colour_combo.grid(row=0, column=2, sticky=tk.E, padx=10)

        number_label = tk.Label(frames.game_button, font=(TYPEFACE, 16),
                                text="Game ID:", bg=ALTERNATE_COLOUR,
                                fg="#FFF", padx=6)
        number_label.grid(row=0, column=3, sticky=tk.E, padx=10)

        self.game_name_entry = tk.Entry(
            frames.game_button, font=(TYPEFACE, 16), width=10,
            justify=tk.CENTER)
        self.game_name_entry.grid(row=0, column=4, sticky=tk.W, padx=10)

        self.generate_unique_game_id()

        number_label = tk.Label(frames.game_button, font=(TYPEFACE, 16),
                                text="Number Of Tickets:", bg=ALTERNATE_COLOUR,
                                fg="#FFF", padx=6)
        number_label.grid(row=0, column=5, sticky=tk.W, padx=10)

        self.tickets_number_entry = tk.Entry(
            frames.game_button, font=(TYPEFACE, 16),
            width=5, justify=tk.CENTER)
        self.tickets_number_entry.grid(row=0, column=6)
        self.tickets_number_entry.insert(0, "24")

        self.buttons.generate_cards.grid(row=0, column=7, padx=20)

        frames.clip_button.grid(row=2, column=0, columnspan=8)

        self.buttons.select_clip_directory.grid(row=0 , column=0, pady=0)

        self.labels.clip_dest.grid(row=0, column=1, padx=10)

        number_label = tk.Label(
            frames.clip_button, font=(TYPEFACE, 16), text="Start time:",
            bg=ALTERNATE_COLOUR, fg="#FFF", padx=6)
        number_label.grid(row=0, column=2, sticky=tk.W, padx=10)
        self.start_time_entry = tk.Entry(
            frames.clip_button, font=(TYPEFACE, 16), width=5,
            justify=tk.CENTER)
        self.start_time_entry.grid(row=0, column=3)
        self.start_time_entry.insert(0, "01:00")

        number_label = tk.Label(
            frames.clip_button, font=(TYPEFACE, 16), text="Duration:",
            bg=ALTERNATE_COLOUR, fg="#FFF", padx=6)
        number_label.grid(row=0, column=4, sticky=tk.W, padx=10)
        self.duration_entry = tk.Entry(frames.clip_button, font=(TYPEFACE, 16),
                                       width=5, justify=tk.CENTER)
        self.duration_entry.grid(row=0, column=5)
        self.duration_entry.insert(0, "30")

        self.buttons.generate_clips.grid(row=0, column=6, padx=20)

        self.labels.bottom_banner.grid(row=3, column=0, columnspan=6)
        self.progressbar = tkinter.ttk.Progressbar(
            frames.game_button, orient=tk.HORIZONTAL, mode="determinate",
            variable=self.variables.progress_pct, length=200, maximum=100.0)
        self.progressbar.grid(row=3, column=6, columnspan=2)
        self.search_clips_directory()


    def generate_unique_game_id(self):
        """Create unique game ID.
        Checks the "./Bingo Games" directory to make sure that the
        generated game ID does not already exist
        """
        game_num = 1
        game_id = lambda num: f"{self.base_game_id}-{num}"
        start = len(self.GAME_PREFIX)
        end = start + len(self.base_game_id)
        self.previous_games_songs = set()
        clashes = []
        for subdir in [x[0] for x in os.walk(self.GAME_DIRECTORY)]:
            if subdir == self.GAME_DIRECTORY:
                continue
            base = os.path.basename(subdir)
            if base[start:end] == self.base_game_id:
                self.load_previous_game_songs(subdir)
                clashes.append(base[start:])
        while game_id(game_num) in clashes:
            game_num += 1
        self.game_id = game_id(game_num)
        self.game_name_entry.delete(0, len(self.game_name_entry.get()))
        self.game_name_entry.insert(0, self.game_id)
        num_prev = len(self.previous_games_songs)
        plural = '' if num_prev==1 else 's'
        txt = f"Previous\nGames:\n{num_prev} song{plural}"
        self.labels.previous_games_size.config(text=txt)

    def load_previous_game_songs(self, dirname: str) -> None:
        """load all the songs from a previous game.
        The previous_games_songs set is updated with
        every song in a previous game. This is then used when
        adding random tracks to a game to attempt to avoid adding
        duplicates
        """
        filename = os.path.join(dirname, self.GAME_TRACKS_FILENAME)
        try:
            with open(filename, 'r') as gt_file:
                for song in json.load(gt_file):
                    if 'ref_id' not in song:
                        song['ref_id'] = 0
                    song = Song(**song)
                    self.previous_games_songs.add(hash(song))
        except IOError as err:
            print(f"IOError {filename}: {err}")

    def update_song_counts(self):
        """Update the song counts at the bottom of each list.
        This function is called after any addition or removal of songs
        to/from the lists.
        """
        self.labels.songs_remaining.config(text='{0}{1:d}'.format(
            Labels.SONGS_REMAINING, self.clips.total_length()))
        if len(self.game_songs) < 30:
            box_col = "#ff0000"
        elif len(self.game_songs) < 45:
            box_col = "#fffa20"
        else:
            box_col = "#00c009"
        duration = sum([s.duration for s in self.game_songs])
        txt = 'Songs In Game = {:d} ({:s})'.format(
            len(self.game_songs), format_duration(duration))
        self.labels.songs_in_game.config(text=txt, fg=box_col)

    def ask_select_source_directory(self):
        """Ask user for clip source directory.
        Called when the select_source_directory button is pressed
        """
        self.clip_directory = tkinter.filedialog.askdirectory()
        self.remove_available_songs_from_treeview()
        self.search_clips_directory()
        self.add_available_songs_to_treeview()
        self.update_song_counts()

    def ask_select_destination_directory(self):
        """Ask user for new clip destination directory.
        Called when the select_clip_directory is pressed
        """
        self.variables.new_clips_destination.set(
            tkinter.filedialog.askdirectory())

    def add_selected_songs_to_game(self):
        """add the selected songs from the source list to the game"""
        selections = list(self.song_list_tree.selection())
        focus_elt = self.song_list_tree.focus()
        if not selections and not focus_elt:
            return
        if not selections:
            selections = [focus_elt]
        ids = set()
        for ref_id in selections:
            for song in self.clips.get_songs(int(ref_id)):
                ids.add(str(song.ref_id))
        selections = ids
        for ref_id in selections:
            song = self.clips.find(int(ref_id))
            if song is None:
                print(f"Song {ref_id} Not Found")
                continue
            self.game_songs.append(song)
            try:
                self.song_list_tree.delete(ref_id)
            except tkinter.TclError as err:
                print(f"Failed to remove {ref_id}: {err}")
                print(song)
            self.game_songs_tree.insert('', 'end', str(song.ref_id),
                                        values=(song.title, song.artist))
        self.update_song_counts()

    def add_random_songs_to_game(self, amount: int = 5) -> None:
        """add random songs (if available) to the game list"""
        selections = list(self.song_list_tree.selection())
        if not selections:
            selections = self.song_list_tree.get_children()
        ids = set()
        song: Optional[Song] = None
        for ref_id in selections:
            for song in self.clips.get_songs(int(ref_id)):
                if hash(song) not in self.previous_games_songs:
                    ids.add(str(song.ref_id))
        for song in self.game_songs:
            try:
                ids.remove(str(song.ref_id))
            except KeyError:
                pass
        selections = list(ids)
        todo = min(len(selections), amount)
        while ids and todo > 0:
            try:
                ref_id = secrets.choice(selections)
                selections.remove(ref_id)
                song = self.clips.find(int(ref_id))
                if song is None:
                    print(f"Song {ref_id} Not Found")
                    continue
                self.game_songs.append(song)
                self.song_list_tree.delete(str(song.ref_id))
                self.game_songs_tree.insert('', 'end', str(song.ref_id),
                                            values=(song.title, song.artist))
                todo -= 1
            except (ValueError, KeyError) as err:
                print((sys.exc_info()))
                print(f"Couldn't Add To Game List: {err}")
        self.update_song_counts()

    def remove_song_from_game(self):
        """remove the selected song from the game list and
        return it to the main list.
        """
        selections = list(self.game_songs_tree.selection())
        focus_elt = self.game_songs_tree.focus()
        if not selections and not focus_elt:
            return
        if not selections:
            selections = [focus_elt]
        try:
            self.remove_available_songs_from_treeview()
            for ref_id in selections:
                song = self.clips.find(int(ref_id))
                if song is None:
                    print(("Song {0} not found.".format(ref_id)))
                    continue
                self.game_songs.remove(song)
                self.game_songs_tree.delete(str(song.ref_id))
            self.add_available_songs_to_treeview()
        except (ValueError, KeyError) as err:
            print((sys.exc_info()))
            print(f"Couldn't Add To Game List: {err}")
        finally:
            self.update_song_counts()

    def remove_all_songs_from_game(self):
        """remove all of the songs from the game list"""
        answer = 'yes'
        if len(self.game_songs) > 1:
            num_songs = len(self.game_songs)
            question = f"Are you sure you want to remove all {num_songs} songs from the game?"
            answer = tkinter.messagebox.askquestion(
                "Are you sure?", question)
        if answer == 'yes':
            self.remove_songs_from_game_treeview()
            self.remove_available_songs_from_treeview()
            self.game_songs = []
            self.add_available_songs_to_treeview()
            if self._sort_by_title_option:
                self.sort_by_title()
            else:
                self.sort_by_artists()
        self.update_song_counts()

    def toggle_exclude_artists(self):
        """toggle the "exclude artists" setting"""
        self.include_artist = not self.include_artist
        text="Exclude Artist Names" if self.include_artist else "Include Artist Names"
        self.buttons.toggle_artist.config(text=text)

    def add_available_songs_to_treeview(self):
        """adds every available song to the "available songs" Tk Treeview"""
        _, tail = os.path.split(self.clip_directory)
        self.variables.all_songs.set("Available Songs: {0}".format(tail))
        writer=None
        if self.CREATE_INDEX:
            index_file = open("song_index.csv", "wb")
            writer = csv.writer(index_file)
        self.clips.add_to_tree_view(self.song_list_tree, index_file=writer)
        for song in self.game_songs:
            self.song_list_tree.delete(str(song.ref_id))
        if self.CREATE_INDEX:
            index_file.close()

    def remove_available_songs_from_treeview(self):
        """remove all songs from "available songs" Treeview"""
        children = self.song_list_tree.get_children()
        if children:
            self.song_list_tree.delete(*children)

    def add_songs_to_game_treeview(self):
        """adds list of selected songs to game_songs_tree Treeview.
        Takes the representation of the list of game songs and adds them
        all to the game GUI list
        """
        for song in self.game_songs:
            self.game_songs_tree.insert('', 'end', str(song.ref_id),
                                        values=(song.title, song.artist))
        self.update_song_counts()

    def remove_songs_from_game_treeview(self):
        """Remove all songs from game list"""
        children = self.game_songs_tree.get_children()
        if children:
            self.game_songs_tree.delete(*children)
        self.update_song_counts()

    def sort_available_songs_by_artist(self):
        """sort the song list by artist"""
        self.remove_available_songs_from_treeview()
        self.clips.sort(key=lambda x: x.artist, reverse=False)
        self.add_available_songs_to_treeview()

    def sort_available_songs_by_title(self):
        """sort the available song list by title"""
        self.remove_available_songs_from_treeview()
        self.clips.sort(key=lambda x: x.title, reverse=False)
        self.add_available_songs_to_treeview()

    def sort_game_list_by_artist(self):
        """sort the game song list by artist"""
        self.remove_songs_from_game_treeview()
        self.game_songs.sort(key=lambda x: x.artist, reverse=False)
        self.add_songs_to_game_treeview()

    def sort_game_list_by_title(self):
        """sort the game song list by title"""
        self.remove_songs_from_game_treeview()
        self.game_songs.sort(key=lambda x: x.title, reverse=False)
        self.add_songs_to_game_treeview()

    def sort_by_artists(self):
        """sort both the song list and game song list by artist"""
        self._sort_by_title_option = False
        self.sort_available_songs_by_artist()
        self.sort_game_list_by_artist()

    def sort_by_title(self):
        """sort both the song list and game song list by title"""
        self._sort_by_title_option = True
        self.sort_available_songs_by_title()
        self.sort_game_list_by_title()

    def search_clips_directory(self):
        """Start thread to search for songs and sub-directories.
        """
        self.buttons.disable()
        self.progress = Progress(text='', pct=0.0, num_phases=1)
        self.bg_status = BackgroundOperation.SEARCHING_MUSIC
        self.bg_thread = threading.Thread(
            target=self.search_clips_directory_thread)
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def search_clips_directory_thread(self):
        """Walk clip_directory finding all songs and sub-directories.
        This function retrieves a list of songs from the Clips folder,
        gets the Title/Artist data and adds them to the song list.
        This function runs in its own thread
        """
        self.clips = Directory(1, self.clip_directory)
        self.progress.text = 'Searching for clips'
        self.progress.pct = 0.0
        engine = MP3Engine()
        self.clips.search(engine, self.search_progress)
        self.progress.text = ''
        self.progress.pct = 0.0

    def search_progress(self, directory: str, filename: str,
                        pct: float) -> None:
        """progress callback from Directory.search()"""
        self.progress.text = f'Searching {directory}: {filename}'
        self.progress.pct = pct

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
                                card: BingoTicket, num_tracks: int):
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
        return self.include_artist and not re.match(r'various\s+artist',
                                                    track.artist, re.IGNORECASE)

    def box_colour_style(self, col: int, row: int) -> tuple:
        """Choose the background colour for a given bingo ticket"""
        try:
            colours = self.palette['colours']
            colour = colours[(col + row*5) % len(colours)]
        except KeyError:
            # if col & row are both even or both odd, use boxAltColour
            if (((col & 1) == 0 and (row & 1) == 0) or
                    ((col & 1) == 1 and (row & 1) == 1)):
                colour = self.palette["boxAltColour"]
            else:
                colour = self.palette["boxNorColour"]
        return ('BACKGROUND', (col, row), (col, row), colour)

    def render_bingo_ticket(self, card: BingoTicket) -> List[Any]:
        """render a bingo ticket PDF Table"""
        img = Image(get_data_filename(self.palette['logo']))
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
                   self.box_colour_style(1,0),
                   self.box_colour_style(3,0),
                   self.box_colour_style(0,1),
                   self.box_colour_style(2,1),
                   self.box_colour_style(4,1),
                   self.box_colour_style(1,2),
                   self.box_colour_style(3,2),
                   ('PADDINGTOP', (0, 0), (-1, -1), 0),
                   ('PADDINGLEFT', (0, 0), (-1, -1), 0),
                   ('PADDINGRIGHT', (0, 0), (-1, -1), 0),
                   ('PADDINGBOTTOM', (0, 0), (-1, -1), 0),
                   self.box_colour_style(0,0),
                   self.box_colour_style(2,0),
                   self.box_colour_style(4,0),
                   self.box_colour_style(1,1),
                   self.box_colour_style(3,1),
                   self.box_colour_style(0,2),
                   self.box_colour_style(2,2),
                   self.box_colour_style(4,2)])
        return [img, Spacer(width=0, height=0.1*inch), table]

    def generate_track_listing(self, tracks: List[Song]) -> None:
        """generate a PDF version of the track order in the game"""
        doc = SimpleDocTemplate(os.path.join(self.dest_directory,
                                             self.game_id+" Track Listing.pdf"),
                                pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements: List[Flowable] = []
        img = Image(get_data_filename(self.palette['logo']))
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
            f'Track Listing For Game Number: <b>{self.game_id}</b>', pstyle)
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
                            self.palette["boxTitleColour"])])
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
            os.path.join(self.dest_directory,
                         f"{self.game_id} Ticket Results.pdf"),
            pagesize=A4)
        doc.topMargin = 0.05*inch
        doc.bottomMargin = 0.05*inch
        elements: List[Flowable] = []

        img = Image(get_data_filename(self.palette['logo']))
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
            Paragraph(f'Results For Game Number: <b>{self.game_id}</b>',
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
                            self.palette["boxTitleColour"])])
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
            card = BingoTicket()
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
        num_on_last = self.number_of_cards * decay_rate
        num_second_last = (self.number_of_cards-num_on_last) * decay_rate
        num_third_last = (self.number_of_cards - num_on_last -
                          num_second_last) * decay_rate
        num_fourth_last = ((self.number_of_cards - num_on_last -
                            num_second_last - num_third_last) *
                           decay_rate)
        num_on_last = int(num_on_last)
        num_second_last = int(num_second_last)
        num_third_last = int(num_third_last)
        num_fourth_last = max(int(num_fourth_last), 1)
        amount_left = (self.number_of_cards - num_on_last -
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
        increment: float = self.number_of_cards / float(amount_to_go)
        start_point: float = 0
        random.shuffle(good_cards)
        for card in good_cards:
            rand_point = self.randrange(
                int(math.ceil(start_point)),
                int(math.ceil(start_point+increment)))
            rand_point = int(math.ceil(rand_point))
            rand_point = min(rand_point, self.number_of_cards - 1)
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
        noc3c = int(math.ceil(self.number_of_cards/3))
        noc3f = int(math.floor(self.number_of_cards/3))
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
        name = f"{self.game_id} Bingo Tickets - ({self.number_of_cards} Tickets).pdf"
        doc = SimpleDocTemplate(os.path.join(self.dest_directory, name),
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
            ticket_id = f"{self.game_id} / T{card.ticket_number} / P{page}"
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
        filename = os.path.join(self.dest_directory, "ticketTracks")
        with open(filename, 'wt') as ttf:
            for card in cards:
                ttf.write(f"{card.ticket_number}/{card.card_id}\n")

    def gen_track_order(self) -> List[Song]:
        """generate a random order of tracks for the game"""
        def rand_float() -> float:
            return float(secrets.randbelow(1000)) / 1000.0
        list_copy = copy.copy(self.game_songs)
        if not self.QUIZ_MODE:
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

    @staticmethod
    def clean(text: str) -> str:
        """remove all non-ascii characters from a string"""
        if not isinstance(text, str):
            text = text.decode('utf-8')
        return ''.join(filter(lambda c: c.isalnum(), list(text)))

    def generate_mp3(self):
        """generate the mp3 for the game with the generated order of tracks"""
        self.progress.phase = (1,3)
        song_order = Mp3Order(self.gen_track_order())
        transition = AudioSegment.from_mp3(get_data_filename(self.TRANSITION_FILENAME))
        transition = transition.normalize(headroom=0)
        countdown = AudioSegment.from_mp3(get_data_filename(self.START_COUNTDOWN_FILENAME))
        countdown = countdown.normalize(headroom=0)
        if self.QUIZ_MODE:
            start, end = self.COUNTDOWN_POSITIONS['1']
            combined_track = countdown[start:end]
        else:
            combined_track = countdown
        tracks = []
        num_tracks = len(song_order.items)
        for index, song in enumerate(song_order.items, start=1):
            if index==1:
                cur_pos = combined_track.__len__()
            else:
                cur_pos = combined_track.__len__() + transition.__len__()
            next_track = AudioSegment.from_mp3(song.filepath)
            next_track = next_track.normalize(headroom=0)
            if index==1:
                combined_track = combined_track + next_track
            elif self.QUIZ_MODE:
                try:
                    start, end = self.COUNTDOWN_POSITIONS[str(index)]
                    number = countdown[start:end]
                    combined_track = (combined_track + transition + number +
                                      transition + next_track)
                except KeyError:
                    break
            else:
                combined_track = combined_track + transition + next_track
            del next_track
            song_with_pos = song.marshall()
            song_with_pos['start_time'] = format_duration(cur_pos)
            song_with_pos['index'] = index
            tracks.append(Song(**song_with_pos))
            self.progress.text = f'Adding track {index}/{num_tracks}'
            self.progress.pct = 100.0 * float(index) / float(num_tracks)

        self.save_game_tracks_json(tracks)
        combined_track = combined_track + transition
        self.progress.text = 'Exporting MP3'
        mp3_name = os.path.join(self.dest_directory,
                                self.game_id + " Game Audio.mp3")
        combined_track.export(mp3_name, format="mp3", bitrate="256k")
        self.progress.text = 'MP3 Generated, creating track listing PDF'
        self.progress.pct = 100.0
        self.generate_track_listing(tracks)
        self.progress.text = 'MP3 and Track listing PDF generated'
        return tracks

    def save_game_tracks_json(self, tracks: List[Song]) -> None:
        """saves the track listing to gameTracks.json"""
        filename = os.path.join(self.dest_directory, self.GAME_TRACKS_FILENAME)
        with open(filename, 'w') as jsf:
            marshalled: List[Dict] = []
            for track in tracks:
                track_dict = track.marshall(exclude=['ref_id', 'filename', 'index'])
                if track_dict['filepath'].startswith(self.clip_directory):
                    track_dict['filepath'] = track_dict['filepath'][len(self.clip_directory)+1:]
                marshalled.append(track_dict)
            json.dump(marshalled, jsf, sort_keys=True, indent=2)

    def generate_bingo_game(self):
        """
        generate tickets and mp3.
        called on pressing the generate game button
        """
        self.number_of_cards = self.tickets_number_entry.get()
        self.number_of_cards = int(self.number_of_cards.strip())
        extra = ""
        min_cards = 15
        max_cards = self.combinations(len(self.game_songs), BingoTicket.NUM_SONGS)
        min_songs = 17 # 17 songs allows 136 combinations

        num_songs = len(self.game_songs)
        if num_songs < 45:
            extra = "\nNOTE: At least 45 songs is recommended"

        if self.number_of_cards > max_cards or num_songs < min_songs:
            self.variables.progress_text.set(
                (f'{num_songs} songs only allows '+
                 f'{max_cards} cards to be generated'))
            return

        if (len(self.game_songs) < min_songs or self.number_of_cards < min_cards or
                self.number_of_cards > max_cards):
            text = (f"You must select at least {min_songs} songs " +
                    f"(at least 45 is better) and between {min_cards} and " +
                    f"{max_cards} tickets for a bingo game to be generated.")
            self.variables.progress_text.set(text)
            #self.labels.bottom_banner.config(text=text, fg="#F11")
            return
        answer = 'yes'

        question_msg = "Are you sure you want to generate a bingo game with "+\
                       "{num_cards:d} tickets and the {num_songs:d} songs in "+\
                       "the white box on the right? {extra}\nThis process might "+\
                       "take a few minutes."
        question_msg = question_msg.format(num_cards=self.number_of_cards,
                                           num_songs=len(self.game_songs),
                                           extra=extra)
        answer = tkinter.messagebox.askquestion("Are you sure?", question_msg)

        if answer != 'yes':
            return
        self.buttons.disable()
        try:
            self.palette = self.TICKET_COLOURS[self.variables.colour.get()]
        except KeyError:
            self.palette = self.TICKET_COLOURS["BLUE"]
        self.variables.progress_text.set(f"Generating Bingo Game - {self.game_id}")
        self.game_id = self.game_name_entry.get().strip()
        self.dest_directory = os.path.join(os.getcwd(),
                                           self.GAME_DIRECTORY,
                                           self.GAME_PREFIX + self.game_id)
        if not os.path.exists(self.dest_directory):
            os.makedirs(self.dest_directory)
        self.progress = Progress(text='', pct=0.0, num_phases=3)
        self.bg_thread = threading.Thread(
            target=self.generate_bingo_tickets_and_mp3_thread)
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_bingo_tickets_and_mp3_thread(self):
        """Creates MP3 file and PDF files.
        This function runs in its own thread
        """
        if not self.assign_song_ids(self.game_songs):
            self.progress.text = 'Failed to assign song IDs - '+\
                                 'maybe not enough tracks in the game?'
            return
        self.progress.phase = (1,3)
        tracks = self.generate_mp3()
        self.progress.phase = (2,3)
        if not self.QUIZ_MODE:
            cards = self.generate_all_cards(tracks)
            self.progress.phase = (3,3)
            self.generate_tickets_pdf(cards)
            self.generate_ticket_tracks_file(cards)
            self.generate_card_results(tracks, cards)
        self.progress.text = f"Finished Generating Bingo Game: {self.game_id}"
        self.progress.pct = 100.0

    def _poll_progress(self):
        """Checks progress of encoding thread and updates progress bar.
        Other threads are not allowed to update Tk components, so this
        function (which runs in the main thread) is used to update the
        progress bar and to detect when the thread has finished.
        """
        if not self.bg_thread:
            return
        pct = self.progress.pct / float(self.progress.phase[1])
        pct += float(self.progress.phase[0] - 1)/float(self.progress.phase[1])
        self.variables.progress_pct.set(pct)
        self.variables.progress_text.set(self.progress.text)
        #self.labels.bottom_banner.config(text=self.progress.text)
        if self.bg_thread.is_alive():
            self.poll_id = self.root.after(250, self._poll_progress)
            return
        self.variables.progress_pct.set(100)
        self.bg_thread.join()
        self.bg_thread = None
        self.buttons.enable()
        if self.bg_status == BackgroundOperation.SEARCHING_MUSIC:
            self.update_song_counts()
            self.add_available_songs_to_treeview()
            self.sort_available_songs_by_title()
            self.variables.progress_text.set('')
        elif self.bg_status == BackgroundOperation.GENERATING_GAME:
            self.generate_unique_game_id()
        self.progress.text = ''
        self.bg_status = BackgroundOperation.IDLE
        self.variables.progress_pct.set(0.0)

    def generate_clips(self):
        """Generate all clips for all selected Songs in a new thread.
        Creates a new thread and uses that thread to create clips of
        every selected Song
        """
        if not self.game_songs:
            return
        self.buttons.disable()
        self.progress = Progress('')
        self.bg_status = BackgroundOperation.GENERATING_CLIPS
        self.bg_thread = threading.Thread(target=self.generate_clips_thread)
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_clips_thread(self):
        """Generate all clips for all selected Songs
        This function runs in its own thread
        """
        total_songs = len(self.game_songs)
        for index, song in enumerate(self.game_songs):
            #print(song.title, song.artist, song.album)
            self.progress.text = '{} ({:d}/{:d})'.format(self.clean(song.title),
                                                         index, total_songs)
            self.progress.pct = 100.0 * float(index) / float(total_songs)
            #pylint: disable=broad-except
            try:
                self.generate_clip(song)
            except Exception as err:
                traceback.print_exc()
                print(r'Error generating clip: {0} - {1}'.format(
                    self.clean(song.title), str(err)))
        self.progress.pct = 100.0
        self.progress.text = 'Finished generating clips'

    def generate_clip(self, song: Song) -> None:
        """Create one clip from an existing MP3 file.
        It will take the start time and duration values from the GUI fields
        and create a "duration" length clip starting at "start_time_entry"
        in the "NewClips" directory, using the name and directory of the
        source MP3 file as its filename.
        """
        assert song.filepath is not None
        head, tail = os.path.split(os.path.dirname(song.filepath))
        dirname = tail if tail else head
        assert dirname is not None
        dest_dir = os.path.join(self.variables.new_clips_destination.get(),
                                dirname)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        start = parse_time(self.start_time_entry.get())
        end = start + parse_time(self.duration_entry.get())
        src = AudioSegment.from_mp3(song.filepath)
        dst = src[start:end]
        tags = {
            "artist": self.clean(song.artist),
            "title": self.clean(song.title)
        }
        if song.album:
            tags["album"] = self.clean(song.album)
        assert song.filename is not None
        dest_path = os.path.join(dest_dir, song.filename)
        dst.export(dest_path, format='mp3', bitrate='256k', tags=tags)

    @staticmethod
    def combinations(total: int, select: int) -> int:
        """calculate combinations
        Calculates the number of combinations of selecting 'select' items
        from 'total' items
        """
        if select > total:
            return 0
        return int(math.factorial(total)/(math.factorial(select)*math.factorial(total-select)))


def main():
    """main loop"""
    root = tk.Tk()
    root.resizable(0, 0)
    root.wm_title("Music Bingo Game Generator")
    if sys.platform.startswith('win'):
        ico_file = get_data_filename("Icon.ico")
        if os.path.exists(ico_file):
            root.iconbitmap(os.path.abspath(ico_file))
    else:
        ico_file = get_data_filename("Icon.gif")
        if os.path.exists(ico_file):
            logo = tk.PhotoImage(file=ico_file)
            root.call('wm', 'iconphoto', root._w, logo)
    clip_directory = None
    if len(sys.argv) > 1:
        clip_directory = sys.argv[1]
    MainApp(root, clip_directory)
    root.mainloop()

if __name__ == "__main__":
    main()
