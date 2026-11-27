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
