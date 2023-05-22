"""
EnumWrapper is a Generic that can be used any option that is based upon
an Enum or IntEnum.
"""
from typing import Generic, List, TypeVar, Union

EnumType = TypeVar('EnumType') # pylint: disable=invalid-name

class EnumWrapper(Generic[EnumType]):
    """
    Interface for a TypeConvert that has helper functions
    """

    def __init__(self, enum_type):
        self.type = enum_type

    def names(self) -> List[str]:
        """
        Get all of the key names of this enum, sorted alphabetically
        """
        try:
            return self.type.names()
        except AttributeError:
            return sorted(self.type.__members__.keys()) # type: ignore

    def __call__(self, name: Union[str, EnumType]) -> EnumType:
        """
        Convert a string to this enum
        """
        if isinstance(name, self.type):
            return name
        return self.type[name.upper()]  # type: ignore
