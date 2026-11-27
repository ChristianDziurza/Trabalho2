from __future__ import annotations
import random
from entities.diamond import Diamond
from entities.trap import Trap, TrapType
from entities.clue import Clue
from entities.tile import Tile, TileContent
from config.settings import settings

class MapGenerator:
    @staticmethod
    def build_board(rows, cols):
        total = rows * cols
        n_traps = max(2, round(total * settings.TRAP_RATIO))
        n_dead = max(1, n_traps // 2)
        n_hide = max(1, n_traps - n_dead)
        n_clues = max(1, round(total * settings.CLUE_RATIO))
        n_diamonds = total - n_traps - n_clues

        contents = []
        for _ in range(n_dead): contents.append((TileContent.TRAP, Trap(TrapType.DEAD_END)))
        for _ in range(n_hide): contents.append((TileContent.TRAP, Trap(TrapType.HIDEOUT)))
        for _ in range(n_clues): contents.append((TileContent.CLUE, Clue()))
        for _ in range(n_diamonds): contents.append((TileContent.DIAMOND, Diamond.random()))

        random.shuffle(contents)

        board = []
        idx = 0
        for r in range(rows):
            row_tiles = []
            for c in range(cols):
                tile = Tile(r, c)
                ct, item = contents[idx]
                tile.content = ct
                tile.item = item
                idx += 1
                row_tiles.append(tile)
            board.append(row_tiles)
        return board
