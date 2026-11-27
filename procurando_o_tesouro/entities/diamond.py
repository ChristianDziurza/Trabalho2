from __future__ import annotations
import random
from dataclasses import dataclass

@dataclass
class Diamond:
    carats: int
    discovered: bool = False
    discovered_by: int = None
    collected: bool = False

    @staticmethod
    def random():
        return Diamond(carats=random.randint(1, 10))

    @property
    def scale(self):
        if self.carats <= 3: return 0.55
        if self.carats <= 6: return 0.75
        if self.carats <= 8: return 0.95
        return 1.2

    @property
    def color(self):
        if self.carats <= 3: return (0.55, 0.85, 0.95)
        if self.carats <= 6: return (0.35, 0.75, 0.98)
        if self.carats <= 8: return (0.75, 0.55, 0.95)
        return (1.0, 0.85, 0.35)
