"""
Implementation of the MP3Engine interface using mutagen and pydub
"""

from typing import Any, Dict, Optional

from pydub import AudioSegment, playback, utils  # type: ignore

try:
    import pyaudio  # type: ignore
    USE_PYAUDIO = True
except ImportError:
    USE_PYAUDIO = False

from musicbingo.mp3.editor import MP3Editor, MP3File, MP3FileWriter
from musicbingo.progress import Progress


class PydubEditor(MP3Editor):
    """MP3Editor implementation using pydub"""

    def _generate(self, destination: MP3FileWriter,
                  progress: Progress) -> None:
        """generate output file, combining all input files"""
        assert destination._metadata is not None
        output: Optional[AudioSegment] = None
        num_files = float(len(destination._files))
        for index, mp3file in enumerate(destination._files, 1):
            progress.pct = 50.0 * index / num_files
            progress.text = f'Adding {mp3file.filename.name}'
            if progress.abort:
                return
            seg = AudioSegment.from_mp3(str(mp3file.filename))
            if mp3file.start is not None and mp3file.start > 0:
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
                output = output.append(seg, crossfade=int(mp3file.overlap))
        tags: Dict[str, Any] = {
            "artist": destination._metadata.artist,
            "title": destination._metadata.title
        }
        if destination._metadata.album:
            tags["album"] = destination._metadata.album
        assert output is not None
        progress.text = f'Encoding MP3 file "{destination.filename.name}"'
        progress.pct = 50.0
        if progress.abort:
            return
        dest_dir = destination.filename.parent
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        parameters = [
            '-ar', str(destination._metadata.sample_rate),
            '-ac', str(destination._metadata.channels),
        ]
        #parameters.append(f'-acodec copy')
        output.export(str(destination.filename), format="mp3",
                      bitrate=f'{destination._metadata.bitrate}k',
                      parameters=parameters, tags=tags)
        progress.pct = 100.0

    def play(self, mp3file: MP3File, progress: Progress) -> None:
        """play the specified mp3 file"""
        global USE_PYAUDIO  # pylint: disable=global-statement

        seg = AudioSegment.from_mp3(str(mp3file.filename))
        if mp3file.start is not None:
            if mp3file.end is not None:
                seg = seg[mp3file.start:mp3file.end]
            else:
                seg = seg[mp3file.start:]
        elif mp3file.end is not None:
            seg = seg[:mp3file.end]
        if mp3file.headroom is not None:
            seg = seg.normalize(mp3file.headroom)
        if USE_PYAUDIO:
            self.play_with_pyaudio(seg, progress)
        else:
            # pydub has multiple playback fallbacks, but does not
            # provide an easy way to abort playback
            playback.play(seg)

    @staticmethod
    def play_with_pyaudio(seg: AudioSegment, progress: Progress) -> None:
        """use pyaudio library to play audio segment"""
        pya = pyaudio.PyAudio()
        stream = pya.open(format=pya.get_format_from_width(seg.sample_width),
                          channels=seg.channels,
                          rate=seg.frame_rate,
                          output=True)

        try:
            chunks = utils.make_chunks(seg, 500)
            scale: float = 1.0
            if chunks:
                scale = 100.0 / float(len(chunks))
            for index, chunk in enumerate(chunks):
                if progress.abort:
                    break
                progress.pct = index * scale
                stream.write(chunk._data)
        finally:
            stream.stop_stream()
            stream.close()
            pya.terminate()
