from __future__ import annotations
from enum import Enum

class TrapType(Enum):
    DEAD_END = "dead_end"
    HIDEOUT = "hideout"

class Trap:
    def __init__(self, trap_type):
        self.type = trap_type
        self.discovered = False
        self.discovered_by = None

    @property
    def description(self):
        if self.type == TrapType.DEAD_END: return "Tunel sem saida"
        return "Esconderijo secreto"
