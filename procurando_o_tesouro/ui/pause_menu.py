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
