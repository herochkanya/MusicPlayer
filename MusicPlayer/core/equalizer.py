# equalizer.py

import math

class Equalizer:
    BANDS = [60, 150, 400, 1000, 2400, 15000]

    def __init__(self):
        self.gains = {freq: 0.0 for freq in self.BANDS}  # dB

    def set_band(self, freq: int, gain_db: float):
        if freq not in self.gains:
            raise ValueError("Unknown EQ band")
        self.gains[freq] = float(gain_db)

    def set_all(self, bands: dict):
        for freq, gain in bands.items():
            self.set_band(int(freq), float(gain))

    def get_state(self) -> dict:
        return dict(self.gains)

    # DSP helper — dB → linear gain
    @staticmethod
    def db_to_gain(db: float) -> float:
        return math.pow(10.0, db / 20.0)
