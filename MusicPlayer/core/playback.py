### playback.py

# Playback control module using python-vlc

from typing import Optional, List, Dict
from threading import Thread
import time, vlc
from core.track_info import TrackInfo


class Playback:
    def play_track(self, path: Optional[str] = None, index: Optional[int] = None, playlist: Optional[List[str]] = None) -> Optional[Dict]:
        with self._lock:
            if playlist is not None:
                self.playlist_playback = playlist
                self.current_index = 0
                path = self.playlist_playback[0]

            if index is not None:
                if 0 <= index < len(self.playlist_playback):
                    path = self.playlist_playback[index]
                    self.current_index = index
                else:
                    return None

            elif path:
                if path in self.playlist_playback:
                    self.current_index = self.playlist_playback.index(path)
                else:
                    if hasattr(self, "playlist") and self.playlist:
                        self.playlist_playback = [t.path for t in self.playlist]
                    else:
                        self.playlist_playback = [track.path for track in self._library]

                    self.current_index = self.playlist_playback.index(path)


            else:
                return None

            # ---------- Media player setup ----------
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
            
            if self._shuffle_mode and self.current_index not in self._shuffle_cache:
                self._shuffle_cache[self.current_index] = self.current_track.path

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
