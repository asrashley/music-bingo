"""
base class for all panels
"""

from __future__ import print_function
from abc import ABC, abstractmethod
import tkinter as tk # pylint: disable=import-error

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
