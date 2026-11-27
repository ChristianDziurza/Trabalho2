from __future__ import annotations
from world.map_generator import MapGenerator
from world.board import Board
from config.settings import settings

class Mine:
    def __init__(self, rows=None, cols=None):
        rows = rows or settings.BOARD_ROWS
        cols = cols or settings.BOARD_COLS
        self.board = Board(MapGenerator.build_board(rows, cols))

    def update(self, dt):
        self.board.update(dt)
