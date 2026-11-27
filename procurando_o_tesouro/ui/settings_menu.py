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
