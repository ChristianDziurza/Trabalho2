from __future__ import annotations
import random
from config.settings import settings

class Particle:
    __slots__ = ("x","y","z","vx","vy","vz","life","max_life","r","g","b","size")
    def __init__(self, x, y, z, vx, vy, vz, life, color, size=0.08):
        self.x=x; self.y=y; self.z=z
        self.vx=vx; self.vy=vy; self.vz=vz
        self.life=life; self.max_life=life
        self.r, self.g, self.b = color
        self.size = size

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_burst(self, x, y, z, color, count=20, spread=1.2, speed=2.0):
        if not settings.PARTICLES_ENABLED: return
        for _ in range(count):
            if len(self.particles) >= settings.MAX_PARTICLES: break
            vx = random.uniform(-spread, spread)*speed
            vy = random.uniform(0.5, spread)*speed
            vz = random.uniform(-spread, spread)*speed
            life = random.uniform(0.6, 1.4)
            self.particles.append(Particle(x, y, z, vx, vy, vz, life, color, random.uniform(0.05,0.12)))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0: continue
            p.x += p.vx*dt; p.y += p.vy*dt; p.z += p.vz*dt
            p.vy -= 4.0*dt
            alive.append(p)
        self.particles = alive
