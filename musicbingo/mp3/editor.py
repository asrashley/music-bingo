"""MP3 editing"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from typing import List, Optional

from musicbingo.duration import Duration
from musicbingo.metadata import Metadata
from musicbingo.progress import Progress

from .filemode import FileMode
from .mp3file import MP3File
from .uses_mixin import UsesMP3Mixin

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
        return Duration(sum(int(f.duration) for f in self._files))

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


class MP3Editor(UsesMP3Mixin, ABC):
    """Interface for editing MP3 files"""

    debug = False

    def create(self, filename: Path, metadata: Metadata,
               progress: Optional[Progress] = None) -> MP3FileWriter:
        """create a new MP3 file"""
        return MP3FileWriter(self, filename, metadata=metadata,
                             progress=progress)

    @abstractmethod
    def _generate(self, destination: MP3FileWriter, progress: Progress) -> None:
        """
        Internal API to generate output file, combining all input files
        public API is MP3FileWriter.generate()
        """
        raise NotImplementedError()
