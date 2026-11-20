"""Version 10 (a copy of v9_temple_geo.py, changed for the polish pass; v9 stays as it was).
The apse is replaced by a long corridor of bays that ends in a far doorway of light, so the hall has depth.

Version 9: the temple's geometry around the chest (owner's mockup, 2026-11-19:
~/Downloads/Ancient stone temple with emerald badge.png). Background only: the chest, badge, mist, specks
and beam are unchanged.

Everything is built in the chest's frame (Temple Root copies Reveal Chest Root: x to the right, y away from
the camera, z up from the floor the chest lands on), so the temple turns with the chest's 32 degree yaw.
Positions were solved from the mockup through the resting camera (frame 213): the front pillars stand
about 58 units behind the chest, the apse arch about 87.

- Stone platform (dais) under the chest, its top exactly at the old floor (the chest still lands on it,
  every landing contact checked inside it): one continuous top stone with a worn, chipped rounded edge and
  two thin gold inlay rings, on six base blocks. Slightly oval (4.45 by 3.6) so its front edge sits where
  the mockup has it with the chest's feet on it.
- Floor of separate flagstones (real gaps, rounded and chipped edges, tiny tilts) over a mossy bed. The
  stones grow with distance so the far floor reads as large flags, not a fine brick grid.
- Pillars: round shafts with a slight swell, a rounded base ring, square chamfered plinths and capitals;
  a smaller engaged pair carries the low elliptical apse arch (one continuous band); arches of voussoirs
  elsewhere; walls, dark side aisles, vault, a rounded apse with an opening in its ceiling.
- Thin crack decals on the two front pillars, where the mockup has them.

Run inside Blender (chest_reveal_v9_temple.blend); safe to run again; nothing is deleted."""
import bpy, bmesh, math, random
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())

G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)              # top of the flagstones (the dais top is 0)
DAIS_A, DAIS_B = G("DAIS_AXES", (4.45, 3.6))
RINGS = ((0.27, 0.045), (0.42, 0.045))         # gold rings: inset from the edge, width
FRONT_Y, FRONT_X = 58.0, 17.2                  # front pillars
ARCADE_Y = 22.0                                # pillars nearer the camera (fully out of the picture, carry the arcade)
INNER_Y, INNER_X, INNER_S = 87.0, 17.5, 0.88   # engaged pillars of the apse arch (smaller)
WALL_Y = 89.0                                  # front face of the back wall
APSE_A, APSE_B, APSE_T = 15.3, 9.6, 2.3        # apse arch: half span, rise, band
SIDE_X = 32.0                                  # outer aisle walls
SEED = G("TEMPLE_SEED", 7)
CORR_END = 235.0                               # far end of the corridor beyond the arch
BAYS = (116.0, 145.0, 174.0, 203.0)            # its ribs and pillars

root = temple_root()
TC = coll("Reveal Temple", bpy.data.collections["Reveal"])
ph = lambda n: bpy.data.materials.get(n) or bpy.data.materials.new(n)
M_STONE, M_WALL, M_ARCH, M_DARK, M_FLOOR, M_BED, M_DAIS, M_GOLD, M_GROOVE, M_CRACK = (
    ph("Temple Stone"), ph("Temple Stone Wall"), ph("Temple Stone Arch"), ph("Temple Stone Dark"),
    ph("Temple Floor Slab"), ph("Temple Floor Bed"), ph("Temple Dais Stone"), ph("Temple Gold Inlay"),
    ph("Temple Inlay Groove"), ph("Temple Crack"))


def finish(bm_verts, bm_faces):
    """Mesh lists -> bmesh with outward normals -> lists."""
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in bm_verts]
    for f in bm_faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    verts = [tuple(v.co) for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return verts, faces


def join(parts):
    V, F = [], []
    for v, f in parts:
        o_ = len(V)
        V += v
        F += [tuple(i + o_ for i in ff) for ff in f]
    return V, F


def box(x0, x1, y0, y1, z0, z1):
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return V, F


# ------------------------------------------------------------------ pillars: round shaft, square chamfered blocks
CH = 0.3                                      # chamfer of the square blocks, share of the half width
K = 1.0 - CH
CORNERS = [(1, -K), (1, K), (K, 1), (-K, 1), (-1, K), (-1, -K), (-K, -1), (K, -1)]
PER_SEG = 8
UNIT_C, UNIT_R = [], []
for i in range(8):
    (x0, y0), (x1, y1) = CORNERS[i], CORNERS[(i + 1) % 8]
    for j in range(PER_SEG):
        t = j / PER_SEG
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        UNIT_C.append((x, y))
        th = math.atan2(y, x)
        UNIT_R.append((math.cos(th), math.sin(th)))


def torus_ring(ac, hc, r, n=8):
    return [("r", ac + r * math.cos(t), hc + r * math.sin(t)) for t in [math.radians(-90 + 180 * i / n) for i in range(1, n + 1)]]


def shaft(h0, h1, a0, a1, n=8):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(("r", a0 + (a1 - a0) * t ** 1.6 + 0.035 * math.sin(math.pi * t), h0 + (h1 - h0) * t))
    return out


PROFILE = ([("c", 3.55, 0.0), ("c", 3.55, 0.88), ("c", 3.45, 0.98),            # footing
            ("c", 3.25, 0.98), ("c", 3.25, 4.35), ("c", 3.0, 4.6),               # lower plinth, worn top edge
            ("c", 2.72, 4.6), ("c", 2.72, 5.62), ("c", 2.58, 5.8),               # upper plinth
            ("r", 2.12, 5.8)] + torus_ring(2.12, 6.22, 0.42) +                   # rounded base ring
           [("r", 2.06, 6.8)] + shaft(6.8, 24.35, 2.06, 1.9) +                  # shaft with a slight swell
           torus_ring(1.9, 24.57, 0.22, 6) +                                     # neck ring
           [("r", 1.9, 25.45)] +
           [("r", 1.9 + 0.55 * (1 - math.cos(t)), 25.45 + 0.85 * math.sin(t)) for t in
            [math.radians(15 * i) for i in range(1, 7)]] +                       # flaring echinus
           [("c", 2.45, 26.3), ("c", 2.45, 27.35),                               # lower capital block
            ("c", 2.58, 27.35), ("c", 2.84, 27.62), ("c", 2.84, 28.95)])         # abacus


def pillar(cx, cy, s=1.0):
    n = len(UNIT_C)
    verts, faces = [], []
    starts = []
    for kind, a, h in PROFILE:
        starts.append(len(verts))
        unit = UNIT_C if kind == "c" else UNIT_R
        for x, y in unit:
            verts.append((cx + s * a * x, cy + s * a * y, FLOOR + s * h))
    for j in range(len(PROFILE) - 1):
        for i in range(n):
            a, b = starts[j] + i, starts[j] + (i + 1) % n
            faces.append((a, b, starts[j + 1] + (i + 1) % n, starts[j + 1] + i))
    faces.append(tuple(starts[0] + i for i in reversed(range(n))))
    faces.append(tuple(starts[-1] + i for i in range(n)))
    return verts, faces


for sx in (-1, 1):
    side = "L" if sx < 0 else "R"
    for name, (cx, cy, s) in (("Temple Pillar Front " + side, (sx * FRONT_X, FRONT_Y, 1.0)),
                              ("Temple Pillar Arcade " + side, (sx * FRONT_X, ARCADE_Y, 1.0)),
                              ("Temple Pillar Apse " + side, (sx * INNER_X, INNER_Y, INNER_S))):
        v, f = pillar(cx, cy, s)
        me = mesh_from(name, v, f, smooth=True, sharp_deg=40)
        o = put(name, me, TC, [M_STONE], root)
        bevel(o, 0.06, 2, 30)


# ------------------------------------------------------------------ cracks on the two front pillars (decals)
def crack(cx, cy, phi0, z0, phi1, z1, seed, width=0.075, n=48):
    rng = random.Random(seed)
    verts, faces, uv = [], [], []
    pts = []
    for i in range(n + 1):
        t = i / n
        phi = phi0 + (phi1 - phi0) * t + rng.uniform(-0.01, 0.01)
        z = z0 + (z1 - z0) * t + 0.22 * math.sin(t * 7.0 + seed) * (1 - abs(2 * t - 1)) + rng.uniform(-0.05, 0.05)
        h = (z - FLOOR - 6.8) / 17.55
        a = 2.06 + (1.9 - 2.06) * max(h, 0) ** 1.6 + 0.035 * math.sin(math.pi * min(max(h, 0), 1)) + 0.012
        nrm = Vector((math.cos(phi), math.sin(phi), 0))
        pts.append((Vector((cx, cy, 0)) + nrm * a + Vector((0, 0, z)), nrm))
    for i, (p, nrm) in enumerate(pts):
        q = pts[min(i + 1, n)][0] - pts[max(i - 1, 0)][0]
        side = nrm.cross(q).normalized()
        w = width * (0.35 + 0.65 * math.sin(math.pi * i / n) ** 0.7) * rng.uniform(0.6, 1.3)
        verts += [tuple(p - side * w * 0.5), tuple(p + side * w * 0.5)]
        uv += [(i / n, 0.0), (i / n, 1.0)]
    for i in range(n):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    return verts, faces, uv


d = math.radians
v1, f1, u1 = crack(-FRONT_X, FRONT_Y, d(212), 12.9, d(328), 10.5, 3)      # left pillar, below the middle
v2, f2, u2 = crack(FRONT_X, FRONT_Y, d(328), 19.2, d(212), 15.2, 5)        # right pillar, higher up
V = v1 + v2
F = f1 + [tuple(i + len(v1) for i in f) for f in f2]
me = mesh_from("Temple Pillar Cracks", V, F, uvs={"UVMap": u1 + u2}, smooth=True)
put("Temple Pillar Cracks", me, TC, [M_CRACK], root)


# ------------------------------------------------------------------ arches
def arc_table(fn, n=2000):
    pts = [fn(i / n) for i in range(n + 1)]
    L = [0.0]
    for i in range(n):
        L.append(L[-1] + math.dist(pts[i][0], pts[i + 1][0]))
    return pts, L


def voussoirs(fn, T, d0, d1, count, gap, mapf, samples=6):
    """fn(t) -> ((u, z) intrados point, (nu, nz) outward unit normal), t in [0, 1]; mapf(u, d, z) -> xyz."""
    pts, L = arc_table(fn)
    total = L[-1]

    def at(s):
        lo, hi = 0, len(L) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if L[mid] < s:
                lo = mid
            else:
                hi = mid
        return pts[lo]

    V, F = [], []
    for i in range(count):
        s0 = total * i / count + (gap / 2 if i else 0)
        s1 = total * (i + 1) / count - (gap / 2 if i < count - 1 else 0)
        base = len(V)
        for k in range(samples):
            (u, z), (nu, nz) = at(s0 + (s1 - s0) * k / (samples - 1))
            U, Z = u + T * nu, z + T * nz
            V += [mapf(u, d0, z), mapf(U, d0, Z), mapf(U, d1, Z), mapf(u, d1, z)]
        for k in range(samples - 1):
            for q in range(4):
                a = base + 4 * k + q
                b = base + 4 * k + (q + 1) % 4
                F.append((a, b, b + 4, a + 4))
        F.append(tuple(base + q for q in range(4)))
        F.append(tuple(base + 4 * (samples - 1) + q for q in (3, 2, 1, 0)))
    return finish(V, F)


def ellipse(A, B, zc, uc=0.0):
    def fn(t):
        th = math.pi * (1 - t)
        p = (uc + A * math.cos(th), zc + B * math.sin(th))
        n = Vector((B * math.cos(th), A * math.sin(th))).normalized()
        return p, (n.x, n.y)
    return fn


cap_front = FLOOR + 28.95
cap_apse = FLOOR + INNER_S * 28.95
# apse arch: one continuous worn band (the mockup shows no joints in it)
v, f = voussoirs(ellipse(APSE_A, APSE_B, cap_apse), APSE_T, INNER_Y - 2.2, WALL_Y + 0.4, 1, 0.0,
                 lambda u, dd, z: (u, dd, z), samples=96)
o = put("Temple Apse Arch", mesh_from("Temple Apse Arch", v, f, smooth=True, sharp_deg=30), TC, [M_ARCH], root)
bevel(o, 0.08, 2, 30)
# transverse arch over the nave on the front pillars (mostly above the picture)
R_T = FRONT_X - 2.84
v, f = voussoirs(ellipse(R_T, R_T, cap_front), 2.6, FRONT_Y - 2.84, FRONT_Y + 2.84, 1, 0.0,
                 lambda u, dd, z: (u, dd, z), samples=96)                     # one band: no panel lines
o = put("Temple Nave Arch", mesh_from("Temple Nave Arch", v, f, smooth=True, sharp_deg=30), TC, [M_ARCH], root)
bevel(o, 0.06, 2, 30)
# arcade arches along both sides (seen edge on: few long stones)
spans = [(ARCADE_Y + 2.84, FRONT_Y - 2.84), (FRONT_Y + 2.84, WALL_Y)]
parts = []
for sx in (-1, 1):
    for y0, y1 in spans:
        r = (y1 - y0) / 2
        # a little proud of the wall above it (flush faces flickered as a ladder of bright bars)
        parts.append(voussoirs(ellipse(r, r, cap_front, (y0 + y1) / 2), 2.4, sx * (FRONT_X - 2.5), sx * (FRONT_X + 2.5),
                               1, 0.0, lambda u, dd, z: (dd, u, z), samples=64))
V, F = join(parts)
o = put("Temple Arcade Arches", mesh_from("Temple Arcade Arches", V, F, smooth=True, sharp_deg=30), TC, [M_WALL], root)
bevel(o, 0.06, 2, 30)


# ------------------------------------------------------------------ walls
def slab_outline(pts, d0, d1, mapf):
    n = len(pts)
    V = [mapf(u, d0, z) for u, z in pts] + [mapf(u, d1, z) for u, z in pts]
    F = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return finish(V, F)


def arc_pts(A, B, zc, uc=0.0, n=48):
    return [(uc + A * math.cos(math.pi * (1 - i / n)), zc + B * math.sin(math.pi * (1 - i / n))) for i in range(n + 1)]


LOW = FLOOR - 0.1
walls = []
# back wall with the apse opening
pts = [(-SIDE_X - 1, LOW), (-APSE_A, LOW)] + arc_pts(APSE_A, APSE_B, cap_apse) + [(APSE_A, LOW), (SIDE_X + 1, LOW),
                                                                                  (SIDE_X + 1, 85), (-SIDE_X - 1, 85)]
walls.append(slab_outline(pts, WALL_Y, WALL_Y + 3, lambda u, dd, z: (u, dd, z)))
# spandrel above the nave arch, up into the vault
# cut a little larger than the arch's underside, so the wall's edge hides inside the arch stones (on the same
# curve it poked through as a row of little blocks)
# (0.6 keeps the cut narrower than the wall itself; a wider cut crossed the wall's own sides and drew stray slivers)
pts = [(-FRONT_X + 2.2, cap_front)] + arc_pts(R_T + 0.6, R_T + 0.6, cap_front) + [(FRONT_X - 2.2, cap_front), (FRONT_X - 2.2, 62),
                                                                                  (-FRONT_X + 2.2, 62)]
walls.append(slab_outline(pts, FRONT_Y - 2.0, FRONT_Y + 2.0, lambda u, dd, z: (u, dd, z)))
# clerestory walls on the arcades (unlit by the temple lights, like the aisles: dark between the pillars)
clerestory = []
for sx in (-1, 1):
    pts = [(12.0, cap_front)]
    for y0, y1 in spans:
        r = (y1 - y0) / 2
        # the wall's cut sits inside the arch stones (on the same curve the two surfaces flickered as a ladder of bars)
        pts += [(y0 - 1.2, cap_front)] + arc_pts(r + 1.2, r + 1.2, cap_front, (y0 + y1) / 2)[1:-1] + [(y1 + 1.2, cap_front)]
    pts += [(WALL_Y + 2.0, cap_front), (WALL_Y + 2.0, 62), (12.0, 62)]      # ends inside the back wall, past the last cut
    clerestory.append(slab_outline(pts, sx * (FRONT_X - 2.2), sx * (FRONT_X + 2.2), lambda u, dd, z: (dd, u, z)))
# corridor beyond the arch: the hall carries on, bay after bay, to a far doorway of light
CA, CB = APSE_A, APSE_B
prof = [(-CA, LOW)] + arc_pts(CA, CB, cap_apse, n=48) + [(CA, LOW)]
npf, nyc = len(prof), 20
V, F = [], []
for j in range(nyc + 1):
    yy = WALL_Y + 2.5 + (CORR_END - WALL_Y - 2.5) * j / nyc
    V += [(u, yy, z) for u, z in prof]
for j in range(nyc):
    for i in range(npf - 1):
        a_ = j * npf + i
        F.append((a_, a_ + npf, a_ + npf + 1, a_ + 1))          # facing into the corridor
put("Temple Apse Wall", mesh_from("Temple Apse Wall", V, F, smooth=True, sharp_deg=40), TC, [M_WALL], root)
parts = []
for yb in BAYS:
    parts.append(voussoirs(ellipse(CA - 1.6, CB - 1.2, cap_apse), 1.7, yb - 1.3, yb + 1.3, 1, 0.0,
                           lambda u, dd, z: (u, dd, z), samples=64))
V, F = join(parts)
o = put("Temple Corridor Ribs", mesh_from("Temple Corridor Ribs", V, F, smooth=True, sharp_deg=30), TC, [M_ARCH], root)
bevel(o, 0.08, 2, 30)
parts = [pillar(sx * (CA - 0.9), yb, INNER_S) for yb in BAYS for sx in (-1, 1)]
V, F = join(parts)
o = put("Temple Corridor Pillars", mesh_from("Temple Corridor Pillars", V, F, smooth=True, sharp_deg=40), TC, [M_STONE], root)
# end wall with a tall doorway, and the light beyond it
DW, DH = 3.4, 17.0
pts = ([(-CA - 1, LOW), (-DW, LOW), (-DW, DH)] + arc_pts(DW, DW, DH, n=24)[1:-1] +
       [(DW, DH), (DW, LOW), (CA + 1, LOW), (CA + 1, 40.0), (-CA - 1, 40.0)])
v_, f_ = slab_outline(pts, CORR_END, CORR_END + 2.5, lambda u, dd, z: (u, dd, z))
put("Temple Corridor End", mesh_from("Temple Corridor End", v_, f_, sharp_deg=30), TC, [M_WALL], root)
gv = [(-DW - 1, CORR_END + 6.0, LOW), (DW + 1, CORR_END + 6.0, LOW), (DW + 1, CORR_END + 6.0, DH + DW + 1), (-DW - 1, CORR_END + 6.0, DH + DW + 1)]
put("Temple Far Light", mesh_from("Temple Far Light", gv, [(0, 1, 2, 3)]), TC, [ph("Temple Far Glow")], root)
V, F = join(walls)
o = put("Temple Walls", mesh_from("Temple Walls", V, F, sharp_deg=30), TC, [M_WALL], root)
bevel(o, 0.05, 1, 30)
# outer aisle walls and aisle ceilings: kept out of the temple lights so the sides fall to black
aisle = list(clerestory)
for sx in (-1, 1):
    aisle.append(box(*sorted((sx * SIDE_X, sx * (SIDE_X + 1.5))), 10.0, WALL_Y + 0.5, LOW, 47.5))
    aisle.append(box(*sorted((sx * (FRONT_X + 2.2), sx * (SIDE_X + 1.5))), 10.0, WALL_Y + 0.5, 46.0, 47.5))
V, F = join(aisle)
put("Temple Aisle Walls", mesh_from("Temple Aisle Walls", V, F), TC, [M_DARK], root)

# barrel vault over the nave (seen only from below, from the opening shots)
VR, VZ = FRONT_X - 2.2, 46.0
V, F = [], []
ny, nv = 40, 32
for j in range(ny + 1):
    y = 10.0 + (WALL_Y + 0.5 - 10.0) * j / ny
    for i in range(nv + 1):
        th = math.pi * i / nv
        V.append((VR * math.cos(th), y, VZ + VR * math.sin(th)))
for j in range(ny):
    for i in range(nv):
        a = j * (nv + 1) + i
        F.append((a, a + 1, a + nv + 2, a + nv + 1))
put("Temple Vault", mesh_from("Temple Vault", V, F, smooth=True), TC, [M_DARK], root)


# ------------------------------------------------------------------ dais
def oval_table(a, b, n=4000):
    P = [(a * math.cos(2 * math.pi * i / n - math.pi / 2), b * math.sin(2 * math.pi * i / n - math.pi / 2)) for i in range(n + 1)]
    L = [0.0]
    for i in range(n):
        L.append(L[-1] + math.dist(P[i], P[i + 1]))
    return P, L


_OVAL = oval_table(DAIS_A, DAIS_B)
PER = _OVAL[1][-1]


def oval_at(s):
    P, L = _OVAL
    s = s % L[-1]
    lo, hi = 0, len(L) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if L[mid] < s:
            lo = mid
        else:
            hi = mid
    t = 2 * math.pi * lo / (len(P) - 1) - math.pi / 2
    return Vector((DAIS_A * math.cos(t), DAIS_B * math.sin(t))), Vector((DAIS_B * math.cos(t), DAIS_A * math.sin(t))).normalized()


rng = random.Random(SEED)
WAVES = [(rng.uniform(0.004, 0.011), rng.randint(3, 23), rng.uniform(0, 6.3)) for _ in range(7)]
CHIPS = [(rng.uniform(0, PER), rng.uniform(0.12, 0.38), rng.uniform(0.025, 0.06)) for _ in range(9)]


def wear(s):
    """How far the worn edge sits inside the clean oval at perimeter position s, and how much it drops."""
    off = 0.012 + sum(a * math.sin(k * 2 * math.pi * s / PER + p) for a, k, p in WAVES)
    drop = 0.0
    for c, half, depth in CHIPS:
        dd = abs((s - c + PER / 2) % PER - PER / 2)
        if dd < half:
            w = 0.5 + 0.5 * math.cos(math.pi * dd / half)
            off += depth * w
            drop = max(drop, 0.6 * depth * w)
    return max(off, 0.0), drop


CAP = [(0.065, 0.0), (0.04, -0.004), (0.019, -0.013), (0.006, -0.028), (0.0, -0.05), (0.0, -0.17)]
NS = 420
V = []
for i in range(NS):
    p, n = oval_at(PER * i / NS)
    off, drop = wear(PER * i / NS)
    for j, (inset, z) in enumerate(CAP):
        q = p - n * (inset + off)
        V.append((q.x, q.y, z - (drop if j < 4 else 0.0) * (1.0 - j / 4)))
F = [tuple(i * len(CAP) for i in range(NS))]                              # the top
for i in range(NS):
    a, b = i * len(CAP), ((i + 1) % NS) * len(CAP)
    for j in range(len(CAP) - 1):
        F.append((a + j, a + j + 1, b + j + 1, b + j))
V, F = finish(V, F)
me = mesh_from("Temple Dais Top", V, F, smooth=True, sharp_deg=55)
put("Temple Dais Top", me, TC, [M_DAIS], root)
# six base blocks under the top stone (their joints show only on the side)
DLOW = FLOOR - 0.07
NB = 6
bounds = [PER * (i + (rng.uniform(-0.12, 0.12) if 0 < i < NB else 0.0)) / NB + PER * 0.04 for i in range(NB + 1)]
V, F = [], []
for bi in range(NB):
    s0, s1 = bounds[bi] + 0.02, bounds[bi + 1] - 0.02
    m = 24
    base = len(V)
    for k in range(m):
        s = s0 + (s1 - s0) * k / (m - 1)
        p, n = oval_at(s)
        off = wear(s)[0] * 0.6
        for inset, z in ((0.7, -0.17), (off, -0.17), (off + 0.004, -0.2), (off, DLOW + 0.03), (off + 0.02, DLOW), (0.7, DLOW)):
            q = p - n * inset
            V.append((q.x, q.y, z))
    npf = 6
    for k in range(m - 1):
        for j in range(npf):
            a = base + k * npf + j
            b = base + k * npf + (j + 1) % npf
            F.append((a, b, b + npf, a + npf))
    F.append(tuple(base + j for j in range(npf)))
    F.append(tuple(base + (m - 1) * npf + j for j in reversed(range(npf))))
V, F = finish(V, F)
me = mesh_from("Temple Dais Blocks", V, F, smooth=True, sharp_deg=50)
put("Temple Dais Blocks", me, TC, [M_DAIS], root)


def strip(inset, width, z, n=480, edge=0.0):
    V, F = [], []
    for i in range(n):
        p, nn = oval_at(PER * i / n)
        a = p - nn * (inset - width / 2)
        b = p - nn * (inset + width / 2)
        V += [(a.x, a.y, z), (b.x, b.y, z)]
        if edge:
            V += [(a.x, a.y, z - edge), (b.x, b.y, z - edge)]
    st = 4 if edge else 2
    for i in range(n):
        a, b = i * st, ((i + 1) % n) * st
        F.append((a, b, b + 1, a + 1))
        if edge:
            F.append((a + 2, b + 2, b, a))
            F.append((a + 1, b + 1, b + 3, a + 3))
    return V, F


V, F = join([strip(i, w, 0.004, edge=0.0035) for i, w in RINGS])
put("Temple Dais Gold Rings", mesh_from("Temple Dais Gold Rings", V, F, smooth=True), TC, [M_GOLD], root)
V, F = join([strip(i, w + 0.03, 0.0012) for i, w in RINGS])
put("Temple Dais Ring Grooves", mesh_from("Temple Dais Ring Grooves", V, F), TC, [M_GROOVE], root)


# ------------------------------------------------------------------ flagstone floor
def inside_dais(x, y, grow=0.0):
    return (x / (DAIS_A + grow)) ** 2 + (y / (DAIS_B + grow)) ** 2 < 1.0


def grow(y):
    """Stones get larger with distance: the far floor reads as large flags, not a fine grid."""
    return min(1.0 + max(0.0, y - 6.0) / 30.0, 3.4)


def offset_poly(pts, d):
    """Move a convex counter clockwise polygon inward by d (mitred)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        m = n1 + n2
        if m.length < 1e-6:
            m = n1
        m.normalize()
        out.append(tuple(p1 + m * (d / max(m.dot(n1), 0.3))))
    return out


rng = random.Random(SEED + 1)
V, F, SM, UV_slab, UV_half, UV_rand, UV_world = [], [], [], [], [], [], []
GAP = 0.05
count = 0


def add_slab(cx, cy, hx, hy, s):
    global count
    fp = []
    for ci, (sx, sy) in enumerate(((1, -1), (1, 1), (-1, 1), (-1, -1))):
        chipped = rng.random() < 0.22
        rc = min((rng.uniform(0.18, 0.4) if chipped else rng.uniform(0.03, 0.14)) * s, hx * 0.45, hy * 0.45)
        ccx, ccy = sx * (hx - rc), sy * (hy - rc)
        a0 = math.atan2(sy, sx) - math.pi / 4
        for k in range(3):
            t = a0 + (math.pi / 2) * k / 2
            rr = rc * (0.75 if (chipped and k == 1) else 1.0)       # a chipped corner is a straighter cut
            fp.append((ccx + rr * math.cos(t) + rng.uniform(-0.025, 0.025) * s,
                       ccy + rr * math.sin(t) + rng.uniform(-0.025, 0.025) * s))
    bev = 0.022 * math.sqrt(s)
    tilt = (rng.gauss(0, 0.004), rng.gauss(0, 0.004))
    top = FLOOR + rng.uniform(-0.012, 0.008)
    r1, r2 = rng.random(), rng.random()
    rings = ((bev, 0.0), (bev * 0.32, -bev * 0.28), (0.0, -bev), (0.0, -0.16))
    base = len(V)
    for inset, dz in rings:
        poly = offset_poly(fp, inset) if inset > 0 else fp
        for (px, py) in poly:
            V.append((cx + px, cy + py, top + dz + tilt[0] * px + tilt[1] * py))
            UV_slab.append((px, py))
            UV_half.append((hx, hy))
            UV_rand.append((r1, r2))
            UV_world.append((cx + px, cy + py))
    npf = len(fp)
    F.append(tuple(base + i for i in range(npf)))
    SM.append(False)                     # flat top, rounded edge
    for j in range(len(rings) - 1):
        for i in range(npf):
            a = base + j * npf + i
            b = base + j * npf + (i + 1) % npf
            F.append((a, a + npf, b + npf, b))
            SM.append(True)
    count += 1


y = -22.0
Y_END = CORR_END + 1.0
while y < Y_END:
    sc = grow(y)
    dpt = rng.uniform(1.35, 1.95) * sc
    in_apse = y >= WALL_Y
    xa, xb = (-APSE_A - 2, APSE_A + 2) if in_apse else (-SIDE_X, SIDE_X)
    x = xa - rng.uniform(0.0, 1.8) * sc
    while x < xb:
        L = rng.uniform(1.9, 3.3) * sc
        cx, cy = x + L / 2, y + dpt / 2
        hx, hy = L / 2 - GAP / 2, dpt / 2 - GAP / 2
        if not all(inside_dais(cx + sx * hx, cy + sy * hy, -0.05) for sx in (-1, 1) for sy in (-1, 1)):
            add_slab(cx, cy, hx, hy, sc)
        x += L
    y += dpt
me = mesh_from("Temple Floor", V, F, uvs={"UVMap": UV_world, "SlabUV": UV_slab, "SlabHalf": UV_half, "SlabRand": UV_rand},
               smooth=SM, sharp_deg=70)
put("Temple Floor", me, TC, [M_FLOOR], root)
V, F = box(-SIDE_X - 1, SIDE_X + 1, -24.0, CORR_END + 3.0, FLOOR - 0.3, FLOOR - 0.065)
put("Temple Floor Bed", mesh_from("Temple Floor Bed", V, F, uvs={"UVMap": [(v[0], v[1]) for v in V]}), TC, [M_BED], root)

# the old plain floor stops rendering (kept in the file)
old = bpy.data.objects.get("Reveal Floor")
if old:
    old.hide_render = True
    old.hide_viewport = True

result = {"slabs": count, "dais_perimeter": round(PER, 2)}
