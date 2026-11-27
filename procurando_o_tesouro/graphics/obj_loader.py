import logging
logging.getLogger('pywavefront').setLevel(logging.ERROR)

import ctypes
import numpy as np
from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray, glGenBuffers, glBindBuffer,
    glBufferData, glVertexAttribPointer, glEnableVertexAttribArray,
    GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
)
from pywavefront import Wavefront

def carregar_obj(caminho):
    try:
        scene = Wavefront(caminho, collect_faces=True)
    except Exception as e:
        print(f"Erro ao carregar modelo {caminho}: {e}")
        return None

    vertices = np.array(scene.vertices, dtype=np.float32)
    if len(vertices) == 0:
        return None

    centro = (vertices.max(axis=0) + vertices.min(axis=0)) / 2.0
    vertices -= centro

    max_dim = np.max(np.abs(vertices))
    if max_dim > 0:
        vertices /= max_dim

    dados = []
    for name, mesh in scene.meshes.items():
        for face in mesh.faces:
            for v_idx in face:
                v = vertices[v_idx]
                dados.extend([v[0], v[1], v[2], 0.0, 1.0, 0.0, 0.0, 0.0])

    dados = np.array(dados, dtype=np.float32)
    
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, dados.nbytes, dados, GL_STATIC_DRAW)
    
    stride = 8 * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, False, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)
    glBindVertexArray(0)
    
    return {"vao": vao, "vbo": vbo, "count": len(dados) // 8}