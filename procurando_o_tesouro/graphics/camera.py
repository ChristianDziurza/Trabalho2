from __future__ import annotations
import math
import numpy as np
from config.settings import settings

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m

def look_at(eye, target, up):
    f = target - eye
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m

class Camera:
    def __init__(self):
        self.yaw = settings.CAMERA_INITIAL_YAW
        self.pitch = settings.CAMERA_INITIAL_PITCH
        self.distance = settings.CAMERA_INITIAL_DISTANCE
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.aspect = settings.WINDOW_WIDTH / settings.WINDOW_HEIGHT

    def reset(self):
        self.yaw = settings.CAMERA_INITIAL_YAW
        self.pitch = settings.CAMERA_INITIAL_PITCH
        self.distance = settings.CAMERA_INITIAL_DISTANCE
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def rotate(self, dx, dy):
        self.yaw += dx * settings.CAMERA_ROTATE_SPEED
        self.pitch = max(settings.CAMERA_MIN_PITCH,
                         min(settings.CAMERA_MAX_PITCH,
                             self.pitch + dy * settings.CAMERA_ROTATE_SPEED))

    def zoom(self, delta):
        self.distance = max(settings.CAMERA_MIN_DISTANCE,
                            min(settings.CAMERA_MAX_DISTANCE,
                                self.distance - delta * settings.CAMERA_ZOOM_SPEED))

    def pan(self, dx, dy):
        rad = math.radians(self.yaw)
        fwd = np.array([math.sin(rad), 0, math.cos(rad)], dtype=np.float32)
        right = np.array([math.cos(rad), 0, -math.sin(rad)], dtype=np.float32)
        self.target += right * dx * settings.CAMERA_PAN_SPEED * 0.1
        self.target += fwd * dy * settings.CAMERA_PAN_SPEED * 0.1
        
        self.target[0] = max(-2.0, min(2.0, self.target[0]))
        self.target[2] = max(-2.0, min(2.0, self.target[2]))

    def eye(self):
        py = math.radians(self.pitch)
        yw = math.radians(self.yaw)
        x = self.distance * math.cos(py) * math.sin(yw)
        y = self.distance * math.sin(py)
        z = self.distance * math.cos(py) * math.cos(yw)
        
        ex = self.target[0] + x
        ey = self.target[1] + y
        ez = self.target[2] + z
        
        ex = max(-5.5, min(5.5, ex))
        ey = max(0.5, min(6.5, ey))
        ez = max(-5.5, min(5.5, ez))
        
        return np.array([ex, ey, ez], dtype=np.float32)

    def view_matrix(self):
        return look_at(self.eye(), self.target, np.array([0, 1, 0], dtype=np.float32))

    def projection_matrix(self):
        return perspective(settings.CAMERA_FOV, self.aspect,
                           settings.CAMERA_NEAR, settings.CAMERA_FAR)