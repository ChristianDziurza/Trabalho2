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
