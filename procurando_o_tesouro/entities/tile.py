from __future__ import annotations
from enum import Enum

class TileState(Enum):
    HIDDEN = "hidden"
    REVEALED = "revealed"

class TileContent(Enum):
    EMPTY = "empty"
    DIAMOND = "diamond"
    TRAP = "trap"
    CLUE = "clue"

class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = TileState.HIDDEN
        self.content = TileContent.EMPTY
        self.item = None
        self.discovered_by = None
        self.reveal_anim = 0.0

    def is_hidden(self):
        return self.state == TileState.HIDDEN

    def reveal(self, player_id):
        self.state = TileState.REVEALED
        self.discovered_by = player_id
        self.reveal_anim = 0.0

    def update(self, dt):
        if self.state == TileState.REVEALED and self.reveal_anim < 1.0:
            self.reveal_anim = min(1.0, self.reveal_anim + dt * 2.5)
