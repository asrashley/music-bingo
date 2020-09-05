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
        self.generate_quiz = tk.Button(
            self.frame, text="Generate Music Quiz",
            command=generate_quiz, pady=0,
            font=(self.TYPEFACE, 18), bg="#00cc00")
        self.generate_quiz.pack(side=tk.RIGHT)

    def disable(self) -> None:
        """disable all widgets in this frame"""
        # self.generate_quiz.config(state=tk.DISABLED)

    def enable(self) -> None:
        """enable all widgets in this frame"""
        # self.generate_quiz.config(state=tk.NORMAL)

    def set_generate_button(self, text: str) -> None:
        """Set the text inside the generate quiz"""
        self.generate_quiz.config(text=text)
