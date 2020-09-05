"""MP3 editing"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from enum import IntEnum
from pathlib import Path
from typing import List, Optional, Union

from musicbingo.assets import MP3Asset
from musicbingo.duration import Duration
from musicbingo.metadata import Metadata
from musicbingo.progress import Progress
from musicbingo.song import Song


class FileMode(IntEnum):
    """file mode"""
    CLOSED = 0
    READ_ONLY = 1
    WRITE_ONLY = 2


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
        assert isinstance(filename, Path)
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


class MP3FileWriter(MP3File, AbstractContextManager):
    """Represents one output MP3 file"""

    def __init__(self,
                 editor: "MP3Editor",
                 filename: Path,
                 metadata: Metadata,
                 progress: Optional[Progress] = None):
        super().__init__(filename,
                         mode=FileMode.WRITE_ONLY,
                         metadata=metadata,
                         start=0, end=0)
        assert isinstance(metadata, Metadata)
        self._editor = editor
        self._files: List["MP3File"] = []
        if progress is None:
            progress = Progress()
        self.progress = progress

    def generate(self) -> "MP3File":
        """generate output file, combining all input files"""
        self._editor._generate(self, self.progress)
        self.mode = FileMode.READ_ONLY
        return MP3File(self.filename, FileMode.READ_ONLY,
                       start=0, end=int(self.duration),
                       metadata=self._metadata)

    def close(self):
        if self.mode == FileMode.WRITE_ONLY:
            self.generate()
        self._files = []
        super().close()

    def normalize(self, headroom: int) -> "MP3FileWriter":
        self.headroom = headroom
        return self

    def clip(self, start: Optional[int], end: Optional[int]) -> "MP3File":
        """
        Extract the specified section from the MP3File
        """
        raise NotImplementedError("Clipping a MP3FileWriter not implemented")

    @property
    def duration(self) -> Duration:
        """total duration of the file"""
        return Duration(sum([int(f.duration) for f in self._files]))

    def append(self, mp3file: MP3File, overlap: Optional[Duration] = None) -> None:
        """append an MP3 file to this output"""
        if self.mode != FileMode.WRITE_ONLY:
            raise IOError(f'Cannot append to a {self.mode.name} MP3File')
        if self.filename == '':
            raise IOError("Output filename is not valid")
        if overlap is None:
            self._files.append(mp3file)
        else:
            self._files.append(mp3file.overlap_with_previous(overlap))

    def set_metadata(self, metadata: Metadata) -> None:
        """set the metadata associated with the output file"""
        if self.mode != FileMode.WRITE_ONLY:
            raise IOError(f'Cannot set metadata on a {self.mode.name} MP3File')
        self._metadata = metadata

    def __enter__(self) -> "MP3FileWriter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class MP3Editor(ABC):
    """Interface for editing MP3 files"""

    #pylint: disable=no-self-use
    def use(self, item: Union[Song, MP3Asset]) -> MP3File:
        """
        Create an MP3File object from a song or an asset.
        """
        return MP3File(item.fullpath, FileMode.READ_ONLY, start=0,
                       end=int(item.duration), metadata=item)

    def create(self, filename: Path, metadata: Metadata,
               progress: Optional[Progress] = None) -> MP3FileWriter:
        """create a new MP3 file"""
        return MP3FileWriter(self, filename, metadata=metadata,
                             progress=progress)

    @abstractmethod
    def play(self, mp3file: MP3File, progress: Progress) -> None:
        """play the specified MP3 file"""
        raise NotImplementedError()

    @abstractmethod
    def _generate(self, destination: MP3FileWriter, progress: Progress) -> None:
        """
        Internal API to generate output file, combining all input files
        public API is MP3FileWriter.generate()
        """
        raise NotImplementedError()
