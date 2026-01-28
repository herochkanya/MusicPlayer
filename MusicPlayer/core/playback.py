# playback.py

# Modified playback module using sounddevice and soundfile with equalizer support

from typing import Optional, List, Dict
from threading import Thread
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
from core.track_info import TrackInfo

class Playback:
    def _audio_callback(self, outdata, frames, time_info, status):
        if self.is_paused or not self.is_playing:
            outdata.fill(0)
            return

        chunk = self._audio_data[self._pos : self._pos + frames]
        
        # Equalizer processing
        if len(chunk) < frames:
            if len(chunk) > 0:
                chunk = self.equalizer.process(chunk, self._samplerate)
                outdata[:len(chunk)] = chunk
            outdata[len(chunk):].fill(0)
            self.is_playing = False
            self._on_end()
            raise sd.CallbackStop
        else:
            # Apply equalizer
            processed_chunk = self.equalizer.process(chunk, self._samplerate)
            outdata[:] = processed_chunk
            self._pos += frames

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
                else: return None
            elif path:
                if path in self.playlist_playback:
                    self.current_index = self.playlist_playback.index(path)
                else:
                    if hasattr(self, "playlist") and self.playlist:
                        self.playlist_playback = [t.path for t in self.playlist]
                    else:
                        self.playlist_playback = [track.path for track in self._library]
                    self.current_index = self.playlist_playback.index(path)
            else: return None

            if self._stream:
                self._stream.stop()
                self._stream.close()

            try:
                # Read audio file(float32 for better processing)
                self._audio_data, self._samplerate = sf.read(path, dtype='float32')
                
                # Ensure stereo
                if len(self._audio_data.shape) == 1:
                    self._audio_data = np.column_stack((self._audio_data, self._audio_data))
                
                self._pos = 0
                self.current_track = TrackInfo(path)
                
                # Start playback stream
                self._stream = sd.OutputStream(
                    samplerate=self._samplerate,
                    channels=self._audio_data.shape[1],
                    callback=self._audio_callback
                )
                self._stream.start()
                
                self.is_playing = True
                self.is_paused = False

                # Callback on track change
                if callable(self._track_change_callback):
                    try: self._track_change_callback(self.current_track.as_dict())
                    except: pass
                
                # Shuffle cache update
                if self._shuffle_mode and self.current_index not in self._shuffle_cache:
                    self._shuffle_cache[self.current_index] = self.current_track.path

                return self.current_track.as_dict()
            except Exception as e:
                print(f"Error loading track: {e}")
                return None

    def toggle_pause(self):
        with self._lock:
            if not self._stream: return
            self.is_paused = not self.is_paused
            self.is_playing = not self.is_paused
            if self.state_callback:
                self.state_callback(self.is_playing)

    def stop(self):
        with self._lock:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self.is_playing = False
            self.is_paused = False

    def seek(self, seconds: float) -> bool:
        with self._lock:
            if self._audio_data is None: return False
            target_pos = int(seconds * self._samplerate)
            if 0 <= target_pos < len(self._audio_data):
                self._pos = target_pos
                return True
            return False

    def get_playback_info(self) -> Dict:
        with self._lock:
            if self._audio_data is None:
                return {'position': 0.0, 'duration': 0.0, 'is_paused': self.is_paused, 'current_index': self.current_index}
            
            pos = self._pos / self._samplerate
            dur = len(self._audio_data) / self._samplerate
            return {
                'position': float(pos),
                'duration': float(dur),
                'is_paused': self.is_paused,
                'current_index': self.current_index,
            }

    def next_track(self) -> Optional[Dict]:
        with self._lock:
            if not self.playlist_playback: return None
            if self.current_index + 1 < len(self.playlist_playback):
                return self.play_track(index=self.current_index + 1)
            if self._cycle_mode == 1: return self.play_track(index=0)
            elif self._cycle_mode == 2: return self.play_track(index=self.current_index)
            return None

    def prev_track(self) -> Optional[Dict]:
        with self._lock:
            if not self.playlist_playback: return None
            if self.current_index - 1 >= 0:
                return self.play_track(index=self.current_index - 1)
            if self._cycle_mode == 1: return self.play_track(index=len(self.playlist_playback) - 1)
            elif self._cycle_mode == 2: return self.play_track(index=self.current_index)
            return None

    def _on_end(self):
        if not self._auto_next_enabled: return

        def delayed_next():
            time.sleep(0.2)
            if self._cycle_mode == 2:
                self.play_track(index=self.current_index)
            elif self.current_index + 1 < len(self.playlist_playback):
                self.next_track()
            elif self._cycle_mode == 1:
                self.play_track(index=0)
            else:
                self.is_playing = False
                print("✅ Playlist finished.")

        Thread(target=delayed_next, daemon=True).start()

    def is_active(self) -> bool:
        return self.is_playing or self.is_paused
