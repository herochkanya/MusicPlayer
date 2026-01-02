# player_logic.py

# Core music player logic using python-vlc and mutagen for metadata

import vlc
from threading import RLock
from typing import Optional, Callable, List, Dict
from config import get_music_base_dir
from core.track_info import TrackInfo
from core.playlist import PlaylistManager
from core.playback import Playback


# ---------- MusicPlayer ----------
# Main music player class
class MusicPlayer(PlaylistManager, Playback):
    def __init__(self):
        self.base_dir = get_music_base_dir()
        self.instance = vlc.Instance("--no-video", "--quiet")
        self.player: Optional[vlc.MediaPlayer] = None 
        self.current_track: Optional[TrackInfo] = None 
        self.playlist: List[str] = []
        self.playlist_playback: List[str] = []
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

        self.current_query = None
        self._shuffle_cache = {}
        self.current_folder = None
        
        # INDEX
        self._library = []  # list of TrackInfo
        self._by_author = {}  # author -> list of TrackInfo
        self._by_playlist = {}  # (author, playlist) -> list of TrackInfo
        self._library_ready = False 
    
    # ---------- Utility ----------
    def set_track_change_callback(self, cb: Callable[[Dict], None]):
        self._track_change_callback = cb
    
    def set_state_callback(self, callback):
        self.state_callback = callback
    
    def clear_library_index(self):
        with self._lock:
            self.base_dir = get_music_base_dir()
            self.current_query = None
            if self.player:
                self.player.stop()
                self.player.release()
                self.player = None

            self.current_track = None
            self.current_index = -1
            self.is_playing = False
            self.is_paused = False
            self.playlist.clear()
            self.playlist_playback.clear()
            self._library.clear()
            self._by_author.clear()
            self._by_playlist.clear()
            self._library_ready = False

