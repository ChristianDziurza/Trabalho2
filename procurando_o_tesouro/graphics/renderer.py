from __future__ import annotations
import math
import numpy as np
from OpenGL.GL import (
    glEnable, glClearColor, glClear, glViewport, glDrawArrays,
    glBindVertexArray, glBlendFunc, glDepthFunc, glCullFace, glFrontFace, glDisable,
    GL_DEPTH_TEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_LESS,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TRIANGLES,
    GL_CULL_FACE, GL_CW, GL_CCW
)
from config.settings import settings
from graphics.shader import Shader
from graphics.lighting import Lighting, PointLight
from graphics.primitives import (
    make_cube, make_plane, make_pyramid, make_octahedron,
    make_cylinder, make_sphere,
)
from graphics.particle_system import ParticleSystem
from entities.tile import TileState, TileContent
from entities.trap import TrapType

VS = '''
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec2 aUV;
uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProj;
out vec3 vWorldPos;
out vec3 vNormal;
out vec2 vUV;
void main() {
    vec4 world = uModel * vec4(aPos, 1.0);
    vWorldPos = world.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    vUV = aUV;
    gl_Position = uProj * uView * world;
}
'''

FS = '''
#version 330 core
in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vUV;
uniform vec3 uAmbient;
uniform vec3 uDirDir;
uniform vec3 uDirColor;
struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
    float radius;
};
uniform int uNumLights;
uniform PointLight uPointLights[8];
uniform vec3 uTint;
uniform vec3 uEmissive;
uniform float uAlpha;
uniform sampler2D uTex;
uniform int uUseTexture;
uniform vec2 uTexScale;
out vec4 fragColor;
void main() {
    vec3 baseColor = uTint;
    if (uUseTexture == 1) {
        baseColor *= texture(uTex, vUV * uTexScale).rgb;
    }
    vec3 N = normalize(vNormal);
    vec3 lighting = uAmbient;
    vec3 L = normalize(-uDirDir);
    float d = max(dot(N, L), 0.0);
    lighting += uDirColor * d;
    for (int i = 0; i < uNumLights; i++) {
        vec3 lp = uPointLights[i].position - vWorldPos;
        float dist = length(lp);
        float att = clamp(1.0 - dist / uPointLights[i].radius, 0.0, 1.0);
        att *= att;
        vec3 Lp = normalize(lp);
        float diff = max(dot(N, Lp), 0.0);
        lighting += uPointLights[i].color * uPointLights[i].intensity * diff * att;
    }
    vec3 color = baseColor * lighting + uEmissive;
    fragColor = vec4(color, uAlpha);
}
'''

def translation(x, y, z):
    m = np.identity(4, dtype=np.float32)
    m[0, 3] = x; m[1, 3] = y; m[2, 3] = z
    return m

def scale_m(sx, sy, sz):
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = sx; m[1, 1] = sy; m[2, 2] = sz
    return m

def rotation_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c; m[0, 2] = s
    m[2, 0] = -s; m[2, 2] = c
    return m

class Renderer:
    def __init__(self, camera, textures):
        self.camera = camera
        self.textures = textures
        self.shader = Shader(VS, FS)
        self.lighting = Lighting()
        self.particles = ParticleSystem()
        self.time = 0.0
        self.mesh_cube = make_cube(1.0)
        self.mesh_plane = make_plane(1.0)
        self.mesh_pyramid = make_pyramid(1.0, 1.4)
        self.mesh_diamond = make_octahedron(1.0, 1.6)
        self.mesh_cylinder = make_cylinder(0.5, 1.0, 12)
        self.mesh_sphere = make_sphere(0.5, 12, 8)
        
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.02, 0.02, 0.04, 1.0)

    def resize(self, w, h):
        glViewport(0, 0, w, h)
        self.camera.aspect = w / max(1, h)

    def _draw(self, mesh, model, tint=(1,1,1), emissive=(0,0,0), texture_name=None, alpha=1.0, tex_scale=(1.0, 1.0)):
        self.shader.set_mat4("uModel", model.T)
        self.shader.set_vec3("uTint", tint)
        self.shader.set_vec3("uEmissive", emissive)
        self.shader.set_float("uAlpha", alpha)
        self.shader.set_vec2("uTexScale", tex_scale)
        if texture_name:
            self.shader.set_int("uUseTexture", 1)
            self.shader.set_int("uTex", 0)
            self.textures.bind(texture_name)
        else:
            self.shader.set_int("uUseTexture", 0)
        glBindVertexArray(mesh["vao"])
        glDrawArrays(GL_TRIANGLES, 0, mesh["count"])
        glBindVertexArray(0)

    def begin_frame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        self.shader.set_mat4("uView", self.camera.view_matrix().T)
        self.shader.set_mat4("uProj", self.camera.projection_matrix().T)

    def upload_lights(self, state):
        self.lighting.clear()
        for pos, color in [
            ((-6, 4, -6), (1.0, 0.65, 0.3)),
            (( 6, 4, -6), (1.0, 0.65, 0.3)),
            ((-6, 4,  6), (1.0, 0.65, 0.3)),
            (( 6, 4,  6), (1.0, 0.65, 0.3)),
        ]:
            flicker = 0.9 + 0.2 * math.sin(self.time * 8.0 + pos[0])
            self.lighting.add_light(PointLight(pos, color, flicker, 10.0))
        player = state.current_player
        if player:
            pos = (player.visual_x, 1.2, player.visual_z)
            self.lighting.add_light(PointLight(pos, (1.0, 0.9, 0.6), 1.2, 5.0))
        self.lighting.upload(self.shader)

    def draw_scene(self, state):
        self.time += 0.016
        self.upload_lights(state)
        
        ground = translation(0, -0.05, 0) @ scale_m(50, 1, 50)
        self._draw(self.mesh_plane, ground, tint=(0.3,0.25,0.2), texture_name="dirt", tex_scale=(25, 25))
        
        self._draw_skybox(state)
        self._draw_walls(state)
        self._draw_board(state)
        self._draw_players(state)
        self._draw_particles()

    def _draw_skybox(self, state):
        size = 40.0
        m = translation(0, 15, 0) @ scale_m(size, size, size)
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        self._draw(self.mesh_cube, m, tint=(0.1,0.1,0.15), texture_name="rock", tex_scale=(10, 10))
        glFrontFace(GL_CCW)
        glDisable(GL_CULL_FACE)

    def _cell_world_pos(self, row, col, rows, cols):
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        return (col - (cols-1)/2.0) * sx, (row - (rows-1)/2.0) * sx

    def _draw_walls(self, state):
        rows = state.mine.board.rows
        cols = state.mine.board.cols
        sx = settings.TILE_SIZE + settings.TILE_SPACING
        ex = cols * sx / 2 + 1.5
        ez = rows * sx / 2 + 1.5
        h = 7.0
        
        for (px, pz, sxx, szz) in [
            (0, -ez, ex*2, 0.6),
            (0, ez, ex*2, 0.6),
            (-ex, 0, 0.6, ez*2),
            (ex, 0, 0.6, ez*2),
        ]:
            m = translation(px, h/2, pz) @ scale_m(sxx, h, szz)
            escala_u = max(sxx, szz) * 0.5
            escala_v = h * 0.5
            self._draw(self.mesh_cube, m, tint=(0.3,0.28,0.25), texture_name="rock", tex_scale=(escala_u, escala_v))

        for (px, pz) in [(-ex+1.5, -ez+2), (ex-2, ez-1.5), (-ex+2, ez-1.5)]:
            m = translation(px, 0.5, pz) @ scale_m(1.0, 1.0, 1.0)
            self._draw(self.mesh_cube, m, tint=(0.6,0.4,0.2), texture_name="wood")
            m = translation(px, 1.0, pz) @ scale_m(1.05, 0.1, 1.05)
            self._draw(self.mesh_cube, m, tint=(0.4,0.4,0.4), texture_name="stone")
        
        for (px, pz, color) in [
            (-ex+1, -ez+1, (0.3,0.7,1.0)),
            (ex-1, -ez+1, (0.4,0.9,0.5)),
            (-ex+1, ez-1, (1.0,0.5,0.8)),
            (ex-1, ez-1, (0.9,0.9,0.4)),
        ]:
            glow = 0.6 + 0.4 * math.sin(self.time * 2 + px)
            m = translation(px, 1.5, pz) @ scale_m(0.6, 2.0, 0.6)
            self._draw(self.mesh_diamond, m, tint=color,
                       emissive=(color[0]*0.5*glow, color[1]*0.5*glow, color[2]*0.5*glow))

    def _draw_board(self, state):
        board = state.mine.board
        for r in range(board.rows):
            for c in range(board.cols):
                tile = board.get(r, c)
                x, z = self._cell_world_pos(r, c, board.rows, board.cols)
                self._draw_tile(tile, x, z, state)

    def _draw_tile(self, tile, x, z, state):
        if tile.state == TileState.HIDDEN:
            tex = "stone"; tint = (0.55, 0.5, 0.45)
        else:
            tex = "revealed"; tint = (0.85, 0.78, 0.65)
        m = translation(x, 0, z) @ scale_m(settings.TILE_SIZE, settings.TILE_HEIGHT, settings.TILE_SIZE)
        self._draw(self.mesh_cube, m, tint=tint, texture_name=tex)
        
        if tile.discovered_by is not None:
            color = settings.PLAYER_COLORS[tile.discovered_by % 4]
            marker = translation(x, settings.TILE_HEIGHT + 0.01, z) @ scale_m(settings.TILE_SIZE*0.9, 0.02, settings.TILE_SIZE*0.9)
            self._draw(self.mesh_cube, marker, tint=color,
                       emissive=(color[0]*0.3, color[1]*0.3, color[2]*0.3))
                       
        if tile.state == TileState.REVEALED:
            if tile.content == TileContent.DIAMOND and not tile.item.collected:
                self._draw_diamond(tile.item, x, z)
            elif tile.content == TileContent.TRAP:
                self._draw_trap(tile.item, x, z)
            elif tile.content == TileContent.CLUE:
                self._draw_clue(tile.item, x, z)
        elif tile.state == TileState.HIDDEN:
            bs = 0.25
            m = translation(x, settings.TILE_HEIGHT, z) @ scale_m(bs, bs*0.6, bs)
            self._draw(self.mesh_sphere, m, tint=(0.45,0.4,0.38))

    def _draw_diamond(self, diamond, x, z):
        s = diamond.scale
        bob = 0.05 * math.sin(self.time * 3 + x)
        y = settings.TILE_HEIGHT + 0.4 + bob
        m = translation(x, y, z) @ rotation_y(self.time * 40) @ scale_m(s, s, s)
        c = diamond.color
        self._draw(self.mesh_diamond, m, tint=c,
                   emissive=(c[0]*0.5, c[1]*0.5, c[2]*0.6), texture_name="crystal")

    def _draw_trap(self, trap, x, z):
        if trap.type == TrapType.DEAD_END:
            m = translation(x, settings.TILE_HEIGHT*0.5, z) @ scale_m(0.9, 0.5, 0.9)
            self._draw(self.mesh_cylinder, m, tint=(0.25,0.05,0.05),
                       texture_name="rock", emissive=(0.4,0.05,0.05))
            m2 = translation(x, settings.TILE_HEIGHT, z) @ scale_m(1.0, 0.1, 1.0)
            self._draw(self.mesh_cylinder, m2, tint=(0.7,0.2,0.1), emissive=(0.5,0.1,0.05))
        else:
            m = translation(x, settings.TILE_HEIGHT, z) @ scale_m(1.2, 1.0, 1.2)
            self._draw(self.mesh_sphere, m, tint=(0.15,0.15,0.2),
                       texture_name="rock", emissive=(0.05,0.05,0.1))

    def _draw_clue(self, clue, x, z):
        bob = 0.05 * math.sin(self.time * 3 + x)
        m = translation(x, settings.TILE_HEIGHT + 0.35 + bob, z) @ rotation_y(self.time * 30) @ scale_m(0.6, 0.6, 0.6)
        self._draw(self.mesh_diamond, m, tint=(0.3,1.0,0.4),
                   emissive=(0.3,0.8,0.3), texture_name="crystal")

    def _draw_players(self, state):
        for p in state.players:
            alpha = 0.25 if p.invisible else 1.0
            x, z = p.visual_x, p.visual_z
            bob = 0.05 * math.sin(self.time * 4 + p.id)
            
            m = translation(x, 0.35 + bob, z) @ scale_m(0.35, 0.5, 0.35)
            self._draw(self.mesh_cylinder, m, tint=p.color, alpha=alpha)
            m = translation(x, 0.8 + bob, z) @ scale_m(0.35, 0.35, 0.35)
            self._draw(self.mesh_sphere, m, tint=(0.95,0.85,0.7), alpha=alpha)
            m = translation(x, 0.95 + bob, z) @ scale_m(0.4, 0.35, 0.4)
            self._draw(self.mesh_pyramid, m, tint=(0.9,0.7,0.2), alpha=alpha)
            m = translation(x, 0.7 + bob, z) @ scale_m(0.12,0.12,0.12)
            self._draw(self.mesh_sphere, m, tint=(1.0,0.95,0.7),
                       emissive=(1.0,0.9,0.5), alpha=alpha)

    def _draw_particles(self):
        for p in self.particles.particles:
            t = p.life / max(0.001, p.max_life)
            s = p.size * t
            m = translation(p.x, p.y, p.z) @ scale_m(s, s, s)
            self._draw(self.mesh_cube, m, tint=(p.r, p.g, p.b),
                       emissive=(p.r*p.life*0.5, p.g*p.life*0.5, p.b*p.life*0.5))