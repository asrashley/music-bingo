"""
Classes to store directories of mp3 files.
"""

import csv
import hashlib
import json
import math
import os
import stat
import sys

from typing import Dict, List, Optional

from musicbingo.mp3.exceptions import InvalidMP3Exception, NotAnMP3Exception
from musicbingo.mp3.parser import MP3Parser
from musicbingo.progress import Progress
from musicbingo.song import HasParent, Metadata, Song

class Directory(HasParent):
    """Represents one directory full of mp3 files.
    It will parse reach mp3 file it finds to create Song objects.
    As this process is quite slow, it caches its results in a
    songs.json file.
    """

    maxFileSize = 32 * 1024 * 1024
    cache_filename = 'songs.json'

    def __init__(self, parent: Optional[HasParent], ref_id: int,
                 directory: str, parser: MP3Parser,
                 progress: Progress):
        super(Directory, self).__init__(parent)
        self.ref_id = ref_id
        self.directory = directory
        self.parser = parser
        self.progress = progress
        self.songs: List[Song] = []
        self.subdirectories: List[Directory] = []
        _, tail = os.path.split(directory)
        self.title: str = '[{0}]'.format(tail)
        self.artist: str = ''
        self.cache_hash: str = ''

    def search(self, depth: int = 0, start_pct: float = 0.0) -> None:
        """Walk self.directory finding all songs and sub-directories."""
        if not os.path.isdir(self.directory):
            raise IOError(f'Directory "{self.directory}" does not exist')
        cache = {}
        try:
            with open(os.path.join(self.directory, self.cache_filename), 'r') as cfn:
                data = cfn.read()
            contents = json.loads(data)
            sha = hashlib.sha256()
            sha.update(data.encode('utf-8'))
            self.cache_hash = sha.hexdigest()
            for song in contents:
                cache[song['filename']] = song
            del data
            del contents
            del sha
        except IOError as err:
            print(err)
        folder_list = os.listdir(self.directory)
        divisor = math.pow(10, depth) * len(folder_list)
        for index, filename in enumerate(folder_list):
            pct = start_pct + (100.0 * index / divisor)
            self.progress.text = f'{self.directory}: {filename}'
            self.progress.pct = pct
            try:
                self.songs.append(
                    self._check_file(cache, filename, index, pct, depth))
            except NotAnMP3Exception:
                pass
            except InvalidMP3Exception as err:
                print(sys.exc_info())
                print(f"Error inspecting file: {filename} - {err}")
        if self.songs:
            self.save_cache()

    def _check_file(self, cache: Dict[str, dict],
                    filename: str, index: int, start_pct: float,
                    depth: int) -> Song:
        """Check one file to see if it an MP3 file or a directory.
        If it is a directory, a new Directory object is created for that
        directory. If it is an MP3 file, as new Song object is created
        """
        abs_path = os.path.join(self.directory, filename)
        stats = os.stat(abs_path)
        if stat.S_ISDIR(stats.st_mode):
            subdir = Directory(self, 1000 * (self.ref_id + index), abs_path,
                               self.parser, self.progress)
            subdir.search(depth + 1, start_pct)
            self.subdirectories.append(subdir)
        elif not stat.S_ISREG(stats.st_mode):
            raise NotAnMP3Exception("Not a regular file")
        if filename.lower()[-4:] != ".mp3":
            raise NotAnMP3Exception("Wrong file extension")
        if stats.st_size > self.maxFileSize:
            raise InvalidMP3Exception(f'{filename} is too large')
        try:
            mdata = cache[filename]
            try:
                mdata['filepath'] = os.path.join(self.directory,
                                                 mdata['filename'])
            except KeyError:
                pass
            try:
                mdata['song_id'] = mdata['songId']
                del mdata['songId']
            except KeyError:
                pass
            try:
                del mdata['index']
            except KeyError:
                pass
            return Song(self, self.ref_id + index + 1, Metadata(**mdata))
        except KeyError:
            pass
        metadata = self.parser.parse(self.directory, filename)
        return Song(self, self.ref_id + index + 1, metadata)

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
        """Get all matching songs.
        Returns a list of all songs that match ref_id or all songs
        in a directory if its ref_id matches
        """
        song_list = []
        for sub_dir in self.subdirectories:
            for song in sub_dir.get_songs(ref_id):
                song_list.append(song)
        for song in self.songs:
            if ref_id in [song.ref_id, self.ref_id]:
                song_list.append(song)
        return song_list

    def sort(self, key, reverse=False):
        """Sort directories and songs within each directory"""
        self.subdirectories.sort(key=key, reverse=reverse)
        for sub_dir in self.subdirectories:
            sub_dir.sort(key=key, reverse=reverse)
        self.songs.sort(key=key, reverse=reverse)

    def save_cache(self):
        """Write contents of this directory to a cache file"""
        songs = [song.marshall(exclude=['filepath', 'ref_id', 'song_id']) for song in self.songs]
        js_str = json.dumps(songs, ensure_ascii=True)
        sha = hashlib.sha256()
        sha.update(js_str.encode('utf-8'))
        if self.cache_hash != sha.hexdigest():
            cfn = os.path.join(self.directory, self.cache_filename)
            with open(cfn, 'w') as cache_file:
                cache_file.write(js_str)

    def create_index(self, filename: str) -> None:
        """Create a CSV file that contains a list of all songs"""
        with open(filename, "wb") as index_file:
            writer = csv.writer(index_file)
            self._add_to_index(writer)

    def _add_to_index(self, writer) -> None:
        """add songs and sub-directories to the CSV index"""
        for sub_dir in self.subdirectories:
            sub_dir._add_to_index(writer)
        for song in self.songs:
            try:
                writer.writerow([song.artist, song.title, song.filepath])
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
            self.directory, str(self.subdirectories), str(self.songs))
