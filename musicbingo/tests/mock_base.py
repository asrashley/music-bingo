"""
Base classes for use by mocks
"""

import datetime
from enum import Enum
import math
from pathlib import Path
import re
from typing import List, Union

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes import Dimension
from musicbingo.docgen.styles import Padding
from musicbingo.duration import Duration

class MockBase:
    """
    Base class used by other mocks
    """

    #pylint: disable=too-many-branches
    def flatten(self, items, convert_numbers=False):
        """Converts an object in to a form suitable for JSON encoding.
        flatten will take a dictionary, list or tuple and inspect each item
        in the object looking for items such as datetime.datetime objects
        that need to be converted to a canonical form before
        they can be processed for storage.
        """
        if isinstance(items, dict):
            retval = {}
        else:
            retval = []
        for item in items:
            key = None
            if isinstance(items, dict):
                key = item
                item = items[key]
            if hasattr(item, 'as_dict'):
                item = self.flatten(item.as_dict())
            if isinstance(item, (datetime.datetime, datetime.time)):
                item = self.to_iso_datetime(item)
            elif isinstance(item, (datetime.timedelta)):
                item = self.to_iso_duration(item)
            elif isinstance(item, Colour):
                item = item.css()
            elif isinstance(item, Dimension):
                item = str(item)
            elif isinstance(item, Duration):
                item = int(item)
            elif isinstance(item, Padding):
                item = self.flatten(tuple(item))
            elif isinstance(item, Path):
                item = '/'.join([item.parent.name, item.name])
            elif isinstance(item, Enum):
                item = item.name
            elif convert_numbers and isinstance(item, int):
                item = str(item).replace('l', '')
            elif isinstance(item, str):
                item = item.replace("'", "\'")
            elif isinstance(item, (list, set, tuple)):
                item = self.flatten(list(item))
            elif isinstance(item, dict):
                item = self.flatten(item)
            if callable(item):
                continue
            if key:
                retval[key] = item
            else:
                retval.append(item)
        if items.__class__ == tuple:
            return tuple(retval)
        return retval

    @staticmethod
    def to_iso_datetime(value: Union[datetime.datetime, datetime.time]) -> str:
        """
        Convert a datetime to an ISO8601 formatted dateTime string.
        :param value: the dateTime to convert
        :returns: an ISO8601 formatted string version of the dateTime
        """
        retval = value.isoformat()
        if value.tzinfo is None:
            retval += 'Z'
        else:
            # replace +00:00 timezone with Z
            retval = re.sub('[+-]00:00$', 'Z', retval)
        return retval

    @staticmethod
    def to_iso_duration(secs: Union[datetime.timedelta, str, float]) -> str:
        """
        Convert a time period to an ISO8601 formatted duration string.
        :param secs: the duration to convert, in seconds
        :returns: an ISO8601 formatted string version of the duration
        """
        if isinstance(secs, str):
            secs = float(secs)
        elif isinstance(secs, datetime.timedelta):
            secs = secs.total_seconds()
        hrs = int(math.floor(secs / 3600.0))
        retval: List[str] = ['PT']
        secs %= 3600
        mins = int(math.floor(secs / 60.0))
        secs %= 60
        if hrs:
            retval.append(f'{hrs}H')
        if hrs or mins:
            retval.append(f'{mins}M')
        retval.append('{0:0.2f}S'.format(secs))
        return ''.join(retval)
