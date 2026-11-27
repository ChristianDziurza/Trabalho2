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
    CAMERA_FOV = 45.0
    CAMERA_NEAR = 0.1
    CAMERA_FAR = 200.0
    CAMERA_MIN_DISTANCE = 4.0
    CAMERA_MAX_DISTANCE = 12.0
    CAMERA_MIN_PITCH = 15.0
    CAMERA_MAX_PITCH = 80.0
    CAMERA_INITIAL_YAW = 45.0
    CAMERA_INITIAL_PITCH = 55.0
    CAMERA_INITIAL_DISTANCE = 8.0
    CAMERA_ROTATE_SPEED = 0.35
    CAMERA_ZOOM_SPEED = 1.0
    CAMERA_PAN_SPEED = 6.0
    AMBIENT_COLOR = (0.25, 0.25, 0.35)
    DIRECTIONAL_DIR = (-0.3, -1.0, -0.4)
    DIRECTIONAL_COLOR = (0.5, 0.5, 0.6)
    AUDIO_VOLUME = 0.6
    PLAYER_MOVE_DURATION = 0.25
    PARTICLES_ENABLED = True
    MAX_PARTICLES = 800
    RECORDS_FILE = "saves/records.json"

settings = Settings()