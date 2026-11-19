"""Swept mesh for the lower iron rim (numpy only). Used by the simple style builder."""
import numpy as np

U = np.array([0.8480481513760686, 0.529919175863294, 0.0])
N = np.array([0.529919175863294, -0.8480481513760686, 0.0])
Z = np.array([0.0, 0.0, 1.0])


def rim_arrays(prof, NS=2560, mesh_rows=(20, 8, 56, 8, 6), ZT=-1.7140, ZB=-2.2175, INNER=-0.186, round_mix=0.0):
    """prof: dict with at, bt, ab, bb (chamfer legs along the perimeter), perim, rows, A, BD, RC.
    Returns verts (n,3), quads (m,4), loop uvs (m*4,2). round_mix 0 = flat chamfer, 1 = quarter round."""
    PERIM = float(prof["perim"]); A, BD, RC = float(prof["A"]), float(prof["BD"]), float(prof["RC"])
    n_top, n_tch, n_front, n_bch, n_bot = [int(v) for v in prof["rows"]]
    RT = n_top + n_tch + n_front + n_bch + n_bot
    s = np.arange(NS) / NS * PERIM
    Wt = len(prof["at"]); sx = (np.arange(Wt) + 0.5) / Wt * PERIM
    at, bt, ab, bb = [np.interp(s, sx, prof[k], period=PERIM) for k in ("at", "bt", "ab", "bb")]
    segs = [("L", (0.0, -BD), (1, 0), (0, -1), A - RC), ("A", (A - RC, -BD + RC), -90.0, (1, -1), np.pi * RC / 2),
            ("L", (A, -BD + RC), (0, 1), (1, 0), 2 * (BD - RC)), ("A", (A - RC, BD - RC), 0.0, (1, 1), np.pi * RC / 2),
            ("L", (A - RC, BD), (-1, 0), (0, 1), 2 * (A - RC)), ("A", (-(A - RC), BD - RC), 90.0, (-1, 1), np.pi * RC / 2),
            ("L", (-A, BD - RC), (0, -1), (-1, 0), 2 * (BD - RC)), ("A", (-(A - RC), -BD + RC), 180.0, (-1, -1), np.pi * RC / 2),
            ("L", (-(A - RC), -BD), (1, 0), (0, -1), A - RC)]
    P0 = np.zeros((NS, 2)); NRM = np.zeros((NS, 2)); ARC = np.zeros(NS, bool); CEN = np.zeros((NS, 2)); SGN = np.zeros((NS, 2))
    acc = 0.0
    for kind, p, d, n, ln in segs:
        m = (s >= acc - 1e-9) & (s < acc + ln - 1e-9)
        t = s[m] - acc
        if kind == "L":
            P0[m] = np.array(p)[None, :] + t[:, None] * np.array(d, float)[None, :]; NRM[m] = np.array(n, float)
        else:
            th = np.deg2rad(d) + t / RC
            nn = np.stack([np.cos(th), np.sin(th)], axis=1)
            P0[m] = np.array(p)[None, :] + RC * nn; NRM[m] = nn; ARC[m] = True; CEN[m] = np.array(p); SGN[m] = np.array(n, float)
        acc += ln

    def offs(o):
        pt = P0 + o[:, None] * NRM
        rad = RC + o
        sharp = ARC & (rad < 0)
        pt[sharp] = CEN[sharp] + rad[sharp, None] * SGN[sharp]
        return pt

    m_top, m_tch, m_front, m_bch, m_bot = mesh_rows
    ro, rz, rvv = [], [], []
    for j in range(m_top):
        g = j / m_top; ro.append(INNER + g * (-at - INNER)); rz.append(np.full(NS, ZT)); rvv.append(g * n_top)
    for j in range(m_tch):
        g = j / m_tch
        fo, fz = 1 - g, g                                   # flat chamfer
        qo, qz = 1 - np.sin(g * np.pi / 2), 1 - np.cos(g * np.pi / 2)   # quarter round
        ro.append(-at * ((1 - round_mix) * fo + round_mix * qo)); rz.append(ZT - bt * ((1 - round_mix) * fz + round_mix * qz))
        rvv.append(n_top + g * n_tch)
    for j in range(m_front):
        g = j / m_front; ro.append(np.zeros(NS)); rz.append((ZT - bt) + g * ((ZB + bb) - (ZT - bt))); rvv.append(n_top + n_tch + g * n_front)
    for j in range(m_bch):
        g = j / m_bch
        fo, fz = g, 1 - g
        qo, qz = 1 - np.cos(g * np.pi / 2), 1 - np.sin(g * np.pi / 2)
        ro.append(-ab * ((1 - round_mix) * fo + round_mix * qo)); rz.append(ZB + bb * ((1 - round_mix) * fz + round_mix * qz))
        rvv.append(n_top + n_tch + n_front + g * n_bch)
    for j in range(m_bot):
        g = j / (m_bot - 1); ro.append(-ab + g * (INNER + ab)); rz.append(np.full(NS, ZB)); rvv.append(n_top + n_tch + n_front + n_bch + g * (n_bot - 1))
    R = len(ro)
    rvv = np.array(rvv + [RT]) / RT
    rv = np.zeros((R, NS, 3))
    for j in range(R):
        p2 = offs(ro[j])
        rv[j] = U[None, :] * p2[:, :1] + N[None, :] * p2[:, 1:2] + Z[None, :] * rz[j][:, None]
    ii, jj = np.meshgrid(np.arange(NS), np.arange(R))
    ii = ii.ravel(); jj = jj.ravel()
    i1 = (ii + 1) % NS; j1 = (jj + 1) % R
    quads = np.stack([jj * NS + ii, jj * NS + i1, j1 * NS + i1, j1 * NS + ii], axis=1)
    uvq = np.stack([np.stack([ii / NS, rvv[jj]], 1), np.stack([(ii + 1) / NS, rvv[jj]], 1),
                    np.stack([(ii + 1) / NS, rvv[jj + 1]], 1), np.stack([ii / NS, rvv[jj + 1]], 1)], axis=1)
    return rv.reshape(-1, 3), quads, uvq.reshape(-1, 2)
