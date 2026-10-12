"""Established Home projection used for the fixed-scale badge still."""
import numpy as np
CAM_POS = np.array([0, 1.8, 23.0]); CAM_TARGET = np.array([0, -0.55, 0]); FOCAL = 75 / 36 * 1080
def to_screen(pts):
    """Model points (N,3) to iPhone 17 screenshot pixels (Codex's measured mapping: master * 47/60 + [180, 70])."""
    f = CAM_TARGET - CAM_POS; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = pts - CAM_POS; depth = d @ f
    m = np.stack([540 + FOCAL * (d @ r) / depth, 720 - FOCAL * (d @ u) / depth], axis=-1)
    return m * 47 / 60 + np.array([180, 70])
