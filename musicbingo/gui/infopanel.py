"""
Panel that contains progress info and progress bar
"""
import tkinter as tk # pylint: disable=import-error
import tkinter.ttk # pylint: disable=import-error

from musicbingo.gui.panel import Panel

class InfoPanel(Panel):
    """Panel that contains progress info and progress bar"""
    def __init__(self, main: tk.Frame):
        super(InfoPanel, self).__init__(main)
        self.progress_pct_value = tk.DoubleVar(self.frame)
        self.progress_pct_text = tk.StringVar(self.frame, value="")
        self.progress_text = tk.StringVar(self.frame, value="")
        info_text = tk.Label(
            self.frame, textvariable=self.progress_text,
            bg=self.BANNER_BACKGROUND, fg="#FFF", width=60,
            font=(self.TYPEFACE, 14), justify=tk.LEFT) #, anchor=tk.W)
        pct_text_label = tk.Label(
            self.frame, textvariable=self.progress_pct_text,
            bg=self.BANNER_BACKGROUND, fg="#FFF", width=8,
            font=(self.TYPEFACE, 11), justify=tk.RIGHT) #, anchor=tk.W)
        progressbar = tkinter.ttk.Progressbar(
            self.frame, orient=tk.HORIZONTAL, mode="determinate",
            variable=self.progress_pct_value, length=180, maximum=100.0)
        pct_text_label.pack(side=tk.RIGHT)
        progressbar.pack(side=tk.RIGHT)
        info_text.pack(fill=tk.X)

    def get_text(self) -> str:
        """get contents of info label"""
        return self.progress_text.get()

    def set_text(self, value: str) -> None:
        """set contents of info label"""
        self.progress_text.set(value)

    text = property(get_text, set_text)

    def get_percentage(self) -> float:
        """get value of progress bar"""
        return self.progress_pct_value.get()

    def set_percentage(self, value: float) -> None:
        """set value of progress bar"""
        self.progress_pct_value.set(value)

    pct = property(get_percentage, set_percentage)

    def get_percentage_text(self) -> float:
        """get value of text inside the progress bar"""
        return self.progress_pct_text.get()

    def set_percentage_text(self, text: str) -> None:
        """set value of text inside the progress bar"""
        self.progress_pct_text.set(text)
        self.frame.update()

    pct_text = property(get_percentage_text, set_percentage_text)

    def disable(self) -> None:
        """disable panel"""
        pass #pylint: disable=unnecessary-pass

    def enable(self) -> None:
        """enable panel"""
        pass #pylint: disable=unnecessary-pass
