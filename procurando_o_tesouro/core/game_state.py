from enum import Enum

class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYER_SELECTION = "player_selection"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
