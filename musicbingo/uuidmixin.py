"""
Mixin that provides functions to generate UUIDs.
These UUIDs can be used as a portable unique ID when importing data
or de-duplicating the database.
"""

import base64
import re
from typing import Optional
import uuid

from .duration import Duration

class UuidMixin:
    """
    Mix-in to create a UUID from the metadata in an object
    """
    NORMALIZE_RE = re.compile(r'([\W_])')
    UID_NAMESPACE = uuid.UUID('14fd5638-258c-451d-ad16-8367f1be252a')
    UID_FIELDS = r'{filename}{title}{artist}{album}{dur:08d}{sw:02d}{ch:02d}{sr:06d}{br:03d}'
    URN_PREFIX = 'urn:uuid:'

    # pylint: disable=unused-argument
    @classmethod
    def create_uuid(
            cls,
            filename: str,  # relative filename of mp3 file
            title: str,  # the title of the Song
            artist: str,  # the artist credited with the song
            duration: Optional[Duration] = None,  # duration of song (in milliseconds)
            sample_width: int = 0,  # bits per sample (e.g. 16)
            channels: int = 0,  # number of audio channels (e.g. 2)
            sample_rate: int = 0,  # samples per second (e.g. 44100)
            bitrate: int = 0,  # bitrate, in kilobits per second
            album: str = '',  # the artist credited with the song,
            **kwargs
    ) -> str:
        """
        Generate a UUID using the provided metadata
        :returns: a base85 encoded UUID v5
        """
        if duration is None:
            duration = Duration(0)
        mdata = cls.UID_FIELDS.format(
            filename=filename, title=title, artist=artist, dur=int(duration),
            sw=sample_width, ch=channels,
            sr=sample_rate, br=bitrate, album=album
        )
        mdata = cls.NORMALIZE_RE.sub('', mdata).lower()
        return cls.str_from_uuid(uuid.uuid5(cls.UID_NAMESPACE, mdata))

    @classmethod
    def str_to_uuid(cls, b85_str: str) -> uuid.UUID:
        """
        Convert string into a UUID object
        :b85_str: either a base85 encoded string or an RFC4122 string
        """
        if b85_str[:9].lower() == cls.URN_PREFIX:
            return uuid.UUID(b85_str)
        data = base64.a85decode(b85_str)
        return uuid.UUID(bytes=data)

    @classmethod
    def str_from_uuid(cls, uid: uuid.UUID) -> str:
        """
        Convert a UUID object into a base85 encoded string
        """
        return str(base64.a85encode(uid.bytes), 'ascii')
