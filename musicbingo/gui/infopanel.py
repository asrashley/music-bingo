"""
Panel that contains progress info and progress bar
"""
import tkinter as tk # pylint: disable=import-error
import tkinter.messagebox # pylint: disable=import-error
import tkinter.constants # pylint: disable=import-error
import tkinter.filedialog # pylint: disable=import-error
import tkinter.ttk # pylint: disable=import-error

from musicbingo.gui.panel import Panel

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

    def disable(self) -> None:
        """disable panel"""
        pass #pylint: disable=unnecessary-pass

    def enable(self) -> None:
        """enable panel"""
        pass #pylint: disable=unnecessary-pass
