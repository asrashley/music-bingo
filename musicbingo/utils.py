"""
Various utility functions
"""

import datetime
from enum import Enum
import math
from pathlib import Path
import re
import time
from typing import Any, List, Optional, Union

from musicbingo.docgen.colour import Colour
from musicbingo.docgen.sizes import Dimension
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
    if hasattr(item, 'as_dict'):
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
        item = '/'.join([item.parent.name, item.name])
    elif isinstance(item, Enum):
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
    retval.append('{0:0.2f}S'.format(secs))
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


def parse_date(date: str,
               format: Optional[str] = None) -> Optional[Union[datetime.datetime,
                                                               datetime.timedelta,
                                                               datetime.time]]:
    """Try to create a datetime from the given string"""
    formats = ["%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%b %Y", "%b %y", "%m/xx/%y",
               "%a %b %d %Y", "%B %d %Y %H:%M", "%b %d %Y %H:%M",
               "%B %d %Y", "%b %d %Y", '%a %b %d, %Y',
               "%Y-%m-%d %H:%M:%S%z"
               ]
    if format is not None:
        formats.insert(0, format)
    if not isinstance(date, str):
        date = str(date)
    try:
        return from_isodatetime(date)
    except ValueError:
        pass
    d = date
    tz = datetime.timedelta(0)
    if re.match(r'.+\s+ES?T$', date):
        tz = datetime.timedelta(hours=5)
    elif re.match(r'.+\s+EDT$', date):
        tz = datetime.timedelta(hours=4)
    elif re.match(r'.+\s+PS?T$', date):
        tz = datetime.timedelta(hours=8)
    elif re.match(r'.+\s+PDT$', date):
        tz = datetime.timedelta(hours=7)
    for regex, sub in date_hacks:
        d = regex.sub(sub, d)
    for f in formats:
        try:
            rv = datetime.datetime.strptime(d, f)
            if '%z' not in f:
                rv += tz
            return rv
        except ValueError as err:
            # print(err)
            pass
    return datetime.datetime(*(time.strptime(date)[0:6]))


def make_naive_utc(t: datetime.datetime) -> datetime.datetime:
    """
    Convert a timezone aware datetime into a naive datetime
    using UTC timezone
    """
    utc_timezone = datetime.timezone(datetime.timedelta(seconds=0))
    return t.astimezone(utc_timezone).replace(tzinfo=None)
