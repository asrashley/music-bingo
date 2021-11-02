"""
Classes used when generating music clips
"""

from pathlib import Path
import traceback
from typing import Optional, List

from musicbingo.duration import Duration
from musicbingo.mp3 import MP3Editor, InvalidMP3Exception
from musicbingo.options import Options
from musicbingo.progress import Progress
from musicbingo.metadata import Metadata
from musicbingo.song import Song
from musicbingo.utils import clean_string

class ClipGenerator:
    """A class to create clips from MP3 files"""

    def __init__(self, options: Options, mp3_editor: MP3Editor,
                 progress: Progress):
        self.options = options
        self.mp3 = mp3_editor
        self.progress = progress

    def generate(self, songs: List[Song]) -> List[Path]:
        """
        Generate all clips for all selected Songs
        Returns list of filenames of new clips
        """
        total_songs = len(songs)
        clips: List[Path] = []
        start = int(Duration(self.options.clip_start))
        end = start + 1000 * self.options.clip_duration
        self.progress.num_phases = 1
        self.progress.current_phase = 0
        for index, song in enumerate(songs):
            # pylint: disable=consider-using-f-string
            self.progress.text = '{} ({:d}/{:d})'.format(Song.clean(song.title),
                                                         index, total_songs)
            self.progress.pct = 100.0 * float(index) / float(total_songs)
            # pylint: disable=broad-except
            try:
                clips.append(self.generate_clip(song, start, end))
            except (InvalidMP3Exception, ValueError) as err:
                traceback.print_exc()
                print(r'Error generating clip: {0} - {1}'.format(
                    Song.clean(song.title), str(err)))
        self.progress.pct = 100.0
        if len(songs) == 1:
            self.progress.text = f'Finished generating {Song.clean(songs[0].title)}'
        else:
            self.progress.text = f'Finished generating {len(songs)} clips'
        return clips

    def generate_clip(self, song: Song, start: int, end: int) -> Path:
        """Create one clip from an existing MP3 file."""
        album: Optional[str] = song.album
        if album is None:
            album = song.fullpath.parent.name
        assert album is not None
        album = clean_string(album)
        dest_dir = self.options.clip_destination_dir(album)
        filename = song.filename
        assert filename is not None
        assert filename != ''
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        dest_path = dest_dir / filename
        metadata = song.as_dict(exclude={'filename', 'ref_id', 'uuid'})
        metadata['album'] = album
        metadata['artist'] = clean_string(song.artist)
        if start > int(song.duration):
            raise ValueError(f'{start} is beyond the duration of song "{song.title}"')
        with self.mp3.create(dest_path, metadata=Metadata(**metadata)) as output:
            src = self.mp3.use(song).clip(start, end)
            output.append(src)
            output.generate()
        return dest_path
