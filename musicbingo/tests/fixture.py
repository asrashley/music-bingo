"""
Utilities for finding test fixtures
"""

from pathlib import Path
from typing import Union

def fixture_filename(name: Union[str, Path]) -> Path:
    """returns absolute file path of the given fixture"""
    return Path(__file__).parent / "fixtures" / name
