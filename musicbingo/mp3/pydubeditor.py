"""
Implementation of the MP3Engine interface using mutagen and pydub
"""

import os
from typing import Optional

from pydub import AudioSegment # type: ignore

from musicbingo.mp3.editor import MP3Editor, MP3FileWriter
from musicbingo.progress import Progress
from musicbingo.song import Song

class PydubEditor(MP3Editor):
    """MP3Editor implementation using pydub"""
    def _generate(self, destination: MP3FileWriter,
                  progress: Progress) -> None:
        """generate output file, combining all input files"""
        output: Optional[AudioSegment] = None
        num_files = float(len(destination._files))
        for index, mp3file in enumerate(destination._files, 1):
            progress.pct = 50.0 * index / num_files
            filename = os.path.basename(mp3file.filename)
            progress.text = f'Adding {filename}'
            seg = AudioSegment.from_mp3(mp3file.filename)
            if mp3file.start is not None:
                if mp3file.end is not None:
                    seg = seg[mp3file.start:mp3file.end]
                else:
                    seg = seg[mp3file.start:]
            elif mp3file.end is not None:
                seg = seg[:mp3file.end]
            if mp3file.headroom is not None:
                seg = seg.normalize(mp3file.headroom)
            if output is None:
                output = seg
            else:
                output += seg
        tags = None
        if destination._metadata is not None:
            tags = {
                "artist": Song.clean(destination._metadata.artist),
                "title": Song.clean(destination._metadata.title)
            }
            if destination._metadata.album:
                tags["album"] = Song.clean(destination._metadata.album)
        assert output is not None
        #print(f'export {destination.filename}')
        progress.text = 'Encoding MP3 file'
        progress.pct = 50.0
        dest_dir = os.path.dirname(destination.filename)
        if dest_dir is not None and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        output.export(destination.filename, format="mp3",
                      bitrate=destination.bitrate, tags=tags)
        progress.pct = 100.0
