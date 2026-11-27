from __future__ import annotations
from OpenGL.GL import (
    glCreateShader, glShaderSource, glCompileShader, glGetShaderiv,
    glGetShaderInfoLog, glCreateProgram, glAttachShader, glLinkProgram,
    glGetProgramiv, glGetProgramInfoLog, glDeleteShader, glUseProgram,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_COMPILE_STATUS, GL_LINK_STATUS,
    glGetUniformLocation, glUniformMatrix4fv, glUniform3f, glUniform1f,
    glUniform1i, glUniform2f, GL_FALSE,
)
import numpy as np

class Shader:
    def __init__(self, vs, fs):
        self.program = self._compile(vs, fs)
        self._cache = {}

    def _compile(self, vs, fs):
        prog = glCreateProgram()
        v = self._one(vs, GL_VERTEX_SHADER)
        f = self._one(fs, GL_FRAGMENT_SHADER)
        glAttachShader(prog, v)
        glAttachShader(prog, f)
        glLinkProgram(prog)
        if not glGetProgramiv(prog, GL_LINK_STATUS):
            raise RuntimeError("Link shader falhou")
        glDeleteShader(v)
        glDeleteShader(f)
        return prog

    def _one(self, src, kind):
        sid = glCreateShader(kind)
        glShaderSource(sid, src)
        glCompileShader(sid)
        if not glGetShaderiv(sid, GL_COMPILE_STATUS):
            raise RuntimeError("Compile shader falhou")
        return sid

    def use(self):
        glUseProgram(self.program)

    def _loc(self, name):
        if name not in self._cache:
            self._cache[name] = glGetUniformLocation(self.program, name)
        return self._cache[name]

    def set_mat4(self, name, mat):
        glUniformMatrix4fv(self._loc(name), 1, GL_FALSE, np.asarray(mat, dtype=np.float32).flatten())

    def set_vec3(self, name, v):
        glUniform3f(self._loc(name), float(v[0]), float(v[1]), float(v[2]))

    def set_vec2(self, name, v):
        glUniform2f(self._loc(name), float(v[0]), float(v[1]))

    def set_float(self, name, v):
        glUniform1f(self._loc(name), float(v))

    def set_int(self, name, v):
        glUniform1i(self._loc(name), int(v))
