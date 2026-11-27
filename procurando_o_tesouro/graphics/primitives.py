from __future__ import annotations
import ctypes
import math
import numpy as np
from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray, glGenBuffers, glBindBuffer,
    glBufferData, glVertexAttribPointer, glEnableVertexAttribArray,
    GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_FLOAT,
)

def _v(off): return ctypes.c_void_p(off)

def _pack(vs, ns, ts):
    data = []
    for i in range(len(vs)):
        v = vs[i]; n = ns[i]; t = ts[i]
        data.extend([v[0], v[1], v[2], n[0], n[1], n[2], t[0], t[1]])
    return np.array(data, dtype=np.float32)

def _mesh(vs, ns, ts):
    data = _pack(vs, ns, ts)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
    stride = 32
    glVertexAttribPointer(0, 3, GL_FLOAT, False, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, False, stride, _v(12))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 2, GL_FLOAT, False, stride, _v(24))
    glEnableVertexAttribArray(2)
    glBindVertexArray(0)
    return {"vao": vao, "vbo": vbo, "count": len(vs)}

def make_cube(size=1.0):
    s = size / 2.0
    vs, ns, ts = [], [], []
    faces = [
        ((0,0,1), [(-s,-s,s),(s,-s,s),(s,s,s),(-s,-s,s),(s,s,s),(-s,s,s)]),
        ((0,0,-1),[(-s,-s,-s),(-s,s,-s),(s,s,-s),(-s,-s,-s),(s,s,-s),(s,-s,-s)]),
        ((1,0,0), [(s,-s,-s),(s,s,-s),(s,s,s),(s,-s,-s),(s,s,s),(s,-s,s)]),
        ((-1,0,0),[(-s,-s,-s),(-s,-s,s),(-s,s,s),(-s,-s,-s),(-s,s,s),(-s,s,-s)]),
        ((0,1,0), [(-s,s,-s),(-s,s,s),(s,s,s),(-s,s,-s),(s,s,s),(s,s,-s)]),
        ((0,-1,0),[(-s,-s,-s),(s,-s,-s),(s,-s,s),(-s,-s,-s),(s,-s,s),(-s,-s,s)]),
    ]
    for n, vv in faces:
        for v in vv:
            vs.append(v); ns.append(n); ts.append((v[0]+s, v[2]+s))
    return _mesh(vs, ns, ts)

def make_plane(size=1.0):
    s = size / 2.0
    vs = [(-s,0,-s),(s,0,-s),(s,0,s),(-s,0,-s),(s,0,s),(-s,0,s)]
    ns = [(0,1,0)]*6
    ts = [(0,0),(1,0),(1,1),(0,0),(1,1),(0,1)]
    return _mesh(vs, ns, ts)

def make_pyramid(base=1.0, height=1.5):
    b = base / 2.0
    top = (0, height, 0)
    c = [(-b,0,-b),(b,0,-b),(b,0,b),(-b,0,b)]
    vs, ns, ts = [], [], []
    def tri(a, b_, cc, n):
        for v in (a, b_, cc): vs.append(v); ns.append(n)
        ts.extend([(0,0),(1,0),(0.5,1)])
    tri(c[0], c[1], top, (0,0.6,-0.8))
    tri(c[1], c[2], top, (0.8,0.6,0))
    tri(c[2], c[3], top, (0,0.6,0.8))
    tri(c[3], c[0], top, (-0.8,0.6,0))
    tri(c[0], c[3], c[2], (0,-1,0))
    tri(c[0], c[2], c[1], (0,-1,0))
    return _mesh(vs, ns, ts)

def make_octahedron(size=1.0, height=1.6):
    s = size / 2.0
    top = (0, height, 0)
    bot = (0, -height*0.5, 0)
    ring = [(s,0,0),(0,0,s),(-s,0,0),(0,0,-s)]
    vs, ns, ts = [], [], []
    for i in range(4):
        a = ring[i]; b = ring[(i+1)%4]
        for v in (a, b, top): vs.append(v); ns.append((v[0], v[1], v[2]))
        ts.extend([(0,0),(1,0),(0.5,1)])
        for v in (b, a, bot): vs.append(v); ns.append((v[0], -v[1], v[2]))
        ts.extend([(0,0),(1,0),(0.5,1)])
    return _mesh(vs, ns, ts)

def make_cylinder(radius=0.5, height=1.0, seg=12):
    vs, ns, ts = [], [], []
    for i in range(seg):
        a0 = 2*math.pi*i/seg
        a1 = 2*math.pi*(i+1)/seg
        x0, z0 = radius*math.cos(a0), radius*math.sin(a0)
        x1, z1 = radius*math.cos(a1), radius*math.sin(a1)
        vs.extend([(x0,0,z0),(x1,0,z1),(x1,height,z1),(x0,0,z0),(x1,height,z1),(x0,height,z0)])
        for _ in range(6): ns.append((x0, 0, z0))
        ts.extend([(i/seg,0),((i+1)/seg,0),((i+1)/seg,1),(i/seg,0),((i+1)/seg,1),(i/seg,1)])
        vs.extend([(0,height,0),(x0,height,z0),(x1,height,z1)])
        ns.extend([(0,1,0)]*3)
        ts.extend([(0.5,0.5),(0,0),(1,0)])
        vs.extend([(0,0,0),(x1,0,z1),(x0,0,z0)])
        ns.extend([(0,-1,0)]*3)
        ts.extend([(0.5,0.5),(1,0),(0,0)])
    return _mesh(vs, ns, ts)

def make_sphere(radius=0.5, seg=12, rings=8):
    vs, ns, ts = [], [], []
    for r in range(rings):
        v0 = r/rings; v1 = (r+1)/rings
        phi0 = math.pi*v0; phi1 = math.pi*v1
        for s in range(seg):
            u0 = s/seg; u1 = (s+1)/seg
            th0 = 2*math.pi*u0; th1 = 2*math.pi*u1
            def p(phi, th):
                return (radius*math.sin(phi)*math.cos(th),
                        radius*math.cos(phi),
                        radius*math.sin(phi)*math.sin(th))
            p00 = p(phi0, th0); p01 = p(phi0, th1)
            p10 = p(phi1, th0); p11 = p(phi1, th1)
            for v in (p00, p10, p11, p00, p11, p01):
                vs.append(v)
                nn = np.array(v)
                nn = nn / (np.linalg.norm(nn) + 1e-9)
                ns.append((nn[0], nn[1], nn[2]))
            ts.extend([(u0,v0),(u0,v1),(u1,v1),(u0,v0),(u1,v1),(u1,v0)])
    return _mesh(vs, ns, ts)
