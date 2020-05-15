"""
Base classes for use by mocks
"""

import datetime
from enum import Enum
import math
from pathlib import Path
import re
from typing import List, Union

from musicbingo import utils


class MockBase:
    """
    Base class used by other mocks
    """

    def flatten(self, items, convert_numbers=False):
        return utils.flatten(items, convert_numbers=convert_numbers)
