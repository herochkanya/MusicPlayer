# player_logic.py

# Core music player logic using python-vlc and mutagen for metadata

import os, time, vlc, random
from threading import RLock, Thread
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from typing import Optional, Callable, List, Dict
from config import get_music_base_dir

# ---------- TrackInfo ----------
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

# ---------- MusicPlayer ----------
# Main music player class
class MusicPlayer:
    def __init__(self):
        self.base_dir = get_music_base_dir()
        self.instance = vlc.Instance("--no-video", "--quiet")
        self.player: Optional[vlc.MediaPlayer] = None 
        self.current_track: Optional[TrackInfo] = None 
        self.playlist: List[str] = []
        self.current_index = -1
        self.is_paused = False
        self.is_playing = False
        self._lock = RLock()
        self._track_change_callback: Optional[Callable[[Dict], None]] = None
        self._auto_next_enabled = True
        self._cycle_mode = 0
        self._shuffle_mode = False
        self._original_playlist: List[str] = []
        self.state_callback = None    
    
    # ---------- Utility ----------
    def set_global_playlist(self) -> List[Dict]:
        with self._lock:
            items = []
            for root, _, files in os.walk(self.base_dir):
                for f in sorted(files):
                    if f.lower().endswith('.mp3'):
                        items.append(os.path.join(root, f))
            self.playlist = items
            self.current_index = -1
            return [TrackInfo(p).as_dict() for p in self.playlist]

    def _build_playlist_for_path(self, path: str) -> List[str]:
        directory = os.path.dirname(path)
        try:
            items = sorted([
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if f.lower().endswith('.mp3')
            ])
            return items if items else [path]
        except Exception:
            return [path]

    def set_track_change_callback(self, cb: Callable[[Dict], None]):
        self._track_change_callback = cb
    
    def get_playlist_dicts(self) -> List[Dict]:
        with self._lock:
            return [TrackInfo(path).as_dict() for path in self.playlist]

    def set_playlist_from_folder(self, folder: str) -> List[Dict]:
        playlist_name = folder
        if getattr(self, "set_playlist_mode", False):
            if not hasattr(self, "selected_playlists_for_set"):
                self.selected_playlists_for_set = []

            if playlist_name in self.selected_playlists_for_set:
                self.selected_playlists_for_set.remove(playlist_name)
                self.update_playlist_highlight(playlist_name, False)
            else:
                self.selected_playlists_for_set.append(playlist_name)
                self.update_playlist_highlight(playlist_name, True)

            self.show_playlist_tracks(playlist_name)

        else:
            with self._lock:
                target_dir = os.path.join(self.base_dir, folder)
                try:
                    items = sorted([
                        os.path.join(target_dir, f)
                        for f in os.listdir(target_dir)
                        if f.lower().endswith('.mp3')
                    ])
                except Exception:
                    items = []

                self.playlist = items
                if self.current_track and self.current_track.path in self.playlist:
                    self.current_index = self.playlist.index(self.current_track.path)
                else:
                    self.current_index = -1

                return [TrackInfo(p).as_dict() for p in self.playlist]
    
    def set_state_callback(self, callback):
        self.state_callback = callback

    def set_custom_playlist(self, selected_playlists: List[str]) -> List[Dict]:
        with self._lock:
            combined_tracks = []
            for root, _, files in os.walk(self.base_dir):
                folder_name = os.path.basename(root)
                if folder_name not in selected_playlists:
                    continue
                for f in sorted(files):
                    if f.lower().endswith('.mp3'):
                        combined_tracks.append(os.path.join(root, f))
            self.playlist = combined_tracks
            self.current_index = 0
            return [TrackInfo(p).as_dict() for p in combined_tracks]

    # ---------- Core control ----------
    def play_track(self, path: Optional[str] = None, index: Optional[int] = None, playlist: Optional[List[str]] = None) -> Optional[Dict]:
        with self._lock:
            if playlist is not None:
                self.playlist = playlist
                self.current_index = 0
                path = self.playlist[0]
            if index is not None:
                if 0 <= index < len(self.playlist):
                    path = self.playlist[index]
                    self.current_index = index
                else:
                    return None
            elif path:
                if not self._shuffle_mode:
                    if path not in self.playlist:
                        self.playlist = self._build_playlist_for_path(path)
                else:
                    if path not in self.playlist:
                        self.playlist.append(path)
                try:
                    self.current_index = self.playlist.index(path)
                except ValueError:
                    self.playlist = [path]
                    self.current_index = 0
            else:
                return None

            if self.player:
                try:
                    self.player.stop()
                    self.player.release()
                except Exception:
                    pass

            self.current_track = TrackInfo(path)
            media = self.instance.media_new(path)
            self.player = self.instance.media_player_new()
            self.player.set_media(media)
            self._bind_events()

            self.player.play()
            self.is_playing = True
            self.is_paused = False

            if callable(self._track_change_callback):
                try:
                    self._track_change_callback(self.current_track.as_dict())
                except Exception:
                    pass

            return self.current_track.as_dict()

    def toggle_pause(self):
        with self._lock:
            if not self.player:
                return
            if self.is_paused:
                self.player.play()
                self.is_paused = False
                self.is_playing = True
                if self.state_callback:
                    self.state_callback(True)
            else:
                self.player.pause()
                self.is_paused = True
                self.is_playing = False
                if self.state_callback:
                    self.state_callback(False)

    def stop(self):
        with self._lock:
            if self.player:
                try:
                    self.player.stop()
                    self.player.release()
                except Exception:
                    pass
            self.player = None
            self.is_playing = False
            self.is_paused = False

    def seek(self, seconds: float) -> bool:
        with self._lock:
            if not self.player:
                return False
            try:
                length = self.player.get_length() / 1000.0
                if length > 0:
                    self.player.set_time(int(seconds * 1000))
                    return True
            except Exception:
                pass
            return False

    def next_track(self) -> Optional[Dict]:
        with self._lock:
            if not self.playlist:
                return None

            if self.current_index + 1 < len(self.playlist):
                return self.play_track(index=self.current_index + 1)

            if self._cycle_mode == 1:
                return self.play_track(index=0)
            elif self._cycle_mode == 2:
                return self.play_track(index=self.current_index)

            return None

    def prev_track(self) -> Optional[Dict]:
        with self._lock:
            if not self.playlist:
                return None

            if self.current_index - 1 >= 0:
                return self.play_track(index=self.current_index - 1)

            if self._cycle_mode == 1:
                return self.play_track(index=len(self.playlist) - 1)
            elif self._cycle_mode == 2:
                return self.play_track(index=self.current_index)

            return None

    # ---------- Info ----------
    def get_playback_info(self) -> Dict:
        with self._lock:
            if not self.player:
                return {'position': 0.0, 'duration': 0.0, 'is_paused': self.is_paused, 'current_index': self.current_index}
            try:
                pos = self.player.get_time() / 1000.0
                dur = self.player.get_length() / 1000.0
                return {
                    'position': float(pos),
                    'duration': float(dur),
                    'is_paused': self.is_paused,
                    'current_index': self.current_index,
                }
            except Exception:
                return {'position': 0.0, 'duration': 0.0, 'is_paused': self.is_paused, 'current_index': self.current_index}

    def list_files(self, folder: Optional[str] = None) -> List[Dict]:
        result = []
        if folder:
            target_dir = os.path.join(self.base_dir, folder)
        else:
            target_dir = self.base_dir
        for root, _, files in os.walk(target_dir):
            for file in sorted(files):
                if file.lower().endswith('.mp3'):
                    path = os.path.join(root, file)
                    try:
                        result.append(TrackInfo(path).as_dict())
                    except Exception:
                        continue
        return result

    # ---------- Event binding ----------
    def _bind_events(self):
        if not self.player:
            return
        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end)

    def _on_end(self, event):
        if not self._auto_next_enabled:
            return

        def delayed_next():
            time.sleep(0.2)
            with self._lock:
                if self._cycle_mode == 2:
                    self.play_track(index=self.current_index)
                elif self.current_index + 1 < len(self.playlist):
                    self.next_track()
                elif self._cycle_mode == 1:
                    self.play_track(index=0)
                else:
                    self.is_playing = False
                    self.is_paused = False
                    print("✅ Playlist finished.")

        Thread(target=delayed_next, daemon=True).start()
    
    def is_active(self) -> bool:
        with self._lock:
            return bool(self.player and (self.is_playing or self.is_paused))

    # ---------- Modes ----------
    def toggle_shuffle(self):
        with self._lock:
            self._shuffle_mode = not self._shuffle_mode
            cur_path = None
            if self.current_track:
                cur_path = self.current_track.path

            if self._shuffle_mode:
                self._original_playlist = self.playlist.copy()
                if cur_path and cur_path in self.playlist:
                    rest = [p for p in self.playlist if p != cur_path]
                    random.shuffle(rest)
                    self.playlist = [cur_path] + rest
                    self.current_index = 0
                else:
                    random.shuffle(self.playlist)
                    if cur_path and cur_path in self.playlist:
                        self.current_index = self.playlist.index(cur_path)
                    else:
                        self.current_index = -1
            else:
                if self._original_playlist:
                    cur = None
                    if 0 <= self.current_index < len(self.playlist):
                        cur = self.playlist[self.current_index]
                    self.playlist = self._original_playlist.copy()
                    if cur and cur in self.playlist:
                        self.current_index = self.playlist.index(cur)
                    else:
                        self.current_index = -1
                self._original_playlist = []
            return self._shuffle_mode

    def set_cycle_mode(self, mode: int):
        with self._lock:
            self._cycle_mode = mode
