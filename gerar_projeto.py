import pathlib

ROOT = pathlib.Path("procurando_o_tesouro")
ROOT.mkdir(exist_ok=True)

def w(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.lstrip("\n"), encoding="utf-8")
    print("OK:", rel)

# Marca d'água para confirmar execução
print("=== INICIANDO GERACAO ===")

w("requirements.txt", """
pygame-ce>=2.4.0
PyOpenGL>=3.1.6
PyOpenGL-accelerate>=3.1.6
Pillow>=10.0.0
numpy>=1.24.0
pytest>=7.0.0
""")

w(".gitignore", """
__pycache__/
*.pyc
.venv/
saves/*.json
""")

w("config/__init__.py", """
from .settings import settings, Settings
__all__ = ["settings", "Settings"]
""")

w("config/settings.py", """
from __future__ import annotations

class Settings:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    WINDOW_TITLE = "Procurando o Tesouro"
    FPS = 60
    BOARD_ROWS = 6
    BOARD_COLS = 6
    TILE_SIZE = 1.6
    TILE_HEIGHT = 0.25
    TILE_SPACING = 0.05
    PLAYER_COLORS = [
        (0.9, 0.2, 0.2),
        (0.2, 0.4, 0.95),
        (0.2, 0.85, 0.3),
        (0.95, 0.85, 0.15),
    ]
    PLAYER_NAMES = ["Vermelho", "Azul", "Verde", "Amarelo"]
    TRAP_DEADEND_PENALTY = 10
    TRAP_HIDEOUT_OPPONENT_PENALTY = 5
    CLUE_BONUS = 3
    TRAP_RATIO = 0.10
    CLUE_RATIO = 0.05
    INVISIBILITY_TURNS = 1
    CAMERA_FOV = 55.0
    CAMERA_NEAR = 0.1
    CAMERA_FAR = 200.0
    CAMERA_MIN_DISTANCE = 5.0
    CAMERA_MAX_DISTANCE = 40.0
    CAMERA_MIN_PITCH = 5.0
    CAMERA_MAX_PITCH = 85.0
    CAMERA_INITIAL_YAW = 45.0
    CAMERA_INITIAL_PITCH = 50.0
    CAMERA_INITIAL_DISTANCE = 16.0
    CAMERA_ROTATE_SPEED = 0.35
    CAMERA_ZOOM_SPEED = 1.5
    CAMERA_PAN_SPEED = 8.0
    AMBIENT_COLOR = (0.18, 0.20, 0.28)
    DIRECTIONAL_DIR = (-0.3, -1.0, -0.4)
    DIRECTIONAL_COLOR = (0.35, 0.36, 0.45)
    AUDIO_VOLUME = 0.6
    PLAYER_MOVE_DURATION = 0.25
    PARTICLES_ENABLED = True
    MAX_PARTICLES = 800
    RECORDS_FILE = "saves/records.json"

settings = Settings()
""")

w("entities/__init__.py", """
from .player import Player
from .tile import Tile, TileState, TileContent
from .diamond import Diamond
from .trap import Trap, TrapType
from .clue import Clue
__all__ = ["Player", "Tile", "TileState", "TileContent", "Diamond", "Trap", "TrapType", "Clue"]
""")

w("entities/player.py", """
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
""")

w("entities/tile.py", """
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
""")

w("entities/diamond.py", """
from __future__ import annotations
import random
from dataclasses import dataclass

@dataclass
class Diamond:
    carats: int
    discovered: bool = False
    discovered_by: int = None
    collected: bool = False

    @staticmethod
    def random():
        return Diamond(carats=random.randint(1, 10))

    @property
    def scale(self):
        if self.carats <= 3:
            return 0.55
        if self.carats <= 6:
            return 0.75
        if self.carats <= 8:
            return 0.95
        return 1.2

    @property
    def color(self):
        if self.carats <= 3:
            return (0.55, 0.85, 0.95)
        if self.carats <= 6:
            return (0.35, 0.75, 0.98)
        if self.carats <= 8:
            return (0.75, 0.55, 0.95)
        return (1.0, 0.85, 0.35)
""")

w("entities/trap.py", """
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
        if self.type == TrapType.DEAD_END:
            return "Tunel sem saida"
        return "Esconderijo secreto"
""")

w("entities/clue.py", """
from __future__ import annotations

class Clue:
    def __init__(self):
        self.discovered = False
        self.discovered_by = None
    description = "Prossiga"
""")

w("world/__init__.py", """
from .mine import Mine
from .board import Board
from .map_generator import MapGenerator
__all__ = ["Mine", "Board", "MapGenerator"]
""")

w("world/map_generator.py", """
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
        for _ in range(n_dead):
            contents.append((TileContent.TRAP, Trap(TrapType.DEAD_END)))
        for _ in range(n_hide):
            contents.append((TileContent.TRAP, Trap(TrapType.HIDEOUT)))
        for _ in range(n_clues):
            contents.append((TileContent.CLUE, Clue()))
        for _ in range(n_diamonds):
            contents.append((TileContent.DIAMOND, Diamond.random()))

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
""")

w("world/board.py", """
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
""")

w("world/mine.py", """
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
""")

w("systems/__init__.py", """
from .scoring_system import ScoringSystem
from .turn_system import TurnSystem
from .movement_system import MovementSystem
from .item_system import ItemSystem
from .save_system import SaveSystem
__all__ = ["ScoringSystem", "TurnSystem", "MovementSystem", "ItemSystem", "SaveSystem"]
""")

w("systems/scoring_system.py", """
from __future__ import annotations
from config.settings import settings

class ScoringSystem:
    def __init__(self, players):
        self.players = players
        self.last_message = ""

    def _find(self, pid):
        for p in self.players:
            if p.id == pid:
                return p
        raise ValueError("Jogador nao encontrado")

    def on_diamond(self, pid, diamond):
        p = self._find(pid)
        p.add_carats(diamond.carats)
        p.diamonds_found += 1
        diamond.collected = True
        diamond.discovered = True
        diamond.discovered_by = pid
        self.last_message = f"{p.name} encontrou diamante de {diamond.carats} ct!"

    def on_dead_end(self, pid, trap):
        p = self._find(pid)
        p.add_carats(-settings.TRAP_DEADEND_PENALTY)
        p.traps_found += 1
        trap.discovered = True
        trap.discovered_by = pid
        self.last_message = f"{p.name} caiu em tunel sem saida! -{settings.TRAP_DEADEND_PENALTY} ct"

    def on_hideout(self, pid, trap):
        p = self._find(pid)
        p.traps_found += 1
        p.set_invisible(settings.INVISIBILITY_TURNS)
        trap.discovered = True
        trap.discovered_by = pid
        for o in self.players:
            if o.id != pid:
                o.add_carats(-settings.TRAP_HIDEOUT_OPPONENT_PENALTY)
        self.last_message = f"{p.name} ficou invisivel! Oponentes -{settings.TRAP_HIDEOUT_OPPONENT_PENALTY} ct"

    def on_clue(self, pid, clue):
        p = self._find(pid)
        p.add_carats(settings.CLUE_BONUS)
        clue.discovered = True
        clue.discovered_by = pid
        self.last_message = f"{p.name} achou Prossiga! +{settings.CLUE_BONUS} ct"

    def ranking(self):
        return sorted(self.players, key=lambda p: p.carats, reverse=True)

    def winners(self):
        if not self.players:
            return []
        best = max(p.carats for p in self.players)
        return [p for p in self.players if p.carats == best]
""")

w("systems/turn_system.py", """
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
        if self.is_finished():
            return True
        self.current_index = (self.current_index + 1) % len(self.players)
        self.current_player.on_own_turn_start()
        return False

    def is_finished(self):
        return self.total_moves >= self.max_total_moves

    @property
    def round_number(self):
        return self.total_moves // len(self.players) + 1
""")

w("systems/movement_system.py", """
from __future__ import annotations

class MovementSystem:
    def __init__(self, board, players):
        self.board = board
        self.players = players

    def is_valid(self, player, dr, dc):
        if abs(dr) + abs(dc) != 1:
            return False
        return self.board.in_bounds(player.row + dr, player.col + dc)

    def try_move(self, player, dr, dc):
        if not self.is_valid(player, dr, dc):
            return False
        player.row += dr
        player.col += dc
        return True
""")

w("systems/item_system.py", """
from __future__ import annotations
from entities.tile import TileContent
from entities.trap import TrapType

class ItemSystem:
    def __init__(self, scoring):
        self.scoring = scoring

    def trigger(self, tile, player):
        if not tile.is_hidden():
            return None
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
""")

w("systems/save_system.py", """
from __future__ import annotations
import json
import os
from datetime import datetime
from config.settings import settings

class SaveSystem:
    def __init__(self, path=None):
        self.path = path or settings.RECORDS_FILE
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.records = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def add_result(self, name, score, num_players):
        self.records.append({
            "name": name,
            "score": score,
            "date": datetime.now().isoformat(timespec="seconds"),
            "players": num_players,
        })
        self.records.sort(key=lambda r: r.get("score", 0), reverse=True)
        self.records = self.records[:50]
        self._save()

    def top(self, n=10):
        return self.records[:n]
""")

w("graphics/__init__.py", """
from .camera import Camera
from .renderer import Renderer
from .texture_manager import TextureManager
from .particle_system import ParticleSystem
from .effects import EffectsManager
__all__ = ["Camera", "Renderer", "TextureManager", "ParticleSystem", "EffectsManager"]
""")

w("core/__init__.py", """
from .game_state import GameState
__all__ = ["GameState"]
""")

w("core/game_state.py", """
from enum import Enum

class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYER_SELECTION = "player_selection"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
""")

w("saves/records.json", "[]\n")

print("=== GERACAO CONCLUIDA ===")
print("Pasta criada em:", ROOT.resolve())
print("Arquivos gerados ate agora. Avise se apareceu esta mensagem.")