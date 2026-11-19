"""Smooth curve through the lid's outer arch points (Catmull-Rom, chord length parameter)."""
import numpy as np


def dense_curve(pts, n=40001):
    """pts: (k,2) ordered arch points (d, z). Returns dense points, cumulative arc length, unit tangents."""
    p = np.asarray(pts, float)
    t = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
    m = np.gradient(p, t, axis=0)                      # tangents at the knots
    s = np.linspace(0, t[-1], n)
    i = np.clip(np.searchsorted(t, s) - 1, 0, len(t) - 2)
    h = (t[i + 1] - t[i])[:, None]
    q = ((s - t[i]) / h[:, 0])[:, None]
    h00, h10 = 2 * q**3 - 3 * q**2 + 1, q**3 - 2 * q**2 + q
    h01, h11 = -2 * q**3 + 3 * q**2, q**3 - q**2
    c = h00 * p[i] + h10 * h * m[i] + h01 * p[i + 1] + h11 * h * m[i + 1]
    arc = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
    tan = np.gradient(c, arc, axis=0)
    tan /= np.linalg.norm(tan, axis=1)[:, None]
    return c, arc, tan
