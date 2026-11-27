from __future__ import annotations
import random
import numpy as np
from PIL import Image
from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexImage2D, glTexParameteri,
    GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_REPEAT,
)

class TextureManager:
    def __init__(self):
        self.textures = {}
        self._defaults()

    def _upload(self, name, image):
        image = image.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
        data = image.tobytes()
        w, h = image.size
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        self.textures[name] = tex

    def _noise(self, size, base, amp, rng):
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                n = rng.randint(-amp, amp)
                arr[y, x] = [max(0, min(255, base[0]+n)),
                             max(0, min(255, base[1]+n)),
                             max(0, min(255, base[2]+n))]
        return Image.fromarray(arr, "RGB")

    def _wood(self, size, rng):
        arr = np.zeros((size, size, 3), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                stripe = int(20 * np.sin(x * 0.5 + rng.uniform(-0.3, 0.3)))
                arr[y, x] = [max(0, min(255, 120 + stripe)),
                             max(0, min(255, 80 + stripe)),
                             max(0, min(255, 40 + stripe))]
        return Image.fromarray(arr, "RGB")

    def _defaults(self):
        rng = random.Random(42)
        self._upload("stone", self._noise(128, (90, 85, 80), 30, rng))
        self._upload("dirt", self._noise(128, (60, 45, 35), 25, rng))
        self._upload("rock", self._noise(128, (50, 50, 55), 35, rng))
        self._upload("revealed", self._noise(128, (110, 95, 70), 20, rng))
        self._upload("crystal", self._noise(64, (80, 180, 220), 40, rng))
        self._upload("wood", self._wood(128, rng))

    def bind(self, name):
        tex = self.textures.get(name)
        if tex is None: tex = self.textures.get("stone", 0)
        glBindTexture(GL_TEXTURE_2D, tex)
        return tex
