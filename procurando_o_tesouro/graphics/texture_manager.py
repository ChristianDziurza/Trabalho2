import os
import numpy as np
from PIL import Image
from OpenGL.GL import *


class TextureManager:
    def __init__(self):
        self.textures = {}
        self._defaults()

    def _upload(self, name, image):
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        img_data = np.array(image, dtype=np.uint8)
        img_data = np.flipud(img_data)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, img_data
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        self.textures[name] = tex_id

    def load_from_file(self, name, filepath, fallback=None):
        if os.path.exists(filepath):
            self._upload(name, Image.open(filepath))
        elif fallback is not None:
            self._upload(name, fallback())
        else:
            self._upload(name, self._make_solid((180, 180, 180)))

    def bind(self, name):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.get(name))

    def get(self, name):
        return self.textures.get(name, self.textures.get("white"))

    def _make_noise(self, size, base_color, variation):
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        for i in range(size):
            for j in range(size):
                r = max(0, min(255, base_color[0] + np.random.randint(-variation, variation)))
                g = max(0, min(255, base_color[1] + np.random.randint(-variation, variation)))
                b = max(0, min(255, base_color[2] + np.random.randint(-variation, variation)))
                arr[i, j] = (r, g, b, 255)
        return Image.fromarray(arr, "RGBA")

    def _make_solid(self, color, size=64):
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        arr[:, :, 0] = color[0]
        arr[:, :, 1] = color[1]
        arr[:, :, 2] = color[2]
        arr[:, :, 3] = 255
        return Image.fromarray(arr, "RGBA")

    def _make_crystal(self, size=64):
        arr = np.zeros((size, size, 4), dtype=np.uint8)
        c = size // 2
        for i in range(size):
            for j in range(size):
                d = abs(i - c) + abs(j - c)
                if d < size * 0.45:
                    v = max(0, 255 - d * 5)
                    arr[i, j] = (min(255, 120 + v), min(255, 200 + v), 255, 255)
                else:
                    arr[i, j] = (30, 50, 80, 255)
        return Image.fromarray(arr, "RGBA")

    def _defaults(self):
        self._upload("white", Image.new("RGBA", (1, 1), (255, 255, 255, 255)))
        base = "assets/textures/"
        self.load_from_file("dirt",     base + "dirt.png",     lambda: self._make_noise(64, (110,  80,  50), 25))
        self.load_from_file("rock",     base + "rock.png",     lambda: self._make_noise(64, ( 90,  85,  80), 30))
        self.load_from_file("wood",     base + "wood.png",     lambda: self._make_noise(64, (140,  95,  50), 20))
        self.load_from_file("stone",    base + "stone.png",    lambda: self._make_noise(64, (140, 135, 125), 25))
        self.load_from_file("revealed", base + "revealed.png", lambda: self._make_noise(64, (200, 185, 155), 20))
        self.load_from_file("crystal",  base + "crystal.png",  self._make_crystal)