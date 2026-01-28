import math
import numpy as np
import scipy.signal as signal

class Equalizer:
    BANDS = [60, 150, 400, 1000, 2400, 15000]

    def __init__(self):
        self.gains = {freq: 0.0 for freq in self.BANDS}
        self.filters_state = {}
        self._cache = {}

    def set_band(self, freq: int, gain_db: float):
        freq = int(freq)
        if freq in self.gains:
            self.gains[freq] = float(gain_db)
            self._cache.pop(freq, None)

    def set_all(self, bands: dict):
        for freq_str, gain in bands.items():
            self.set_band(int(freq_str), float(gain))

    def get_state(self) -> dict:
        return dict(self.gains)

    # Biquad filter coefficients calculation
    def _get_coefficients(self, freq, sr, gain_db):
        q = 1.0
        a_gain = math.pow(10, gain_db / 40)
        w0 = 2 * math.pi * freq / sr
        alpha = math.sin(w0) / (2 * q)
        
        # Coefficients for peaking EQ filter
        b0 = 1 + alpha * a_gain
        b1 = -2 * math.cos(w0)
        b2 = 1 - alpha * a_gain
        a0 = 1 + alpha / a_gain
        a1 = -2 * math.cos(w0)
        a2 = 1 - alpha / a_gain

        return np.array([b0/a0, b1/a0, b2/a0]), np.array([1.0, a1/a0, a2/a0])

    # Apply equalizer to audio data
    def process(self, data: np.ndarray, samplerate: int) -> np.ndarray:
        if all(g == 0 for g in self.gains.values()):
            return data

        output = data.copy()
        
        for freq in self.BANDS:
            gain = self.gains[freq]
            if gain == 0:
                continue
            
            # Cache coefficients
            if (freq, samplerate) not in self._cache:
                self._cache[freq] = self._get_coefficients(freq, samplerate, gain)
            
            # Retrieve cached coefficients
            if freq not in self._cache:
                self._cache[freq] = self._get_coefficients(freq, samplerate, gain)

            b, a = self._cache[freq]
            
            # Initialize filter state if not present
            if freq not in self.filters_state or self.filters_state[freq].shape[1] != data.shape[1]:
                n_order = max(len(a), len(b)) - 1
                self.filters_state[freq] = np.zeros((n_order, data.shape[1]))

            # Chain filtering
            output, self.filters_state[freq] = signal.lfilter(
                b, a, output, axis=0, zi=self.filters_state[freq]
            )
            
        return output.astype('float32')
