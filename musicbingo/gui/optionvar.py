"""
Wrapper for properties of the Options class as a tk.Variable that will
automatically keep the option and the tk.Variable in sync.
"""
from typing import Callable, Optional, Type

import tkinter as tk # pylint: disable=import-error

from musicbingo.options import Options

class OptionVar(tk.Variable):
    """
    Wraps a property of Options as a tk.Variable that will automatically
    keep the option and the tk.Variable in sync.
    """
    def __init__(self, parent: tk.Frame, options: Options, prop_name: str,
                 prop_type: Type, command: Optional[Callable] = None) -> None:
        value = prop_type(getattr(options, prop_name))
        super(OptionVar, self).__init__(parent, value=value,
                                        name=f'PV_VAR_{prop_name}')
        self.options = options
        self.prop_name = prop_name
        self.prop_type = prop_type
        self.command = command
        self.trace_add("write", self._on_set) # type: ignore

    def set(self, value):
        """set an option, also pushes change to Option object"""
        if getattr(self.options, self.prop_name, None) != value:
            setattr(self.options, self.prop_name, value)
            self.options.save_ini_file()
        super(OptionVar, self).set(value)

    def _on_set(self, *args): #pylint: disable=unused-argument
        value = self.get()
        try:
            if not isinstance(value, self.prop_type):
                value = self.prop_type(value)
            if getattr(self.options, self.prop_name, None) != value:
                setattr(self.options, self.prop_name, value)
                if self.command is not None:
                    self.command(value)
                self.options.save_ini_file()
        except ValueError as err:
            if value:
                print(err)
