"""
Base class for additional option sections
"""
import argparse
from abc import ABC, abstractmethod
import os
from typing import Any, Dict, List, cast

from .option_field import OptionField, TypeConvert

class ExtraOptions(ABC):
    """
    Base class for additional option sections
    """
    OPTIONS: List[OptionField] = []
    LONG_PREFIX: str = ""
    SHORT_PREFIX: str = ""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        adds command line options for database settings
        """
        # pylint: disable=no-member
        group = parser.add_argument_group(title=cls.LONG_PREFIX,  # type: ignore
                                          description=cls.DESCRIPTION)  # type: ignore
        for opt in cls.OPTIONS:
            try:
                ftype = opt.ftype.from_string  # type: ignore
            except AttributeError:
                ftype = opt.ftype
            group.add_argument(
                f"--{cls.SHORT_PREFIX}-{opt.name}",  # type: ignore
                dest=f"{cls.SHORT_PREFIX}_{opt.name}",  # type: ignore
                nargs='?',
                help=f'{opt.help}  [%(default)s]',
                type=cast(TypeConvert, ftype))

    def load_environment_settings(self):
        """
        Check environment for database settings
        """
        # pylint: disable=no-member
        for opt in self.OPTIONS:
            try:
                env = (self.SHORT_PREFIX + opt.name).upper()
                value = opt.ftype(os.environ[env])
                setattr(self, opt.name, value)
            except ValueError as err:
                print(f'Failed to parse {env}: {err}')
            except KeyError:
                pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to a dictionary
        """
        retval = {}
        for key, value in self.__dict__.items():
            if key[0] == '_':
                continue
            retval[key] = value
        return retval

    @abstractmethod
    def update(self, **kwargs) -> bool:
        """
        Apply supplied arguments to this settings section
        """
        raise NotImplementedError("method must be implemented by super class")
