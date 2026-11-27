from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Player:
    id: int
    name: str
    color: tuple
    row: int = 0
    col: int = 0
    carats: int = 0
    invisible: bool = False
    invisible_turns_left: int = 0
    moves_done: int = 0
    diamonds_found: int = 0
    traps_found: int = 0
    visual_x: float = 0.0
    visual_z: float = 0.0
    target_x: float = 0.0
    target_z: float = 0.0
    bob_phase: float = 0.0

    def add_carats(self, amount):
        self.carats += amount

    def set_invisible(self, turns):
        self.invisible = True
        self.invisible_turns_left = turns

    def on_own_turn_start(self):
        if self.invisible and self.invisible_turns_left > 0:
            self.invisible_turns_left -= 1
            if self.invisible_turns_left <= 0:
                self.invisible = False
