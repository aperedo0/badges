"""Ruby Heart facet layout (left half in reference pixels, mirrored for the right).

Vertices are traced from the reference; girdle vertices snap to the gem outline.
Faces list vertex names; the right half mirrors every name with a trailing ' (prime).
"""
import numpy as np

O = np.load('/Users/antonioperedo/Desktop/badges/ruby_heart_claude_20261107/trace/outline.npz')
S, CX, BOTTOM = float(O['S']), float(O['CX']), float(O['BOTTOM'])
INNER = O['inner']  # model units, left half, notch -> lobe -> tip

def to_model(p):
    p = np.asarray(p, float)
    return np.array([(p[0] - CX) * S, -2.455 + (BOTTOM - p[1]) * S])

def to_ref(q):
    q = np.asarray(q, float)
    return np.array([q[0] / S + CX, BOTTOM - (q[1] + 2.455) / S])

def snap(p):
    q = to_model(p)
    d = np.linalg.norm(INNER - q, axis=1)
    return INNER[np.argmin(d)].copy()

# Interior vertices (reference pixels).
INTERIOR = dict(
    B=(420, 232), C=(285, 295), D=(369, 376), E=(455, 329),
    H=(240, 455), P1=(367, 611), P2=(500, 697), P3=(280, 622), Q=(430, 795),
    c1=(CX, 386), c2=(CX, 490), c3=(CX, 780), c4=(CX, 935),
)
# Girdle vertices (snapped onto the gem outline).
GIRDLE = dict(
    g0=(530, 228), g1=(415, 205), g2=(300, 240), g3=(215, 330), g4=(195, 455),
    g5=(230, 590), g6=(300, 700), g7=(400, 820), g8=(510, 925),
)
FACES = [
    ('g0', 'g1', 'B'), ('c0', 'g0', 'c1'), ('g0', 'B', 'c1'),
    ('B', 'C', 'D', 'E'), ('B', 'E', 'c1'), ('E', 'D', 'c2'), ('E', 'c1', 'c2'),
    ('g1', 'g2', 'C'), ('g1', 'C', 'B'), ('g2', 'g3', 'C'), ('g3', 'g4', 'C'), ('g4', 'H', 'C'), ('C', 'H', 'D'),
    ('g4', 'g5', 'H'), ('g5', 'P3', 'H'), ('H', 'P3', 'P1'), ('H', 'P1', 'D'), ('D', 'P1', 'P2', 'c2'),
    ('c2', 'P2', 'c3'), ('g5', 'g6', 'P3'), ('P3', 'g6', 'Q'), ('P3', 'Q', 'P1'), ('P1', 'Q', 'P2'),
    ('P2', 'Q', 'c3'), ('g6', 'g7', 'Q'), ('Q', 'g7', 'c4'), ('Q', 'c4', 'c3'), ('g7', 'g8', 'c4'),
    ('g8', 'c5', 'c4'),
]

def layout():
    """Return (names, xy model array, is_girdle, faces as index tuples) for the full heart."""
    pts = {}
    for k, v in INTERIOR.items():
        pts[k] = to_model(v)
    for k, v in GIRDLE.items():
        pts[k] = snap(v)
    pts['c0'] = INNER[0].copy()
    pts['c5'] = INNER[-1].copy()
    for k in ('c1', 'c2', 'c3', 'c4', 'c0', 'c5'):
        pts[k][0] = 0.0
    names = list(pts)
    xy = [pts[k] for k in names]
    girdle = [k.startswith('g') or k in ('c0', 'c5') for k in names]
    # mirror
    mirror = {}
    for k in list(names):
        if k.startswith('c'):
            mirror[k] = k
        else:
            mirror[k] = k + "'"
            names.append(k + "'")
            xy.append(pts[k] * [-1, 1])
            girdle.append(k.startswith('g'))
    idx = {k: i for i, k in enumerate(names)}
    faces = [tuple(idx[k] for k in f) for f in FACES]
    faces += [tuple(idx[mirror[k]] for k in reversed(f)) for f in FACES]
    return names, np.array(xy), np.array(girdle), faces
