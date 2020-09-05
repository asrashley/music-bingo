"""
HasParent - an interface used for classes that have a parent-child relationship
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from .models.modelmixin import ModelMixin
from .models.db import DatabaseSession


class HasParent(ABC):
    """interface used for classes that have a parent-child relationship"""

    def __init__(self, filename: str, parent: Optional["HasParent"] = None):
        self._parent = parent
        self.filename = filename
        self._fullpath: Optional[Path] = None

    def get_fullpath(self) -> Optional[Path]:
        """return absolute name of this object"""
        if self._fullpath is None and self._parent is not None:
            if self._parent.fullpath is None:
                return None
            self._fullpath = self._parent.fullpath / self.filename
        return self._fullpath

    def set_fullpath(self, path: Union[Path, str]) -> None:
        """set absolute path of this object"""
        if isinstance(path, str):
            path = Path(path)
        self._fullpath = path

    fullpath = property(get_fullpath, set_fullpath)

    @abstractmethod
    def model(self, session: DatabaseSession) -> Optional[ModelMixin]:
        """
        get database model for this object
        """
        raise NotImplementedError()
