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
