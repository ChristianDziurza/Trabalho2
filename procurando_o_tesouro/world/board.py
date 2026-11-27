from __future__ import annotations
from entities.tile import TileState

class Board:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0

    def get(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    @property
    def total_cells(self):
        return self.rows * self.cols

    @property
    def revealed_count(self):
        return sum(1 for r in self.grid for t in r if t.state == TileState.REVEALED)

    def update(self, dt):
        for row in self.grid:
            for tile in row:
                tile.update(dt)
