from __future__ import annotations
from dataclasses import dataclass
from config.settings import settings

@dataclass
class PointLight:
    position: tuple
    color: tuple
    intensity: float = 1.0
    radius: float = 6.0

class Lighting:
    def __init__(self):
        self.ambient = settings.AMBIENT_COLOR
        self.dir_dir = settings.DIRECTIONAL_DIR
        self.dir_color = settings.DIRECTIONAL_COLOR
        self.lights = []

    def add_light(self, l):
        self.lights.append(l)

    def clear(self):
        self.lights.clear()

    def upload(self, shader):
        shader.set_vec3("uAmbient", self.ambient)
        shader.set_vec3("uDirDir", self.dir_dir)
        shader.set_vec3("uDirColor", self.dir_color)
        n = min(len(self.lights), 8)
        shader.set_int("uNumLights", n)
        for i in range(n):
            l = self.lights[i]
            shader.set_vec3(f"uPointLights[{i}].position", l.position)
            shader.set_vec3(f"uPointLights[{i}].color", l.color)
            shader.set_float(f"uPointLights[{i}].intensity", l.intensity)
            shader.set_float(f"uPointLights[{i}].radius", l.radius)
