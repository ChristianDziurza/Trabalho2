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
