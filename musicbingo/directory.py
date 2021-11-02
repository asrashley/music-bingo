"""
Classes to store directories of mp3 files.
"""

from concurrent import futures
import csv
import hashlib
import json
import os
import logging
from pathlib import Path
import stat
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Sequence
from typing import Set, Union, cast

from .mp3.parser import MP3Parser
from .hasparent import HasParent
from .progress import Progress, TextProgress
from .song import Song
from . import models, utils
from .models.db import session_scope


class Directory(HasParent):
    """Represents one directory full of mp3 files.
    It will parse reach mp3 file it finds to create Song objects.
    As this process is quite slow, it caches its results in a
    songs.json file.
    """

    maxFileSize = 32 * 1024 * 1024
    cache_filename = 'songs.json'
    required_fields = ["bitrate", "duration", "filename", "title",
                       "sample_width", "channels", "sample_rate"]
    LEGACY_SONG_ATTRIBUTES = ["song_id", "songId", "index", "prime", "start_time"]

    STORE_LEGACY_JSON = False

    def __init__(self,
                 parent: Optional[HasParent],
                 directory: Path,
                 ref_id: int = -1
                 ):
        super().__init__(directory.name, parent)
        self.ref_id = ref_id
        self._fullpath: Path = directory
        self.songs: List[Song] = []
        self.subdirectories: List[Directory] = []
        self.title: str = directory.name
        self.cache_hash: str = ''
        # A reentrant lock is used because task.add_done_callback()
        # will cause the function to be executed straight away if
        # the task has completed. This is an issue in
        # _search_async_locked() because it needs to add _after_parse_song()
        # as a done callback. That function also needs to acquire the lock
        self._lock = threading.RLock()
        self._disable_database = False
        if parent is not None:
            self._disable_database = cast(Directory, parent)._disable_database
        self.log = logging.getLogger(__name__)

    def search(self, parser: MP3Parser, progress: Progress) -> None:
        """
        Walk self._fullpath searching for all songs and
        sub-directories.
        This function will block until all of the songs and
        directories have been checked.
        """
        try:
            max_workers = len(os.sched_getaffinity(0)) + 2  # type: ignore
        except AttributeError:
            cpu_count = os.cpu_count()
            if cpu_count is None:
                max_workers = 2
            else:
                max_workers = cpu_count + 2
        db_opts = models.db.current_options()
        progress.num_phases = 1
        progress.current_phase = 0
        if (db_opts is not None and db_opts.provider == 'sqlite'
                and db_opts.name == ':memory:'):
            # in-memory sqlite does not support multi-threading unless
            # serialized mode is used. As there does not appear to be
            # a portable way to select serialized mode, disable using
            # the database
            # See https://www.sqlite.org/threadsafe.html
            self.log.warning(
                'Disabling database as sqlite :memory: not threadsafe')
            self._disable_database = True
        with futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            todo = set(self._search_async(pool, parser, 0))
            done: Set[futures.Future] = set()
            while todo and not progress.abort:
                completed, not_done = futures.wait(
                    todo,
                    timeout=0.25,
                    return_when=futures.FIRST_COMPLETED)
                todo.update(set(not_done))
                for future in completed:
                    if progress.abort:
                        break
                    try:
                        err = future.exception()
                        if err is not None:
                            progress.text = f'Error: {err}'
                        else:
                            result = future.result()
                            if isinstance(result, list):
                                todo.update(set(result))
                            elif result is not None:
                                progress.text = result.filename
                    except (futures.TimeoutError, futures.CancelledError):
                        pass
                    except KeyboardInterrupt:
                        progress.abort = True
                    todo.remove(future)
                    done.add(future)
                num_tasks = len(todo) + len(done)
                if num_tasks > 0:
                    progress.pct = 100.0 * len(done) / num_tasks
        next_id = max(1, self._max_dir_id(), self._max_song_id())
        next_id = self.assign_dir_ids(next_id)
        self.assign_song_ids(next_id)

    def _search_async(self, pool: futures.Executor, parser: MP3Parser,
                      depth: int) -> List[futures.Future]:
        """
        Walk self._fullpath scheduling tasks to find all songs and
        sub-directories.
        Checking of files and subdirectories is submitted as tasks
        to the specified pool.
        """
        with self._lock:
            return self._search_async_locked(pool, parser, depth)

    def _search_async_locked(self, pool: futures.Executor, parser: MP3Parser,
                             depth: int) -> List[futures.Future]:
        """
        Walk self._fullpath scheduling tasks to find all songs and
        sub-directories.
        Checking of files and subdirectories is submitted as tasks
        to the specified pool. Must be called with the lock held
        """
        cache = self._load_cache()
        tasks: List[futures.Future] = []
        assert self._fullpath is not None
        if not self._fullpath.is_dir():
            raise IOError(f'Directory "{self._fullpath}" does not exist')
        self.log.debug('Search %s', self._fullpath.name)
        for filename in self._fullpath.iterdir():
            abs_fname = str(filename)
            fstats = os.stat(abs_fname)
            if stat.S_ISDIR(fstats.st_mode):
                subdir = Directory(self, filename)
                self.subdirectories.append(subdir)
                tasks.append(
                    pool.submit(subdir._search_async, pool, parser, depth + 1))
            elif (stat.S_ISREG(fstats.st_mode) and
                  abs_fname.lower().endswith(".mp3") and
                  fstats.st_size <= self.maxFileSize):
                task = pool.submit(self._parse_song, parser, cache, filename)
                tasks.append(task)
        return tasks

    def toplevel_directory(self) -> Path:
        """
        Get absolute path of the directory at the top of the tree
        """
        if self._parent is None:
            assert self._fullpath is not None
            return self._fullpath
        parent = self._parent
        while parent._parent is not None:
            parent = parent._parent
        assert parent._fullpath is not None
        return parent._fullpath

    def relative_name(self) -> Path:
        """
        Calculate a path relative to the top level directory
        """
        if self._parent is None:
            return Path(".")
        top = self.toplevel_directory()
        assert self._fullpath is not None
        return self._fullpath.relative_to(top)

    def model(self, session) -> Optional[models.Directory]:
        """
        Get the database version of this directory
        """
        assert self._fullpath is not None
        name = cast(Path, self._fullpath).resolve().as_posix()
        return cast(Optional[models.Directory], models.Directory.get(session, name=name))

    def save_all(self, session) -> models.Directory:
        """
        Save this directory, its songs and its subdirectories
        """
        db_dir = self.save(session, True)
        for song in self.songs:
            song.save(session, db_dir)
        for sub_dir in self.subdirectories:
            sub_dir.save_all(session)
        return db_dir

    def save(self, session, flush: bool = False) -> models.Directory:
        """
        Save directory to database
        """
        assert self._fullpath is not None
        name = self._fullpath.resolve().as_posix()
        db_dir = cast(Optional[models.Directory], models.Directory.get(session, name=name))
        add = False
        if db_dir is None:
            db_dir = models.Directory(name=name, title=self.title)
            add = True
        if self._parent is not None:
            db_dir.parent = cast(Directory, self._parent).model(session)
        if add:
            session.add(db_dir)
        if flush:
            session.flush()
        return db_dir

    def _load_cache(self) -> Dict[str, Dict]:
        """
        load and validate the song cache.
        Must be called with the lock held
        """
        assert self._fullpath is not None
        self.log.debug('Load cache %s', self._fullpath.name)
        if not self._disable_database:
            cache = self._check_database()
            if cache is not None:
                return cache
        self.log.debug('fallback to JSON')
        return self._check_json_file()

    def _check_database(self) -> Optional[Dict[str, Dict]]:
        """
        Check database for this directory.
        If found, load all songs for this directory into the
        cache
        """
        with session_scope() as session:
            db_dir = self.model(session)
            if db_dir is None:
                return None
            cache: Dict[str, Dict] = {}
            self.log.debug('Found DB model')
            exclude = {'pk', 'directory', 'artist', 'album'}
            # self._model = db_dir
            for db_song in db_dir.songs:
                cache[db_song.filename] = db_song.to_dict(exclude=exclude)
                if db_song.album is not None:
                    cache[db_song.filename]['album'] = db_song.album.name
                if db_song.artist is not None:
                    cache[db_song.filename]['artist'] = db_song.artist.name
                if 'classtype' in cache[db_song.filename]:
                    del cache[db_song.filename]['classtype']
                del cache[db_song.filename]['filename']
            self.log.debug('Found %d songs in DB', len(cache.keys()))
            return cache

    def _check_json_file(self) -> Dict[str, Dict]:
        """
        Check this directory for a JSON cache file.
        If found, load all songs from the JSON file.
        """
        cache: Dict[str, Dict] = {}
        assert self._fullpath is not None
        filename = self._fullpath / self.cache_filename
        if not filename.exists():
            self.log.debug('No cache file %s', filename)
            return cache
        with filename.open('r') as cfn:
            data = cfn.read()
        contents = json.loads(data)
        sha = hashlib.sha256()
        sha.update(data.encode('utf-8'))
        self.cache_hash = sha.hexdigest()
        for song in contents:
            skip = False
            for field in self.required_fields:
                if field not in song:
                    self.log.debug('Missing field %s from %s',
                                   field, song['filename'])
                    skip = True
            if not skip and song['sample_width'] < 8:
                self.log.debug('Invalid sample width %d for %s',
                               song['sample_width'], song['filename'])
                # work-around for invalid cached data
                skip = True
            if not skip:
                fname = song.pop('filename')
                cache[fname] = song
        self.log.debug('Loaded %d songs from cache %s', len(cache.keys()), self._fullpath.name)
        return cache

    def _parse_song(self, parser: MP3Parser, cache: Dict[str, dict],
                    filename: Path) -> None:
        """
        Create a Song object for an MP3 file and append to songs list.
        The cache is checked and if that does not contain a match,
        the file will be parsed.
        """
        song: Optional[Song] = None
        try:
            mdata = cache[filename.name]
            for name in self.LEGACY_SONG_ATTRIBUTES:
                try:
                    del mdata[name]
                except KeyError:
                    pass
            self.log.debug('Use cache for "%s"', filename.name)
            self.log.debug('   %s', mdata)
            if 'ref_id' not in mdata:
                mdata['ref_id'] = -1
            for field in ['title', 'album']:
                if field in mdata:
                    mdata[field] = utils.clean_string(mdata[field])
            song = Song(filename.name, parent=self, **mdata)
        except KeyError:
            self.log.debug('"%s": Failed to find "%s" in cache', self.filename,
                           filename.name)
        if song is None:
            self.log.info('Parse "%s"', filename.name)
            metadata = parser.parse(filename).as_dict()
            song = Song(filename.name, parent=self, **metadata)
        assert song is not None
        with self._lock:
            self.songs.append(song)

    def find(self, ref_id: int) -> Optional[Song]:
        """Find a Song by its ref_id"""
        for song in self.songs:
            if song.ref_id == ref_id:
                return song
        for sub_dir in self.subdirectories:
            song2 = sub_dir.find(ref_id)
            if song2 is not None:
                return song2
        return None

    def total_length(self) -> int:
        """Returns total number of songs.
        Returns total of songs in this directory plus any subdirectories
        """
        total = len(self.songs)
        for sub_dir in self.subdirectories:
            total += len(sub_dir)
        return total

    def get_songs(self, ref_id: int) -> List[Song]:
        """
        Get all matching songs.
        Returns a list of all songs that match ref_id or all songs
        in a directory if its ref_id matches
        """
        song_list: List[Song] = []
        if ref_id == self.ref_id:
            for sub_dir in self.subdirectories:
                song_list += sub_dir.get_songs(sub_dir.ref_id)
            song_list += self.songs
        else:
            for sub_dir in self.subdirectories:
                song_list += sub_dir.get_songs(ref_id)
            for song in self.songs:
                if ref_id == song.ref_id:
                    song_list.append(song)
        return song_list

    def sort(self, key: Union[str, Callable[[HasParent], Any]], reverse: bool = False) -> None:
        """Sort directories and songs within each directory"""
        if isinstance(key, str):
            name = key
            key = lambda item: getattr(item, name)
        self.subdirectories.sort(key=key, reverse=reverse)  # type: ignore
        for sub_dir in self.subdirectories:
            sub_dir.sort(key=key, reverse=reverse)  # type: ignore
        self.songs.sort(key=key, reverse=reverse)  # type: ignore

    def _save_cache_locked(self) -> None:
        """
        Write contents of this directory to a cache file.
        Only caches the songs in the directory. It does not
        cache information about which subdirectories are
        within this directory.
        *Must be called with self._lock acquired*
        """
        if self._disable_database:
            return
        with session_scope() as session:
            db_dir = self.save(session, flush=True)
            for song in self.songs:
                song.save(session, db_dir)
        if not self.STORE_LEGACY_JSON:
            return
        songs = [
            song.to_dict(
                exclude={'fullpath', 'ref_id'}) for song in self.songs]
        js_str = json.dumps(songs, ensure_ascii=True)
        sha = hashlib.sha256()
        sha.update(js_str.encode('utf-8'))
        digest = sha.hexdigest()
        if self.cache_hash != digest:
            assert self._fullpath is not None
            cfn = self._fullpath / self.cache_filename
            with cfn.open('w') as cache_file:
                cache_file.write(js_str)
            self.cache_hash = digest

    def create_index(self, filename: str) -> None:
        """Create a CSV file that contains a list of all songs"""
        with open(filename, "w", encoding='utf-8') as index_file:
            writer = csv.writer(index_file)
            self._add_to_index(writer)

    def _add_to_index(self, writer) -> None:
        """add songs and sub-directories to the CSV index"""
        for sub_dir in self.subdirectories:
            sub_dir._add_to_index(writer)
        for song in self.songs:
            try:
                writer.writerow([self.title, song.artist, song.title, song.filename])
            except UnicodeEncodeError:
                pass

    def __len__(self):
        return len(self.songs) + len(self.subdirectories)

    def __getitem__(self, index):
        sub_len = len(self.subdirectories)
        if index < sub_len:
            return self.subdirectories[index]
        return self.songs[index - sub_len]

    def __repr__(self):
        return f'Directory({self._fullpath}, {self.subdirectories}, {self.songs})'

    def dump(self, level: int = 0) -> str:
        """
        Return a string representation of this directory in a form
        similar to tree.
        """
        result: List[str] = []
        if level == 0:
            dir_indent = ''
            song_indent = '|-- '
        else:
            dir_indent = '|   ' * (level - 1) + '|-- '
            song_indent = '|   ' * level + '|-- '
        result.append(dir_indent + self.filename)
        for subdir in self.subdirectories:
            result.append(subdir.dump(level + 1))
        last_song = len(self.songs) - 1
        for index, song in enumerate(self.songs):
            indent = song_indent
            if index == last_song:
                indent = indent.replace('|--', '`--')
            result.append(f'{indent} "{song.filename}"')
        return '\n'.join(result)

    def assign_dir_ids(self, next_id: int) -> int:
        """
        Assign a ref_id to any directory that does not have a ref_id
        """
        if self.ref_id < 1:
            self.ref_id = next_id
            next_id += 1
        for subdir in self.subdirectories:
            if subdir.ref_id < 1:
                subdir.ref_id = next_id
                next_id += 1
            next_id = subdir.assign_dir_ids(next_id)
        return next_id

    def assign_song_ids(self, next_id: int) -> int:
        """
        Assign a ref_id to any song that does not have a ref_id
        """
        for song in self.songs:
            if song.ref_id < 1:
                song.ref_id = next_id
                next_id += 1
        for subdir in self.subdirectories:
            next_id = subdir.assign_song_ids(next_id)
        return next_id

    def _max_dir_id(self) -> int:
        """
        Find the highest ref_id of any directory in this
        directory
        """
        max_ref_id = self.ref_id
        for subdir in self.subdirectories:
            max_ref_id = max(max_ref_id, subdir._max_dir_id())
        return max_ref_id

    def _max_song_id(self) -> int:
        """
        Find the highest ref_id of any song in this
        directory or subdirectories
        """
        max_id = -1
        for song in self.songs:
            max_id = max(max_id, song.ref_id)
        for subdir in self.subdirectories:
            max_id = max(max_id, subdir._max_song_id())
        return max_id


def main(args: Sequence[str]) -> int:
    """used for testing directory searching from the command line"""
    # pylint: disable=import-outside-toplevel
    from musicbingo.options import Options
    from musicbingo.mp3 import MP3Factory

    log_format = "%(thread)d %(filename)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_format)
    opts = Options.parse(args)
    if opts.debug:
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logging.getLogger(models.db.__name__).setLevel(logging.DEBUG)
    models.db.DatabaseConnection.bind(opts.database, debug=opts.debug)
    mp3parser = MP3Factory.create_parser()
    clips = Directory(None, Path(opts.clip_directory))
    progress = TextProgress()
    clips.search(mp3parser, progress)
    clips.sort('filename')
    with session_scope() as session:
        clips.save_all(session)
        models.Directory.show(session)
    #print()
    #print(clips.dump())
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
