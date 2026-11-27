from __future__ import annotations

class MovementSystem:
    def __init__(self, board, players):
        self.board = board
        self.players = players

    def is_valid(self, player, dr, dc):
        if abs(dr) + abs(dc) != 1: return False
        return self.board.in_bounds(player.row + dr, player.col + dc)

    def try_move(self, player, dr, dc):
        if not self.is_valid(player, dr, dc): return False
        player.row += dr
        player.col += dc
        return True
