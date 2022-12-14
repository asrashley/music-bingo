"""
Representation of one MP3 file for editing, parsing or playing
"""
from pathlib import Path
from typing import Optional

from musicbingo.duration import Duration
from musicbingo.metadata import Metadata

from .filemode import FileMode

class MP3File:
    """
    Represents one source MP3 file
    Functions that modify the file return a new instance of
    MP3File
    """

    def __init__(self,
                 filename: Path,
                 mode: FileMode,
                 start: int,
                 end: int,
                 metadata: Metadata,
                 headroom: Optional[int] = None,
                 overlap: int = 0):
        self.filename = filename
        self.mode = mode
        self.headroom = headroom
        self.start = start
        self.end = end
        self.overlap = overlap
        self._metadata = metadata

    def close(self):
        """close open file"""
        if self.mode != FileMode.CLOSED:
            self.filename = ''
            self.mode = FileMode.CLOSED

    @property
    def duration(self) -> Duration:
        """total duration of the file"""
        assert self.start is not None
        assert self.end is not None
        return Duration(int(self.end) - int(self.start) - self.overlap)

    @property
    def metadata(self) -> Metadata:
        """get the (optional) metadata associated with the output file"""
        return self._metadata

    def normalize(self, headroom: int) -> "MP3File":
        """
        modify volume of MP3 file to be "headroom" dB from maximum volume.
        """
        return MP3File(self.filename, self.mode,
                       metadata=self._metadata, start=self.start,
                       end=self.end, headroom=headroom, overlap=self.overlap)

    def clip(self, start: Optional[int], end: Optional[int]) -> "MP3File":
        """
        Extract the specified section from the MP3File
        """
        new_start = self.start
        new_end = self.end
        if start is not None:
            new_start += start
        if end is not None:
            new_end = min(end, new_end)
        return MP3File(self.filename, mode=self.mode,
                       metadata=self._metadata, headroom=self.headroom,
                       start=new_start, end=new_end, overlap=self.overlap)

    def overlap_with_previous(self, overlap: Duration) -> "MP3File":
        """
        Signal that this MP3File should overlap with its previous file
        """
        return MP3File(self.filename, mode=self.mode,
                       metadata=self._metadata, headroom=self.headroom,
                       start=self.start, end=self.end, overlap=int(overlap))

    def __len__(self) -> int:
        return int(self.duration) - self.overlap
