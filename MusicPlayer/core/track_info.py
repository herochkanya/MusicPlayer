### track_info.py

# Core module to read track metadata using mutagen
# There is only TrackInfo class here

import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from typing import Optional, Dict

# Helper class to read metadata from an MP3 file
class TrackInfo:
    def __init__(self, path: str):
        self.path = path
        self.title = None
        self.artist = None
        self.album = None
        self.cover_path: Optional[str] = None
        self._read_metadata()

    def _read_metadata(self):
        # Read ID3 tags
        try:
            audio = MP3(self.path, ID3=ID3)
            tags = audio.tags or {}
        except Exception:
            tags = {}

        # Title
        try:
            tit = tags.get('TIT2')
            self.title = tit.text[0] if tit is not None else os.path.basename(self.path)
        except Exception:
            self.title = os.path.basename(self.path)

        # Artist
        try:
            art = tags.get('TPE1')
            self.artist = art.text[0] if art is not None else 'Unknown Artist'
        except Exception:
            self.artist = 'Unknown Artist'

        # Album
        try:
            alb = tags.get('TALB')
            self.album = alb.text[0] if alb is not None else 'Unknown Album'
        except Exception:
            self.album = 'Unknown Album'

        # Cover (APIC)
        try:
            for frame in tags.values():
                if isinstance(frame, APIC):
                    mime = getattr(frame, 'mime', 'image/jpeg') or 'image/jpeg'
                    ext = '.jpg' if 'jpeg' in mime.lower() or 'jpg' in mime.lower() else '.png'
                    cover_path = os.path.splitext(self.path)[0] + ext
                    try:
                        with open(cover_path, 'wb') as fh:
                            fh.write(frame.data)
                        self.cover_path = cover_path
                    except Exception:
                        self.cover_path = None
                    break
        except Exception:
            self.cover_path = None

    def as_dict(self) -> Dict:
        return {
            'path': self.path,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'cover_path': self.cover_path,
        }
