"""MP3 editing"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from enum import IntEnum
from typing import List, Optional, overload

from musicbingo.assets import MP3Asset
from musicbingo.progress import Progress
from musicbingo.song import Duration, Metadata, Song

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
                 filename: str,
                 mode: FileMode,
                 start: int,
                 end: int,
                 metadata: Optional[Metadata] = None,
                 headroom: Optional[int] = None):
        self.filename = filename
        self.mode = mode
        self.headroom = headroom
        self.start = start
        self.end = end
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
        return Duration(int(self.end) - int(self.start))

    @property
    def metadata(self) -> Optional[Metadata]:
        """get the (optional) metadata associated with the output file"""
        return self._metadata

    def normalize(self, headroom: int) -> "MP3File":
        """
        modify volume of MP3 file to be "headroom" dB from maximum volume.
        """
        return MP3File(self.filename, self.mode,
                       metadata=self._metadata, start=self.start,
                       end=self.end, headroom=headroom)

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
                       start=new_start, end=new_end)

    def __len__(self) -> int:
        return int(self.duration)

class MP3FileWriter(MP3File, AbstractContextManager):
    """Represents one output MP3 file"""
    def __init__(self,
                 editor: "MP3Editor",
                 filename: str,
                 bitrate: str,
                 metadata: Optional[Metadata] = None,
                 progress: Optional[Progress] = None):
        super(MP3FileWriter, self).__init__(filename,
                                            FileMode.WRITE_ONLY,
                                            metadata=metadata,
                                            start=0, end=0)
        self._editor = editor
        self._files: List["MP3File"] = []
        self.bitrate = bitrate
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
        super(MP3FileWriter, self).close()

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

    def append(self, mp3file: MP3File) -> None:
        """append an MP3 file to this output"""
        if self.mode != FileMode.WRITE_ONLY:
            raise IOError(f'Cannot append to a {self.mode.name} MP3File')
        if self.filename == '':
            raise IOError("Output filename is not valid")
        self._files.append(mp3file)

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

    @overload
    def use(self, item: Song) -> MP3File: #pylint: disable=no-self-use
        """
        Create an MP3File object from specified song
        """
        ...

    @overload
    def use(self, item: MP3Asset) -> MP3File: #pylint: disable=no-self-use
        """
        Create an MP3File object from specified asset
        """
        ...

    def use(self, item) -> MP3File: #pylint: disable=no-self-use
        """Create an MP3File object"""
        filename: Optional[str] = getattr(item, "filepath", None)
        if filename is None:
            filename = item.filename
        return MP3File(filename, FileMode.READ_ONLY, start=0,
                       end=item.duration)

    def create(self, filename: str, bitrate: str = "256k",
               metadata: Optional[Metadata] = None,
               progress: Optional[Progress] = None) -> MP3FileWriter:
        """create a new MP3 file"""
        #self.destination = filename
        #self.bitrate = bitrate
        return MP3FileWriter(self, filename, bitrate=bitrate,
                             metadata=metadata, progress=progress)

    @abstractmethod
    def _generate(self, destination: MP3FileWriter, progress: Progress) -> None:
        """
        Internal API to generate output file, combining all input files
        public API is MP3FileWriter.generate()
        """
