"""
Base class for work that is performed in a background thread
"""

from __future__ import print_function
from abc import ABC, abstractmethod
from pathlib import Path
import threading
from typing import Any, Callable, List, Optional, Tuple

from musicbingo.clips import ClipGenerator
from musicbingo.directory import Directory
from musicbingo.docgen import DocumentFactory
from musicbingo.duration import Duration
from musicbingo.generator import GameGenerator
from musicbingo.mp3 import MP3Factory
from musicbingo.options import GameMode, Options
from musicbingo.progress import Progress
from musicbingo.song import Song

class BackgroundWorker(ABC):
    """Base class for work that is performed in a background thread"""
    def __init__(self, args: Tuple[Any, ...], options: Options,
                 finalise: Callable[[Any], None]):
        self.progress = Progress()
        self.options = options
        self.finalise = finalise
        self.bg_thread = threading.Thread(target=self.run,
                                          args=args, daemon=True)
        self.result: Optional[Any] = None

    def start(self) -> None:
        """start a new thread to execute the run() method"""
        self.bg_thread.start()

    def abort(self) -> None:
        """try to stop the background thread"""
        self.progress.abort = True

    @abstractmethod
    def run(self, *args) -> None:
        """function that is called in the background thread"""
        raise NotImplementedError()


class SearchForClips(BackgroundWorker):
    """worker for running Directory.search()"""

    #pylint: disable=arguments-differ
    def run(self, clipdir: Path) -> None:  # type: ignore
        """Walk clip_directory finding all songs and sub-directories.
        This function retrieves a list of songs from the Clips folder,
        gets the Title/Artist data and adds them to the song list.
        This function runs in its own thread
        """
        mp3parser = MP3Factory.create_parser()
        clips = Directory(None, 1, clipdir)
        self.progress.text = 'Searching for clips'
        self.progress.pct = 0.0
        clips.search(mp3parser, self.progress)
        self.result = clips

class GenerateBingoGame(BackgroundWorker):
    """worker for generating a bingo game"""

    #pylint: disable=arguments-differ
    def run(self, game_songs) -> None:  # type: ignore
        """
        Creates MP3 file and PDF files.
        """
        mp3editor = MP3Factory.create_editor(self.options.mp3_engine)
        docgen = DocumentFactory.create_generator('pdf')
        gen = GameGenerator(self.options, mp3editor, docgen,
                            self.progress)
        try:
            gen.generate(game_songs)
            if self.progress.abort:
                self.progress.text = 'Aborted generation'
            elif self.options.mode == GameMode.BINGO:
                self.progress.text = f"Finished Generating Bingo Game: {self.options.game_id}"
            else:
                self.progress.text = "Finished Generating Bingo Quiz"
        except ValueError as err:
            self.progress.text = str(err)
        finally:
            self.progress.pct = 100.0

class GenerateClips(BackgroundWorker):
    """worker for generating song clips"""

    #pylint: disable=arguments-differ
    def run(self, songs: List[Song]) -> None: # type: ignore
        """Generate all clips for all selected Songs
        This function runs in its own thread
        """
        mp3editor = MP3Factory.create_editor()
        gen = ClipGenerator(self.options, mp3editor, self.progress)
        self.result = gen.generate(songs)

class PlaySong(BackgroundWorker):
    """worker for playing song clips"""

    #pylint: disable=arguments-differ
    def run(self, songs: List[Song]) -> None: # type: ignore
        """
        Play one or more songs
        This function runs in its own thread
        """
        mp3editor = MP3Factory.create_editor()
        for song in songs:
            afile = mp3editor.use(song)
            if self.options.mode == GameMode.CLIP:
                start = int(Duration.parse(self.options.clip_start))
                if start >= int(song.duration):
                    continue
                end = start + self.options.clip_duration * 1000
                afile = afile.clip(start, end)
            self.progress.text = f'{song.artist}: {song.title}'
            mp3editor.play(afile, self.progress)
            if self.progress.abort:
                return
