# Playlist management module (single-scan, query-based, simplified)

import os
from typing import List, Dict
from core.track_info import TrackInfo
from core.modes import Modes


class PlaylistManager(Modes):
    # ------------------ BUILD INDEX ------------------

    def build_library_index(self):
        """
        One-time scan. Builds in-memory index.
        """
        self._library.clear()
        self._by_playlist.clear()

        for root, _, files in os.walk(self.base_dir):
            mp3s = [f for f in files if f.lower().endswith(".mp3")]
            if not mp3s:
                continue

            rel = os.path.relpath(root, self.base_dir)

            # skip base dir itself
            if rel == ".":
                playlist = None
            else:
                playlist = rel.split(os.sep)[0]

            for f in mp3s:
                path = os.path.join(root, f)
                try:
                    track = TrackInfo(path)
                except Exception:
                    continue

                track.playlist = playlist
                self._library.append(track)

                if playlist:
                    self._by_playlist.setdefault(playlist, []).append(track)

        self._library_ready = True

    # ------------------ PUBLIC API ------------------

    def set_global_playlist(self) -> List[Dict]:
        self.current_query = {"type": "global"}
        return self._apply_query()

    def set_playlist_from_folder(self, folder: str) -> List[Dict]:
        self.current_folder = folder

        # UI multi-select mode (unchanged behavior)
        if getattr(self, "set_playlist_mode", False):
            if not hasattr(self, "selected_playlists_for_set"):
                self.selected_playlists_for_set = []

            if folder in self.selected_playlists_for_set:
                self.selected_playlists_for_set.remove(folder)
                self.update_playlist_highlight(folder, False)
            else:
                self.selected_playlists_for_set.append(folder)
                self.update_playlist_highlight(folder, True)

            return []

        self.current_query = {
            "type": "playlist",
            "value": folder,
        }
        return self._apply_query()

    def set_custom_playlist(self, selected_playlists: List[str]) -> List[Dict]:
        self.current_query = {
            "type": "custom",
            "value": selected_playlists,
        }
        return self._apply_query()

    def get_playlist_dicts(self) -> List[Dict]:
        with self._lock:
            return [t.as_dict() for t in self.playlist]

    # ------------------ CORE QUERY PIPELINE ------------------

    def _apply_query(self) -> List[Dict]:
        with self._lock:
            if not self._library_ready:
                self.build_library_index()

            tracks = self._resolve_query(self.current_query)
            self.playlist = tracks
            self.current_index = self._sync_current_index(tracks)

            return [t.as_dict() for t in tracks]

    def _resolve_query(self, query: Dict) -> List[TrackInfo]:
        if not query or not self._library_ready:
            return []

        qtype = query["type"]

        if qtype == "global":
            return list(self._library)

        if qtype == "playlist":
            return list(self._by_playlist.get(query["value"], []))

        if qtype == "custom":
            result = []
            for pl in query["value"]:
                result.extend(self._by_playlist.get(pl, []))
            return result

        return []

    # ------------------ HELPERS ------------------

    def _sync_current_index(self, playlist: List[TrackInfo]) -> int:
        if self.current_track:
            for i, t in enumerate(playlist):
                if t.path == self.current_track.path:
                    return i
        return -1
