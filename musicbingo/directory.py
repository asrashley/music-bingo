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
from typing import Dict, List, Optional, Sequence, Set

from musicbingo.mp3.parser import MP3Parser
from musicbingo.progress import Progress, TextProgress
from musicbingo.song import HasParent, Song

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

    def __init__(self, parent: Optional[HasParent], ref_id: int,
                 directory: Path):
        super(Directory, self).__init__(directory.name, parent)
        self.ref_id = ref_id
        self._fullpath = directory
        self.songs: List[Song] = []
        self.subdirectories: List[Directory] = []
        self.title: str = f'[{directory.name}]'
        self.artist: str = ''
        self.cache_hash: str = ''
        self._lock = threading.Lock()
        self._todo: int = 0
        self.log = logging.getLogger(__name__)

    def search(self, parser: MP3Parser, progress: Progress) -> None:
        """
        Walk self._fullpath searching for all songs and
        sub-directories.
        This function will block until all of the songs and
        directories have been checked.
        """
        try:
            max_workers = len(os.sched_getaffinity(0)) + 2 # type: ignore
        except AttributeError:
            cpu_count = os.cpu_count()
            if cpu_count is None:
                max_workers = 3
            else:
                max_workers = cpu_count + 2
        with futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            todo = set(self.search_async(pool, parser, 0))
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

    def search_async(self, pool: futures.Executor, parser: MP3Parser,
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
        for index, filename in enumerate(self._fullpath.iterdir()):
            abs_fname = str(filename)
            fstats = os.stat(abs_fname)
            if stat.S_ISDIR(fstats.st_mode):
                subdir = Directory(self, 1000 * (self.ref_id + index), filename)
                self.subdirectories.append(subdir)
                tasks.append(
                    pool.submit(subdir.search_async, pool, parser, depth + 1))
            elif (stat.S_ISREG(fstats.st_mode) and
                  abs_fname.lower().endswith(".mp3") and
                  fstats.st_size <= self.maxFileSize):
                self._todo += 1
                task = pool.submit(self._parse_song, parser, cache, filename,
                                   index)
                task.add_done_callback(self._after_parse_song)
                tasks.append(task)
        return tasks

    def _load_cache(self) -> Dict[str, Dict]:
        """load and validate the song cache"""
        assert self._fullpath is not None
        filename = self._fullpath / self.cache_filename
        cache: Dict[str, Dict] = {}
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
                    filename: Path, index: int) -> None:
        """
        Create a Song object for an MP3 file and append to songs list.
        The cache is checked and if that does not contain a match,
        the file will be parsed.
        """
        song: Optional[Song] = None
        try:
            mdata = cache[filename.name]
            try:
                mdata['song_id'] = mdata['songId']
                del mdata['songId']
            except KeyError:
                pass
            try:
                del mdata['index']
            except KeyError:
                pass
            self.log.debug('Use cache for "%s"', filename.name)
            song = Song(filename.name, parent=self,
                        ref_id=(self.ref_id + index + 1), **mdata)
        except KeyError:
            self.log.debug('"%s": Failed to find "%s" in cache', self.filename,
                           filename.name)
        if song is None:
            self.log.info('Parse "%s"', filename.name)
            metadata = parser.parse(filename).as_dict()
            song = Song(filename.name, parent=self,
                        ref_id=(self.ref_id + index + 1), **metadata)
        assert song is not None
        with self._lock:
            self.songs.append(song)


    #pylint: disable=unused-argument
    def _after_parse_song(self, done: futures.Future) -> None:
        """
        Called when a _parse_song future has completed.
        If all files in this directory has been scanned, save the
        cache file.
        """
        with self._lock:
            self._todo -= 1
            if self._todo == 0:
                self._save_cache_locked()

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

    def sort(self, key, reverse=False):
        """Sort directories and songs within each directory"""
        self.subdirectories.sort(key=key, reverse=reverse)
        for sub_dir in self.subdirectories:
            sub_dir.sort(key=key, reverse=reverse)
        self.songs.sort(key=key, reverse=reverse)

    def _save_cache_locked(self) -> None:
        """
        Write contents of this directory to a cache file.
        Only caches the songs in the directory. It does not
        cache information about which subdirectories are
        within this directory.
        *Must be called with self._lock acquired*
        """
        if not self.songs:
            return
        songs = [
            song.marshall(exclude=['fullpath',
                                   'ref_id',
                                   'song_id']) for song in self.songs]
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
        with open(filename, "w") as index_file:
            writer = csv.writer(index_file)
            self._add_to_index(writer)

    def _add_to_index(self, writer) -> None:
        """add songs and sub-directories to the CSV index"""
        for sub_dir in self.subdirectories:
            sub_dir._add_to_index(writer)
        for song in self.songs:
            try:
                writer.writerow([song.artist, song.title, song.filename])
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
        return 'Directory({0}, {1}, {2})'.format(
            self._fullpath, str(self.subdirectories), str(self.songs))

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
            result.append(subdir.dump(level+1))
        last_song = len(self.songs) - 1
        for index, song in enumerate(self.songs):
            indent = song_indent
            if index == last_song:
                indent = indent.replace('|--', '`--')
            result.append(f'{indent} "{song.filename}"')
        return '\n'.join(result)

def main(args: Sequence[str]) -> int:
    """used for testing directory searching from the command line"""
    #pylint: disable=import-outside-toplevel
    from musicbingo.options import Options
    from musicbingo.mp3 import MP3Factory

    log_format = "%(filename)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_format)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    opts = Options.parse(args)
    mp3parser = MP3Factory.create_parser()
    clips = Directory(None, 1, Path(opts.clip_directory))
    progress = TextProgress()
    clips.search(mp3parser, progress)
    print()
    print(clips.dump())
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])
