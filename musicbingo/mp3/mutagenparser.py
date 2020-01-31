"""
Implementation of the MP3Parser interface using mutagen
"""

import io
import os

from mutagen.easyid3 import EasyID3 # type: ignore
from pydub import AudioSegment # type: ignore

from musicbingo.mp3.parser import MP3Parser
from musicbingo.mp3.exceptions import InvalidMP3Exception
from musicbingo.song import Metadata


class MutagenParser(MP3Parser):
    """MP3Parser implementation using Mutagen"""
    def parse(self, directory: str, filename: str) -> Metadata:
        """Extract the metadata from an MP3 file"""
        #print(filename)
        abs_path = os.path.join(directory, filename)
        try:
            mp3_data = io.BytesIO(open(abs_path, 'rb').read())
        except IOError as err:
            raise InvalidMP3Exception(err)
        mp3info = EasyID3(mp3_data)
        artist = mp3info["artist"]
        title = mp3info["title"]
        if len(artist) == 0 or len(title) == 0:
            raise InvalidMP3Exception(
                f"File: {filename} does not both title and artist info")
        metadata = {
            "artist": artist[0],
            "title": title[0],
            "filepath": str(abs_path),
            "filename": str(filename),
        }
        try:
            metadata["album"] = str(mp3info["album"][0])
        except KeyError:
            head, tail = os.path.split(directory)
            metadata["album"] = tail if tail else head
        del mp3info
        mp3_data.seek(0)
        # duration is in milliseconds
        metadata["duration"] = len(AudioSegment.from_mp3(mp3_data))
        return Metadata(**metadata) # type: ignore
