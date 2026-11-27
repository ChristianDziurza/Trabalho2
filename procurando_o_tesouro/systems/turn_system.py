from __future__ import annotations

class TurnSystem:
    def __init__(self, players, max_moves_per_player):
        self.players = players
        self.max_moves_per_player = max_moves_per_player
        self.current_index = 0
        self.total_moves = 0
        self.max_total_moves = max_moves_per_player * len(players)

    @property
    def current_player(self):
        return self.players[self.current_index]

    def advance(self):
        self.current_player.moves_done += 1
        self.total_moves += 1
        if self.is_finished(): return True
        self.current_index = (self.current_index + 1) % len(self.players)
        self.current_player.on_own_turn_start()
        return False

    def is_finished(self):
        return self.total_moves >= self.max_total_moves

    @property
    def round_number(self):
        return self.total_moves // len(self.players) + 1
