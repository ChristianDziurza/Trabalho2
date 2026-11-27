from __future__ import annotations
import math
from entities.player import Player
from world.mine import Mine
from systems.scoring_system import ScoringSystem
from systems.turn_system import TurnSystem
from systems.movement_system import MovementSystem
from systems.item_system import ItemSystem
from systems.save_system import SaveSystem
from config.settings import settings

class GameSession:
    def __init__(self, players, mine, scoring, turn, movement, item):
        self.players = players
        self.mine = mine
        self.scoring = scoring
        self.turn = turn
        self.movement = movement
        self.item = item

    @property
    def current_player(self):
        return self.turn.current_player

class GameManager:
    def __init__(self, game):
        self.game = game
        self.session = None
        self.scoring = None
        self.save_system = SaveSystem()

    def start_new_game(self, num_players=2, nomes=None):
        rows = settings.BOARD_ROWS
        cols = settings.BOARD_COLS
        total_cells = rows * cols
        max_moves = total_cells // num_players

        if nomes is None:
            nomes = settings.PLAYER_NAMES

        players = []
        for i in range(num_players):
            nome_final = nomes[i] if i < len(nomes) and nomes[i].strip() else settings.PLAYER_NAMES[i]
            players.append(Player(
                id=i,
                name=nome_final,
                color=settings.PLAYER_COLORS[i],
            ))

        mine = Mine(rows, cols)

        spawns = [(0, 0), (rows-1, cols-1), (0, cols-1), (rows-1, 0)]
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        for p, (r, c) in zip(players, spawns[:num_players]):
            p.row, p.col = r, c
            p.visual_x = (c - (cols-1)/2.0) * sx
            p.visual_z = (r - (rows-1)/2.0) * sx
            p.target_x = p.visual_x
            p.target_z = p.visual_z

        scoring = ScoringSystem(players)
        turn = TurnSystem(players, max_moves)
        movement = MovementSystem(mine.board, players)
        item = ItemSystem(scoring)

        for p in players:
            t = mine.board.get(p.row, p.col)
            if t and t.is_hidden():
                item.trigger(t, p)

        self.scoring = scoring
        self.session = GameSession(players, mine, scoring, turn, movement, item)

        from core.game_state import GameState
        self.game.state = GameState.PLAYING
        self.game.hud.show_message(f"Partida iniciada! Vez de {players[0].name}")

    def try_player_move(self, dr, dc):
        if not self.session: 
            return False
        s = self.session
        if s.turn.is_finished(): 
            return False
        player = s.current_player
        if not s.movement.try_move(player, dr, dc): 
            return False

        rows = s.mine.board.rows
        cols = s.mine.board.cols
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        player.target_x = (player.col - (cols-1)/2.0) * sx
        player.target_z = (player.row - (rows-1)/2.0) * sx

        tile = s.mine.board.get(player.row, player.col)
        ev = s.item.trigger(tile, player) if tile else None
        self._handle_effect(ev, tile, player)

        finished = s.turn.advance()
        if finished:
            self._end_game()
        else:
            self.game.hud.show_message(s.scoring.last_message + " | Vez de " + s.current_player.name)
        return True

    def _handle_effect(self, ev, tile, player):
        r = self.game.renderer
        if not ev or not r: 
            return
        x, z = player.visual_x, player.visual_z
        if ev == "diamond":
            c = tile.item.color
            r.particles.emit_burst(x, 0.6, z, c, count=30, speed=2.5)
        elif ev == "trap_deadend":
            r.particles.emit_burst(x, 0.5, z, (0.9,0.2,0.1), count=25, speed=2.0)
        elif ev == "trap_hideout":
            r.particles.emit_burst(x, 0.5, z, (0.4,0.4,0.8), count=25, speed=1.5)
        elif ev == "clue":
            r.particles.emit_burst(x, 0.5, z, (0.3,1.0,0.4), count=20, speed=2.0)

    def _end_game(self):
        if not self.session: 
            return
        from core.game_state import GameState
        for p in self.session.players:
            self.save_system.add_result(p.name, p.carats, len(self.session.players))
        self.game.state = GameState.GAME_OVER

    def update(self, dt):
        if not self.session: 
            return
        s = self.session
        s.mine.update(dt)
        
        for p in s.players:
            k = min(1.0, dt * 8.0)
            p.visual_x += (p.target_x - p.visual_x) * k
            p.visual_z += (p.target_z - p.visual_z) * k
            
            distance = math.sqrt((p.target_x - p.visual_x)**2 + (p.target_z - p.visual_z)**2)
            if distance > 0.1: 
                p.bob_phase += dt * 10.0
            else: 
                p.bob_phase = 0.0