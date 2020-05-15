"""
Duration class is used to wrap an int millisecond
period of time.
"""
from typing import SupportsInt, Union


class Duration(SupportsInt):
    """Duration of a song (in milliseconds)"""

    def __init__(self, value: Union[int, str]) -> None:
        if isinstance(value, str):
            value = int(self.parse(value))
        self._value: int = value

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return self.format()

    def __add__(self, dur: "Duration") -> "Duration":
        return Duration(int(self) + int(dur))

    def __iadd__(self, dur: "Duration") -> "Duration":
        self._value += int(dur)
        return self

    def __floordiv__(self, other: int) -> int:
        return self._value // other

    @staticmethod
    def parse(time_str: str) -> "Duration":
        """Convert string in the form MM:SS to milliseconds"""
        parts = time_str.split(':')
        parts.reverse()
        secs = 0
        while parts:
            secs = (60 * secs) + int(parts.pop(), 10)
        return Duration(secs * 1000)

    def format(self) -> str:
        """convert the time in milliseconds to a MM:SS form"""
        secs: int = self._value // 1000
        seconds = secs % 60
        minutes = secs // 60
        if minutes < 60:
            return '{0:d}:{1:02d}'.format(minutes, seconds)
        hours = minutes // 60
        minutes = minutes % 60
        return '{0:d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)
