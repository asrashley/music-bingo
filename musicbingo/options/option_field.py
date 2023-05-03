"""
Tuple used to describe each option
"""
from argparse import FileType
from typing import Any, Callable, Optional, List, NamedTuple, Union

# pylint: disable=invalid-name
TypeConvert = Union[Callable[[str], Any], FileType]

class OptionField(NamedTuple):
    """
    Tuple used to describe each option
    """
    name: str
    ftype: TypeConvert
    help: str
    default: Any
    min_value: Optional[int]
    max_value: Optional[int]
    choices: Optional[List[Any]]
