from __future__ import annotations
from entities.tile import TileContent
from entities.trap import TrapType

class ItemSystem:
    def __init__(self, scoring):
        self.scoring = scoring

    def trigger(self, tile, player):
        if not tile.is_hidden(): return None
        tile.reveal(player.id)
        if tile.content == TileContent.DIAMOND:
            self.scoring.on_diamond(player.id, tile.item)
            return "diamond"
        if tile.content == TileContent.TRAP:
            if tile.item.type == TrapType.DEAD_END:
                self.scoring.on_dead_end(player.id, tile.item)
                return "trap_deadend"
            self.scoring.on_hideout(player.id, tile.item)
            return "trap_hideout"
        if tile.content == TileContent.CLUE:
            self.scoring.on_clue(player.id, tile.item)
            return "clue"
        return "empty"
