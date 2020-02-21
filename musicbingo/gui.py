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
from abc import ABC, abstractmethod
import enum
import datetime
from functools import partial
from pathlib import Path
import json
import os
import secrets
import sys
import threading
from typing import Callable, Dict, List, Optional, Set, Tuple, Type, Union, cast

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

class OptionVar(tk.Variable):
    """
    Wraps a property of Options as a tk.Variable that will automatically
    keep the option and the tk.Variable in sync.
    """
    def __init__(self, parent: tk.Frame, options: Options, prop_name: str,
                 prop_type: Type, command: Optional[Callable] = None) -> None:
        value = prop_type(getattr(options, prop_name))
        super(OptionVar, self).__init__(parent, value=value,
                                        name=f'PV_VAR_{prop_name}')
        self.options = options
        self.prop_name = prop_name
        self.prop_type = prop_type
        self.command = command
        self.trace_add("write", self._on_set) # type: ignore

    def set(self, value):
        setattr(self.options, self.prop_name, value)
        super(OptionVar, self).set(value)

    def _on_set(self, *args): #pylint: disable=unused-argument
        value = self.get()
        if not isinstance(value, self.prop_type):
            value = self.prop_type(value)
        setattr(self.options, self.prop_name, value)
        if self.command is not None:
            self.command(value)

class Panel(ABC):
    """base class for all panels"""
    BTN_SUCCESS = "#63ff5f"
    BTN_WARNING = "#ff9090"
    BTN_DANGER = "#ff5151"
    BANNER_BACKGROUND = "#222"
    NORMAL_BACKGROUND = "#343434"
    ALTERNATE_COLOUR = "#282828"
    TYPEFACE = "Arial"

    def __init__(self, main: tk.Frame) -> None:
        self.frame = tk.Frame(main, bg=self.NORMAL_BACKGROUND)

    def grid(self, **kwargs) -> None:
        """
        Use grid layout on top level frame of this panel
        """
        self.frame.grid(**kwargs)

    def forget(self) -> None:
        """
        Remove frame from layout
        """
        if self.frame.winfo_manager():
            self.frame.grid_forget()

    @abstractmethod
    def enable(self):
        """enable this panel"""
        raise NotImplementedError()

    @abstractmethod
    def disable(self):
        """disable this panel"""
        raise NotImplementedError()

#pylint: disable=too-many-instance-attributes
class SongsPanel(Panel):
    """
    Panel used for both available songs and songs in game
    """

    FOOTER_TEMPLATE = r"{num_songs} songs available ({duration})"
    COLUMNS = ("filename", "title", "artist", "album", "duration",)
    DISPLAY_COLUMNS = ('title', 'artist',)

    def __init__(self, main: tk.Frame) -> None:
        super(SongsPanel, self).__init__(main)
        self.inner = tk.Frame(self.frame)
        self._duration: int = 0
        self._num_songs: int = 0
        self._data: Dict[int, Union[Directory, Song]] = {}
        self._hidden: Set[int] = set()
        self._sorting: Tuple[str, bool] = ('', True)
        scrollbar = tk.Scrollbar(self.inner)
        self.tree = tkinter.ttk.Treeview(
            self.inner, columns=self.COLUMNS,
            displaycolumns=self.DISPLAY_COLUMNS,
            height=20,
            yscrollcommand=scrollbar.set)
        self.tree.column('#0', width=20, anchor='center')
        for column in self.DISPLAY_COLUMNS:
            self.tree.column(column, width=200, anchor='center')
            self.tree.heading(column, text=column.title(),
                              command=partial(self.sort, column, True))
        scrollbar.config(command=self.tree.yview)
        self.title = tk.Label(
            self.frame, text='',
            padx=5, bg=self.NORMAL_BACKGROUND, fg="#FFF",
            font=(self.TYPEFACE, 16))
        self.footer = tk.Label(
            self.frame, text='', padx=5, bg=self.NORMAL_BACKGROUND,
            fg="#FFF", font=(self.TYPEFACE, 14))
        self.tree.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.title.pack(side=tk.TOP, pady=10)
        self.inner.pack(side=tk.TOP, pady=10)
        self.footer.pack(side=tk.BOTTOM)

    def disable(self):
        """disable panel"""
        self.tree.state(("disabled",))

    def enable(self):
        """enable panel"""
        self.tree.state(("!disabled",))

    def add_directory(self, directory: Directory) -> None:
        """Add directory contents to the TreeView widget"""
        self._add_directory(directory, '')
        self._update_footer()

    def _add_directory(self, directory: Directory, parent: str) -> None:
        """
        Internal API used for adding directory contents to the TreeView widget
        """
        for sub_dir in directory.subdirectories:
            item_id = self.tree.insert(
                parent, 'end', str(sub_dir.ref_id),
                values=(sub_dir.filename, sub_dir.title, '', '', '',),
                open=False)
            self._add_directory(sub_dir, item_id)
        self._data[directory.ref_id] = directory
        for song in directory.songs:
            self._data[song.ref_id] = song
            self.tree.insert(parent, 'end', str(song.ref_id),
                             values=song.pick(self.COLUMNS))
            self._duration += int(song.duration)
            self._num_songs += 1

    def add_song(self, song: Song) -> None:
        """Add a song to this panel"""
        self._data[song.ref_id] = song
        self.tree.insert('', 'end', str(song.ref_id),
                         values=song.pick(self.COLUMNS))
        self._duration += int(song.duration)
        self._num_songs += 1
        self._update_footer()

    def clear(self):
        """remove all songs from Treeview"""
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)
        self._duration = Duration(0)
        self._num_songs = 0
        self._data = {}

    def hide_song(self, song: Song, update: bool = True) -> None:
        """
        Hide one song from this panel.
        @raises KeyError if song not in this panel
        """
        _ = self._data[song.ref_id]
        self._hidden.add(song.ref_id)
        self.tree.detach(str(song.ref_id))
        self._duration -= int(song.duration)
        self._num_songs -= 1
        if update:
            self._update_footer()

    def restore_all(self) -> None:
        """Restores all hidden songs"""
        songs = [self._data[ref_id] for ref_id in self._hidden]
        for song in songs:
            self.restore_song(cast(Song, song))

    def restore_song(self, song: Song, update: bool = True) -> None:
        """
        Restores a hidden song from this panel.
        @raises KeyError if song not in this panel
        """
        self._hidden.remove(song.ref_id)
        if song._parent is not None:
            parent = str(cast(Directory, song._parent).ref_id)
            if int(parent) not in self._data:
                parent = ''
        else:
            parent = ''
        songs: List[Union[Song, Directory]] = []
        if self.tree.exists(parent):
            songs = [self._data[int(rid)] for rid in self.tree.get_children(parent)]
        songs.append(song)
        column, reverse = self._sorting
        songs.sort(key=lambda s: getattr(s, column), reverse=reverse)
        index: int = 0
        for item in songs:
            if item.ref_id == song.ref_id:
                break
            index += 1
        try:
            self.tree.reattach(str(song.ref_id), parent, index)
        except tk.TclError as err:
            print(err)
            print(song.ref_id, parent, index)
            self.tree.insert(parent, 'end', str(song.ref_id),
                             values=song.pick(self.COLUMNS))

        self._duration += int(song.duration)
        self._num_songs += 1
        if update:
            self._update_footer()

    def remove_song(self, song: Song, update: bool = True) -> None:
        """
        Remove one song from this panel.
        @raises KeyError if song not in this panel
        """
        del self._data[song.ref_id]
        self.tree.delete(str(song.ref_id))
        self._duration -= int(song.duration)
        self._num_songs -= 1
        if update:
            self._update_footer()

    def remove_directory(self, directory: Directory,
                         update: bool = True) -> None:
        """
        Remove all songs from one directory from this panel.
        @raises KeyError if directory not in this panel
        """
        del self._data[directory.ref_id]
        self.tree.delete(str(directory.ref_id))
        for sub_dir in directory.subdirectories:
            try:
                self.remove_directory(sub_dir, False)
            except KeyError as err:
                print(err)
        for song in directory.songs:
            try:
                self.remove_song(song, False)
            except KeyError:
                pass
        if update:
            self._update_footer()

    def set_title(self, title: str) -> None:
        """Set the title at the top of this panel"""
        self.title.config(text=title)

    def get_title(self) -> str:
        """Get the title at the top of this panel"""
        return self.title.cget('text')

    def _update_footer(self):
        """
        Update the duration text at the bottom of the treeview.
        This function is called after any addition or removal of songs
        to/from the lists.
        """
        txt = self.FOOTER_TEMPLATE.format(
            num_songs=self._num_songs,
            duration=Duration(self._duration).format())
        self.footer.config(text=txt)

    def sort(self, column: Union[str, Tuple[str]], reverse: bool = False) -> None:
        """
        Sort whole tree.
        The sort is recursive, so that each level is individually
        sorted. The sort can be multi-level by specifying a tuple
        of column names.
        """
        if not isinstance(column, str):
            for col in column:
                self.sort(col, reverse)
            return
        self._sorting = (column, reverse)
        self._sort_level('', column, reverse)
        # update heading to sort in other direction if clicked upon
        if column in self.DISPLAY_COLUMNS:
            self.tree.heading(
                column, command=partial(self.sort, column, not reverse))

    def _sort_level(self, parent: str, column: str, reverse: bool) -> None:
        """
        Sort specified directory level and then any children of that
        level.
        """
        # create tuple of the value of selected column + its ID for
        # each item at this level of the tree
        has_children = False
        pairs: List[Tuple[str, str]] = []
        for ref_id in self.tree.get_children(parent):
            value = Song.clean(self.tree.set(ref_id, column)).lower()
            pairs.append((value, ref_id,))
            children = self.tree.get_children(ref_id)
            if children:
                self._sort_level(ref_id, column, reverse)
                has_children = True

        if has_children and column != 'filename':
            return

        pairs.sort(reverse=reverse)

        # rearrange items into sorted positions
        for index, (_, ref_id) in enumerate(pairs):
            self.tree.move(ref_id, parent, index)

    def selections(self, focus: bool) -> List[Song]:
        """
        Return list of selected songs in this panel.
        If focus == true, only explictly selected items are returned
        If focus == false, all songs are returned if no items have
        been selected.
        """
        ref_ids = list(self.tree.selection())
        if not ref_ids:
            focus_elt = self.tree.focus()
            if focus and not focus_elt:
                return []
            if focus_elt:
                ref_ids = [focus_elt]
            else:
                ref_ids = self.tree.get_children()
        selections: List[Song] = []
        for rid in map(int, ref_ids):
            item = self._data[rid]
            if isinstance(item, Directory):
                selections += item.get_songs(rid)
            else:
                selections.append(item)
        return selections

    def all_songs(self) -> List[Song]:
        """get list of all songs in this panel"""
        songs: List[Song] = []
        for rid in map(int, self.tree.get_children()):
            item = self._data[rid]
            if isinstance(item, Directory):
                songs += cast(Directory, item).get_songs(rid)
            else:
                songs.append(item)
        return songs

    def get_song_ids(self) -> Set[int]:
        """get ref_id values for every song in panel"""
        return set(self._data.keys())


class SelectedSongsPanel(SongsPanel):
    """
    Panel used for songs in game
    """
    FOOTER_TEMPLATE = r"Songs in Game = {num_songs} ({duration})"

    def add_directory(self, directory: Directory) -> None:
        """Add directory contents to the TreeView widget"""
        super(SelectedSongsPanel, self).add_directory(directory)
        self.choose_title()

    def add_song(self, song: Song) -> None:
        """Add a song to this panel"""
        super(SelectedSongsPanel, self).add_song(song)
        self.choose_title()

    def remove_song(self, song: Song, update: bool = True) -> None:
        """
        Remove one song from this panel.
        @raises KeyError if song not in this panel
        """
        super(SelectedSongsPanel, self).remove_song(song, update)
        self.choose_title()

    def clear(self):
        """remove all songs from Treeview"""
        super(SelectedSongsPanel, self).clear()
        self.choose_title()

    def choose_title(self) -> None:
        """try to find a suitable title based upon the songs in the game"""
        folders: Set[str] = set()
        parents: Set[str] = set()
        for item in self._data.values():
            if not isinstance(item, Song):
                continue
            if item._parent is not None:
                folders.add(cast(Directory, item._parent).filename)
                if (item._parent._parent is not None and
                        item._parent._parent._parent is not None):
                    parents.add(cast(Directory, item._parent._parent).filename)
        if len(folders) == 1:
            self.set_title(folders.pop())
        elif len(parents) == 1:
            self.set_title(parents.pop())
        else:
            self.set_title('')

    def _update_footer(self):
        """
        Update the duration text at the bottom of the panel.
        This function is called after any addition or removal of songs
        to/from the lists.
        """
        if self._num_songs < 30:
            box_col = "#ff0000"
        elif self._num_songs < 45:
            box_col = "#fffa20"
        else:
            box_col = "#00c009"
        txt = self.FOOTER_TEMPLATE.format(
            num_songs=self._num_songs,
            duration=Duration(self._duration).format())
        self.footer.config(text=txt, fg=box_col)


class ActionPanel(Panel):
    """
    Panel containing all the action buttons.
    Action panel is the middle panel between the "available songs"
    and "selected songs" panels.
    """

    def __init__(self, app):
        super(ActionPanel, self).__init__(app.main)
        self.add_song = tk.Button(
            self.frame, text="Add Selected Songs",
            command=app.add_selected_songs_to_game, bg=self.BTN_SUCCESS)
        self.add_random_songs = tk.Button(
            self.frame, text="Add 5 Random Songs",
            command=app.add_random_songs_to_game, bg=self.BTN_SUCCESS)
        self.remove_song = tk.Button(
            self.frame, text="Remove Selected Songs",
            command=app.remove_song_from_game, bg=self.BTN_WARNING)
        self.remove_all_songs = tk.Button(
            self.frame, text="Remove All Songs",
            command=app.remove_all_songs_from_game, bg=self.BTN_DANGER)
        self.toggle_artist = tk.Button(
            self.frame, text="Exclude Artist Names",
            command=app.toggle_exclude_artists, bg=self.BTN_SUCCESS)
        self.previous_games_size = tk.Label(
            self.frame, font=(self.TYPEFACE, 16),
            bg=self.NORMAL_BACKGROUND, fg="#fff",
            text="Previous\ngames:\n0 songs",
            padx=6)
        self.add_song.grid(row=0, column=0, pady=10, sticky=tk.E+tk.W)
        self.add_random_songs.grid(row=1, column=0, pady=10, sticky=tk.E+tk.W)
        self.remove_song.grid(row=2, column=0, pady=10, sticky=tk.E+tk.W)
        self.remove_all_songs.grid(row=3, column=0, pady=10, sticky=tk.E+tk.W)
        self.toggle_artist.grid(row=4, column=0, pady=10, sticky=tk.E+tk.W)
        self.previous_games_size.grid(row=5, column=0, pady=10, sticky=tk.E+tk.W)

    def disable(self):
        """disable all buttons"""
        self.add_song.config(state=tk.DISABLED)
        self.add_random_songs.config(state=tk.DISABLED)
        self.remove_song.config(state=tk.DISABLED)
        self.remove_all_songs.config(state=tk.DISABLED)
        self.toggle_artist.config(state=tk.DISABLED)

    def enable(self):
        """enable all buttons"""
        self.add_song.config(state=tk.NORMAL)
        self.add_random_songs.config(state=tk.NORMAL)
        self.remove_song.config(state=tk.NORMAL)
        self.remove_all_songs.config(state=tk.NORMAL)
        self.toggle_artist.config(state=tk.NORMAL)
    def set_num_previous_songs(self, num_prev: int) -> None:
        """
        Set the label showing number of songs in previous games
        """
        plural = '' if num_prev == 1 else 's'
        txt = f"Previous\nGames:\n{num_prev} song{plural}"
        self.previous_games_size.config(text=txt)

class GenerateGamePanel(Panel):
    """
    Panel that contains all of the options for generating a
    Bingo game, plus the "Generate Bingo Game" button
    """

    def __init__(self, main: tk.Frame, options: Options,
                 generate_game: Callable) -> None:
        super(GenerateGamePanel, self).__init__(main)
        colour_label = tk.Label(self.frame, font=(self.TYPEFACE, 16),
                                text="Ticket Colour:",
                                bg=self.NORMAL_BACKGROUND,
                                fg="#FFF", padx=6)
        self.colour_combo = tkinter.ttk.Combobox(
            self.frame,
            state='readonly', font=(self.TYPEFACE, 16),
            values=tuple(map(str.title, Palette.colour_names())),
            width=8, justify=tk.CENTER)
        self.colour_combo.set(options.colour_scheme.title())
        game_name_label = tk.Label(self.frame, font=(self.TYPEFACE, 16),
                                   text="Game ID:", bg=self.NORMAL_BACKGROUND,
                                   fg="#FFF", padx=6)
        self.game_name_entry = tk.Entry(
            self.frame, font=(self.TYPEFACE, 16), width=10,
            justify=tk.CENTER)
        num_tickets_label = tk.Label(
            self.frame, font=(self.TYPEFACE, 16), text="Ticket Quantity:",
            bg=self.NORMAL_BACKGROUND, fg="#FFF", padx=6)
        self.num_tickets = OptionVar(self.frame, options, "number_of_cards", int)
        self.num_tickets_entry = tk.Spinbox(
            self.frame, font=(self.TYPEFACE, 16),
            textvariable=self.num_tickets, from_=GameGenerator.MIN_CARDS,
            to=199, width=5, justify=tk.CENTER)
        self.generate_cards = tk.Button(
            self.frame, text="Generate Bingo Game",
            command=generate_game, pady=0,
            font=(self.TYPEFACE, 18), bg="#00cc00")
        colour_label.grid(row=0, column=1)
        self.colour_combo.grid(row=0, column=2, sticky=tk.E+tk.W, padx=5)
        game_name_label.grid(row=0, column=3, padx=5)
        self.game_name_entry.grid(row=0, column=4, sticky=tk.E+tk.W, padx=5)
        num_tickets_label.grid(row=0, column=5)
        self.num_tickets_entry.grid(row=0, column=6, padx=5)
        self.generate_cards.grid(row=0, column=7, padx=20)

    def disable(self):
        """disable all widgets in this frame"""
        self.colour_combo.config(state=tk.DISABLED)
        self.game_name_entry.config(state=tk.DISABLED)
        self.num_tickets_entry.config(state=tk.DISABLED)
        self.generate_cards.config(state=tk.DISABLED)

    def enable(self):
        """enable all widgets in this frame"""
        self.colour_combo.config(state=tk.NORMAL)
        self.game_name_entry.config(state=tk.NORMAL)
        self.num_tickets_entry.config(state=tk.NORMAL)
        self.generate_cards.config(state=tk.NORMAL)

    def set_game_id(self, value: str) -> None:
        """set the current game ID"""
        self.game_name_entry.delete(0, len(self.game_name_entry.get()))
        self.game_name_entry.insert(0, value)

    def get_game_id(self) -> str:
        """Get the current game ID"""
        return self.game_name_entry.get()

    game_id = property(get_game_id, set_game_id)

    def get_palette(self) -> Palette:
        """get the selected colour scheme"""
        return Palette[self.colour_combo.get().upper()]

    def set_palette(self, scheme: Palette) -> None:
        """set the selected colour scheme"""
        self.colour_combo.set(scheme.name.title())

    palette = property(get_palette, set_palette)

class GenerateQuizPanel(Panel):
    """
    Panel that contains all of the options for generating a
    music quiz, plus the "Generate Quiz" button
    """

    def __init__(self, main: tk.Frame, generate_quiz: Callable) -> None:
        super(GenerateQuizPanel, self).__init__(main)
        self.generate_quiz = tk.Button(
            self.frame, text="Generate Music Quiz",
            command=generate_quiz, pady=0,
            font=(self.TYPEFACE, 18), bg="#00cc00")
        self.generate_quiz.pack(side=tk.RIGHT)

    def disable(self):
        """disable all widgets in this frame"""
        self.generate_quiz.config(state=tk.DISABLED)

    def enable(self):
        """enable all widgets in this frame"""
        self.generate_quiz.config(state=tk.NORMAL)


class GenerateClipsPanel(Panel):
    """Panel for the "generate clips" row"""
    def __init__(self, main: tk.Frame, options: Options,
                 generate_clips: Callable):
        super(GenerateClipsPanel, self).__init__(main)
        self.options = options
        clip_start_label = tk.Label(
            self.frame, font=(self.TYPEFACE, 16), text="Start time:",
            bg=self.NORMAL_BACKGROUND, fg="#FFF", padx=6)
        self.start_time = OptionVar(self.frame, options, "clip_start", str)
        start_time_entry = tk.Entry(
            self.frame, font=(self.TYPEFACE, 16), width=6,
            textvariable=self.start_time, justify=tk.RIGHT)
        #self.start_time_entry.insert(0, self.options.clip_start)

        clip_dur_label = tk.Label(
            self.frame, font=(self.TYPEFACE, 16), text="Duration:",
            bg=self.NORMAL_BACKGROUND, fg="#FFF", padx=6)
        self.duration = OptionVar(self.frame, options, "clip_duration", int)
        duration_entry = tk.Spinbox(self.frame, font=(self.TYPEFACE, 16),
                                    from_=1.0, to=60.0, wrap=False,
                                    textvariable=self.duration,
                                    width=5, justify=tk.CENTER)
        self.generate_clips = tk.Button(
            self.frame, text="Generate clips",
            command=generate_clips, pady=0,
            font=(self.TYPEFACE, 18), bg="#00cc00")
        self.generate_clips.pack(side=tk.RIGHT, padx=5)
        tk.Label(self.frame, bg=self.NORMAL_BACKGROUND).pack(side=tk.RIGHT,
                                                             padx=10)
        duration_entry.pack(side=tk.RIGHT, padx=5)
        clip_dur_label.pack(side=tk.RIGHT)
        tk.Label(self.frame, bg=self.NORMAL_BACKGROUND).pack(side=tk.RIGHT,
                                                             padx=10)
        start_time_entry.pack(side=tk.RIGHT)
        clip_start_label.pack(side=tk.RIGHT)


    def disable(self):
        """disable all buttons"""
        self.generate_clips.config(state=tk.DISABLED)

    def enable(self):
        """enable all buttons"""
        self.generate_clips.config(state=tk.NORMAL)


class InfoPanel(Panel):
    """Panel that contains progress info and progress bar"""
    def __init__(self, main: tk.Frame):
        super(InfoPanel, self).__init__(main)
        #self.frame = tk.Frame(main, bg=ALTERNATE_COLOUR, pady=5)
        self.progress_pct = tk.DoubleVar(self.frame)
        self.progress_text = tk.StringVar(self.frame, value="Example progress_text")
        self.info_text = tk.Label(
            self.frame, textvariable=self.progress_text,
            bg=self.BANNER_BACKGROUND, fg="#FFF", width=60,
            font=(self.TYPEFACE, 14), justify=tk.LEFT) #, anchor=tk.W)
        self.progressbar = tkinter.ttk.Progressbar(
            self.frame, orient=tk.HORIZONTAL, mode="determinate",
            variable=self.progress_pct, length=200, maximum=100.0)
        self.progressbar.pack(side=tk.RIGHT)
        self.info_text.pack(fill=tk.X)

    def get_text(self) -> str:
        """get contents of info label"""
        return self.progress_text.get()

    def set_text(self, value: str) -> None:
        """set contents of info label"""
        self.progress_text.set(value)

    text = property(get_text, set_text)

    def get_percentage(self) -> float:
        """get value of progress bar"""
        return self.progress_pct.get()

    def set_percentage(self, value: float) -> None:
        """set value of progress bar"""
        self.progress_pct.set(value)

    pct = property(get_percentage, set_percentage)

    def disable(self):
        """disable panel"""
        pass #pylint: disable=unnecessary-pass

    def enable(self):
        """enable panel"""
        pass #pylint: disable=unnecessary-pass


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
        self._local = threading.local()
        self.clips: Directory = Directory(None, 0, Path(''), NullMP3Parser(),
                                          self.progress)
        self.poll_id = None
        self.bg_status: BackgroundOperation = BackgroundOperation.IDLE
        self.dest_directory: str = ''
        self.previous_games_songs: Set[int] = set() # uses hash of song
        self.base_game_id: str = datetime.date.today().strftime("%y-%m-%d")

        self.main = tk.Frame(root_elt, bg=Panel.NORMAL_BACKGROUND)
        self.menu = tk.Menu(root_elt)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Select clip source",
                              command=self.ask_select_source_directory)
        file_menu.add_command(label="Select new clip destination",
                              command=self.ask_select_clip_destination)
        file_menu.add_command(label="Select new game destination",
                              command=self.ask_select_game_destination)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root_elt.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        game_mode = OptionVar(self.main, options, "mode", GameMode,
                              command=self.set_mode)

        mode_menu = tk.Menu(self.menu, tearoff=0)
        mode_menu.add_radiobutton(label="Bingo Game",
                                  value=GameMode.BINGO.value,
                                  variable=game_mode)
        mode_menu.add_radiobutton(label="Music Quiz", value=GameMode.QUIZ.value,
                                  variable=game_mode)
        mode_menu.add_radiobutton(label="Clip generation",
                                  value=GameMode.CLIP.value,
                                  variable=game_mode)
        self.menu.add_cascade(label="Mode", menu=mode_menu)

        root_elt.config(menu=self.menu)

        self.available_songs_panel = SongsPanel(self.main)
        self.action_panel = ActionPanel(self)
        self.selected_songs_panel = SelectedSongsPanel(self.main)
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

        self.main.pack(side=tk.TOP, fill=tk.BOTH, expand=1, ipadx=5, ipady=5)
        self.available_songs_panel.grid(row=0, column=0, padx=0)
        self.action_panel.grid(row=0, column=1, padx=5)
        self.selected_songs_panel.grid(row=0, column=2)

        self.generate_unique_game_id()
        self.set_mode(self.options.mode)
        self.search_clips_directory()

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
                                 sticky=tk.E+tk.W)
        elif mode == GameMode.QUIZ:
            self.quiz_panel.grid(row=1, column=0, columnspan=3, pady=5, padx=10,
                                 sticky=tk.E+tk.W)
        else: # mode == GameMode.CLIP
            self.clip_panel.grid(row=1, column=0, columnspan=3, pady=5, padx=10,
                                 sticky=tk.E+tk.W)
        self.info_panel.grid(row=2, column=0, columnspan=3, pady=5,
                             padx=10, sticky=tk.E+tk.W)

    @property
    def mp3editor(self) -> MP3Editor:
        """get MP3Editor instance, creating if required"""
        if getattr(self._local, "mp3editor", None) is None:
            self._local.mp3editor = MP3Factory.create_editor()
        return self._local.mp3editor

    @property
    def mp3parser(self) -> MP3Parser:
        """
        Get MP3Parser instance, creating if required.
        Note that mp3parser instances are thread-local so that they
        are not shared between threads.
        """
        if getattr(self._local, "mp3parser", None) is None:
            self._local.mp3parser = MP3Factory.create_parser()
        return self._local.mp3parser

    @property
    def docgen(self) -> DocumentGenerator:
        """get DocumentGenerator instance, creating if required"""
        if getattr(self._local, "docgen", None) is None:
            self._local.docgen = DocumentFactory.create_generator('pdf')
        return self._local.docgen

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
                song = Song(None, index, Metadata(**song))
                self.previous_games_songs.add(hash(song))

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

    def add_selected_songs_to_game(self):
        """add the selected songs from the source list to the game"""
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

    def generate_bingo_game(self):
        """
        generate tickets and mp3.
        called on pressing the generate game button
        """
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
        self.info_panel.text = f"Generating Bingo Game - {self.options.game_id}"
        self.bg_status = BackgroundOperation.GENERATING_GAME
        self.bg_thread = threading.Thread(
            target=self.generate_bingo_tickets_and_mp3_thread,
            args=(game_songs,))
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_music_quiz(self):
        """
        generate mp3 for a music quiz.
        called on pressing the generate quiz button
        """
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
        self.bg_status = BackgroundOperation.GENERATING_GAME
        self.bg_thread = threading.Thread(
            target=self.generate_bingo_tickets_and_mp3_thread,
            args=(game_songs,))
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_bingo_tickets_and_mp3_thread(self, game_songs):
        """Creates MP3 file and PDF files.
        This function runs in its own thread
        """
        gen = GameGenerator(self.options, self.mp3editor, self.docgen,
                            self.progress)
        try:
            gen.generate(game_songs)
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
        self.info_panel.pct = self.progress.total_percentage
        self.info_panel.text = self.progress.text
        #self.labels.info_text.config(text=self.progress.text)
        if self.bg_thread.is_alive():
            self.poll_id = self.root.after(250, self._poll_progress)
            return
        self.info_panel.pct = 100
        self.bg_thread.join()
        self.bg_thread = None
        self.enable_panels()
        if self.bg_status == BackgroundOperation.SEARCHING_MUSIC:
            self.add_available_songs_to_treeview()
            self.info_panel.text = ''
        elif self.bg_status == BackgroundOperation.GENERATING_GAME:
            self.generate_unique_game_id()
        self.bg_status = BackgroundOperation.IDLE
        self.info_panel.pct = 0.0

    def generate_clips(self):
        """Generate all clips for all selected Songs in a new thread.
        Creates a new thread and uses that thread to create clips of
        every selected Song.
        It will take the start time and duration values from the GUI fields
        and create a "duration" length clip starting at "start_time_entry"
        in the "NewClips" directory, using the name and directory of the
        source MP3 file as its filename.
        """
        game_songs = self.selected_songs_panel.all_songs()
        if not game_songs:
            return
        self.options.mode = GameMode.CLIP
        self.disable_panels()
        self.bg_status = BackgroundOperation.GENERATING_CLIPS
        self.bg_thread = threading.Thread(target=self.generate_clips_thread,
                                          args=(game_songs,))
        self.bg_thread.daemon = True
        self.bg_thread.start()
        self._poll_progress()

    def generate_clips_thread(self, songs: List[Song]):
        """Generate all clips for all selected Songs
        This function runs in its own thread
        """
        gen = ClipGenerator(self.options, self.mp3editor, self.progress)
        gen.generate(songs)

    @classmethod
    def mainloop(cls):
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
