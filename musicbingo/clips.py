"""
Classes used when generating music clips
"""

import os
import traceback
from typing import List

from musicbingo.mp3 import MP3Editor, InvalidMP3Exception
from musicbingo.progress import Progress
from musicbingo.song import Metadata, Song

class ClipGenerator:
    """A class to create clips from MP3 files"""
    def __init__(self, destination: str, mp3_editor: MP3Editor,
                 progress: Progress):
        self.destination = destination
        self.mp3 = mp3_editor
        self.progress = progress

    def generate(self, songs: List[Song], start: int, end: int) -> List[str]:
        """
        Generate all clips for all selected Songs
        @start - starting time (in milliseconds)
        @end - ending time (in milliseconds)
        Returns list of filenames of new clips
        """
        total_songs = len(songs)
        clips: List[str] = []
        for index, song in enumerate(songs):
            #print(song.title, song.artist, song.album)
            self.progress.text = '{} ({:d}/{:d})'.format(Song.clean(song.title),
                                                         index, total_songs)
            self.progress.pct = 100.0 * float(index) / float(total_songs)
            #pylint: disable=broad-except
            try:
                clips.append(self.generate_clip(song, start, end))
            except InvalidMP3Exception as err:
                traceback.print_exc()
                print(r'Error generating clip: {0} - {1}'.format(
                    Song.clean(song.title), str(err)))
        self.progress.pct = 100.0
        self.progress.text = 'Finished generating clips'
        return clips

    def generate_clip(self, song: Song, start: int, end: int) -> str:
        """Create one clip from an existing MP3 file."""
        assert song.filepath is not None
        head, tail = os.path.split(os.path.dirname(song.filepath))
        dirname = tail if tail else head
        assert dirname is not None
        dest_dir = os.path.join(self.destination, dirname)
        assert song.filename is not None
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest_path = os.path.join(dest_dir, song.filename)
        album = ''
        if song.album:
            album = Song.clean(song.album)
        metadata = Metadata(artist=Song.clean(song.artist),
                            title=Song.clean(song.title),
                            album=album)
        with self.mp3.create(dest_path, metadata=metadata) as output:
            src = self.mp3.use(song).clip(start, end)
            src = src.normalize(0)
            output.append(src)
            output.generate()
        return dest_path
