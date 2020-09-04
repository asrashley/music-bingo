"""
Panel for the "generate clips" row
"""
from typing import Callable

import tkinter as tk  # pylint: disable=import-error

from musicbingo.gui.optionvar import OptionVar
from musicbingo.gui.panel import Panel
from musicbingo.options import Options


class GenerateClipsPanel(Panel):
    """Panel for the "generate clips" row"""

    def __init__(self, main: tk.Frame, options: Options,
                 generate_clips: Callable[[], None]):
        super().__init__(main)
        self.options = options
        clip_start_label = tk.Label(
            self.frame, font=(self.TYPEFACE, 16), text="Start time:",
            bg=self.NORMAL_BACKGROUND, fg="#FFF", padx=6)
        self.start_time = OptionVar(self.frame, options, "clip_start", str)
        start_time_entry = tk.Entry(
            self.frame, font=(self.TYPEFACE, 16), width=6,
            textvariable=self.start_time, justify=tk.RIGHT)
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

    def disable(self) -> None:
        """disable all buttons"""
        # self.generate_clips.config(state=tk.DISABLED)

    def enable(self) -> None:
        """enable all buttons"""
        # self.generate_clips.config(state=tk.NORMAL)

    def set_generate_button(self, text: str) -> None:
        """Set the text inside the generate game button"""
        self.generate_clips.config(text=text)
