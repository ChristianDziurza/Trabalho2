from __future__ import annotations
from dataclasses import dataclass

@dataclass
class FlashEffect:
    color: tuple
    duration: float
    elapsed: float = 0.0
    intensity: float = 1.0

    def update(self, dt):
        self.elapsed += dt
        return self.elapsed < self.duration

    @property
    def alpha(self):
        t = min(1.0, self.elapsed / self.duration)
        return (1.0 - t) * self.intensity

class EffectsManager:
    def __init__(self):
        self.flashes = []

    def flash(self, color, duration=0.5, intensity=1.0):
        self.flashes.append(FlashEffect(color, duration, 0.0, intensity))

    def update(self, dt):
        self.flashes = [f for f in self.flashes if f.update(dt)]
