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
import collections
import datetime
from pathlib import Path
import json
import logging
import os
import secrets
import sys
from typing import Any, Callable, Dict, List, Optional, Set, Type, cast

import tkinter as tk  # pylint: disable=import-error
import tkinter.messagebox  # pylint: disable=import-error
import tkinter.constants  # pylint: disable=import-error
import tkinter.filedialog  # pylint: disable=import-error
import tkinter.ttk  # pylint: disable=import-error

from musicbingo import models, workers
from musicbingo.assets import Assets
from musicbingo.directory import Directory
from musicbingo.generator import GameGenerator
from musicbingo.models.importer import Importer, JsonObject
from musicbingo.models.modelmixin import PrimaryKeyMap
from musicbingo.options import GameMode, Options
from musicbingo.progress import Progress
from musicbingo.palette import Palette
from musicbingo.song import Song
from musicbingo.utils import to_iso_datetime

from .actionpanel import ActionPanel, ActionPanelCallbacks
from .clipspanel import GenerateClipsPanel
from .gamepanel import GenerateGamePanel
from .infopanel import InfoPanel
from .optionvar import OptionVar
from .panel import Panel
from .quizpanel import GenerateQuizPanel
from .selectiondialog import SelectOption, ask_selection
from .songspanel import SelectedSongsPanel, SongsPanel

# pylint: disable=too-many-instance-attributes

MenuContainer = collections.namedtuple('MenuContainer', ['file', 'db', 'mode'])

class TrackFacade:
    """
    Implements the same interface as models.Track but without using the
    database
    """
    def __init__(self, item: JsonObject, songs: Dict[int, Song]):
        for key, value in item.items():
            setattr(self, key, value)
        self.song = songs[item["song"]]
        self.song_pk = item["song"]


class GameFacade:
    """
    Implements the same interface as models.Game but without using the
    database
    """
    def __init__(self, data: JsonObject):
        # pylint: disable=invalid-name
        self.pk = data["Games"][0]["pk"]
        self.id = data["Games"][0]["id"]
        self.title = data["Games"][0]["title"]
        self.start = data["Games"][0]["start"]
        self.end = data["Games"][0]["end"]
        self.options = data["Games"][0].get("options", None)
        self.tracks: List[TrackFacade] = []
        directories: Dict[int, Directory] = {}
        for item in data["Directories"]:
            direc = Directory(parent=None, directory=Path(item["name"]),
                              ref_id=item["pk"])
            directories[item["pk"]] = direc
        songs: Dict[int, Song] = {}
        for item in data["Songs"]:
            parent = directories[item["directory"]]
            del item["directory"]
            if 'classtype' in item:
                del item['classtype']
                pk = item["pk"]
            del item["pk"]
            song = Song(ref_id=pk, parent=parent, **item)
            song.pk = pk # type: ignore
            songs[pk] = song
        for item in data["Tracks"]:
            self.tracks.append(TrackFacade(item, songs))

class MainApp(ActionPanelCallbacks):
    """The GUI of the program.
    It also contains all the functions used in generating the bingo tickets.
    """
    #pylint: disable=too-many-statements

    def __init__(self, root_elt: tk.Tk, options: Options):
        self.root = root_elt
        self.options = options
        self._sort_by_title_option = True
        self.clips: Directory = Directory(None, Path(''))
        self.poll_id: Optional[str] = None
        self.dest_directory: str = ''
        self.threads: List[workers.BackgroundWorker] = []
        self.previous_games_songs: Set[int] = set()  # uses hash of song
        self.base_game_id: str = datetime.date.today().strftime("%y-%m-%d")
        self.current_game_filename: Optional[str] = None

        self.main = tk.Frame(root_elt, bg=Panel.NORMAL_BACKGROUND)
        self.menu = self.create_main_menu(root_elt, options)

        self.available_songs_panel = SongsPanel(self.main, self.options,
                                                self.add_selected_songs_to_game)
        self.action_panel = ActionPanel(self.main, self)
        self.selected_songs_panel = SelectedSongsPanel(self.main,
                                                       self.options,
                                                       self.play_song)
        self.game_panel = GenerateGamePanel(self.main, self.options,
                                            self.generate_bingo_game)
        self.quiz_panel = GenerateQuizPanel(self.main, self.generate_music_quiz)
        self.clip_panel = GenerateClipsPanel(self.main, self.options,
                                             self.generate_clips)
        self.info_panel = InfoPanel(self.main)
        self.panels = [
            self.available_songs_panel, self.action_panel,
            self.selected_songs_panel, self.game_panel,
            self.quiz_panel, self.clip_panel, self.info_panel,
        ]

        self.main.pack(side=tk.TOP, fill=tk.BOTH, expand=True, ipadx=5, ipady=5)
        self.available_songs_panel.grid(row=0, column=0, padx=0)
        self.action_panel.grid(row=0, column=1, padx=5)
        self.selected_songs_panel.grid(row=0, column=2)

        self.generate_unique_game_id()
        self.set_mode(self.options.mode)
        self.search_clips_directory()

    def create_main_menu(self, root_elt: tk.Tk, options: Options) -> MenuContainer:
        """
        Create the top level menu widget
        """
        menu = tk.Menu(root_elt)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Load game",
                              command=self.ask_open_game_from_file)
        file_menu.add_command(label="Save game", state=tk.DISABLED,
                              command=self.save_game_to_file)
        file_menu.add_command(label="Save game as ...",
                              command=self.ask_save_game_to_file)
        file_menu.add_separator()
        file_menu.add_command(label="Select clip source",
                              command=self.ask_select_source_directory)
        file_menu.add_command(label="Select new clip destination",
                              command=self.ask_select_clip_destination)
        file_menu.add_command(label="Select new game destination",
                              command=self.ask_select_game_destination)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root_elt.quit)
        menu.add_cascade(label="File", menu=file_menu)

        game_mode = OptionVar(self.main, options, "mode", GameMode,
                              command=self.set_mode)

        db_menu = tk.Menu(menu, tearoff=False)
        db_menu.add_command(label="Open game",
                            command=self.ask_open_game_from_database)
        db_menu.add_command(label="Import database",
                            command=self.ask_import_database)
        db_menu.add_command(label="Export database",
                            command=self.ask_export_database)
        menu.add_cascade(label="Database", menu=db_menu)

        mode_menu = tk.Menu(menu, tearoff=False)
        mode_menu.add_radiobutton(label="Bingo Game",
                                  value=GameMode.BINGO.value,
                                  variable=game_mode)
        mode_menu.add_radiobutton(label="Music Quiz", value=GameMode.QUIZ.value,
                                  variable=game_mode)
        mode_menu.add_radiobutton(label="Clip generation",
                                  value=GameMode.CLIP.value,
                                  variable=game_mode)
        menu.add_cascade(label="Mode", menu=mode_menu)
        root_elt.config(menu=menu)
        return MenuContainer(file_menu, db_menu, mode_menu)

    def set_mode(self, mode: GameMode) -> None:
        """
        Update current mode operating mode (game, quiz, clip)
        """
        for panel in [self.game_panel,
                      self.quiz_panel,
                      self.clip_panel,
                      self.info_panel]:
            panel.forget()
        if mode == GameMode.BINGO:
            self.game_panel.grid(row=1, column=0, columnspan=3, pady=5, padx=10,
                                 sticky=tk.E + tk.W)
        elif mode == GameMode.QUIZ:
            self.quiz_panel.grid(row=1, column=0, columnspan=3, pady=5, padx=10,
                                 sticky=tk.E + tk.W)
        else:  # mode == GameMode.CLIP
            self.clip_panel.grid(row=1, column=0, columnspan=3, pady=5, padx=10,
                                 sticky=tk.E + tk.W)
        self.info_panel.grid(row=2, column=0, columnspan=3, pady=5,
                             padx=10, sticky=tk.E + tk.W)

    def generate_unique_game_id(self):
        """Create unique game ID.
        Checks the "./Bingo Games" directory to make sure that the
        generated game ID does not already exist
        """
        game_num = 1
        def game_id(num):
            return f"{self.base_game_id}-{num}"
        self.previous_games_songs.clear()
        #clashes: Set[str] = set()
        games_dest = self.options.game_destination_dir()
        for subdir in [Path(x[0]) for x in os.walk(games_dest)]:
            if subdir == games_dest:
                continue
            if subdir.name.startswith(game_id(game_num)):
                self.load_previous_game_songs(subdir)
                # clashes.append(subdir.name)
        while self.options.game_destination_dir(game_id(game_num)).exists():
            game_num += 1
        self.game_panel.set_game_id(game_id(game_num))
        self.action_panel.set_num_previous_songs(len(self.previous_games_songs))

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
                # should be possible to search for song in self.clips
                song = Song(filename.name, parent=None, ref_id=index, **song)
                self.previous_games_songs.add(hash(song))

    def ask_save_game_to_file(self):
        """
        Save current game data to a JSON file
        """
        filename = tkinter.filedialog.asksaveasfilename(
            initialdir=self.options.games_dest, title="Save game file",
            filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if not filename:
            return
        self.current_game_filename = filename
        self.menu.file.entryconfig('Save game', state=tk.NORMAL)
        self.set_root_title(filename)
        self.save_game_to_file()

    def save_game_to_file(self):
        """
        Save a previously saved game JSON file
        """
        filename = self.current_game_filename
        if filename is None:
            return
        options = self.options.to_dict(
            only={'bitrate', 'cards_per_page', 'checkbox', 'colour_scheme',
                  'columns', 'crossfade', 'doc_per_page', 'include_artist',
                  'number_of_cards', 'include_artist'})
        start = datetime.datetime.now()
        end = start + datetime.timedelta(days=30)
        result = {
            "BingoTickets": [],
            "Games": [
                {
                    "end": to_iso_datetime(end),
                    "id": self.game_panel.game_id,
                    "options": options,
                    "pk": 1,
                    "start": to_iso_datetime(start),
                    "title": self.selected_songs_panel.get_title()
                }
            ],
            "Tracks": [],
        }
        start_time = 0
        for index, song in enumerate(self.selected_songs_panel.all_songs()):
            track = song.to_dict(exclude={'ref_id'})
            track["number"] = index
            track["pk"] = song.ref_id
            track["start_time"] = start_time
            start_time += song.duration
            result["Tracks"].append(track)
        fname = Path(filename).with_suffix('.json')
        with fname.open('wt') as json_file:
            json.dump(result, json_file)

    def ask_open_game_from_file(self):
        """
        load a previous game from a file
        """
        filename = tkinter.filedialog.askopenfilename(
            initialdir=self.options.games_dest, title="Select game file",
            filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if not filename:
            return
        self.current_game_filename = filename
        self.menu.file.entryconfig('Save game', state=tk.NORMAL)
        self.set_root_title(filename)
        with models.db.session_scope() as session:
            imp = Importer(self.options, session, Progress())
            game_id = imp.detect_game_id_from_filename(Path(filename))
            data = imp.translate_game_tracks(Path(filename), game_id)
            game = GameFacade(data)
            self.load_game(session, game)

    def set_root_title(self, filename: str) -> None:
        """
        Set the title of the top level frame
        """
        self.root.wm_title("Music Bingo Game Generator - {0}".format(
            Path(filename).name))

    def ask_select_source_directory(self):
        """Ask user for clip source directory.
        Called when the select_source_directory button is pressed
        """
        chosen = tkinter.filedialog.askdirectory(mustexist=True)
        if not chosen:
            return
        self.options.clip_directory = chosen
        self.available_songs_panel.clear()
        self.search_clips_directory()

    def ask_select_clip_destination(self):
        """
        Ask user for new clip destination directory.
        """
        new_dest = tkinter.filedialog.askdirectory()
        if new_dest:
            self.options.new_clips_dest = new_dest

    def ask_select_game_destination(self):
        """
        Ask user for new Bingo game destination directory.
        """
        new_dest = tkinter.filedialog.askdirectory()
        if new_dest:
            self.options.games_dest = new_dest

    def ask_open_game_from_database(self):
        """
        Ask user to select a previous game from the database
        """
        games: List[SelectOption] = []
        with models.db.session_scope() as session:
            for game in session.query(models.Game.id, models.Game.title).order_by(models.Game.id):
                games.append(SelectOption(f'{game.id}: {game.title}', game.id))
        selected = ask_selection(self.root, 'Select game', games)
        if not selected:
            return
        with models.db.session_scope() as session:
            game = models.Game.get(session, id=selected)
            if game:
                self.load_game(session, game)

    def ask_import_database(self):
        """
        Import a complete database from a JSON export
        """
        filename = tkinter.filedialog.askopenfilename(
            initialdir=self.options.games_dest, title="Select game file",
            filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if not filename:
            return
        self.start_background_worker(
            workers.ImportDatabase, self.import_database_done, Path(filename))

    def import_database_done(self, result: workers.DbIoResult):
        """
        Called when importing database has completed
        """
        assert result.added is not None
        total = sum(result.added.values())
        assert result.filename is not None
        filename = result.filename.name
        self.info_panel.text = f'Added {total} database items from {filename}'

    def ask_export_database(self):
        """
        Save entire database to a JSON file
        """
        filename = tkinter.filedialog.asksaveasfilename(
            initialdir=self.options.games_dest, title="Save game file",
            filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if not filename:
            return
        self.start_background_worker(
            workers.ExportDatabase, self.export_database_done, Path(filename),
            self.options)

    def export_database_done(self, result):
        """
        Called when exporting database has completed
        """
        self.info_panel.text = f'Exported database to {result}'

    def load_game(self, session: models.DatabaseSession, game: models.Game) -> None:
        """
        Load a previous game into the GUI using a game from the database
        """
        self.selected_songs_panel.clear()
        self.game_panel.set_game_id(game.id)
        if game.options:
            for key, value in game.options.items():
                if hasattr(self.options, key):
                    setattr(self.options, key, value)
            palette = Palette[game.options['colour_scheme'].upper()]
            self.game_panel.set_palette(palette)
            self.game_panel.num_tickets.set(game.options['number_of_cards'])
        pk_maps: PrimaryKeyMap = {}
        for track in game.tracks:
            song = self.available_songs_panel.get_song(track.song.pk)
            if song:
                self.selected_songs_panel.add_song(song)
                continue
            item = track.song.to_dict(exclude={'directory'})
            count, songs = models.Song.search_for_songs(session, pk_maps, item)
            if count == 0:
                continue
            for db_song in songs:
                song = self.available_songs_panel.get_song(db_song.pk)
                if song:
                    self.selected_songs_panel.add_song(song)
                    break
        self.selected_songs_panel.set_title(game.title)

    def add_selected_songs_to_game(self, selections: Optional[List[Song]] = None):
        """add the selected songs from the source list to the game"""
        if selections is None:
            selections = self.available_songs_panel.selections(True)
        for song in selections:
            self.available_songs_panel.hide_song(song)
            self.selected_songs_panel.add_song(song)

    def add_random_songs_to_game(self, amount: int = 5) -> None:
        """add random songs (if available) to the game list"""
        selections = self.available_songs_panel.selections(False)
        songs: Dict[int, Song] = {}
        already_chosen = self.selected_songs_panel.get_song_ids()
        for song in selections:
            if (hash(song) not in self.previous_games_songs and
                    song.ref_id not in already_chosen):
                songs[song.ref_id] = song
        todo = min(len(songs), amount)
        ref_ids: List[int] = list(songs.keys())
        while songs and todo > 0:
            ref_id = secrets.choice(ref_ids)
            ref_ids.remove(ref_id)
            song = songs[ref_id]
            self.available_songs_panel.hide_song(song)
            self.selected_songs_panel.add_song(song)
            todo -= 1

    def remove_song_from_game(self):
        """
        remove the selected song from the game list and
        return it to the main list.
        """
        selections = self.selected_songs_panel.selections(True)
        if not selections:
            return
        for song in selections:
            self.selected_songs_panel.remove_song(song)
            self.available_songs_panel.restore_song(song)

    def remove_all_songs_from_game(self):
        """remove all of the songs from the game list"""
        num_songs = len(self.selected_songs_panel.get_song_ids())
        if num_songs == 0:
            return
        if num_songs > 1:
            question = f"Are you sure you want to remove all {num_songs} songs from the game?"
            answer = tkinter.messagebox.askquestion("Are you sure?", question)
            if answer != 'yes':
                return
        self.selected_songs_panel.clear()
        self.available_songs_panel.restore_all()

    def toggle_exclude_artists(self):
        """toggle the "exclude artists" setting"""
        self.options.include_artist = not self.options.include_artist
        if self.options.include_artist:
            text = "Include Artist Names"
        else:
            text = "Exclude Artist Names"
        self.action_panel.toggle_artist.config(text=text)

    def add_available_songs_to_treeview(self):
        """adds every available song to the "available songs" Tk Treeview"""
        name = self.options.clips().name
        self.available_songs_panel.set_title(f"Available Songs: {name}")
        if self.options.create_index:
            self.clips.create_index("song_index.csv")
        self.available_songs_panel.add_directory(self.clips)
        for song in self.selected_songs_panel.all_songs():
            try:
                self.available_songs_panel.remove_song(song)
            except KeyError:
                pass
        self.available_songs_panel.sort(('filename', 'title',))

    def sort_by_artists(self):
        """sort both the song list and game song list by artist"""
        self._sort_by_title_option = False
        self.available_songs_panel.sort('artist')
        self.selected_songs_panel.sort('artist')

    def sort_by_title(self):
        """sort both the song list and game song list by title"""
        self._sort_by_title_option = True
        self.available_songs_panel.sort('title')
        self.selected_songs_panel.sort('title')

    def disable_panels(self):
        """disable all panels"""
        for panel in self.panels:
            panel.disable()

    def enable_panels(self):
        """enable all panels"""
        for panel in self.panels:
            panel.enable()

    def search_clips_directory(self):
        """
        Start thread to search for songs and sub-directories.
        """
        self.disable_panels()
        self.start_background_worker(workers.SearchForClips,
                                     self.finalise_search_clips_directory,
                                     self.options.clips())

    def finalise_search_clips_directory(self, result: Any) -> None:
        """
        Put all discovered songs into the available songs panel.
        This function is called from the main thread
        """
        if result is not None:
            self.clips = cast(Directory, result)
        self.add_available_songs_to_treeview()
        self.info_panel.text = ''
        self.info_panel.pct = 0
        self.info_panel.pct_text = ''
        self.enable_panels()

    def start_background_worker(self, worker: Type[workers.BackgroundWorker],
                                finalise: Callable[[workers.BackgroundWorker], None],
                                *args):
        """
        Start a worker thread with the specified arguments.
        When the worker has finished, the finalise() method will be
        called from the main thread, which can be used to update UI
        components.
        """
        work = worker(args, self.options, finalise)
        self.threads.append(work)
        work.start()
        self._poll_progress()

    def generate_bingo_game(self):
        """
        generate tickets and mp3.
        called on pressing the generate game button
        """
        for worker in self.threads:
            if isinstance(worker, workers.GenerateBingoGame):
                worker.abort()
                return

        self.options.mode = GameMode.BINGO
        self.options.game_id = self.game_panel.game_id
        self.options.palette = self.game_panel.palette
        self.options.title = self.selected_songs_panel.get_title()

        game_songs = self.selected_songs_panel.all_songs()

        try:
            GameGenerator.check_options(self.options, game_songs)
        except ValueError as err:
            tkinter.messagebox.showerror(title="Invalid settings",
                                         message=str(err))
            return

        extra = ""
        num_songs = len(game_songs)
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
        self.disable_panels()
        self.game_panel.set_generate_button("Stop Generating Game")
        self.info_panel.text = f"Generating Bingo Game - {self.options.game_id}"
        self.start_background_worker(workers.GenerateBingoGame,
                                     self.finalise_generate_bingo_game,
                                     game_songs)

    def finalise_generate_bingo_game(self, _: Any) -> None:
        """generate a new game ID"""
        self.enable_panels()
        self.game_panel.set_generate_button("Generate Bingo Game")
        self.generate_unique_game_id()

    def generate_music_quiz(self):
        """
        generate mp3 for a music quiz.
        called on pressing the generate quiz button
        """
        for worker in self.threads:
            if isinstance(worker, workers.GenerateBingoGame):
                worker.abort()
                return

        self.options.mode = GameMode.QUIZ

        game_songs = self.selected_songs_panel.all_songs()

        try:
            GameGenerator.check_options(self.options, game_songs)
        except ValueError as err:
            tkinter.messagebox.showerror(title="Invalid settings",
                                         message=str(err))
            return

        num_songs = len(game_songs)
        question_msg = ''.join([
            "Are you sure you want to generate a music quiz with ",
            f"{num_songs} songs in the white box on the right?",
        ])
        answer = tkinter.messagebox.askquestion("Are you sure?", question_msg)
        if answer != 'yes':
            return
        self.disable_panels()
        self.info_panel.text = "Generating music quiz"
        self.quiz_panel.set_generate_button("Stop Generating")
        self.start_background_worker(workers.GenerateBingoGame,
                                     self.finalise_generate_music_quiz,
                                     game_songs)

    def finalise_generate_music_quiz(self, _: Any) -> None:
        """generate a new game ID"""
        self.enable_panels()
        self.quiz_panel.set_generate_button("Generate Music Quiz")
        self.generate_unique_game_id()

    def _poll_progress(self) -> None:
        """Checks progress of encoding thread and updates progress bar.
        Other threads are not allowed to update Tk components, so this
        function (which runs in the main thread) is used to update the
        progress bar and to detect when the thread has finished.
        """
        if not self.threads:
            return
        pct: float = 0
        pct_text: Optional[str] = None
        done: List[workers.BackgroundWorker] = []
        for worker in self.threads:
            if self.info_panel.text != worker.progress.text:
                self.info_panel.text = worker.progress.text
            if worker.progress.pct_text:
                pct_text = worker.progress.pct_text
            if not worker.bg_thread.is_alive():
                worker.bg_thread.join()
                worker.finalise(worker.result)
                done.append(worker)
                pct += 100
            else:
                pct += worker.progress.total_percentage
        if len(self.threads) > len(done):
            pct /= float(len(self.threads))
            self.info_panel.pct = pct
            if pct_text is not None:
                self.info_panel.pct_text = pct_text
            elif pct >= 0.1:
                self.info_panel.pct_text = '{0:0.2f}%'.format(pct)
        for worker in done:
            self.threads.remove(worker)
        self.poll_id = self.root.after(250, self._poll_progress)

    def generate_clips(self) -> None:
        """
        Generate all clips for all selected Songs in a new thread.
        Creates a new thread and uses that thread to create clips of
        every selected Song.
        It will take the start time and duration values from the GUI fields
        and create a "duration" length clip starting at "start_time_entry"
        in the "NewClips" directory, using the name and directory of the
        source MP3 file as its filename.
        """
        for worker in self.threads:
            if isinstance(worker, workers.GenerateClips):
                worker.abort()
                return
        game_songs = self.selected_songs_panel.all_songs()
        if not game_songs:
            return
        self.options.mode = GameMode.CLIP
        self.disable_panels()
        self.clip_panel.set_generate_button("Stop Generating")
        self.start_background_worker(workers.GenerateClips,
                                     self.finalise_generate_clips,
                                     game_songs)

    def finalise_generate_clips(self, _: Any) -> None:
        """called when clip generation complete"""
        self.enable_panels()
        self.clip_panel.set_generate_button("Generate clips")
        self.info_panel.text = 'Finished generating clips'
        self.info_panel.pct_text = ''

    def start_stop_playback(self) -> None:
        """
        Toggle between playing songs and aborting playback.
        If nothing is playing, play all selected songs.
        If songs are playing, stop playback.
        """
        playing = self.stop_playback()
        if not playing:
            songs = self.selected_songs_panel.selections(True)
            if not songs:
                songs = self.available_songs_panel.selections(True)
            self.play_song(songs)

    def play_song(self, songs: List[Song]) -> None:
        """play the given song in the background"""
        self.stop_playback()
        if songs:
            self.action_panel.set_play_button('Stop playback')
            self.start_background_worker(workers.PlaySong,
                                         self.finalise_play_song,
                                         songs)

    def finalise_play_song(self, _: Any) -> None:
        """called when songs have finished playing"""
        self.info_panel.text = ''
        self.info_panel.pct_text = ''
        self.info_panel.pct = 0.0
        self.action_panel.set_play_button('Play Songs')

    def stop_playback(self) -> bool:
        """abort playback of any currently playing song"""
        playing = False
        for worker in self.threads:
            if isinstance(worker, workers.PlaySong):
                worker.abort()
                playing = True
        return playing

    @classmethod
    def mainloop(cls):
        """main loop"""
        log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
        logging.basicConfig(format=log_format)
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
        models.db.DatabaseConnection.bind(options.database, debug=False)
        MainApp(root, options)
        root.mainloop()
