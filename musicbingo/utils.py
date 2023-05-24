"""
Various utility functions
"""

import datetime
from enum import Enum, IntEnum
import math
from pathlib import Path
import re
import time
from typing import (
    AbstractSet, Any, Dict, List, Optional, Protocol,
    Union
)

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes.dimension import Dimension
from musicbingo.docgen.styles import Padding
from musicbingo.duration import Duration

#pylint: disable=too-many-branches


def flatten(obj: Any, convert_numbers=False) -> Any:
    """
    Converts an object in to a form suitable for JSON encoding.
    flatten will take a dictionary, list or tuple and inspect each item
    in the object looking for items such as datetime.datetime objects
    that need to be converted to a canonical form before
    they can be processed for storage.
    """
    if isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, dict):
        ret_dict = {}
        for key, value in obj.items():
            if callable(value):
                continue
            ret_dict[key] = flatten(value, convert_numbers)
        return ret_dict
    if isinstance(obj, (list, tuple)):
        ret_list: List[Any] = []
        for value in obj:
            if callable(value):
                continue
            ret_list.append(flatten(value, convert_numbers))
        if isinstance(obj, tuple):
            return tuple(ret_list)
        return ret_list
    item = obj
    if hasattr(item, 'to_json'):
        item = item.to_json()
    elif hasattr(item, 'as_dict'):
        item = flatten(item.as_dict(), convert_numbers)
    elif isinstance(item, (datetime.datetime, datetime.time)):
        item = to_iso_datetime(item)
    elif isinstance(item, (datetime.timedelta)):
        item = to_iso_duration(item)
    elif isinstance(item, Colour):
        item = item.css()
    elif isinstance(item, Dimension):
        item = str(item)
    elif isinstance(item, Duration):
        item = int(item)
    elif isinstance(item, Padding):
        item = flatten(tuple(item))
    elif isinstance(item, Path):
        item = item.as_posix()
    elif isinstance(item, (IntEnum, Enum)):
        item = item.name
    elif convert_numbers and isinstance(item, int):
        item = str(item).replace('l', '')
    elif isinstance(item, str):
        item = item.replace("'", "\'")
    return item


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
    retval.append('{0:0.2f}S'.format(secs)) # pylint: disable=consider-using-f-string
    return ''.join(retval)


duration_re = re.compile(
    r'^PT((?P<hours>\d+)[H:])?((?P<minutes>\d+)[M:])?((?P<seconds>[\d.]+)S?)?$')


def from_isodatetime(date_time: str) -> Optional[Union[datetime.datetime,
                                                       datetime.timedelta,
                                                       datetime.time]]:
    """
    Convert an ISO formated date string to a datetime, timedelta or time.
    """
    if not date_time:
        return None
    utc = datetime.timezone(datetime.timedelta(0))
    if date_time[:2] == 'PT':
        match = duration_re.match(date_time)
        if not match:
            raise ValueError(date_time)
        hours, minutes, seconds = match.group(
            'hours'), match.group('minutes'), match.group('seconds')
        secs: float = 0
        if hours is not None:
            secs += int(match.group('hours')) * 3600
        if minutes is not None:
            secs += int(match.group('minutes')) * 60
        if seconds is not None:
            secs += float(match.group('seconds'))
        return datetime.timedelta(seconds=secs)
    if 'T' in date_time:
        try:
            return datetime.datetime.strptime(
                date_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=utc)
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc)
        except ValueError:
            return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%MZ").replace(tzinfo=utc)
    if not 'Z' in date_time:
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            return datetime.datetime.strptime(date_time, "%d/%m/%Y")
    return datetime.datetime.strptime(date_time, "%H:%M:%SZ").replace(tzinfo=utc).time()


date_hacks = [
    (re.compile('Apri[^l]'), 'Apr '), (re.compile('Sept[^e]'), 'Sep '),
    (re.compile(r'(\w{3} \d{1,2},? \d{4})\s*-\s*(.*$)'), r'\1 \2'),
    (re.compile(r'(\w{3} \d{1,2}), (\d{4}\s*\d{1,2}:\d{2})'), r'\1 \2'),
    (re.compile(r'(\w{3})-(\d{2})$'), r'\1 \2'),
    (re.compile(r'([+-])(\d{2}):(\d{2})$'), r'\1\2\3'),
    (re.compile(r'(.+) ([PCE][SD]?T)$'), r'\1')
]


def parse_date(date_str: str,
               date_format: Optional[str] = None) -> Optional[Union[datetime.datetime,
                                                                    datetime.timedelta,
                                                                    datetime.time]]:
    """Try to create a datetime from the given string"""
    formats = ["%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%b %Y", "%b %y", "%m/xx/%y",
               "%a %b %d %Y", "%B %d %Y %H:%M", "%b %d %Y %H:%M",
               "%B %d %Y", "%b %d %Y", '%a %b %d, %Y',
               "%Y-%m-%d %H:%M:%S%z"
               ]
    if date_format is not None:
        formats.insert(0, date_format)
    if not isinstance(date_str, str):
        date_str = str(date_str)
    try:
        return from_isodatetime(date_str)
    except ValueError:
        pass
    tzinfo = datetime.timedelta(0)
    if re.match(r'.+\s+ES?T$', date_str):
        tzinfo = datetime.timedelta(hours=5)
    elif re.match(r'.+\s+EDT$', date_str):
        tzinfo = datetime.timedelta(hours=4)
    elif re.match(r'.+\s+PS?T$', date_str):
        tzinfo = datetime.timedelta(hours=8)
    elif re.match(r'.+\s+PDT$', date_str):
        tzinfo = datetime.timedelta(hours=7)
    dte = date_str
    for regex, sub in date_hacks:
        dte = regex.sub(sub, dte)
    for fmt in formats:
        try:
            retval = datetime.datetime.strptime(dte, fmt)
            if '%z' not in fmt:
                retval += tzinfo
            return retval
        except ValueError:
            pass
    return datetime.datetime(*(time.strptime(date_str)[0:6]))


def make_naive_utc(date_time: datetime.datetime) -> datetime.datetime:
    """
    Convert a timezone aware datetime into a naive datetime
    using UTC timezone
    """
    utc_timezone = datetime.timezone(datetime.timedelta(seconds=0))
    return date_time.astimezone(utc_timezone).replace(tzinfo=None)

def clean_string(text: str, ascii_only=False) -> str:
    """
    removes common errors from a field
    """
    done = False
    while text and not done:
        done = True
        if ((text[0] == '"' and text[-1] == '"') or
            (text[0] == '[' and text[-1] == ']')):
            text = text[1:-1]
            done = False
        if text[:2] == "u'" and text[-1] == "'":
            text = text[2:-1]
            done = False
    if ascii_only:
        try:
            # Python v3.7
            if text.isascii(): # type: ignore
                return text
        except AttributeError:
            # Python less than v3.7
            pass
        return ''.join(filter(lambda c: ord(c) >= 32 and ord(c) < 0x7F,
                              list(text)))
    return text

def pick(src: Dict, fields: AbstractSet[str]) -> Dict:
    """
    Pick each key in "fields" from "src"
    """
    retval = {}
    for field in fields:
        if field in src:
            retval[field] = src[field]
    return retval

class EnumProtocol(Protocol):
    """
    Some useful functions to add to an Enum
    """
    @classmethod
    def names(cls) -> List[str]:
        """get list of items in this enum"""

    @classmethod
    def from_string(cls, name: str) -> Enum:
        """convert string to enum"""
