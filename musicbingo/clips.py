"""
Classes used when generating music clips
"""

from pathlib import Path
import traceback
from typing import Optional, List

from musicbingo.mp3 import MP3Editor, InvalidMP3Exception
from musicbingo.options import Options
from musicbingo.progress import Progress
from musicbingo.song import Metadata, Song

class ClipGenerator:
    """A class to create clips from MP3 files"""
    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 progress: Progress):
        self.options = options
        self.mp3 = mp3_editor
        self.progress = progress

    def generate(self, songs: List[Song], start: int, end: int) -> List[Path]:
        """
        Generate all clips for all selected Songs
        @start - starting time (in milliseconds)
        @end - ending time (in milliseconds)
        Returns list of filenames of new clips
        """
        total_songs = len(songs)
        clips: List[Path] = []
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

    def generate_clip(self, song: Song, start: int, end: int) -> Path:
        """Create one clip from an existing MP3 file."""
        assert song.filepath is not None
        album: Optional[str] = song.album
        if album is None:
            album = song.filepath.parent.name
        assert album is not None
        album = Song.clean(album)
        dest_dir = self.options.clip_destination_dir(album)
        filename = song.filename
        if filename is None or filename == '':
            filename = song.filepath.name
        assert filename is not None
        assert filename != ''
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        dest_path = dest_dir / filename
        metadata = Metadata(artist=Song.clean(song.artist),
                            title=Song.clean(song.title),
                            album=album)
        with self.mp3.create(dest_path, metadata=metadata) as output:
            src = self.mp3.use(song).clip(start, end)
            src = src.normalize(0)
            output.append(src)
            output.generate()
        return dest_path
