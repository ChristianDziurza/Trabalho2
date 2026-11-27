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
        if self.active_input >= n: 
            self.active_input = 0

    def _start(self): 
        self.game.game_manager.start_new_game(self.num_players, self.nomes)

    def handle_event(self, e):
        for b in self.buttons: 
            b.handle_event(e)
            
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            w, h = self.screen.get_size()
            for i in range(self.num_players):
                cx = w//2 - (self.num_players-1)*100 + i*200
                rect = pygame.Rect(cx - 90, 210, 180, 40)
                if rect.collidepoint(e.pos):
                    self.active_input = i

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN: 
                self._start()
            elif e.key == pygame.K_ESCAPE: 
                self.game.change_state(GameState.MAIN_MENU)
            elif e.key == pygame.K_TAB: 
                self.active_input = (self.active_input + 1) % self.num_players
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
        for b in self.buttons: 
            b.update(pos)

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
        
        for b in self.buttons: 
            b.draw(self.screen)