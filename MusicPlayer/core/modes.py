### modes.py

import random

# Module to manage playback modes: shuffle and cycle

class Modes:
    def toggle_shuffle(self):
        with self._lock:
            self._shuffle_mode = not self._shuffle_mode

            if not getattr(self, "playlist_playback", None):
                return self._shuffle_mode

            current_path = None
            if self.current_index != -1:
                current_path = self.playlist_playback[self.current_index]

            if self._shuffle_mode:
                shuffled = self.playlist_playback.copy()
                random.shuffle(shuffled)
                self.playlist_playback = shuffled
            else:
                self.playlist_playback = [t.path for t in self.playlist]

            if current_path and current_path in self.playlist_playback:
                self.current_index = self.playlist_playback.index(current_path)
            else:
                self.current_index = 0 if self.playlist_playback else -1

            return self._shuffle_mode

    def set_cycle_mode(self, mode: int):
        with self._lock:
            self._cycle_mode = mode
