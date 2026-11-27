from __future__ import annotations
import ctypes
import pygame
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import (
    glClearColor, glClear, glGenTextures, glBindTexture, glTexImage2D,
    glTexParameteri, glEnable, glDisable, glBlendFunc, glUseProgram,
    glGenVertexArrays, glBindVertexArray, glGenBuffers, glBindBuffer,
    glBufferData, glEnableVertexAttribArray, glVertexAttribPointer,
    glDrawArrays, glDeleteTextures, glActiveTexture,
    GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE, GL_BLEND, GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA, GL_LINEAR, GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER, GL_DEPTH_TEST, GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT, GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
    GL_TRIANGLES, GL_TEXTURE0,
)
from config.settings import settings
from core.game_state import GameState
from core.event_manager import EventManager
from core.game_manager import GameManager
from graphics.camera import Camera
from graphics.renderer import Renderer
from graphics.texture_manager import TextureManager
from graphics.effects import EffectsManager
from graphics.shader import Shader
from ui.menu import MainMenu
from ui.player_selection import PlayerSelection
from ui.hud import HUD
from ui.scoreboard import GameOverScreen
from ui.settings_menu import SettingsMenu
from ui.pause_menu import PauseMenu

OVERLAY_VS = '''
#version 330 core
layout(location=0) in vec2 aPos;
layout(location=1) in vec2 aUV;
out vec2 vUV;
void main() {
    vUV = aUV;
    gl_Position = vec4(aPos, 0.0, 1.0);
}
'''

OVERLAY_FS = '''
#version 330 core
in vec2 vUV;
uniform sampler2D uTex;
out vec4 fragColor;
void main() {
    fragColor = texture(uTex, vUV);
}
'''

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                         pygame.GL_CONTEXT_PROFILE_CORE)
        self.screen = pygame.display.set_mode(
            (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL)
        pygame.display.set_caption(settings.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        self.show_records = False

        self.camera = Camera()
        self.textures = TextureManager()
        self.renderer = Renderer(self.camera, self.textures)
        self.effects = EffectsManager()
        self.events = EventManager()

        self.ui_screen = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        self.game_manager = GameManager(self)
        self.save_system = self.game_manager.save_system

        self.main_menu = MainMenu(self.ui_screen, self)
        self.player_selection = PlayerSelection(self.ui_screen, self)
        self.hud = HUD(self.ui_screen)
        self.game_over = GameOverScreen(self.ui_screen, self)
        self.settings_menu = SettingsMenu(self.ui_screen, self)
        self.pause_menu = PauseMenu(self.ui_screen, self)

        self._init_overlay()

    def _init_overlay(self):
        self._overlay_shader = Shader(OVERLAY_VS, OVERLAY_FS)
        verts = np.array([
            -1, -1, 0, 0,
             1, -1, 1, 0,
             1,  1, 1, 1,
            -1, -1, 0, 0,
             1,  1, 1, 1,
            -1,  1, 0, 1,
        ], dtype=np.float32)
        self._overlay_vao = glGenVertexArrays(1)
        glBindVertexArray(self._overlay_vao)
        self._overlay_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._overlay_vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        stride = 4 * 4
        glVertexAttribPointer(0, 2, GL_FLOAT, False, stride, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, stride, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

    def change_state(self, state):
        self.state = state

    def _handle_events(self):
        events = self.events.pump()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
                return
            if self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(e)
            elif self.state == GameState.PLAYER_SELECTION:
                self.player_selection.handle_event(e)
            elif self.state == GameState.SETTINGS:
                self.settings_menu.handle_event(e)
            elif self.state == GameState.PLAYING:
                self._handle_play_event(e)
            elif self.state == GameState.PAUSED:
                self.pause_menu.handle_event(e)
            elif self.state == GameState.GAME_OVER:
                self.game_over.handle_event(e)

    def _handle_play_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.change_state(GameState.PAUSED)
                return
            if e.key == pygame.K_r:
                self.camera.reset()
                return
            if e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if e.key == pygame.K_UP: dr, dc = -1, 0
                elif e.key == pygame.K_DOWN: dr, dc = 1, 0
                elif e.key == pygame.K_LEFT: dr, dc = 0, -1
                else: dr, dc = 0, 1
                self.game_manager.try_player_move(dr, dc)

    def _update(self, dt):
        self.events.update_keys()
        dx, dy = self.events.mouse_delta
        if dx or dy:
            self.camera.rotate(-dx, dy)
        if self.events.scroll_delta:
            self.camera.zoom(self.events.scroll_delta)
            
        k = self.events.keys_pressed
        if pygame.K_w in k: self.camera.pan(0, -1)
        if pygame.K_s in k: self.camera.pan(0, 1)
        if pygame.K_a in k: self.camera.pan(-1, 0)
        if pygame.K_d in k: self.camera.pan(1, 0)

        self.effects.update(dt)

        if self.state == GameState.PLAYING:
            self.game_manager.update(dt)
            self.hud.update(dt)
            self.renderer.particles.update(dt)
        elif self.state == GameState.MAIN_MENU:
            self.main_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.PLAYER_SELECTION:
            self.player_selection.update(pygame.mouse.get_pos())
        elif self.state == GameState.SETTINGS:
            self.settings_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.PAUSED:
            self.pause_menu.update(pygame.mouse.get_pos())
        elif self.state == GameState.GAME_OVER:
            self.game_over.update(pygame.mouse.get_pos())

    def _draw(self):
        if self.state in (GameState.PLAYING, GameState.PAUSED):
            self.renderer.begin_frame()
            s = self.game_manager.session
            if s: self.renderer.draw_scene(s)
            self._hud_overlay()
            if self.state == GameState.PAUSED:
                self.pause_menu.draw()
                self._blit_surface(self.ui_screen)
        else:
            self._render_2d()
        pygame.display.flip()

    def _hud_overlay(self):
        surf = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        old = self.hud.screen
        self.hud.screen = surf
        if self.game_manager.session:
            self.hud.draw(self.game_manager.session)
        self.hud.screen = old
        self._blit_surface(surf)

    def _render_2d(self):
        glClearColor(0.05, 0.04, 0.03, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.state == GameState.MAIN_MENU: self.main_menu.draw()
        elif self.state == GameState.PLAYER_SELECTION: self.player_selection.draw()
        elif self.state == GameState.SETTINGS: self.settings_menu.draw()
        elif self.state == GameState.GAME_OVER: self.game_over.draw()
        self._blit_surface(self.ui_screen)

    def _blit_surface(self, surf):
        data = pygame.image.tostring(surf, "RGBA", True)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surf.get_width(), surf.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glUseProgram(self._overlay_shader.program)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex)
        self._overlay_shader.set_int("uTex", 0)
        glBindVertexArray(self._overlay_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)
        glUseProgram(0)
        glEnable(GL_DEPTH_TEST)
        glDeleteTextures([tex])

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events()
            if not self.running: break
            self._update(dt)
            self._draw()
        pygame.quit()
