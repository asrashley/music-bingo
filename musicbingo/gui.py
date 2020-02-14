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
import datetime
from pathlib import Path
import json
import os
import secrets
import sys
import threading
from typing import List, Optional, Set

import tkinter as tk # pylint: disable=import-error
import tkinter.messagebox # pylint: disable=import-error
import tkinter.constants # pylint: disable=import-error
import tkinter.filedialog # pylint: disable=import-error
import tkinter.ttk # pylint: disable=import-error

from musicbingo.assets import Assets
from musicbingo.clips import ClipGenerator
from musicbingo.directory import Directory
from musicbingo.generator import GameGenerator, Palette
from musicbingo.mp3 import MP3Editor, MP3Factory, MP3Parser
from musicbingo.docgen import DocumentFactory, DocumentGenerator
from musicbingo.options import GameMode, Options
from musicbingo.progress import Progress
from musicbingo.song import Duration, Metadata, Song

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
    def __init__(self, options: Options):
        self.all_songs = tk.StringVar()
        self.colour = tk.StringVar()
        self.progress_pct = tk.DoubleVar()
        self.progress_text = tk.StringVar()
        self.new_clips_destination = tk.StringVar()
        self.new_clips_destination.set(options.new_clips_dest)


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

class NullMP3Parser(MP3Parser):
    """
    Empty MP3Parser implementation.
    Used to allow a do-nothing Directory object to be created
    """

    def parse(self, filename: Path) -> Metadata:
        """Extract the metadata from an MP3 file"""
        raise NotImplementedError()

# pylint: disable=too-many-instance-attributes
class MainApp:
    """The GUI of the program.
    It also contains all the functions used in generating the bingo tickets.
    """
    #pylint: disable=too-many-statements
    def __init__(self, root_elt: tk.Tk, options: Options):
        self.root = root_elt
        self.options = options
        self._sort_by_title_option = True
        self.bg_thread = None
        self.progress = Progress()
        self._mp3editor: Optional[MP3Editor] = None
        self._mp3parser: Optional[MP3Parser] = None
        self._docgen: Optional[DocumentGenerator] = None
        self.clips: Directory = Directory(None, 0, Path(''), NullMP3Parser(),
                                          self.progress)
        self.poll_id = None
        self.bg_status: BackgroundOperation = BackgroundOperation.IDLE
        self.dest_directory: str = ''
        self.variables = Variables(self.options)
        self.previous_games_songs: Set[int] = set() # uses hash of song
        self.base_game_id: str = datetime.date.today().strftime("%y-%m-%d")
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

        self.buttons.select_source_directory.grid(row=0, column=0, pady=0)

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
        colour_combo['values'] = tuple(map(str.title, Palette.colour_names()))
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

        self.buttons.select_clip_directory.grid(row=0, column=0, pady=0)

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

    @property
    def mp3editor(self) -> MP3Editor:
        """get MP3Editor instance, creating if required"""
        if self._mp3editor is None:
            self._mp3editor = MP3Factory.create_editor()
        return self._mp3editor

    @property
    def mp3parser(self) -> MP3Parser:
        """get MP3Parser instance, creating if required"""
        if self._mp3parser is None:
            self._mp3parser = MP3Factory.create_parser()
        return self._mp3parser

    @property
    def docgen(self) -> DocumentGenerator:
        """get DocumentGenerator instance, creating if required"""
        if self._docgen is None:
            self._docgen = DocumentFactory.create_generator('pdf')
        return self._docgen

    def generate_unique_game_id(self):
        """Create unique game ID.
        Checks the "./Bingo Games" directory to make sure that the
        generated game ID does not already exist
        """
        game_num = 1
        game_id = lambda num: f"{self.base_game_id}-{num}"
        self.previous_games_songs.clear()
        #clashes: Set[str] = set()
        games_dest = self.options.game_destination_dir()
        for subdir in [Path(x[0]) for x in os.walk(games_dest)]:
            if subdir == games_dest:
                continue
            if subdir.name.startswith(game_id(game_num)):
                self.load_previous_game_songs(subdir)
                #clashes.append(subdir.name)
        while self.options.game_destination_dir(game_id(game_num)).exists():
            game_num += 1
        self.game_name_entry.delete(0, len(self.game_name_entry.get()))
        self.game_name_entry.insert(0, game_id(game_num))
        num_prev = len(self.previous_games_songs)
        plural = '' if num_prev == 1 else 's'
        txt = f"Previous\nGames:\n{num_prev} song{plural}"
        self.labels.previous_games_size.config(text=txt)

    def load_previous_game_songs(self, gamedir: Path) -> None:
        """
        Load all the songs from a previous game.
        The previous_games_songs set is updated with
        every song in a previous game. This is then used when
        adding random tracks to a game to attempt to avoid adding
        duplicates
        """
        filename = gamedir / self.options.games_tracks_filename
        if not filename.exists():
            return
        with filename.open('r') as gt_file:
            for index, song in enumerate(json.load(gt_file), 1):
                song = Song(None, index, Metadata(**song))
                self.previous_games_songs.add(hash(song))

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
        duration = Duration(sum([s.duration for s in self.game_songs]))
        txt = 'Songs In Game = {:d} ({:s})'.format(
            len(self.game_songs), duration.format())
        self.labels.songs_in_game.config(text=txt, fg=box_col)

    def ask_select_source_directory(self):
        """Ask user for clip source directory.
        Called when the select_source_directory button is pressed
        """
        self.options.clip_directory = tkinter.filedialog.askdirectory()
        self.remove_available_songs_from_treeview()
        self.search_clips_directory()
        self.add_available_songs_to_treeview()
        self.update_song_counts()

    def ask_select_destination_directory(self):
        """Ask user for new clip destination directory.
        Called when the select_clip_directory is pressed
        """
        new_dest = tkinter.filedialog.askdirectory()
        self.variables.new_clips_destination.set(new_dest)
        self.options.new_clips_dest = new_dest

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
        self.options.include_artist = not self.options.include_artist
        if self.options.include_artist:
            text = "Include Artist Names"
        else:
            text = "Exclude Artist Names"
        self.buttons.toggle_artist.config(text=text)

    def add_available_songs_to_treeview(self):
        """adds every available song to the "available songs" Tk Treeview"""
        name = self.options.clips().name
        self.variables.all_songs.set(f"Available Songs: {name}")
        if self.options.create_index:
            self.clips.create_index("song_index.csv")
        self.add_to_tree_view(self.song_list_tree, self.clips)
        for song in self.game_songs:
            self.song_list_tree.delete(str(song.ref_id))

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
        self.clips = Directory(None, 1, self.options.clips(), self.mp3parser,
                               self.progress)
        self.progress.text = 'Searching for clips'
        self.progress.pct = 0.0
        self.clips.search()
        self.progress.text = ''
        self.progress.pct = 0.0

    def add_to_tree_view(self, view: tkinter.ttk.Treeview, directory: Directory,
                         parent: str = '') -> None:
        """Add directory contents to a TreeView widget"""
        for sub_dir in directory.subdirectories:
            item_id = view.insert(parent, 'end', str(sub_dir.ref_id),
                                  values=(sub_dir.title, ''), open=False)
            self.add_to_tree_view(view, sub_dir, item_id)
        for song in directory.songs:
            view.insert(parent, 'end', str(song.ref_id),
                        values=(song.title, song.artist))

    def generate_bingo_game(self):
        """
        generate tickets and mp3.
        called on pressing the generate game button
        """
        self.options.number_of_cards = int(self.tickets_number_entry.get().strip())
        self.options.mode = GameMode.BINGO
        game_id = self.game_name_entry.get().strip()
        self.options.game_id = game_id
        self.options.colour_scheme = self.variables.colour.get()

        try:
            GameGenerator.check_options(self.options, self.game_songs)
        except ValueError as err:
            tkinter.messagebox.showerror(title="Invalid settings",
                                         message=str(err))
            return

        extra = ""
        num_songs = len(self.game_songs)
        if num_songs < 45:
            extra = "\nNOTE: At least 45 songs is recommended"

        question_msg = ''.join([
            "Are you sure you want to generate a bingo game with ",
            f"{self.options.number_of_cards} tickets and the ",
            f"{num_songs} songs in the white box on the right?",
            extra,
            "\nThis process might take a few minutes.",
        ])
        answer = tkinter.messagebox.askquestion("Are you sure?", question_msg)
        if answer != 'yes':
            return
        self.buttons.disable()
        self.variables.progress_text.set(f"Generating Bingo Game - {game_id}")
        self.bg_thread = threading.Thread(
            target=self.generate_bingo_tickets_and_mp3_thread)
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_bingo_tickets_and_mp3_thread(self):
        """Creates MP3 file and PDF files.
        This function runs in its own thread
        """
        gen = GameGenerator(self.options, self.mp3editor, self.docgen,
                            self.progress)
        try:
            gen.generate(self.game_songs)
            self.progress.text = f"Finished Generating Bingo Game: {self.options.game_id}"
        except ValueError as err:
            self.progress.text = str(err)
        finally:
            self.progress.pct = 100.0

    def _poll_progress(self):
        """Checks progress of encoding thread and updates progress bar.
        Other threads are not allowed to update Tk components, so this
        function (which runs in the main thread) is used to update the
        progress bar and to detect when the thread has finished.
        """
        if not self.bg_thread:
            return
        #pct = self.progress.pct / float(self.progress.phase[1])
        #pct += float(self.progress.phase[0] - 1)/float(self.progress.phase[1])
        self.variables.progress_pct.set(self.progress.total_percentage)
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
        self.bg_status = BackgroundOperation.IDLE
        self.variables.progress_pct.set(0.0)

    def generate_clips(self):
        """Generate all clips for all selected Songs in a new thread.
        Creates a new thread and uses that thread to create clips of
        every selected Song.
        It will take the start time and duration values from the GUI fields
        and create a "duration" length clip starting at "start_time_entry"
        in the "NewClips" directory, using the name and directory of the
        source MP3 file as its filename.
        """
        if not self.game_songs:
            return
        self.options.mode = GameMode.CLIP
        self.buttons.disable()
        self.bg_status = BackgroundOperation.GENERATING_CLIPS
        self.bg_thread = threading.Thread(target=self.generate_clips_thread)
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_clips_thread(self):
        """Generate all clips for all selected Songs
        This function runs in its own thread
        """
        gen = ClipGenerator(self.options, self.mp3editor, self.progress)
        start = Duration.parse(self.start_time_entry.get())
        end = start + Duration.parse(self.duration_entry.get())
        gen.generate(self.game_songs, start, end)

def main():
    """main loop"""
    root = tk.Tk()
    root.resizable(0, 0)
    root.wm_title("Music Bingo Game Generator")
    ico_file = Assets.icon_file()
    if ico_file.exists():
        if sys.platform.startswith('win'):
            root.iconbitmap(str(ico_file))
        else:
            logo = tk.PhotoImage(file=str(ico_file))
            root.call('wm', 'iconphoto', root._w, logo)
    options = Options.parse(sys.argv[1:])
    MainApp(root, options)
    root.mainloop()
