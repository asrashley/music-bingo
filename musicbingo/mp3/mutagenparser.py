"""
Implementation of the MP3Parser interface using mutagen
"""

import io
from pathlib import Path

from mutagen.easyid3 import EasyID3  # type: ignore
from pydub import AudioSegment  # type: ignore

from musicbingo.mp3.parser import MP3Parser
from musicbingo.mp3.exceptions import InvalidMP3Exception
from musicbingo.song import Metadata


class MutagenParser(MP3Parser):
    """MP3Parser implementation using Mutagen"""

    def parse(self, filename: Path) -> Metadata:
        """Extract the metadata from an MP3 file"""
        # print(filename)
        with open(filename, 'rb') as src:
            try:
                mp3_data = io.BytesIO(src.read())
            except IOError as err:
                raise InvalidMP3Exception(err) from err
        mp3info = EasyID3(mp3_data)
        try:
            artist = mp3info["artist"]
            title = mp3info["title"]
        except KeyError as err:
            raise InvalidMP3Exception(
                f"File: {filename.name} does not both title and artist info") from err
        if len(artist) == 0 or len(title) == 0:
            raise InvalidMP3Exception(
                f"File: {filename.name} does not both title and artist info")
        metadata = {
            "artist": artist[0],
            "title": title[0],
        }
        try:
            metadata["album"] = str(mp3info["album"][0])
        except KeyError:
            metadata["album"] = filename.parent.name
        del mp3info
        mp3_data.seek(0, io.SEEK_END)
        filesize = mp3_data.tell()
        mp3_data.seek(0)
        seg = AudioSegment.from_mp3(mp3_data)
        # duration is in milliseconds
        metadata["duration"] = len(seg)
        # bitrate is in Kbps
        metadata["bitrate"] = int(round(8.0 * filesize /
                                        float(metadata["duration"])))
        metadata["sample_width"] = seg.sample_width * 8
        metadata["channels"] = seg.channels
        # sample rate is in Hz
        metadata["sample_rate"] = seg.frame_rate
        return Metadata(**metadata)  # type: ignore
