import numpy as np

class VolumeWindows:
    def __init__(self, delta_seconds=15):
        self.delta = int(delta_seconds)
        self.n24 = int(round(24*3600 / self.delta))
        self.buf = np.zeros(self.n24, dtype=float)
        self.ptr = 0
        self.v24 = 0.0

        self.daily_total = 0.0
        self.v30 = 0.0
        self.v30_array = np.zeros(30, dtype=float)
        self.v30_ptr = 0
        self.filled = 0
        self.day_idx = 0
        self.block = 0

    def step(self, volume):
        old = self.buf[self.ptr]
        self.buf[self.ptr] = volume
        self.v24 += (volume - old)
        self.ptr = (self.ptr + 1) % self.n24

        self.daily_total += volume
        self.block += 1
        if (self.block * self.delta) // 86400 > self.day_idx:
            old30 = self.v30_array[self.v30_ptr]
            self.v30_array[self.v30_ptr] = self.daily_total
            self.v30_ptr = (self.v30_ptr + 1) % 30
            if self.filled < 30: self.filled += 1
            self.v30 = self.v30_array[:self.filled].mean() if self.filled>0 else self.daily_total
            self.daily_total = 0.0
            self.day_idx += 1

    def V24(self): return self.v24
    def V30(self): return self.v30 if self.filled>0 else max(1e-9, self.daily_total)
