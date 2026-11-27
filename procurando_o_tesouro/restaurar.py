import pathlib

ROOT = pathlib.Path(".")
if not (ROOT / "main.py").exists():
    print("ERRO: Execute este script na pasta raiz do projeto (onde esta o main.py).")
    raise SystemExit(1)

def w(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.lstrip("\n"), encoding="utf-8")
    print("OK:", rel)

print("=== RESTAURANDO PROJETO ===")

w("requirements.txt", """
pygame-ce>=2.4.0
PyOpenGL>=3.1.6
PyOpenGL-accelerate>=3.1.6
Pillow>=10.0.0
numpy>=1.24.0
pytest>=7.0.0
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
    CAMERA_INITIAL_PITCH = 65.0
    CAMERA_INITIAL_DISTANCE = 12.0
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
        if self.carats <= 3: return 0.55
        if self.carats <= 6: return 0.75
        if self.carats <= 8: return 0.95
        return 1.2

    @property
    def color(self):
        if self.carats <= 3: return (0.55, 0.85, 0.95)
        if self.carats <= 6: return (0.35, 0.75, 0.98)
        if self.carats <= 8: return (0.75, 0.55, 0.95)
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
        if self.type == TrapType.DEAD_END: return "Tunel sem saida"
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
            if p.id == pid: return p
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
        self.last_message = f"{p.name} caiu em um tunel sem saida! -{settings.TRAP_DEADEND_PENALTY} ct"

    def on_hideout(self, pid, trap):
        p = self._find(pid)
        p.traps_found += 1
        p.set_invisible(settings.INVISIBILITY_TURNS)
        trap.discovered = True
        trap.discovered_by = pid
        for o in self.players:
            if o.id != pid: o.add_carats(-settings.TRAP_HIDEOUT_OPPONENT_PENALTY)
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
        if not self.players: return []
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
        if self.is_finished(): return True
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
        if abs(dr) + abs(dc) != 1: return False
        return self.board.in_bounds(player.row + dr, player.col + dc)

    def try_move(self, player, dr, dc):
        if not self.is_valid(player, dr, dc): return False
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
        if not os.path.exists(self.path): return []
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
            "name": name, "score": score,
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

w("graphics/shader.py", """
from __future__ import annotations
from OpenGL.GL import (
    glCreateShader, glShaderSource, glCompileShader, glGetShaderiv,
    glGetShaderInfoLog, glCreateProgram, glAttachShader, glLinkProgram,
    glGetProgramiv, glGetProgramInfoLog, glDeleteShader, glUseProgram,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS, GL_LINK_STATUS,
    glGetUniformLocation, glUniformMatrix4fv, glUniform3f, glUniform1f,
    glUniform1i, GL_FALSE,
)
import numpy as np

class Shader:
    def __init__(self, vs, fs):
        self.program = self._compile(vs, fs)
        self._cache = {}

    def _compile(self, vs, fs):
        prog = glCreateProgram()
        v = self._one(vs, GL_VERTEX_SHADER)
        f = self._one(fs, GL_FRAGMENT_SHADER)
        glAttachShader(prog, v)
        glAttachShader(prog, f)
        glLinkProgram(prog)
        if not glGetProgramiv(prog, GL_LINK_STATUS):
            raise RuntimeError("Link shader falhou")
        glDeleteShader(v)
        glDeleteShader(f)
        return prog

    def _one(self, src, kind):
        sid = glCreateShader(kind)
        glShaderSource(sid, src)
        glCompileShader(sid)
        if not glGetShaderiv(sid, GL_COMPILE_STATUS):
            raise RuntimeError("Compile shader falhou")
        return sid

    def use(self):
        glUseProgram(self.program)

    def _loc(self, name):
        if name not in self._cache:
            self._cache[name] = glGetUniformLocation(self.program, name)
        return self._cache[name]

    def set_mat4(self, name, mat):
        glUniformMatrix4fv(self._loc(name), 1, GL_FALSE, np.asarray(mat, dtype=np.float32).flatten())

    def set_vec3(self, name, v):
        glUniform3f(self._loc(name), float(v[0]), float(v[1]), float(v[2]))

    def set_float(self, name, v):
        glUniform1f(self._loc(name), float(v))

    def set_int(self, name, v):
        glUniform1i(self._loc(name), int(v))
""")

w("graphics/camera.py", """
from __future__ import annotations
import math
import numpy as np
from config.settings import settings

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m

def look_at(eye, target, up):
    f = target - eye
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m

class Camera:
    def __init__(self):
        self.yaw = settings.CAMERA_INITIAL_YAW
        self.pitch = settings.CAMERA_INITIAL_PITCH
        self.distance = settings.CAMERA_INITIAL_DISTANCE
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.aspect = settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT

    def reset(self):
        self.yaw = settings.CAMERA_INITIAL_YAW
        self.pitch = settings.CAMERA_INITIAL_PITCH
        self.distance = settings.CAMERA_INITIAL_DISTANCE
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def rotate(self, dx, dy):
        self.yaw += dx * settings.CAMERA_ROTATE_SPEED
        self.pitch = max(settings.CAMERA_MIN_PITCH,
                         min(settings.CAMERA_MAX_PITCH,
                             self.pitch + dy * settings.CAMERA_ROTATE_SPEED))

    def zoom(self, delta):
        self.distance = max(settings.CAMERA_MIN_DISTANCE,
                            min(settings.CAMERA_MAX_DISTANCE,
                                self.distance - delta * settings.CAMERA_ZOOM_SPEED))

    def pan(self, dx, dy):
        rad = math.radians(self.yaw)
        fwd = np.array([math.sin(rad), 0, math.cos(rad)], dtype=np.float32)
        right = np.array([math.cos(rad), 0, -math.sin(rad)], dtype=np.float32)
        self.target += right * dx * settings.CAMERA_PAN_SPEED * 0.1
        self.target += fwd * dy * settings.CAMERA_PAN_SPEED * 0.1

    def eye(self):
        py = math.radians(self.pitch)
        yw = math.radians(self.yaw)
        x = self.distance * math.cos(py) * math.sin(yw)
        y = self.distance * math.sin(py)
        z = self.distance * math.cos(py) * math.cos(yw)
        return self.target + np.array([x, y, z], dtype=np.float32)

    def view_matrix(self):
        return look_at(self.eye(), self.target, np.array([0, 1, 0], dtype=np.float32))

    def projection_matrix(self):
        return perspective(settings.CAMERA_FOV, self.aspect,
                           settings.CAMERA_NEAR, settings.CAMERA_FAR)
""")

w("graphics/lighting.py", """
from __future__ import annotations
from dataclasses import dataclass
from config.settings import settings

@dataclass
class PointLight:
    position: tuple
    color: tuple
    intensity: float = 1.0
    radius: float = 6.0

class Lighting:
    def __init__(self):
        self.ambient = settings.AMBIENT_COLOR
        self.dir_dir = settings.DIRECTIONAL_DIR
        self.dir_color = settings.DIRECTIONAL_COLOR
        self.lights = []

    def add_light(self, l):
        self.lights.append(l)

    def clear(self):
        self.lights.clear()

    def upload(self, shader):
        shader.set_vec3("uAmbient", self.ambient)
        shader.set_vec3("uDirDir", self.dir_dir)
        shader.set_vec3("uDirColor", self.dir_color)
        n = min(len(self.lights), 8)
        shader.set_int("uNumLights", n)
        for i in range(n):
            l = self.lights[i]
            shader.set_vec3(f"uPointLights[{i}].position", l.position)
            shader.set_vec3(f"uPointLights[{i}].color", l.color)
            shader.set_float(f"uPointLights[{i}].intensity", l.intensity)
            shader.set_float(f"uPointLights[{i}].radius", l.radius)
""")

w("graphics/primitives.py", """
from __future__ import annotations
import ctypes
import math
import numpy as np
from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray, glGenBuffers, glBindBuffer,
    glBufferData, glVertexAttribPointer, glEnableVertexAttribArray,
    GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
)

def _v(off): return ctypes.c_void_p(off)

def _pack(vs, ns, ts):
    data = []
    for i in range(len(vs)):
        v = vs[i]; n = ns[i]; t = ts[i]
        data.extend([v[0], v[1], v[2], n[0], n[1], n[2], t[0], t[1]])
    return np.array(data, dtype=np.float32)

def _mesh(vs, ns, ts):
    data = _pack(vs, ns, ts)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    stride = 32
    glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, False, stride, _v(12))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, _v(24))
    glEnableVertexAttribArray(2)
    glBindVertexArray(0)
    return {"vao": vao, "vbo": vbo, "count": len(vs)}

def make_cube(size=1.0):
    s = size / 2.0
    vs, ns, ts = [], [], []
    faces = [
        ((0,0,1), [(-s,-s,s),(s,-s,s),(s,s,s),(-s,-s,s),(s,s,s),(-s,s,s)]),
        ((0,0,-1),[(-s,-s,-s),(-s,s,-s),(s,s,-s),(-s,-s,-s),(s,s,-s),(s,-s,-s)]),
        ((1,0,0), [(s,-s,-s),(s,s,-s),(s,s,s),(s,-s,-s),(s,s,s),(s,-s,s)]),
        ((-1,0,0),[(-s,-s,-s),(-s,-s,s),(-s,s,s),(-s,-s,-s),(-s,s,s),(-s,s,-s)]),
        ((0,1,0), [(-s,s,-s),(-s,s,s),(s,s,s),(-s,s,-s),(s,s,s),(s,s,-s)]),
        ((0,-1,0),[(-s,-s,-s),(s,-s,-s),(s,-s,s),(-s,-s,-s),(s,-s,s),(-s,-s,s)]),
    ]
    for n, vv in faces:
        for v in vv:
            vs.append(v); ns.append(n); ts.append((v[0]+s, v[2]+s))
    return _mesh(vs, ns, ts)

def make_plane(size=1.0):
    s = size / 2.0
    vs = [(-s,0,-s),(s,0,-s),(s,0,s),(-s,0,-s),(s,0,s),(-s,0,s)]
    ns = [(0,1,0)]*6
    ts = [(0,0),(1,0),(1,1),(0,0),(1,1),(0,1)]
    return _mesh(vs, ns, ts)

def make_pyramid(base=1.0, height=1.5):
    b = base / 2.0
    top = (0, height, 0)
    c = [(-b,0,-b),(b,0,-b),(b,0,b),(-b,0,b)]
    vs, ns, ts = [], [], []
    def tri(a, b_, cc, n):
        for v in (a, b_, cc): vs.append(v); ns.append(n)
        ts.extend([(0,0),(1,0),(0.5,1)])
    tri(c[0], c[1], top, (0,0.6,-0.8))
    tri(c[1], c[2], top, (0.8,0.6,0))
    tri(c[2], c[3], top, (0,0.6,0.8))
    tri(c[3], c[0], top, (-0.8,0.6,0))
    tri(c[0], c[3], c[2], (0,-1,0))
    tri(c[0], c[2], c[1], (0,-1,0))
    return _mesh(vs, ns, ts)

def make_octahedron(size=1.0, height=1.6):
    s = size / 2.0
    top = (0, height, 0)
    bot = (0, -height*0.5, 0)
    ring = [(s,0,0),(0,0,s),(-s,0,0),(0,0,-s)]
    vs, ns, ts = [], [], []
    for i in range(4):
        a = ring[i]; b = ring[(i+1)%4]
        for v in (a, b, top): vs.append(v); ns.append((v[0], v[1], v[2]))
        ts.extend([(0,0),(1,0),(0.5,1)])
        for v in (b, a, bot): vs.append(v); ns.append((v[0], -v[1], v[2]))
        ts.extend([(0,0),(1,0),(0.5,1)])
    return _mesh(vs, ns, ts)

def make_cylinder(radius=0.5, height=1.0, seg=12):
    vs, ns, ts = [], [], []
    for i in range(seg):
        a0 = 2*math.pi*i/seg
        a1 = 2*math.pi*(i+1)/seg
        x0, z0 = radius*math.cos(a0), radius*math.sin(a0)
        x1, z1 = radius*math.cos(a1), radius*math.sin(a1)
        vs.extend([(x0,0,z0),(x1,0,z1),(x1,height,z1),(x0,0,z0),(x1,height,z1),(x0,height,z0)])
        for _ in range(6): ns.append((x0, 0, z0))
        ts.extend([(i/seg,0),((i+1)/seg,0),((i+1)/seg,1),(i/seg,0),((i+1)/seg,1),(i/seg,1)])
        vs.extend([(0,height,0),(x0,height,z0),(x1,height,z1)])
        ns.extend([(0,1,0)]*3)
        ts.extend([(0.5,0.5),(0,0),(1,0)])
        vs.extend([(0,0,0),(x1,0,z1),(x0,0,z0)])
        ns.extend([(0,-1,0)]*3)
        ts.extend([(0.5,0.5),(1,0),(0,0)])
    return _mesh(vs, ns, ts)

def make_sphere(radius=0.5, seg=12, rings=8):
    vs, ns, ts = [], [], []
    for r in range(rings):
        v0 = r/rings; v1 = (r+1)/rings
        phi0 = math.pi*v0; phi1 = math.pi*v1
        for s in range(seg):
            u0 = s/seg; u1 = (s+1)/seg
            th0 = 2*math.pi*u0; th1 = 2*math.pi*u1
            def p(phi, th):
                return (radius*math.sin(phi)*math.cos(th),
                        radius*math.cos(phi),
                        radius*math.sin(phi)*math.sin(th))
            p00 = p(phi0, th0); p01 = p(phi0, th1)
            p10 = p(phi1, th0); p11 = p(phi1, th1)
            for v in (p00, p10, p11, p00, p11, p01):
                vs.append(v)
                nn = np.array(v)
                nn = nn / (np.linalg.norm(nn) + 1e-9)
                ns.append((nn[0], nn[1], nn[2]))
            ts.extend([(u0,v0),(u0,v1),(u1,v1),(u0,v0),(u1,v1),(u1,v0)])
    return _mesh(vs, ns, ts)
""")

w("graphics/texture_manager.py", """
from __future__ import annotations
import random
import numpy as np
from PIL import Image
from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexImage2D, glTexParameteri,
    GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_REPEAT,
)

class TextureManager:
    def __init__(self):
        self.textures = {}
        self._defaults()

    def _upload(self, name, image):
        image = image.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
        data = image.tobytes()
        w, h = image.size
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        self.textures[name] = tex

    def _noise(self, size, base, amp, rng):
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                n = rng.randint(-amp, amp)
                arr[y, x] = [max(0, min(255, base[0]+n)),
                             max(0, min(255, base[1]+n)),
                             max(0, min(255, base[2]+n))]
        return Image.fromarray(arr, "RGB")

    def _wood(self, size, rng):
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                stripe = int(20 * np.sin(x * 0.5 + rng.uniform(-0.3, 0.3)))
                arr[y, x] = [max(0, min(255, 120 + stripe)),
                             max(0, min(255, 80 + stripe)),
                             max(0, min(255, 40 + stripe))]
        return Image.fromarray(arr, "RGB")

    def _defaults(self):
        rng = random.Random(42)
        self._upload("stone", self._noise(128, (90, 85, 80), 30, rng))
        self._upload("dirt", self._noise(128, (60, 45, 35), 25, rng))
        self._upload("rock", self._noise(128, (50, 50, 55), 35, rng))
        self._upload("revealed", self._noise(128, (110, 95, 70), 20, rng))
        self._upload("crystal", self._noise(64, (80, 180, 220), 40, rng))
        self._upload("wood", self._wood(128, rng))

    def bind(self, name):
        tex = self.textures.get(name)
        if tex is None: tex = self.textures.get("stone", 0)
        glBindTexture(GL_TEXTURE_2D, tex)
        return tex
""")

w("graphics/particle_system.py", """
from __future__ import annotations
import random
from config.settings import settings

class Particle:
    __slots__ = ("x","y","z","vx","vy","vz","life","max_life","r","g","b","size")
    def __init__(self, x, y, z, vx, vy, vz, life, color, size=0.08):
        self.x=x; self.y=y; self.z=z
        self.vx=vx; self.vy=vy; self.vz=vz
        self.life=life; self.max_life=life
        self.r, self.g, self.b = color
        self.size = size

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_burst(self, x, y, z, color, count=20, spread=1.2, speed=2.0):
        if not settings.PARTICLES_ENABLED: return
        for _ in range(count):
            if len(self.particles) >= settings.MAX_PARTICLES: break
            vx = random.uniform(-spread, spread)*speed
            vy = random.uniform(0.5, spread)*speed
            vz = random.uniform(-spread, spread)*speed
            life = random.uniform(0.6, 1.4)
            self.particles.append(Particle(x, y, z, vx, vy, vz, life, color, random.uniform(0.05,0.12)))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0: continue
            p.x += p.vx*dt; p.y += p.vy*dt; p.z += p.vz*dt
            p.vy -= 4.0*dt
            alive.append(p)
        self.particles = alive
""")

w("graphics/effects.py", """
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class FlashEffect:
    color: tuple
    duration: float
    elapsed: float = 0.0
    intensity: float = 1.0

    def update(self, dt):
        self.elapsed += dt
        return self.elapsed < self.duration

    @property
    def alpha(self):
        t = min(1.0, self.elapsed / self.duration)
        return (1.0 - t) * self.intensity

class EffectsManager:
    def __init__(self):
        self.flashes = []

    def flash(self, color, duration=0.5, intensity=1.0):
        self.flashes.append(FlashEffect(color, duration, 0.0, intensity))

    def update(self, dt):
        self.flashes = [f for f in self.flashes if f.update(dt)]
""")

w("graphics/renderer.py", """
from __future__ import annotations
import math
import numpy as np
from OpenGL.GL import (
    glEnable, glClearColor, glClear, glViewport, glDrawArrays,
    glBindVertexArray, glBlendFunc, glDepthFunc, glCullFace, glFrontFace, glDisable,
    GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_LESS,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TRIANGLES,
    GL_CULL_FACE, GL_CW, GL_CCW
)
from config.settings import settings
from graphics.shader import Shader
from graphics.lighting import Lighting, PointLight
from graphics.primitives import (
    make_cube, make_plane, make_pyramid, make_octahedron,
    make_cylinder, make_sphere,
)
from graphics.particle_system import ParticleSystem
from entities.tile import TileState, TileContent
from entities.trap import TrapType

VS = '''
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec2 aUV;
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;
out vec3 vWorldPos;
out vec3 vNormal;
out vec2 vUV;
void main() {
    vec4 world = uModel * vec4(aPos, 1.0);
    vWorldPos = world.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    vUV = aUV;
    gl_Position = uProj * uView * world;
}
'''

FS = '''
#version 330 core
in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vUV;
uniform vec3 uAmbient;
uniform vec3 uDirDir;
uniform vec3 uDirColor;
struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
    float radius;
};
uniform int uNumLights;
uniform PointLight uPointLights[8];
uniform vec3 uTint;
uniform vec3 uEmissive;
uniform float uAlpha;
uniform sampler2D uTex;
uniform int uUseTexture;
out vec4 fragColor;
void main() {
    vec3 baseColor = uTint;
    if (uUseTexture == 1) {
        baseColor *= texture(uTex, vUV).rgb;
    }
    vec3 N = normalize(vNormal);
    vec3 lighting = uAmbient;
    vec3 L = normalize(-uDirDir);
    float d = max(dot(N, L), 0.0);
    lighting += uDirColor * d;
    for (int i = 0; i < uNumLights; i++) {
        vec3 lp = uPointLights[i].position - vWorldPos;
        float dist = length(lp);
        float att = clamp(1.0 - dist / uPointLights[i].radius, 0.0, 1.0);
        att *= att;
        vec3 Lp = normalize(lp);
        float diff = max(dot(N, Lp), 0.0);
        lighting += uPointLights[i].color * uPointLights[i].intensity * diff * att;
    }
    vec3 color = baseColor * lighting + uEmissive;
    fragColor = vec4(color, uAlpha);
}
'''

def translation(x, y, z):
    m = np.identity(4, dtype=np.float32)
    m[0, 3] = x; m[1, 3] = y; m[2, 3] = z
    return m

def scale_m(sx, sy, sz):
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = sx; m[1, 1] = sy; m[2, 2] = sz
    return m

def rotation_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c; m[0, 2] = s
    m[2, 0] = -s; m[2, 2] = c
    return m

class Renderer:
    def __init__(self, camera, textures):
        self.camera = camera
        self.textures = textures
        self.shader = Shader(VS, FS)
        self.lighting = Lighting()
        self.particles = ParticleSystem()
        self.time = 0.0
        self.mesh_cube = make_cube(1.0)
        self.mesh_plane = make_plane(1.0)
        self.mesh_pyramid = make_pyramid(1.0, 1.4)
        self.mesh_diamond = make_octahedron(1.0, 1.6)
        self.mesh_cylinder = make_cylinder(0.5, 1.0, 12)
        self.mesh_sphere = make_sphere(0.5, 12, 8)
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.02, 0.02, 0.04, 1.0)

    def resize(self, w, h):
        glViewport(0, 0, w, h)
        self.camera.aspect = w / max(1, h)

    def _draw(self, mesh, model, tint=(1,1,1), emissive=(0,0,0), texture_name=None, alpha=1.0):
        self.shader.set_mat4("uModel", model.T)
        self.shader.set_vec3("uTint", tint)
        self.shader.set_vec3("uEmissive", emissive)
        self.shader.set_float("uAlpha", alpha)
        if texture_name:
            self.shader.set_int("uUseTexture", 1)
            self.shader.set_int("uTex", 0)
            self.textures.bind(texture_name)
        else:
            self.shader.set_int("uUseTexture", 0)
        glBindVertexArray(mesh["vao"])
        glDrawArrays(GL_TRIANGLES, 0, mesh["count"])
        glBindVertexArray(0)

    def begin_frame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        self.shader.set_mat4("uView", self.camera.view_matrix().T)
        self.shader.set_mat4("uProj", self.camera.projection_matrix().T)

    def upload_lights(self, state):
        self.lighting.clear()
        for pos, color in [
            ((-6, 4, -6), (1.0, 0.65, 0.3)),
            (( 6, 4, -6), (1.0, 0.65, 0.3)),
            ((-6, 4,  6), (1.0, 0.65, 0.3)),
            (( 6, 4,  6), (1.0, 0.65, 0.3)),
        ]:
            flicker = 0.9 + 0.2 * math.sin(self.time * 8.0 + pos[0])
            self.lighting.add_light(PointLight(pos, color, flicker, 10.0))
        player = state.current_player
        if player:
            pos = (player.visual_x, 1.2, player.visual_z)
            self.lighting.add_light(PointLight(pos, (1.0, 0.9, 0.6), 1.2, 5.0))
        self.lighting.upload(self.shader)

    def draw_scene(self, state):
        self.time += 0.016
        self.upload_lights(state)
        
        ground = translation(0, -0.05, 0) @ scale_m(50, 1, 50)
        self._draw(self.mesh_plane, ground, tint=(0.3,0.25,0.2), texture_name="dirt")
        
        self._draw_skybox(state)
        self._draw_walls(state)
        self._draw_board(state)
        self._draw_players(state)
        self._draw_particles()

    def _draw_skybox(self, state):
        size = 40.0
        m = translation(0, 15, 0) @ scale_m(size, size, size)
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        self._draw(self.mesh_cube, m, tint=(0.1,0.1,0.15), texture_name="rock")
        glFrontFace(GL_CCW)
        glDisable(GL_CULL_FACE)

    def _cell_world_pos(self, row, col, rows, cols):
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        return (col - (cols-1)/2.0) * sx, (row - (rows-1)/2.0) * sx

    def _draw_walls(self, state):
        rows = state.mine.board.rows
        cols = state.mine.board.cols
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        ex = cols * sx / 2 + 1.5
        ez = rows * sx / 2 + 1.5
        h = 7.0
        
        for (px, pz, sxx, szz) in [
            (0, -ez, ex*2, 0.6),
            (0, ez, ex*2, 0.6),
            (-ex, 0, 0.6, ez*2),
            (ex, 0, 0.6, ez*2),
        ]:
            m = translation(px, h/2, pz) @ scale_m(sxx, h, szz)
            self._draw(self.mesh_cube, m, tint=(0.3,0.28,0.25), texture_name="rock")

        import random
        random.seed(42)
        for _ in range(25):
            rx = random.uniform(-ex+1, ex-1)
            rz = random.uniform(-ez+1, ez-1)
            ry = random.uniform(h-1.0, h)
            sc = random.uniform(0.2, 0.6)
            m = translation(rx, ry, rz) @ scale_m(sc, sc*2, sc) @ rotation_y(random.uniform(0, 360))
            self._draw(self.mesh_pyramid, m, tint=(0.2,0.2,0.25), texture_name="rock")

        for (px, pz) in [(-ex+1.5, -ez+2), (ex-2, ez-1.5), (-ex+2, ez-1.5)]:
            m = translation(px, 0.5, pz) @ scale_m(1.0, 1.0, 1.0)
            self._draw(self.mesh_cube, m, tint=(0.6,0.4,0.2), texture_name="wood")
            m = translation(px, 1.0, pz) @ scale_m(1.05, 0.1, 1.05)
            self._draw(self.mesh_cube, m, tint=(0.4,0.4,0.4), texture_name="stone")
        
        for (px, pz, color) in [
            (-ex+1, -ez+1, (0.3,0.7,1.0)),
            (ex-1, -ez+1, (0.4,0.9,0.5)),
            (-ex+1, ez-1, (1.0,0.5,0.8)),
            (ex-1, ez-1, (0.9,0.9,0.4)),
        ]:
            glow = 0.6 + 0.4 * math.sin(self.time * 2 + px)
            m = translation(px, 1.5, pz) @ scale_m(0.6, 2.0, 0.6)
            self._draw(self.mesh_diamond, m, tint=color,
                       emissive=(color[0]*0.5*glow, color[1]*0.5*glow, color[2]*0.5*glow))

    def _draw_board(self, state):
        board = state.mine.board
        for r in range(board.rows):
            for c in range(board.cols):
                tile = board.get(r, c)
                x, z = self._cell_world_pos(r, c, board.rows, board.cols)
                self._draw_tile(tile, x, z, state)

    def _draw_tile(self, tile, x, z, state):
        if tile.state == TileState.HIDDEN:
            tex = "stone"; tint = (0.55, 0.5, 0.45)
        else:
            tex = "revealed"; tint = (0.85, 0.78, 0.65)
        m = translation(x, 0, z) @ scale_m(settings.TILE_SIZE, settings.TILE_HEIGHT, settings.TILE_SIZE)
        self._draw(self.mesh_cube, m, tint=tint, texture_name=tex)
        
        if tile.discovered_by is not None:
            color = settings.PLAYER_COLORS[tile.discovered_by % 4]
            marker = translation(x, settings.TILE_HEIGHT + 0.01, z) @ scale_m(settings.TILE_SIZE*0.9, 0.02, settings.TILE_SIZE*0.9)
            self._draw(self.mesh_cube, marker, tint=color,
                       emissive=(color[0]*0.3, color[1]*0.3, color[2]*0.3))
                       
        if tile.state == TileState.REVEALED:
            if tile.content == TileContent.DIAMOND and not tile.item.collected:
                self._draw_diamond(tile.item, x, z)
            elif tile.content == TileContent.TRAP:
                self._draw_trap(tile.item, x, z)
            elif tile.content == TileContent.CLUE:
                self._draw_clue(tile.item, x, z)
        elif tile.state == TileState.HIDDEN:
            bs = 0.25
            m = translation(x, settings.TILE_HEIGHT, z) @ scale_m(bs, bs*0.6, bs)
            self._draw(self.mesh_sphere, m, tint=(0.45,0.4,0.38))

    def _draw_diamond(self, diamond, x, z):
        s = diamond.scale
        bob = 0.05 * math.sin(self.time * 3 + x)
        y = settings.TILE_HEIGHT + 0.4 + bob
        m = translation(x, y, z) @ rotation_y(self.time * 40) @ scale_m(s, s, s)
        c = diamond.color
        self._draw(self.mesh_diamond, m, tint=c,
                   emissive=(c[0]*0.5, c[1]*0.5, c[2]*0.6), texture_name="crystal")

    def _draw_trap(self, trap, x, z):
        if trap.type == TrapType.DEAD_END:
            m = translation(x, settings.TILE_HEIGHT*0.5, z) @ scale_m(0.9, 0.5, 0.9)
            self._draw(self.mesh_cylinder, m, tint=(0.25,0.05,0.05),
                       texture_name="rock", emissive=(0.4,0.05,0.05))
            m2 = translation(x, settings.TILE_HEIGHT, z) @ scale_m(1.0, 0.1, 1.0)
            self._draw(self.mesh_cylinder, m2, tint=(0.7,0.2,0.1), emissive=(0.5,0.1,0.05))
        else:
            m = translation(x, settings.TILE_HEIGHT, z) @ scale_m(1.2, 1.0, 1.2)
            self._draw(self.mesh_sphere, m, tint=(0.15,0.15,0.2),
                       texture_name="rock", emissive=(0.05,0.05,0.1))

    def _draw_clue(self, clue, x, z):
        bob = 0.05 * math.sin(self.time * 3 + x)
        m = translation(x, settings.TILE_HEIGHT + 0.35 + bob, z) @ rotation_y(self.time * 30) @ scale_m(0.6, 0.6, 0.6)
        self._draw(self.mesh_diamond, m, tint=(0.3,1.0,0.4),
                   emissive=(0.3,0.8,0.3), texture_name="crystal")

    def _draw_players(self, state):
        for p in state.players:
            alpha = 0.25 if p.invisible else 1.0
            x, z = p.visual_x, p.visual_z
            bob = 0.05 * math.sin(self.time * 4 + p.id)
            
            m = translation(x, 0.35 + bob, z) @ scale_m(0.35, 0.5, 0.35)
            self._draw(self.mesh_cylinder, m, tint=p.color, alpha=alpha)
            m = translation(x, 0.8 + bob, z) @ scale_m(0.35, 0.35, 0.35)
            self._draw(self.mesh_sphere, m, tint=(0.95,0.85,0.7), alpha=alpha)
            m = translation(x, 0.95 + bob, z) @ scale_m(0.4, 0.35, 0.4)
            self._draw(self.mesh_pyramid, m, tint=(0.9,0.7,0.2), alpha=alpha)
            m = translation(x, 0.7 + bob, z) @ scale_m(0.12,0.12,0.12)
            self._draw(self.mesh_sphere, m, tint=(1.0,0.95,0.7),
                       emissive=(1.0,0.9,0.5), alpha=alpha)

    def _draw_particles(self):
        for p in self.particles.particles:
            t = p.life / max(0.001, p.max_life)
            s = p.size * t
            m = translation(p.x, p.y, p.z) @ scale_m(s, s, s)
            self._draw(self.mesh_cube, m, tint=(p.r, p.g, p.b),
                       emissive=(p.r*p.life*0.5, p.g*p.life*0.5, p.b*p.life*0.5))
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

w("core/event_manager.py", """
from __future__ import annotations
import pygame

class EventManager:
    def __init__(self):
        self.mouse_dragging = False
        self.last_mouse = (0, 0)
        self.mouse_delta = (0, 0)
        self.scroll_delta = 0.0
        self.keys_pressed = set()

    def pump(self):
        self.mouse_delta = (0, 0)
        self.scroll_delta = 0.0
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.mouse_dragging = True
                    self.last_mouse = e.pos
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    self.mouse_dragging = False
            elif e.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    dx = e.pos[0] - self.last_mouse[0]
                    dy = e.pos[1] - self.last_mouse[1]
                    self.mouse_delta = (dx, dy)
                    self.last_mouse = e.pos
            elif e.type == pygame.MOUSEWHEEL:
                self.scroll_delta += e.y
        return events

    def update_keys(self):
        keys = pygame.key.get_pressed()
        self.keys_pressed = {i for i in range(len(keys)) if keys[i]}
""")

w("core/game_manager.py", """
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
        if not self.session: return False
        s = self.session
        if s.turn.is_finished(): return False
        player = s.current_player
        if not s.movement.try_move(player, dr, dc): return False

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
        if not ev or not r: return
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
        if not self.session: return
        from core.game_state import GameState
        for p in self.session.players:
            self.save_system.add_result(p.name, p.carats, len(self.session.players))
        self.game.state = GameState.GAME_OVER

    def update(self, dt):
        if not self.session: return
        s = self.session
        s.mine.update(dt)
        
        for p in s.players:
            k = min(1.0, dt * 8.0)
            p.visual_x += (p.target_x - p.visual_x) * k
            p.visual_z += (p.target_z - p.visual_z) * k
            
            distance = math.sqrt((p.target_x - p.visual_x)**2 + (p.target_z - p.visual_z)**2)
            if distance > 0.1: p.bob_phase += dt * 10.0
            else: p.bob_phase = 0.0
""")

w("core/game.py", """
from __future__ import annotations
import ctypes
import pygame
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import (
    glClearColor, glClear, glGenTextures, glBindTexture, glTexImage2D,
    glTexParameteri, glEnable, glDisable, glBlendFunc, glUseProgram,
    glGenVertexArrays, glBindVertexArray, glGenBuffers, glBindBuffer,
    glBufferData, glEnableVertexAttribArray, glVertexAttribPointer,
    glDrawArrays, glDeleteTextures, glActiveTexture,
    GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, GL_BLEND, GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA, GL_LINEAR, GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER, GL_DEPTH_TEST, GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT, GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
    GL_TRIANGLES, GL_TEXTURE0,
)
from config.settings import settings
from core.game_state import GameState
from core.event_manager import EventManager
from core.game_manager import GameManager
from graphics.camera import Camera
from graphics.renderer import Renderer
from graphics.texture_manager import TextureManager
from graphics.effects import EffectsManager
from graphics.shader import Shader
from ui.menu import MainMenu
from ui.player_selection import PlayerSelection
from ui.hud import HUD
from ui.scoreboard import GameOverScreen
from ui.settings_menu import SettingsMenu
from ui.pause_menu import PauseMenu

OVERLAY_VS = '''
#version 330 core
layout(location=0) in vec2 aPos;
layout(location=1) in vec2 aUV;
out vec2 vUV;
void main() {
    vUV = aUV;
    gl_Position = vec4(aPos, 0.0, 1.0);
}
'''

OVERLAY_FS = '''
#version 330 core
in vec2 vUV;
uniform sampler2D uTex;
out vec4 fragColor;
void main() {
    fragColor = texture(uTex, vUV);
}
'''

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                         pygame.GL_CONTEXT_PROFILE_CORE)
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL)
        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        self.show_records = False

        self.camera = Camera()
        self.textures = TextureManager()
        self.renderer = Renderer(self.camera, self.textures)
        self.effects = EffectsManager()
        self.events = EventManager()

        self.ui_screen = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        self.game_manager = GameManager(self)
        self.save_system = self.game_manager.save_system

        self.main_menu = MainMenu(self.ui_screen, self)
        self.player_selection = PlayerSelection(self.ui_screen, self)
        self.hud = HUD(self.ui_screen)
        self.game_over = GameOverScreen(self.ui_screen, self)
        self.settings_menu = SettingsMenu(self.ui_screen, self)
        self.pause_menu = PauseMenu(self.ui_screen, self)

        self._init_overlay()

    def _init_overlay(self):
        self._overlay_shader = Shader(OVERLAY_VS, OVERLAY_FS)
        verts = np.array([
            -1, -1, 0, 0,
             1, -1, 1, 0,
             1,  1, 1, 1,
            -1, -1, 0, 0,
             1,  1, 1, 1,
            -1,  1, 0, 1,
        ], dtype=np.float32)
        self._overlay_vao = glGenVertexArrays(1)
        glBindVertexArray(self._overlay_vao)
        self._overlay_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._overlay_vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        stride = 4 * 4
        glVertexAttribPointer(0, 2, GL_FLOAT, False, stride, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, stride, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

    def change_state(self, state):
        self.state = state

    def _handle_events(self):
        events = self.events.pump()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
                return
            if self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(e)
            elif self.state == GameState.PLAYER_SELECTION:
                self.player_selection.handle_event(e)
            elif self.state == GameState.SETTINGS:
                self.settings_menu.handle_event(e)
            elif self.state == GameState.PLAYING:
                self._handle_play_event(e)
            elif self.state == GameState.PAUSED:
                self.pause_menu.handle_event(e)
            elif self.state == GameState.GAME_OVER:
                self.game_over.handle_event(e)

    def _handle_play_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.change_state(GameState.PAUSED)
                return
            if e.key == pygame.K_r:
                self.camera.reset()
                return
            if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if e.key == pygame.K_UP: dr, dc = -1, 0
                elif e.key == pygame.K_DOWN: dr, dc = 1, 0
                elif e.key == pygame.K_LEFT: dr, dc = 0, -1
                else: dr, dc = 0, 1
                self.game_manager.try_player_move(dr, dc)

    def _update(self, dt):
        self.events.update_keys()
        dx, dy = self.events.mouse_delta
        if dx or dy:
            self.camera.rotate(-dx, dy)
        if self.events.scroll_delta:
            self.camera.zoom(self.events.scroll_delta)
            
        k = self.events.keys_pressed
        if pygame.K_w in k: self.camera.pan(0, -1)
        if pygame.K_s in k: self.camera.pan(0, 1)
        if pygame.K_a in k: self.camera.pan(-1, 0)
        if pygame.K_d in k: self.camera.pan(1, 0)

        self.effects.update(dt)

        if self.state == GameState.PLAYING:
            self.game_manager.update(dt)
            self.hud.update(dt)
            self.renderer.particles.update(dt)
        elif self.state == GameState.MAIN_MENU:
            self.main_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.PLAYER_SELECTION:
            self.player_selection.update(pygame.mouse.get_pos())
        elif self.state == GameState.SETTINGS:
            self.settings_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.PAUSED:
            self.pause_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.GAME_OVER:
            self.game_over.update(pygame.mouse.get_pos())

    def _draw(self):
        if self.state in (GameState.PLAYING, GameState.PAUSED):
            self.renderer.begin_frame()
            s = self.game_manager.session
            if s: self.renderer.draw_scene(s)
            self._hud_overlay()
            if self.state == GameState.PAUSED:
                self.pause_menu.draw()
                self._blit_surface(self.ui_screen)
        else:
            self._render_2d()
        pygame.display.flip()

    def _hud_overlay(self):
        surf = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        old = self.hud.screen
        self.hud.screen = surf
        if self.game_manager.session:
            self.hud.draw(self.game_manager.session)
        self.hud.screen = old
        self._blit_surface(surf)

    def _render_2d(self):
        glClearColor(0.05, 0.04, 0.03, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.state == GameState.MAIN_MENU: self.main_menu.draw()
        elif self.state == GameState.PLAYER_SELECTION: self.player_selection.draw()
        elif self.state == GameState.SETTINGS: self.settings_menu.draw()
        elif self.state == GameState.GAME_OVER: self.game_over.draw()
        self._blit_surface(self.ui_screen)

    def _blit_surface(self, surf):
        data = pygame.image.tostring(surf, "RGBA", True)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surf.get_width(), surf.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glUseProgram(self._overlay_shader.program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex)
        self._overlay_shader.set_int("uTex", 0)
        glBindVertexArray(self._overlay_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)
        glUseProgram(0)
        glEnable(GL_DEPTH_TEST)
        glDeleteTextures([tex])

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events()
            if not self.running: break
            self._update(dt)
            self._draw()
        pygame.quit()
""")

w("ui/__init__.py", """
from .menu import MainMenu
from .hud import HUD
from .scoreboard import GameOverScreen
from .settings_menu import SettingsMenu
from .player_selection import PlayerSelection
from .pause_menu import PauseMenu
__all__ = ["MainMenu", "HUD", "GameOverScreen", "SettingsMenu", "PlayerSelection", "PauseMenu"]
""")

w("ui/button.py", """
import pygame

class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.hover = False

    def update(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.callback()
                return True
        return False

    def draw(self, screen):
        base = (95, 70, 40) if self.hover else (60, 45, 30)
        border = (255, 220, 120) if self.hover else (200, 160, 80)
        pygame.draw.rect(screen, base, self.rect, border_radius=8)
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=8)
        t = self.font.render(self.text, True, (245, 230, 200))
        screen.blit(t, t.get_rect(center=self.rect.center))
""")

w("ui/menu.py", """
import pygame
from ui.button import Button
from core.game_state import GameState

class MainMenu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.ft = pygame.font.SysFont("arial", 56, bold=True)
        self.fb = pygame.font.SysFont("arial", 26, bold=True)
        self.buttons = []
        self._build()

    def _build(self):
        w, h = self.screen.get_size()
        cx = w // 2
        bw, bh = 340, 56
        y = h // 2 - 80
        self.buttons = [
            Button((cx-bw//2, y, bw, bh), "JOGAR", self._play, self.fb),
            Button((cx-bw//2, y+70, bw, bh), "CONFIGURACOES", self._settings, self.fb),
            Button((cx-bw//2, y+140, bw, bh), "MELHORES PONTUACOES", self._records, self.fb),
            Button((cx-bw//2, y+210, bw, bh), "SAIR", self._quit, self.fb),
        ]

    def _play(self): self.game.change_state(GameState.PLAYER_SELECTION)
    def _settings(self): self.game.change_state(GameState.SETTINGS)
    def _records(self): self.game.show_records = True
    def _quit(self): self.game.running = False

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.game.show_records = False

    def update(self, pos):
        for b in self.buttons: b.update(pos)

    def draw(self):
        self.screen.fill((18, 14, 10))
        w, h = self.screen.get_size()
        for i in range(0, w, 60):
            pygame.draw.line(self.screen, (30, 25, 18), (i, 0), (i, h))
        t = self.ft.render("PROCURANDO O TESOURO", True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, h//4)))
        s = self.fb.render("Uma aventura nas profundezas da mina", True, (200, 180, 140))
        self.screen.blit(s, s.get_rect(center=(w//2, h//4 + 50)))
        for b in self.buttons: b.draw(self.screen)
        if self.game.show_records: self._draw_records()

    def _draw_records(self):
        w, h = self.screen.get_size()
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0, 0))
        f = pygame.font.SysFont("arial", 32, bold=True)
        t = f.render("MELHORES PONTUACOES", True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, 80)))
        sm = pygame.font.SysFont("arial", 22)
        for i, rec in enumerate(self.game.save_system.top(10)):
            line = f"{i+1}. {rec['name']} - {rec['score']} ct ({rec['players']} jog.) {rec['date'][:10]}"
            r = sm.render(line, True, (230, 220, 200))
            self.screen.blit(r, r.get_rect(center=(w//2, 150 + i*34)))
        hint = sm.render("ESC para voltar", True, (180, 180, 180))
        self.screen.blit(hint, hint.get_rect(center=(w//2, h-40)))
""")

w("ui/hud.py", """
import pygame

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.fb = pygame.font.SysFont("arial", 28, bold=True)
        self.f = pygame.font.SysFont("arial", 20)
        self.fs = pygame.font.SysFont("arial", 16)
        self.message = ""
        self.message_time = 0.0

    def show_message(self, msg):
        self.message = msg
        self.message_time = 3.0

    def update(self, dt):
        if self.message_time > 0: self.message_time -= dt

    def draw(self, state):
        w = self.screen.get_width()
        p = pygame.Surface((w, 60), pygame.SRCALPHA)
        p.fill((0, 0, 0, 160))
        self.screen.blit(p, (0, 0))
        cur = state.current_player
        if cur:
            c = tuple(int(x*255) for x in cur.color)
            t = self.fb.render(f"Vez de: {cur.name}", True, c)
            self.screen.blit(t, (20, 15))
        turns = self.f.render(
            f"Jogada: {state.turn.total_moves}/{state.turn.max_total_moves}   "
            f"Rodada: {state.turn.round_number}", True, (230, 220, 200))
        self.screen.blit(turns, (w//2 - turns.get_width()//2, 20))
        rk = state.scoring.ranking()
        rh = 40 + len(rk) * 28
        pr = pygame.Surface((240, rh), pygame.SRCALPHA)
        pr.fill((0, 0, 0, 160))
        self.screen.blit(pr, (w - 250, 70))
        title = self.f.render("RANKING", True, (255, 210, 100))
        self.screen.blit(title, (w - 240, 76))
        for i, p in enumerate(rk):
            c = tuple(int(x*255) for x in p.color)
            line = self.fs.render(f"{i+1}. {p.name}: {p.carats} ct", True, c)
            self.screen.blit(line, (w - 235, 104 + i*28))
        board = state.mine.board
        info = self.fs.render(
            f"Descobertas: {board.revealed_count}/{board.total_cells}",
            True, (200, 200, 200))
        self.screen.blit(info, (20, self.screen.get_height() - 30))
        ctrl = self.fs.render(
            "Setas: mover | Mouse: girar | Scroll: zoom | WASD: camera | R: reset | ESC: pausar",
            True, (170, 170, 170))
        self.screen.blit(ctrl, ctrl.get_rect(center=(w//2, self.screen.get_height() - 20)))
        if self.message_time > 0 and self.message:
            alpha = min(1.0, self.message_time)
            ms = self.fb.render(self.message, True, (255, 240, 200))
            bg = pygame.Surface((ms.get_width() + 40, 60), pygame.SRCALPHA)
            bg.fill((0, 0, 0, int(180*alpha)))
            self.screen.blit(bg, bg.get_rect(center=(w//2, 130)))
            ms.set_alpha(int(255*alpha))
            self.screen.blit(ms, ms.get_rect(center=(w//2, 130)))
""")

w("ui/scoreboard.py", """
import pygame
from ui.button import Button
from core.game_state import GameState

class GameOverScreen:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.ft = pygame.font.SysFont("arial", 48, bold=True)
        self.f = pygame.font.SysFont("arial", 24)
        self.fs = pygame.font.SysFont("arial", 18)
        self.buttons = []
        self._build()

    def _build(self):
        w, h = self.screen.get_size()
        bw, bh = 260, 50
        self.buttons = [
            Button((w//2 - bw - 10, h - 80, bw, bh), "JOGAR NOVAMENTE",
                   lambda: self.game.game_manager.start_new_game(), self.f),
            Button((w//2 + 10, h - 80, bw, bh), "MENU PRINCIPAL",
                   lambda: self.game.change_state(GameState.MAIN_MENU), self.f),
        ]

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)

    def update(self, pos):
        for b in self.buttons: b.update(pos)

    def draw(self):
        self.screen.fill((15, 12, 8))
        w, h = self.screen.get_size()
        gm = self.game.game_manager
        if not gm.scoring: return
        wins = gm.scoring.winners()
        ranking = gm.scoring.ranking()
        title_text = "EMPATE!" if len(wins) > 1 else f"VENCEDOR: {wins[0].name}"
        t = self.ft.render(title_text, True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, 60)))
        y = 140
        for i, p in enumerate(ranking):
            c = tuple(int(x*255) for x in p.color)
            line = self.f.render(f"{i+1}. {p.name} - {p.carats} quilates", True, c)
            self.screen.blit(line, line.get_rect(center=(w//2, y)))
            d = self.fs.render(
                f"Diamantes: {p.diamonds_found} | Armadilhas: {p.traps_found}",
                True, (200, 200, 200))
            self.screen.blit(d, d.get_rect(center=(w//2, y+26)))
            y += 70
        for b in self.buttons: b.draw(self.screen)
""")

w("ui/settings_menu.py", """
import pygame
from ui.button import Button
from config.settings import settings
from core.game_state import GameState

class SettingsMenu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.f = pygame.font.SysFont("arial", 22)
        self.ft = pygame.font.SysFont("arial", 40, bold=True)
        self.buttons = []
        self._build()

    def _build(self):
        w, h = self.screen.get_size()
        self.buttons = [
            Button((w//2-180, h-120, 360, 50), "VOLTAR",
                   lambda: self.game.change_state(GameState.MAIN_MENU), self.f),
            Button((w//2-180, 200, 360, 50), f"Volume: {int(settings.AUDIO_VOLUME*100)}%",
                   self._cycle_volume, self.f),
            Button((w//2-180, 270, 360, 50),
                   f"Particulas: {'ON' if settings.PARTICLES_ENABLED else 'OFF'}",
                   self._toggle_particles, self.f),
            Button((w//2-180, 340, 360, 50), f"FPS: {settings.FPS}",
                   self._cycle_fps, self.f),
        ]

    def _cycle_volume(self):
        settings.AUDIO_VOLUME = round((settings.AUDIO_VOLUME + 0.2) % 1.2, 1)
        if settings.AUDIO_VOLUME > 1.0: settings.AUDIO_VOLUME = 0.0
        self._build()

    def _toggle_particles(self):
        settings.PARTICLES_ENABLED = not settings.PARTICLES_ENABLED
        self._build()

    def _cycle_fps(self):
        opts = [30, 60, 120]
        i = opts.index(settings.FPS) if settings.FPS in opts else 1
        settings.FPS = opts[(i+1) % len(opts)]
        self._build()

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.game.change_state(GameState.MAIN_MENU)

    def update(self, pos):
        for b in self.buttons: b.update(pos)

    def draw(self):
        self.screen.fill((20, 16, 12))
        w, h = self.screen.get_size()
        t = self.ft.render("CONFIGURACOES", True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, 100)))
        for b in self.buttons: b.draw(self.screen)
""")

w("ui/player_selection.py", """
import pygame
from ui.button import Button
from config.settings import settings
from core.game_state import GameState

class PlayerSelection:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.f = pygame.font.SysFont("arial", 24)
        self.ft = pygame.font.SysFont("arial", 40, bold=True)
        self.fs = pygame.font.SysFont("arial", 18)
        self.num_players = 2
        self.nomes = settings.PLAYER_NAMES.copy()
        self.active_input = 0
        self.buttons = []
        self._build()

    def _build(self):
        w, h = self.screen.get_size()
        self.buttons = [
            Button((w//2-320, h-120, 200, 50), "2 JOGADORES", lambda: self._set(2), self.f),
            Button((w//2-100, h-120, 200, 50), "3 JOGADORES", lambda: self._set(3), self.f),
            Button((w//2+120, h-120, 200, 50), "4 JOGADORES", lambda: self._set(4), self.f),
            Button((w//2-260, h-50, 220, 44), "INICIAR", self._start, self.f),
            Button((w//2+40, h-50, 220, 44), "VOLTAR", lambda: self.game.change_state(GameState.MAIN_MENU), self.f),
        ]

    def _set(self, n): 
        self.num_players = n
        if self.active_input >= n: self.active_input = 0

    def _start(self): 
        self.game.game_manager.start_new_game(self.num_players, self.nomes)

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN: self._start()
            elif e.key == pygame.K_ESCAPE: self.game.change_state(GameState.MAIN_MENU)
            elif e.key == pygame.K_TAB: self.active_input = (self.active_input + 1) % self.num_players
            elif e.key == pygame.K_BACKSPACE:
                if self.active_input < len(self.nomes):
                    self.nomes[self.active_input] = self.nomes[self.active_input][:-1]
            elif e.key == pygame.K_2: self._set(2)
            elif e.key == pygame.K_3: self._set(3)
            elif e.key == pygame.K_4: self._set(4)
            else:
                if self.active_input < len(self.nomes):
                    char = e.unicode
                    if char.isprintable() and len(self.nomes[self.active_input]) < 12:
                        self.nomes[self.active_input] += char

    def update(self, pos):
        for b in self.buttons: b.update(pos)

    def draw(self):
        self.screen.fill((18, 14, 10))
        w, h = self.screen.get_size()
        t = self.ft.render("SELECIONE OS JOGADORES", True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, 60)))
        
        for i in range(self.num_players):
            c = settings.PLAYER_COLORS[i]
            ch = tuple(int(x*255) for x in c)
            cx = w//2 - (self.num_players-1)*100 + i*200
            pygame.draw.circle(self.screen, ch, (cx, 160), 30)
            
            rect = pygame.Rect(cx - 90, 210, 180, 40)
            cor_borda = (255, 255, 255) if i == self.active_input else (100, 100, 100)
            pygame.draw.rect(self.screen, (30, 30, 30), rect)
            pygame.draw.rect(self.screen, cor_borda, rect, 2)
            
            nome_render = self.f.render(self.nomes[i], True, (255, 255, 255))
            self.screen.blit(nome_render, nome_render.get_rect(center=rect.center))
            
            if i == self.active_input:
                pygame.draw.polygon(self.screen, (255, 210, 100), [(cx, 260), (cx-10, 270), (cx+10, 270)])

        info = self.fs.render("Clique na caixa ou use TAB para alternar. Digite o nome.", True, (200, 200, 200))
        self.screen.blit(info, info.get_rect(center=(w//2, 310)))

        info2 = self.f.render(f"Total: {self.num_players} jogadores", True, (230, 220, 200))
        self.screen.blit(info2, info2.get_rect(center=(w//2, 360)))
        
        cells = settings.BOARD_ROWS * settings.BOARD_COLS
        mp = cells // self.num_players
        d = self.fs.render(
            f"Tabuleiro {settings.BOARD_ROWS}x{settings.BOARD_COLS} = {cells} celulas | {mp} jogadas por jogador",
            True, (200, 190, 170))
        self.screen.blit(d, d.get_rect(center=(w//2, 400)))
        
        for b in self.buttons: b.draw(self.screen)
""")

w("ui/pause_menu.py", """
import pygame
from ui.button import Button
from core.game_state import GameState

class PauseMenu:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.f = pygame.font.SysFont("arial", 24)
        self.ft = pygame.font.SysFont("arial", 44, bold=True)
        self.buttons = []
        self._build()

    def _build(self):
        w, h = self.screen.get_size()
        bw, bh = 340, 52
        cy = h//2 - 100
        self.buttons = [
            Button((w//2-bw//2, cy, bw, bh), "CONTINUAR",
                   lambda: self.game.change_state(GameState.PLAYING), self.f),
            Button((w//2-bw//2, cy+70, bw, bh), "REINICIAR",
                   lambda: self.game.game_manager.start_new_game(), self.f),
            Button((w//2-bw//2, cy+140, bw, bh), "MENU PRINCIPAL",
                   lambda: self.game.change_state(GameState.MAIN_MENU), self.f),
            Button((w//2-bw//2, cy+210, bw, bh), "SAIR DO JOGO",
                   lambda: setattr(self.game, "running", False), self.f),
        ]

    def handle_event(self, e):
        for b in self.buttons: b.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.game.change_state(GameState.PLAYING)

    def update(self, pos):
        for b in self.buttons: b.update(pos)

    def draw(self):
        w, h = self.screen.get_size()
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        t = self.ft.render("PAUSADO", True, (255, 210, 100))
        self.screen.blit(t, t.get_rect(center=(w//2, h//2 - 180)))
        for b in self.buttons: b.draw(self.screen)
""")

w("main.py", """
from core.game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
""")

print("=== RESTAURACAO CONCLUIDA ===")
print("Agora rode: python main.py")