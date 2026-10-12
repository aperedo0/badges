"""Exploration: round brilliant as an intersection of planes; prints the face count and key heights for a parameter set."""
import numpy as np, itertools, math

def plane(az_deg, tilt_deg, through_rho, through_y):
    """Outward plane: horizontal normal part at azimuth az (0 = +Z, toward +X), normal elevation tilt.
    Passes through the profile point (rho along the azimuth, y)."""
    a = math.radians(az_deg); t = math.radians(tilt_deg)
    n = np.array([math.cos(t) * math.sin(a), math.sin(t), math.cos(t) * math.cos(a)])
    d = math.cos(t) * through_rho + math.sin(t) * through_y
    return n, d

def polytope(planes, tol=1e-7):
    N = np.array([p[0] for p in planes]); D = np.array([p[1] for p in planes])
    verts = []
    for i, j, k in itertools.combinations(range(len(planes)), 3):
        M = N[[i, j, k]]
        if abs(np.linalg.det(M)) < 1e-9: continue
        v = np.linalg.solve(M, D[[i, j, k]])
        if np.all(N @ v - D < 1e-6): verts.append(v)
    verts = np.array(verts)
    # merge
    uniq = []
    for v in verts:
        for u in uniq:
            if np.linalg.norm(u - v) < 1e-5: break
        else: uniq.append(v)
    return np.array(uniq), N, D

def faces(verts, N, D):
    out = {}
    for i in range(len(N)):
        on = np.where(np.abs(verts @ N[i] - D[i]) < 1e-5)[0]
        if len(on) >= 3: out[i] = on
    return out
