"""
Utilities for finding test fixtures
"""

from pathlib import Path


def fixture_filename(name: str) -> Path:
    """returns absolute file path of the given fixture"""
    return Path(__file__).parent / "fixtures" / name
