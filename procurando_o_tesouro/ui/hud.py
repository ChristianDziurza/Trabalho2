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
