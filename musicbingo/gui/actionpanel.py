"""
Panel containing all the action buttons.
Action panel is the middle panel between the "available songs"
and "selected songs" panels.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import tkinter as tk  # pylint: disable=import-error

from musicbingo.song import Song

from .applicationstate import ApplicationState
from .panel import Panel

class ActionPanelCallbacks(ABC):
    """
    Interface for the functions that the action panel can call when
    one of its buttons are pressed.
    """

    @abstractmethod
    def add_selected_songs_to_game(self, selections: Optional[List[Song]] = None):
        """add the selected songs from the source list to the game"""
        raise NotImplementedError()

    @abstractmethod
    def add_random_songs_to_game(self, amount: int = 5) -> None:
        """add random songs (if available) to the game list"""
        raise NotImplementedError()

    @abstractmethod
    def create_new_game(self):
        """
        Confirm if the user wants to create a new game and
        then create a new game
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_song_from_game(self):
        """
        remove the selected song from the game list and
        return it to the main list.
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_all_songs_from_game(self):
        """remove all of the songs from the game list"""
        raise NotImplementedError()

    @abstractmethod
    def toggle_exclude_artists(self):
        """toggle the "exclude artists" setting"""
        raise NotImplementedError()

    @abstractmethod
    def start_stop_playback(self) -> None:
        """
        Toggle between playing songs and aborting playback.
        If nothing is playing, play all selected songs.
        If songs are playing, stop playback.
        """
        raise NotImplementedError()


class ActionPanel(Panel):
    """
    Panel containing all the action buttons.
    Action panel is the middle panel between the "available songs"
    and "selected songs" panels.
    """

    def __init__(self, main: tk.Frame, app: ActionPanelCallbacks):
        super().__init__(main)
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
        self.start_stop_playback = tk.Button(
            self.frame, text='Play Songs', state=tk.DISABLED,
            command=app.start_stop_playback, bg=self.BTN_SUCCESS)
        self.previous_games_size = tk.Label(
            self.frame, font=(self.TYPEFACE, 16),
            bg=self.NORMAL_BACKGROUND, fg="#fff",
            text="Previous\ngames:\n0 songs",
            padx=6)
        self.new_game = tk.Button(
            self.frame, text='New Game',
            command=app.create_new_game, bg=self.BTN_DANGER)
        self.add_song.grid(row=0, column=0, pady=10, sticky=tk.E + tk.W)
        self.add_random_songs.grid(row=1, column=0, pady=10, sticky=tk.E + tk.W)
        self.remove_song.grid(row=2, column=0, pady=10, sticky=tk.E + tk.W)
        self.remove_all_songs.grid(row=3, column=0, pady=10, sticky=tk.E + tk.W)
        self.toggle_artist.grid(row=4, column=0, pady=10, sticky=tk.E + tk.W)
        self.start_stop_playback.grid(row=5, column=0, pady=10, sticky=tk.E + tk.W)
        self.previous_games_size.grid(row=6, column=0, pady=10, sticky=tk.E + tk.W)
        self.new_game.grid(row=7, column=0, pady=10, sticky=tk.E + tk.W)
        self.state = ApplicationState.IDLE

    def disable(self):
        """disable all buttons"""
        self.add_song.config(state=tk.DISABLED)
        self.add_random_songs.config(state=tk.DISABLED)
        self.remove_song.config(state=tk.DISABLED)
        self.remove_all_songs.config(state=tk.DISABLED)
        self.toggle_artist.config(state=tk.DISABLED)
        self.start_stop_playback.config(state=tk.DISABLED)

    def enable(self):
        """enable all buttons"""
        self.add_song.config(state=tk.NORMAL)
        self.add_random_songs.config(state=tk.NORMAL)
        self.remove_song.config(state=tk.NORMAL)
        self.remove_all_songs.config(state=tk.NORMAL)
        self.toggle_artist.config(state=tk.NORMAL)
        self.start_stop_playback.config(state=tk.NORMAL)

    def enable_button(self, btn: str) -> None:
        """enable the specified button"""
        getattr(self, btn).config(state=tk.NORMAL)

    def disable_button(self, btn: str) -> None:
        """disable_button the specified button"""
        getattr(self, btn).config(state=tk.DISABLED)

    def set_play_button(self, text: str) -> None:
        """Set the text inside the start/stop playback button"""
        self.start_stop_playback.config(text=text)

    def set_num_previous_songs(self, num_prev: int) -> None:
        """
        Set the label showing number of songs in previous games
        """
        plural = '' if num_prev == 1 else 's'
        txt = f"Previous\nGames:\n{num_prev} song{plural}"
        self.previous_games_size.config(text=txt)

    def set_state(self, state: ApplicationState) -> None:
        """set the current game generation state"""
        self.state = state
        if state in {ApplicationState.GENERATING_GAME,
                     ApplicationState.SONG_PLAYING}:
            self.new_game.config(state=tk.DISABLED)
        else:
            self.new_game.config(state=tk.NORMAL)
        if state == ApplicationState.SONG_PLAYING:
            self.set_play_button('Stop playback')
        else:
            self.set_play_button('Play Songs')

    def get_state(self) -> ApplicationState:
        """Get the current app state"""
        return self.state
