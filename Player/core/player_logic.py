import os
from config import get_music_base_dir
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from ffpyplayer.player import MediaPlayer

from threading import Thread
import time

class TrackInfo:
    def __init__(self, path):
        self.path = path
        self.title = None
        self.artist = None
        self.album = None
        self.cover_path = None
        self._read_metadata()

    def _read_metadata(self):
        audio = MP3(self.path, ID3=ID3)
        tags = audio.tags

        self.title = tags.get('TIT2', 'Unknown Title').text[0] if 'TIT2' in tags else os.path.basename(self.path)
        self.artist = tags.get('TPE1', 'Unknown Artist').text[0] if 'TPE1' in tags else 'Unknown Artist'
        self.album = tags.get('TALB', 'Unknown Album').text[0] if 'TALB' in tags else 'Unknown Album'

        if 'APIC:' in tags:
            apic = tags['APIC:']
            cover_path = self.path.replace('.mp3', '.jpg')
            with open(cover_path, 'wb') as img:
                img.write(apic.data)
            self.cover_path = cover_path

class MusicPlayer:
    def __init__(self):
        self.base_dir = get_music_base_dir()
        self.current_track: TrackInfo | None = None
        self.player: MediaPlayer | None = None
        self.is_playing = False
        self.track_thread = None

    def get_folders(self):
        result = []
        for folder in os.listdir(self.base_dir):
            full_path = os.path.join(self.base_dir, folder)
            if os.path.isdir(full_path):
                count = len([f for f in os.listdir(full_path) if f.endswith('.mp3')])
                result.append({'name': folder, 'count': count})
        return result

    def list_files(self, folder=None):
        result = []
        if folder:
            target_dir = os.path.join(self.base_dir, folder)
        else:
            target_dir = self.base_dir

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.mp3'):
                    path = os.path.join(root, file)
                    result.append(TrackInfo(path).__dict__)
        return result

    def play_track(self, path):
        if self.player:
            self.player.close_player()
        self.current_track = TrackInfo(path)
        self.player = MediaPlayer(path)
        self.is_playing = True

        def watch_thread():
            while self.is_playing:
                frame, val = self.player.get_frame()
                if val == 'eof':
                    self.is_playing = False
                    break
                time.sleep(0.01)

        self.track_thread = Thread(target=watch_thread)
        self.track_thread.start()
        return self.current_track.__dict__

    def toggle_pause(self):
        if self.player:
            self.player.toggle_pause()

    def stop(self):
        if self.player:
            self.player.close_player()
            self.player = None
            self.is_playing = False

    def is_active(self):
        return self.is_playing
