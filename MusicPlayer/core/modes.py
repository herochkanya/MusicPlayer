### modes.py

import random

# Module to manage playback modes: shuffle and cycle

class Modes:
    def toggle_shuffle(self):
        with self._lock:
            self._shuffle_mode = not self._shuffle_mode
            return self.apply_shuffle_logic()

    def apply_shuffle_logic(self):
        if not getattr(self, "playlist", None):
            return self._shuffle_mode

        current_path = None
        if getattr(self, "current_index", -1) != -1 and self.playlist_playback:
            current_path = self.playlist_playback[self.current_index]

        if self._shuffle_mode:
            shuffled = [t.path for t in self.playlist]
            random.shuffle(shuffled)
            self.playlist_playback = shuffled
            if current_path and current_path in self.playlist_playback:
                self.playlist_playback.remove(current_path)
                self.playlist_playback.insert(0, current_path)
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
