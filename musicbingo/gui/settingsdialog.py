"""
Dialog box for selecting one item from a list of items
"""
from typing import (
    cast, Any, Dict, List, Optional, Protocol, Set, Union
)

import tkinter as tk  # pylint: disable=import-error

from musicbingo.mp3.factory import MP3Factory
from musicbingo.options import Options, OptionField
from musicbingo.options.enum_wrapper import EnumWrapper
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
    def __init__(self, parent: Union[tk.Tk, tk.Frame], opt: OptionField, value: Any):
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
            self.entry: Union[tk.ttk.Widget, tk.Entry, tk.Spinbox] = tk.ttk.Checkbutton(
                self.frame, variable=self.value, width=35,
                text=opt.help, onvalue=True)
            self.value.set(value)
            add_hint = False
        elif opt.ftype == int:
            self.value = tk.IntVar(self.frame)
            self.entry = tk.Spinbox(
                self.frame, width=35,
                textvariable=self.value,
                from_=cast(float, opt.min_value),
                to=cast(float, opt.max_value))
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

    def __init__(self, parent: tk.Tk, options: Options, scrollbar: bool = True,
                 only: Optional[Set[str]] = None, exclude: Optional[Set[str]] = None):
        self.options = options
        self.fields: Dict[str, SettingField] = {}
        self.use_scrollbar = scrollbar
        self.only = only
        if exclude is not None:
            self.exclude = exclude
        else:
            self.exclude = set()
        # NOTE: the DialogBase will call the body() function
        super().__init__(parent, "Edit Settings", height=self.HEIGHT,
                         width=self.WIDTH)

    def body(self, frame: tk.Frame) -> Optional[Focusable]:
        """
        Generate body of this dialog box
        """
        self.canvas = tk.Canvas(
            frame, width=self.WIDTH-50, height=self.HEIGHT-50,
            bg=self.NORMAL_BACKGROUND)
        if self.use_scrollbar:
            scrollbar = tk.Scrollbar(frame, orient='vertical',
                                     command=self.canvas.yview)
        inside = tk.Frame(self.canvas, bg=self.NORMAL_BACKGROUND) #, width=800, height=500)
        if self.use_scrollbar:
            inside.bind('<Configure>', lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window(0, 0, window=inside, anchor=tk.NW)
        if self.use_scrollbar:
            self.canvas.configure(yscrollcommand=scrollbar.set)

        items = self.options.to_dict()
        row :int = 0
        for opt in Options.OPTIONS:
            if self.only is not None and opt.name not in self.only:
                continue
            if opt.name in self.exclude:
                continue
            field = SettingField(inside, opt, items[opt.name])
            self.fields[opt.name] = field
            field.frame.grid(row=row, column=0, pady=6)
            row += 1
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        if self.use_scrollbar:
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return inside

    def apply(self) -> None:
        """
        Get modified settings
        """
        items = self.options.to_dict()
        changes: Dict[str, Any] = {}
        for opt in Options.OPTIONS:
            try:
                new_value = opt.ftype(cast(str, self.fields[opt.name].get()))
            except KeyError:
                continue
            if new_value != items[opt.name]:
                changes[opt.name] = new_value
        self.options.update(**changes)
        self.result = changes


class RadioButtonSettingField:
    """
    Allows one setting to be modified using radio buttons.
    """
    def __init__(self, parent: Union[tk.Tk, tk.Frame], name: str, value: Any, choices: List[Any]):
        self.frame = tk.Frame(parent, bg=DialogBase.NORMAL_BACKGROUND)
        self.value = tk.IntVar(self.frame)
        self.choices: List[str] = []
        field_name = name.replace('_', ' ')
        label = tk.Label(
            self.frame,
            font=(DialogBase.TYPEFACE, 14),
            text=f'Please choose {field_name}',
            bg=DialogBase.NORMAL_BACKGROUND, padx=20, pady=15,
            width=20, fg=DialogBase.NORMAL_FOREGROUND)
        label.pack(anchor=tk.W)
        for idx, opt in enumerate(choices):
            btn = tk.Radiobutton(
                self.frame, text=opt, variable=self.value,
                padx=20, value=idx, bg=DialogBase.NORMAL_BACKGROUND,
                fg=DialogBase.NORMAL_FOREGROUND)
            btn.pack(anchor=tk.W)
            self.choices.append(opt)
            if opt == value:
                self.value.set(idx)

    def get(self) -> Union[str, int, float]:
        """Get current value"""
        value = cast(int, self.value.get())
        return self.choices[value]


class RadioButtonSettingDialog(DialogBase):
    """
    Dialog box that allows one option to be modified using a radio button
    """
    WIDTH=800
    HEIGHT=500

    def __init__(self, parent: tk.Tk, name: str, value: Any, choices: List[Any],
                 scrollbar: bool = True):
        self.name = name
        self.value = value
        self.result = value
        self.choices = choices
        self.use_scrollbar = scrollbar
        # NOTE: the DialogBase will call the body() function
        super().__init__(parent, f'Edit {name}', height=self.HEIGHT,
                         width=self.WIDTH)

    def body(self, frame: tk.Frame) -> Optional[Focusable]:
        """
        Generate body of this dialog box
        """
        self.canvas = tk.Canvas(
            frame, width=self.WIDTH-50, height=self.HEIGHT-50,
            bg=self.NORMAL_BACKGROUND)
        if self.use_scrollbar:
            scrollbar = tk.Scrollbar(frame, orient='vertical',
                                     command=self.canvas.yview)
        inside = tk.Frame(self.canvas, bg=self.NORMAL_BACKGROUND) #, width=800, height=500)
        if self.use_scrollbar:
            inside.bind('<Configure>', lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window(4, 4, window=inside, anchor=tk.NW)
        if self.use_scrollbar:
            self.canvas.configure(yscrollcommand=scrollbar.set)

        self.field = RadioButtonSettingField(inside, self.name, self.value, self.choices)
        # field.frame.grid(row=row, column=0, pady=6)
        self.field.frame.pack(anchor=tk.W, padx=20, pady=10)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        if self.use_scrollbar:
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return inside

    def apply(self) -> None:
        """
        Get modified settings
        """
        self.result = self.field.get()
