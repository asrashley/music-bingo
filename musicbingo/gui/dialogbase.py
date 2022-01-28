"""
A base class for creating dialog boxes

This class is based upon the code from:
http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

import tkinter as tk  # pylint: disable=import-error
from typing_extensions import Protocol

from .panel import Panel

class Focusable(Protocol):
    """
    Interface for an object that supports focus_set
    """
    def focus_set(self) -> None:
        """
        Set this object as focus
        """
        ...

class DialogBase(tk.Toplevel, ABC):
    """
    Base class for dialog boxes
    """
    NORMAL_BACKGROUND = '#FFF'
    ALTERNATE_BACKGROUND = '#BBB'
    NORMAL_FOREGROUND = "#343434"
    ALTERNATE_FOREGROUND = "#505024"
    TYPEFACE = Panel.TYPEFACE

    def __init__(self, parent: tk.Tk, title: str, height: Union[str, float] = 0,
                 width: Union[str, float] = 0):
        super().__init__(parent, width=width, height=height)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result: Optional[Any] = None

        if height and width:
            self.geometry(f"{width}x{height}")
            body = tk.Frame(self, height=height, width=width)
        else:
            body = tk.Frame(self)
        focus = self.body(body)
        if focus:
            self.initial_focus = focus
        else:
            self.initial_focus = self
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")

        self.initial_focus.focus_set()

        self.wait_window(self)

    @abstractmethod
    def body(self, frame: tk.Frame) -> Optional[Focusable]:
        """
        create dialog body.  return widget that should have
        initial focus.
        """
        return None

    def buttonbox(self):
        """
        add standard button box.
        override if you don't want the standard buttons
        """
        box = tk.Frame(self)
        btn = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        btn.pack(side=tk.LEFT, padx=5, pady=5)
        btn = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    # pylint: disable=invalid-name, unused-argument
    def ok(self, event=None):
        """
        called when ok button is pressed
        """
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    # pylint: disable=unused-argument
    def cancel(self, event=None):
        """
        called when ok or cancel buttons are pressed, or window is closed
        """
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    # pylint: disable=no-self-use
    def validate(self) -> bool:
        """
        Validate the fields in this dialog box
        """
        return True

    @abstractmethod
    def apply(self) -> None:
        """
        Called when OK button is pressed just before the dialog is
        closed. Used to make use of the fields in the dialog before it
        is closed.
        """
        # pylint: disable=unnecessary-pass
        pass
