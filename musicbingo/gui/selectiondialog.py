"""
Dialog box for selecting one item from a list of items
"""
from typing import List, NamedTuple, Optional, Sequence, Union

import tkinter as tk  # pylint: disable=import-error
import tkinter.ttk  # pylint: disable=import-error

from .dialogbase import DialogBase, Focusable

class SelectOption(NamedTuple):
    """
    One option from the selection list
    """
    text: str
    value: str

class SelectionDialog(DialogBase):
    """
    Dialog box that allows one or more items from a list
    """
    def __init__(self, parent: tk.Tk, title: str,
                 options: Sequence[SelectOption],
                 multi_select: bool = False):
        self.options = options
        self.multi_select = multi_select
        super().__init__(parent, title)

    def body(self, frame: tk.Frame) -> Optional[Focusable]:
        """
        Generate body of this dialog box
        """
        selectmode = tk.EXTENDED if self.multi_select else tk.BROWSE
        scrollbar = tk.Scrollbar(frame)
        self.tree = tkinter.ttk.Treeview(
            frame, columns=('text', 'value',),
            displaycolumns=('text',),
            height=20,
            show=[],
            selectmode=selectmode, # type: ignore
            yscrollcommand=scrollbar.set)
        self.tree.column('text', width=200, anchor='center')
        scrollbar.config(command=self.tree.yview)
        self.tree.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        for item in self.options:
            self.tree.insert('', 'end', item.value, values=item)
        #frame.pack(self.tree)
        self.tree.pack()
        return self.tree

    def apply(self) -> None:
        """
        Get selected items
        """
        ref_ids = list(self.tree.selection())
        if not ref_ids:
            focus_elt = self.tree.focus()
            if focus_elt:
                ref_ids = [focus_elt]
            else:
                ref_ids = self.tree.get_children()
        if not self.multi_select:
            if ref_ids:
                ref_ids = ref_ids[0] # type: ignore
            else:
                ref_ids = []
        self.result = ref_ids

def ask_selection(parent: tk.Tk, title: str, options: Sequence[SelectOption],
                  multi_select: bool = False) -> Optional[Union[List[str], str]]:
    """
    Create a dialog box and wait for the user to select an item
    """
    dlg = SelectionDialog(parent, title, options, multi_select)
    return dlg.result
