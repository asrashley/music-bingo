"""
Dialog box for selecting one item from a list of items
"""
from typing import cast, Any, Dict, Optional, Union

import tkinter as tk  # pylint: disable=import-error
from typing_extensions import Protocol

from musicbingo.mp3.factory import MP3Factory
from musicbingo.options import EnumWrapper, Options, OptionField
from musicbingo.utils import EnumProtocol
from .dialogbase import DialogBase, Focusable

class SettingVariable(Protocol):
    """
    Interface for an object that supports get() and set()
    """
    def set(self, value: Any) -> None:
        """
        Set the value
        """
        ...

    def get(self) -> Any:
        """
        Get the value
        """

class StringSetting:
    """
    Wrapper to provide SettingVariable interface for a tk.Entry widget
    """
    def __init__(self, entry: tk.Entry):
        self.entry = entry

    def set(self, value: str) -> None:
        """
        Set the value of this setting
        """
        self.entry.delete(0, len(self.entry.get()))
        self.entry.insert(0, str(value))

    def get(self) -> str:
        """
        Get current value
        """
        return self.entry.get()

class SettingField:
    """
    A collection of Tk Widgets that allows one setting to be modified.
    It will inspect the type of the setting to create the most appropriate
    Widget (e.g. Entry, Combobox, Spinbox)
    """
    def __init__(self, parent: Union[tk.Tk, tk.Frame], opt: OptionField,
                 value: Any):
        self.option = opt
        self.frame = tk.Frame(parent, bg=DialogBase.NORMAL_BACKGROUND)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)
        add_hint = True
        label = tk.Label(
            self.frame, font=(DialogBase.TYPEFACE, 14),
            text=opt.name.replace('_', ' '),
            bg=DialogBase.NORMAL_BACKGROUND,
            width=20,
            fg=DialogBase.NORMAL_FOREGROUND, padx=6)
        if opt.ftype == bool:
            self.value: SettingVariable = tk.BooleanVar(self.frame)
            self.entry: Union[tk.ttk.Widget, tk.Entry] = tk.ttk.Checkbutton(
                self.frame, variable=self.value, width=35,
                text=opt.help, onvalue=True)
            self.value.set(value)
            add_hint = False
        elif opt.ftype == int:
            self.entry = tk.ttk.Spinbox(
                self.frame, width=35,
                from_=cast(float, opt.min_value),
                to=cast(float, opt.max_value))
            self.value = self.entry
            self.value.set(value)
        elif isinstance(opt.ftype, EnumWrapper):
            self.entry = tk.ttk.Combobox(
                self.frame, font=(DialogBase.TYPEFACE, 16), width=35,
                state='readonly', justify=tk.CENTER,
                values=cast(EnumProtocol, opt.ftype).names())
            self.value = self.entry
            self.value.set(value.name)
        elif opt.name == 'mp3_editor':
            self.entry = tk.ttk.Combobox(
                self.frame, font=(DialogBase.TYPEFACE, 16), width=35,
                state='readonly', justify=tk.CENTER,
                values=MP3Factory.available_editors())
            self.value = self.entry
            self.value.set(value)
        else:
            self.entry = tk.Entry(
                self.frame, font=(DialogBase.TYPEFACE, 16), width=35,
                bg=DialogBase.ALTERNATE_BACKGROUND,
                fg=DialogBase.ALTERNATE_FOREGROUND, justify=tk.CENTER)
            self.value = StringSetting(self.entry)
            self.value.set(str(value))
        label.grid(row=0, column=0, sticky=tk.E)
        self.entry.grid(row=0, column=1, sticky=tk.W)
        if add_hint:
            hint = tk.Label(
                self.frame, font=(DialogBase.TYPEFACE, 10),
                text=opt.help, bg=DialogBase.NORMAL_BACKGROUND,
                fg=DialogBase.NORMAL_FOREGROUND, padx=6)
            hint.grid(row=1, column=0, columnspan=2, sticky=tk.NE)

    def get(self) -> Union[str, int, float]:
        """Get current value"""
        value = self.value.get()
        if isinstance(value, str) and self.option.ftype != str:
            value = self.option.ftype(value)
        return value

class SettingsDialog(DialogBase):
    """
    Dialog box that allows options to be modified
    """
    WIDTH=800
    HEIGHT=500

    def __init__(self, parent: tk.Tk, options: Options):
        self.options = options
        self.fields: Dict[str, SettingField] = {}
        super().__init__(parent, "Edit Settings", height=self.HEIGHT,
                         width=self.WIDTH)

    def body(self, frame: tk.Frame) -> Optional[Focusable]:
        """
        Generate body of this dialog box
        """
        self.canvas = tk.Canvas(
            frame, width=self.WIDTH-50, height=self.HEIGHT-50,
            bg=self.NORMAL_BACKGROUND)
        scrollbar = tk.Scrollbar(frame, orient='vertical',
                                 command=self.canvas.yview)
        inside = tk.Frame(self.canvas, bg=self.NORMAL_BACKGROUND) #, width=800, height=500)
        inside.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=inside, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        items = self.options.to_dict()
        row :int = 0
        for opt in Options.OPTIONS:
            field = SettingField(inside, opt, items[opt.name])
            self.fields[opt.name] = field
            field.frame.grid(row=row, column=0, pady=6)
            row += 1
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return inside

    def apply(self) -> None:
        """
        Get modified settings
        """
        items = self.options.to_dict()
        changes: Dict[str, Any] = {}
        for opt in Options.OPTIONS:
            new_value = opt.ftype(cast(str, self.fields[opt.name].get()))
            if new_value != items[opt.name]:
                changes[opt.name] = new_value
        self.options.update(**changes)
        self.result = changes

def edit_settings(parent: tk.Tk, options: Options) -> Optional[bool]:
    """
    Create a dialog box to edit settings
    """
    dlg = SettingsDialog(parent, options)
    return dlg.result
