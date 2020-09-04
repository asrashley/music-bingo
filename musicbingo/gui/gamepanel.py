"""
Panel that contains all of the options for generating a
Bingo game, plus the "Generate Bingo Game" button
"""
from typing import Callable

import tkinter as tk  # pylint: disable=import-error
import tkinter.ttk  # pylint: disable=import-error

from musicbingo.generator import GameGenerator
from musicbingo.gui.optionvar import OptionVar
from musicbingo.gui.panel import Panel
from musicbingo.options import Options
from musicbingo.palette import Palette


class GenerateGamePanel(Panel):
    """
    Panel that contains all of the options for generating a
    Bingo game, plus the "Generate Bingo Game" button
    """

    def __init__(self, main: tk.Frame, options: Options,
                 generate_game: Callable) -> None:
        super().__init__(main)
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
        self.colour_combo.grid(row=0, column=2, sticky=tk.E + tk.W, padx=5)
        game_name_label.grid(row=0, column=3, padx=5)
        self.game_name_entry.grid(row=0, column=4, sticky=tk.E + tk.W, padx=5)
        num_tickets_label.grid(row=0, column=5)
        self.num_tickets_entry.grid(row=0, column=6, padx=5)
        self.generate_cards.grid(row=0, column=7, padx=20)

    def disable(self):
        """disable all widgets in this frame"""
        self.colour_combo.config(state=tk.DISABLED)
        self.game_name_entry.config(state=tk.DISABLED)
        self.num_tickets_entry.config(state=tk.DISABLED)

    def enable(self):
        """enable all widgets in this frame"""
        self.colour_combo.config(state=tk.NORMAL)
        self.game_name_entry.config(state=tk.NORMAL)
        self.num_tickets_entry.config(state=tk.NORMAL)

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

    def set_generate_button(self, text: str) -> None:
        """Set the text inside the generate game button"""
        self.generate_cards.config(text=text)
