"""
Panel that contains all of the options for generating a
music quiz, plus the "Generate Quiz" button
"""
from typing import Callable

import tkinter as tk  # pylint: disable=import-error

from musicbingo.gui.panel import Panel


class GenerateQuizPanel(Panel):
    """
    Panel that contains all of the options for generating a
    music quiz, plus the "Generate Quiz" button
    """

    def __init__(self, main: tk.Frame, generate_quiz: Callable) -> None:
        super().__init__(main)
        game_name_label = tk.Label(self.frame, font=(self.TYPEFACE, 16),
                                   text="Quiz ID:", bg=self.NORMAL_BACKGROUND,
                                   fg="#FFF", padx=6)
        self.game_name_entry = tk.Entry(
            self.frame, font=(self.TYPEFACE, 16), width=10,
            justify=tk.CENTER)
        self.generate_quiz = tk.Button(
            self.frame, text="Generate Music Quiz",
            command=generate_quiz, pady=0,
            font=(self.TYPEFACE, 18), bg="#00cc00")
        self.generate_quiz.pack(side=tk.RIGHT, padx=20)
        self.game_name_entry.pack(side=tk.RIGHT, padx=10)
        game_name_label.pack(side=tk.RIGHT)

    def disable(self) -> None:
        """disable all widgets in this frame"""
        # self.generate_quiz.config(state=tk.DISABLED)

    def enable(self) -> None:
        """enable all widgets in this frame"""
        # self.generate_quiz.config(state=tk.NORMAL)

    def set_game_id(self, value: str) -> None:
        """set the current game ID"""
        self.game_name_entry.delete(0, len(self.game_name_entry.get()))
        self.game_name_entry.insert(0, value)

    def get_game_id(self) -> str:
        """Get the current game ID"""
        return self.game_name_entry.get()

    game_id = property(get_game_id, set_game_id)

    def set_generate_button(self, text: str) -> None:
        """Set the text inside the generate quiz"""
        self.generate_quiz.config(text=text)
