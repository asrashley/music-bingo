"""
Base class for work that is performed in a background thread
"""

from abc import ABC, abstractmethod
from pathlib import Path
import threading
from typing import (
    Any, Callable, Dict, List, NamedTuple, Optional, Tuple,
)

from musicbingo import models
from musicbingo.clips import ClipGenerator
from musicbingo.directory import Directory
from musicbingo.docgen import DocumentFactory
from musicbingo.duration import Duration
from musicbingo.generator import GameGenerator
from musicbingo.models.modelmixin import JsonObject, PrimaryKeyMap
from musicbingo.models.importer import Importer
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
        clips = Directory(None, clipdir)
        self.progress.text = 'Searching for clips'
        self.progress.pct = 0.0
        clips.search(mp3parser, self.progress)
        with models.db.session_scope() as session:
            clips.save_all(session)
        self.result = clips


class GenerateBingoGame(BackgroundWorker):
    """worker for generating a bingo game"""

    #pylint: disable=arguments-differ
    def run(self, game_songs) -> None:  # type: ignore
        """
        Creates MP3 file and PDF files.
        """
        mp3editor = MP3Factory.create_editor(self.options.mp3_editor)
        docgen = DocumentFactory.create_generator('pdf')
        gen = GameGenerator(self.options, mp3editor, docgen,
                            self.progress)
        try:
            # pylint: disable=no-value-for-parameter
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
    def run(self, songs: List[Song]) -> None:  # type: ignore
        """Generate all clips for all selected Songs
        This function runs in its own thread
        """
        mp3editor = MP3Factory.create_editor(self.options.mp3_editor)
        gen = ClipGenerator(self.options, mp3editor, self.progress)
        self.result = gen.generate(songs)


class PlaySong(BackgroundWorker):
    """worker for playing song clips"""

    #pylint: disable=arguments-differ
    def run(self, songs: List[Song]) -> None:  # type: ignore
        """
        Play one or more songs
        This function runs in its own thread
        """
        player = MP3Factory.create_player(self.options.mp3_player)
        for song in songs:
            afile = player.use(song)
            if self.options.mode == GameMode.CLIP:
                start = int(Duration.parse(self.options.clip_start))
                if start >= int(song.duration):
                    continue
                end = start + self.options.clip_duration * 1000
                afile = afile.clip(start, end)
            self.progress.text = f'{song.artist}: {song.title}'

            player.play(afile, self.progress)
            if self.progress.abort:
                return


class DbIoResult(NamedTuple):
    """
    Contains the result of a DB import or export
    """
    filename: Optional[Path] = None
    source: Optional[JsonObject] = None
    pk_maps: PrimaryKeyMap = {}
    added: Dict[str, int] = {}


class ImportDatabase(BackgroundWorker):
    """
    worker for importing an entire database
    """

    #pylint: disable=arguments-differ
    def run(self, filename: Path, source: Optional[JsonObject] = None) -> None:  # type: ignore
        """
        Import an entire database from a JSON file
        """
        with models.db.session_scope() as session:
            imp = Importer(self.options, session, self.progress)
            imp.import_database(filename, source)
            self.result = DbIoResult(filename=filename,
                                     pk_maps=imp.pk_maps, added=imp.added, )


class ImportGameTracks(BackgroundWorker):
    """
    worker for importing a game into the database
    """

    #pylint: disable=arguments-differ
    def run(self, filename: Path, source: JsonObject, game_id: str = '') -> None: # type: ignore
        """
        Import a game into the database from a JSON file
        """
        with models.db.session_scope() as session:
            imp = Importer(self.options, session, self.progress)
            if 'Songs' in source:
                imp.import_json(source)
            else:
                imp.import_game_tracks(filename, game_id, source)
            self.result = DbIoResult(filename=filename, source=source,
                                     pk_maps=imp.pk_maps, added=imp.added)


class ExportDatabase(BackgroundWorker):
    """
    worker for exporting an entire database
    """

    #pylint: disable=arguments-differ
    def run(self, filename: Path, options: Options) -> None:  # type: ignore
        """
        Export an entire database to a JSON file
        """
        with models.db.session_scope() as session:
            models.export_database(filename, options, self.progress, session)
        self.result = DbIoResult(filename=filename)
