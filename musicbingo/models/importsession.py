"""
Helper class that holds state informtion when importing a JSON
file into the database.
"""
import logging
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .modelmixin import ModelMixin


class ImportSession:
    """
    Helper class that holds state informtion when importing a JSON
    file into the database.
    """

    def __init__(self, options, session):
        self.options = options
        self.session = session
        self.log = logging.getLogger('musicbingo.models')
        self.pk_maps: Dict[str, Dict[int, int]] = {}

    def __getitem__(self, table: str) -> Dict[int, int]:
        """
        Get the private key map for the given table.
        This map is from the PK defined in the JSON file to the PK of the item
        in the database.
        """
        return self.pk_maps[table]

    def set_map(self, table: str, pk_map: Dict[int, int]) -> None:
        """
        Set the private key map for the given table
        """
        self.pk_maps[table] = pk_map

    def add(self, model: "ModelMixin") -> None:
        """
        Add model to the database
        """
        self.session.add(model)

    def commit(self) -> None:
        """
        Commit pending changes to the database
        """
        self.session.commit()

    def flush(self) -> None:
        """
        Flush pending changes to the database so that automatic fields (like pk)
        are assigned.
        Transaction can still be rolled-back on error.
        """
        self.session.flush()
