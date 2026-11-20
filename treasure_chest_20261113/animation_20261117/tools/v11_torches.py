"""Version 11: torches whose fire wakes the hall (owner, 2026-11-19: "we can put some torches ... on each hall ...
the fire can wake up the hall"; on the pillars and down the hall, none beside the platform).
Run inside chest_reveal_v11_torches.blend after the version 10 scripts (geo, mat, light, lens, motion); safe to
run again; nothing is deleted. Version 10 keeps the look without torches.

Second design, after the owner's picture (~/Downloads/Flaming Iron Torch on Stone Wall.png: "maybe we can do
even better on the fire ... you can make the flame bigger, change up the shape of the thing that holds the
flame"): the first torches were thin brackets with a candle sized flame.
- Six pairs: the two big pillars, the two small pillars under the arch, and the four bays of the long hall.
  Each is a forged iron sconce: an oval back plate with four bolts, a square arm, a socket with a collar and
  a goblet shaped cup with a thick rim, turned three quarters toward the camera so the arm and the cup read.
- The fire is a card that faces the camera, drawn by a shader: a body as wide as the cup that leans and
  splits into tongues (three layers of noise streaming upward), a pale yellow heart, orange then deep red at
  the edges. A bed of glowing coals sits inside the cup. A second card carries a few tiny embers that rise,
  drift sideways and die out.
- Each flame has its own light (a pool on its pillar, a halo in the hall's air). Each pair of the long hall
  also has a soft glow light for its bay, because a torch's own reach is short and the hall has to be seen.
- "Temple Torch Control" carries one number per pair, lit_0 (big pillars) to lit_5 (far end of the hall), 0 to
  1. Flame size and brightness, coals, embers and every torch light follow it, so lighting the hall pair after
  pair later is six keyed numbers. All are 1 for now (the ending).
- The far doorway no longer lights the hall in gold (that showed the hall before anything woke it): it is
  faint cold moonlight now. The warm edge lights on the big pillars and under the big arch follow lit_0, the
  pool on the small arch follows lit_1."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
TORCH = coll("Temple Torches", TC)
CAM = Vector((0.0, -16.0, 8.0))                 # where the resting camera stands, in the chest's frame
FIRE = (1.0, 0.50, 0.17)
TS = G("TORCH_SIZE", 1.0)
TURN = math.radians(G("TORCH_TURN", 45.0))      # 0 = seen exactly from the side, 90 = pointing at the camera (then snapped
                                                # to the middle of a pillar band: 45 lands on the band that shows the plate's face)
L = 1.25                                        # arm: from the plate to the socket
AX = L + 0.40                                   # the cup's axis, out from the pillar's surface
RIM = 2.1                                       # top of the cup above the plate's middle
# Three shapes (owner, 2026-11-20: "let's change the shape of the fire and torches I think it can be more
# tasteful"). TORCH_STYLE chooses; temple/tools/torch_style.py shows one for a single render without saving.
#   goblet: the stout iron cup with a tall fire (the second design)
#   slim:   a slender torch leaning out of two iron rings, with a small calm teardrop of fire
#   bowl:   a shallow iron dish on a curved arm, with a low, wide, quiet fire
# fire: where the flame starts (out from the pillar, up); coal: glowing bed (radius, up) or None; card: the flame
# card's width and height; then the flame's own shape (width of its body, how round its top is, how far the top
# splits into tongues, how hard they split, how much it leans).
STYLE = G("TORCH_STYLE", "slim")                # the owner picked the slim torch on 2026-11-20 ("Let's go with A")
# The slim torch can lean out from the pillar or stand straight up (owner: "let's try with a slant and no slant
# just straight up"). Standing straight it sits further out, so its fire stays clear of the stone.
LEAN = G("TORCH_LEAN", 17.0)
SLIM_OUT = 0.40 if LEAN > 1.0 else 0.8
SLIM_A = (SLIM_OUT, -0.75)
SLIM_B = (SLIM_OUT + 2.5 * math.tan(math.radians(LEAN)), 1.75)
_ln = math.hypot(SLIM_B[0] - SLIM_A[0], SLIM_B[1] - SLIM_A[1])
SLIM_AX = ((SLIM_B[0] - SLIM_A[0]) / _ln, (SLIM_B[1] - SLIM_A[1]) / _ln)
SLIM_HEAD = (SLIM_B[0] + SLIM_AX[0] * 0.62, SLIM_B[1] + SLIM_AX[1] * 0.62)
SHAPE = {
    "goblet": dict(fire=(AX, 1.9), coal=(0.86, 1.99), card=(4.4, 4.6), width=0.47, round=1.4, tongues=1.5, split=2.8, sway=0.9, few=0.5),
    "slim": dict(fire=(SLIM_HEAD[0], SLIM_HEAD[1] - 0.14), coal=(0.27, SLIM_HEAD[1] + 0.02), card=(3.0, 3.1), width=0.44, round=1.9, tongues=1.0, split=2.0, sway=0.7, few=0.66),
    "bowl": dict(fire=(1.55, 0.86), coal=(0.95, 0.93), card=(4.8, 3.2), width=0.6, round=1.8, tongues=1.1, split=2.2, sway=0.75, few=0.62),
}[STYLE]

ctrl = bpy.data.objects.get("Temple Torch Control")
if ctrl is None:
    ctrl = bpy.data.objects.new("Temple Torch Control", None)
    TORCH.objects.link(ctrl)
ctrl.parent = root
ctrl.matrix_parent_inverse.identity()
ctrl.location = (0.0, 40.0, 30.0)
for g in range(6):
    if f"lit_{g}" not in ctrl:
        ctrl[f"lit_{g}"] = 1.0
    ctrl.id_properties_ui(f"lit_{g}").update(min=0.0, max=1.5, soft_min=0.0, soft_max=1.0)

# pair number, pillar centre x and y, pillar scale, height of the plate's middle on the pillar
SPOTS = []
for sx in (-1, 1):
    SPOTS.append((0, sx * 17.2, 58.0, 1.0, 14.5))
    SPOTS.append((1, sx * 17.5, 87.0, 0.88, 14.5))
    for k, yb in enumerate((116.0, 145.0, 174.0, 203.0)):
        SPOTS.append((2 + k, sx * 14.4, yb, 0.88, 13.5))


def finish(V, F):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = [tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return out


def join(parts):
    V, F = [], []
    for v, f in parts:
        o_ = len(V)
        V += v
        F += [tuple(i + o_ for i in ff) for ff in f]
    return V, F


def extrude(poly, t0, t1, mapf):
    n = len(poly)
    V = [mapf(a, b, t0) for a, b in poly] + [mapf(a, b, t1) for a, b in poly]
    F = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return finish(V, F)


def lathe(profile, mapf, n=24):
    V, F = [], []
    for r, h in profile:
        for i in range(n):
            t = 2 * math.pi * i / n
            V.append(mapf(r * math.cos(t), r * math.sin(t), h))
    for j in range(len(profile) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            F.append((a, b, b + n, a + n))
    F.append(tuple(reversed(range(n))))
    F.append(tuple(range((len(profile) - 1) * n, len(profile) * n)))
    return finish(V, F)


def stadium(R, H):
    return ([(R * math.cos(t), H + R * math.sin(t)) for t in [math.pi * i / 10 for i in range(11)]] +
            [(R * math.cos(t), -H + R * math.sin(t)) for t in [math.pi + math.pi * i / 10 for i in range(11)]])


def tube(P, a, b, r0, r1, n=16):
    """A round bar from a to b, both (out, up): it may lean, in the plane that sticks out of the pillar."""
    ax = Vector((b[0] - a[0], 0.0, b[1] - a[1])).normalized()
    e1 = Vector((0.0, 1.0, 0.0))
    e2 = ax.cross(e1)
    V = []
    for c, r in ((a, r0), (b, r1)):
        for i in range(n):
            t = 2 * math.pi * i / n
            q = Vector((c[0], 0.0, c[1])) + (e1 * math.cos(t) + e2 * math.sin(t)) * r
            V.append(P(q.x, q.y, q.z))
    F = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    F.append(tuple(reversed(range(n))))
    F.append(tuple(range(n, 2 * n)))
    return finish(V, F)


def sweep(P, path, h):
    """A square bar along a path of (out, up) points."""
    m = len(path)
    V = []
    for k, (o_, u_) in enumerate(path):
        o0, u0 = path[max(k - 1, 0)]
        o1, u1 = path[min(k + 1, m - 1)]
        t = Vector((o1 - o0, u1 - u0)).normalized()
        nx, nu = -t.y, t.x
        for sd_, nn in ((-h, -h), (h, -h), (h, h), (-h, h)):
            V.append(P(o_ + nx * nn, sd_, u_ + nu * nn))
    F = []
    for k in range(m - 1):
        for q in range(4):
            F.append((k * 4 + q, k * 4 + (q + 1) % 4, k * 4 + (q + 1) % 4 + 4, k * 4 + q + 4))
    F.append((3, 2, 1, 0))
    F.append(tuple((m - 1) * 4 + q for q in range(4)))
    return finish(V, F)


PLATE_R, PLATE_H = 0.32, 0.98        # a slim strap: a band between two ridges is 0.78 wide on the big pillars
STADIUM = stadium(PLATE_R, PLATE_H)
BOWL = [(0.10, 0.02), (0.17, 0.06), (0.17, 0.2), (0.32, 0.26), (0.64, 0.38), (0.92, 0.56), (1.10, 0.8), (1.15, 0.98),
        (1.11, 1.04), (1.03, 1.0), (0.99, 0.9)]
HEX = [(0.14 * math.cos(math.pi / 6 + math.pi * i / 3), 0.14 * math.sin(math.pi / 6 + math.pi * i / 3)) for i in range(6)]
CUP = [(0.36, -0.62), (0.40, -0.56), (0.40, 0.08), (0.57, 0.08), (0.60, 0.12), (0.60, 0.30), (0.57, 0.34),     # stem and collar
       (0.50, 0.34), (0.56, 0.42), (0.70, 0.62), (0.82, 0.92), (0.90, 1.3), (0.94, 1.78),                    # a rounded bowl
       (1.03, 1.78), (1.06, 1.84), (1.06, 2.04), (1.03, RIM), (0.90, RIM), (0.86, 1.97)]                     # rim band, lip, inner floor

iron, torches = [], []
for i, (g, cx, cy, s, h) in enumerate(SPOTS):
    S = s * TS
    C = Vector((cx, cy, FLOOR + h * s))
    to_cam = Vector((CAM.x - cx, CAM.y - cy, 0.0)).normalized()
    side = Vector((-to_cam.y, to_cam.x, 0.0))
    if side.x * cx > 0:                       # toward the middle of the hall
        side = -side
    d = (side * math.cos(TURN) + to_cam * math.sin(TURN)).normalized()
    # Owner, 2026-11-20: "the torch is sitting on a seam. it would never do that in real life ... it sits on a flat
    # surface". The pillars have 16 grooves; the plate now sits in the middle of one band between two ridges
    # (the nearest one, at most 11 degrees away), and it is slim enough to fit inside that band.
    step = 2 * math.pi / G("FLUTES", 16)
    ang = round((math.atan2(d.y, d.x) - step / 2) / step) * step + step / 2
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    sd = Vector((-d.y, d.x, 0.0))
    r_s = 1.99 * s

    def P(out, sdv, up, C=C, d=d, sd=sd, S=S, r_s=r_s):
        return tuple(C + d * (r_s + out * S) + sd * (sdv * S) + Vector((0, 0, up * S)))

    if STYLE == "goblet":
        iron.append(extrude(STADIUM, -0.12, 0.16, lambda a, b, t: P(t, a, b)))
        for bz in (-0.95, 0.72, -0.5, 0.98):          # four bolts down the strap
            iron.append(extrude([(hx, bz + hz) for hx, hz in HEX], 0.16, 0.3, lambda a, b, t: P(t, a, b)))
        iron.append(extrude([(-0.19, -0.44), (0.19, -0.44), (0.19, -0.04), (-0.19, -0.04)], 0.05, L + 0.15, lambda a, b, t: P(t, a, b)))
        iron.append(lathe(CUP, lambda rx, ry, up: P(AX + rx, ry, up)))
    elif STYLE == "slim":
        iron.append(extrude(stadium(0.22, 0.62), -0.12, 0.14, lambda a, b, t: P(t, a, b)))
        for bz in (-0.68, 0.0, 0.68):
            iron.append(extrude([(hx * 0.8, bz + hz * 0.8) for hx, hz in HEX], 0.14, 0.25, lambda a, b, t: P(t, a, b)))
        A_, B_ = SLIM_A, SLIM_B                                 # leaning out, or straight up
        a0, a1 = SLIM_AX
        iron.append(tube(P, (A_[0] - a0 * 0.12, A_[1] - a1 * 0.12), A_, 0.07, 0.12))      # a small pointed foot
        iron.append(tube(P, A_, B_, 0.12, 0.16))                                           # the shaft
        iron.append(tube(P, B_, (B_[0] + a0 * 0.1, B_[1] + a1 * 0.1), 0.2, 0.27))          # the head flares
        iron.append(tube(P, (B_[0] + a0 * 0.1, B_[1] + a1 * 0.1), (B_[0] + a0 * 0.62, B_[1] + a1 * 0.62), 0.27, 0.3))
        for up_ in (-0.42, 0.5):                               # two rings hold it, each on a short arm
            oc = A_[0] + (up_ - A_[1]) / (B_[1] - A_[1]) * (B_[0] - A_[0])
            iron.append(tube(P, (oc - a0 * 0.1, up_ - a1 * 0.1), (oc + a0 * 0.1, up_ + a1 * 0.1), 0.23, 0.23))
            iron.append(extrude([(-0.09, up_ - 0.09), (0.09, up_ - 0.09), (0.09, up_ + 0.09), (-0.09, up_ + 0.09)], 0.05, oc,
                                lambda a, b, t: P(t, a, b)))
    else:
        iron.append(extrude(stadium(0.26, 0.72), -0.12, 0.14, lambda a, b, t: P(t, a, b)))
        for bz in (-0.76, 0.76):
            iron.append(extrude([(hx * 0.9, bz + hz * 0.9) for hx, hz in HEX], 0.14, 0.26, lambda a, b, t: P(t, a, b)))
        AXB = SHAPE["fire"][0]                                 # a bar that leaves the plate level and curves up under the dish
        path = [(0.08 + (AXB - 0.08) * math.sin(t), -0.55 + 0.6 * (1 - math.cos(t))) for t in [math.pi / 2 * k_ / 10 for k_ in range(11)]]
        iron.append(sweep(P, path, 0.105))
        iron.append(lathe(BOWL, lambda rx, ry, up: P(AXB + rx, ry, up)))
    fo, fu = SHAPE["fire"]
    coal = Vector(P(fo, 0, SHAPE["coal"][1])) if SHAPE["coal"] else None
    torches.append((i, g, s, S, Vector(P(fo, 0, fu)), coal, d))

# ------------------------------------------------------------------ hammered, rusted iron
m_iron = mat("Temple Torch Iron")
n = NT(m_iron)
tc = n.coord()
p = tc.outputs["Object"]
dents = n.node("ShaderNodeTexVoronoi", ins={"Vector": p, "Scale": 3.2}, feature="SMOOTH_F1")
fine = n.noise(p, 22.0, detail=3, rough=0.6)
rustn = n.noise(p, 1.2, detail=5, rough=0.65)
rust = n.ramp(rustn.outputs["Fac"], (0.48, 0.72))
col = n.mix(rust, (0.020, 0.019, 0.019, 1), (0.070, 0.034, 0.017, 1))
hgt = n.math("ADD", n.math("MULTIPLY", dents.outputs["Distance"], 0.8), n.math("MULTIPLY", fine.outputs["Fac"], 0.1))
bump = n.node("ShaderNodeBump", ins={"Strength": 0.9, "Distance": 0.08, "Height": hgt})
rough = n.math("ADD", n.math("ADD", 0.34, n.math("MULTIPLY", rust, 0.3)), n.math("MULTIPLY", n.math("SUBTRACT", fine.outputs["Fac"], 0.5), 0.1))
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": rough, "Metallic": n.math("SUBTRACT", 0.92, n.math("MULTIPLY", rust, 0.4)),
                                            "Normal": bump.outputs[0]})
n.out(pb.outputs[0])
V, F = join(iron)
o = put("Temple Torch Iron", mesh_from("Temple Torch Iron", V, F, smooth=True, sharp_deg=38), TORCH, [m_iron], root)
if o.name not in RECV.objects:
    RECV.objects.link(o)
IRON_ONLY = coll("Temple Torch Iron Only", TC)            # for the small lights that give the iron its sheen
if o.name not in IRON_ONLY.objects:
    IRON_ONLY.objects.link(o)
old = bpy.data.objects.get("Temple Torch Heads")          # from the first design: kept, not rendered
if old:
    old.hide_render = True
    old.hide_viewport = True


def drive(idb, path, expr, index=-1, g=0):
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except Exception:
        pass
    fcu = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    dr = fcu.driver
    dr.type = "SCRIPTED"
    var = dr.variables.new()
    var.name = "lit"
    var.type = "SINGLE_PROP"
    var.targets[0].id = ctrl
    var.targets[0].data_path = f'["lit_{g}"]'
    dr.expression = expr


def time_node(n, name):
    tv = n.node("ShaderNodeValue", label=name)
    fc = tv.outputs[0].driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "frame / 30"
    return tv.outputs[0]


def sstep(n, x, lo, hi):
    return n.ramp(x, (lo, hi), interp="SMOOTH")


# ------------------------------------------------------------------ coals in the cup
cm = mat("Temple Coals")
n = NT(cm)
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "coal time")
pc = n.coord().outputs["Object"]
cell = n.node("ShaderNodeTexVoronoi", ins={"Vector": pc, "Scale": 4.5}, feature="DISTANCE_TO_EDGE")
glow = n.math("SUBTRACT", 1.0, sstep(n, cell.outputs["Distance"], 0.0, 0.22))
pulse = n.noise(n.comb(n.math("MULTIPLY", t, 0.9), n.math("MULTIPLY", oi.outputs["Random"], 9.0), 0.0), 1.0, detail=1.0)
k = n.math("MULTIPLY", n.math("MULTIPLY", n.math("ADD", 0.25, glow), n.math("ADD", 0.7, n.math("MULTIPLY", pulse.outputs["Fac"], 0.6))),
           oi.outputs["Alpha"])
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": (0.012, 0.008, 0.006, 1), "Roughness": 0.9})
pb.inputs["Emission Color"].default_value = (1.0, 0.36, 0.05, 1)
n.set(pb.inputs["Emission Strength"], n.math("MULTIPLY", k, G("COAL_GLOW", 9.0)))
n.out(pb.outputs[0])

# ------------------------------------------------------------------ the flame
# Third version. Fire is light, not paint: every layer only adds light, so where layers overlap the heart
# burns pale yellow and the thin edges stay deep orange and see through. Three layers per torch (a wide dim
# one behind, the body, a small hot heart), each with its own shape, plus a soft glow round the whole fire.
FW, FH = SHAPE["card"]
fm = mat("Temple Flame")
fm.surface_render_method = "BLENDED"
fm.use_backface_culling = False
n = NT(fm)
tc = n.coord()
uv = n.sep(tc.outputs["UV"])
u, v = uv[0], uv[1]
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "flame time")
seed = n.math("MULTIPLY", oi.outputs["Random"], 37.0)
x = n.math("MULTIPLY", n.math("SUBTRACT", u, 0.5), 2.0)
S1, S2, S3 = G("FLAME_SPEEDS", (0.9, 1.5, 1.9))
# the whole fire breathes: taller, then shorter
hp = n.math("ADD", 0.84, n.math("MULTIPLY", n.noise(n.comb(n.math("MULTIPLY", t, 1.5), seed, 0.0), 1.0, detail=1.0).outputs["Fac"], 0.32))
vv = n.math("MINIMUM", n.math("DIVIDE", v, hp), 1.0)
vy = n.math("POWER", vv, 0.8)                     # shapes stretch as they rise


def flow(n, fx, fy, speed, zk, zt, src, detail=2.0, rough=0.5):
    """Noise that streams upward: fx across, fy along the height."""
    return n.noise(n.comb(n.math("MULTIPLY", src, fx), n.math("SUBTRACT", n.math("MULTIPLY", vy, fy), n.math("MULTIPLY", t, speed)),
                          n.math("ADD", n.math("MULTIPLY", seed, zk), n.math("MULTIPLY", t, zt))), 1.0, detail=detail, rough=rough).outputs["Fac"]


w1 = flow(n, 1.0, 1.5, S1, 1.0, 0.21, x, detail=1.0)             # the whole fire leaning
w2 = flow(n, 2.4, 3.0, S2, 1.37, 0.45, x)                        # licks
xs = n.math("ADD", x, n.math("ADD", n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", w1, 0.5), G("FLAME_SWAY", SHAPE["sway"])),
                                                   n.math("ADD", 0.05, n.math("POWER", vv, 1.3))),
                             n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", w2, 0.5), 0.55), n.math("ADD", 0.05, vv))))
wv = n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", 1.0, n.math("POWER", vv, SHAPE["round"])), G("FLAME_WIDTH", SHAPE["width"])),
            n.math("MINIMUM", n.math("ADD", 0.72, n.math("MULTIPLY", vv, 2.4)), 1.0))
across = n.math("SUBTRACT", 1.0, n.math("POWER", n.math("DIVIDE", n.math("ABSOLUTE", xs), n.math("MAXIMUM", wv, 0.001)), 1.5))
tn = flow(n, 3.6, 1.3, S3, 2.1, 0.3, xs)                         # upright streaks: they split the top into tongues
tn = n.math("MINIMUM", n.math("MAXIMUM", n.math("ADD", n.math("MULTIPLY", n.math("SUBTRACT", tn, 0.5), G("FLAME_SPLIT", SHAPE["split"])), 0.5), 0.0), 1.0)
e = n.math("SUBTRACT", across, n.math("MULTIPLY", tn, n.math("ADD", 0.03, n.math("MULTIPLY", n.math("POWER", vv, 0.85), G("FLAME_TONGUES", SHAPE["tongues"])))))
rn = flow(n, 9.0, 2.2, S3 * 1.4, 3.3, 0.5, xs)                   # fine bright threads inside the fire
ridge = n.math("POWER", n.math("SUBTRACT", 1.0, n.math("ABSOLUTE", n.math("SUBTRACT", n.math("MULTIPLY", rn, 2.0), 1.0))), 2.0)
inten = n.math("MULTIPLY", n.math("MULTIPLY", n.math("POWER", n.math("MAXIMUM", n.math("MINIMUM", e, 1.0), 0.0), 1.5),
                                  n.math("ADD", 0.45, n.math("MULTIPLY", ridge, 1.0))),
               n.math("SUBTRACT", 1.0, n.math("MULTIPLY", vv, 0.35)))
core = n.math("MULTIPLY", sstep(n, across, 0.5, 1.0), n.math("POWER", n.math("MAXIMUM", n.math("SUBTRACT", 1.0, vv), 0.0), 2.5))
inten = n.math("ADD", inten, n.math("MULTIPLY", core, 0.6))
inten = n.math("MULTIPLY", inten, n.math("MULTIPLY", sstep(n, v, 0.0, 0.04), n.math("SUBTRACT", 1.0, sstep(n, v, 0.9, 1.0))))
cr = n.node("ShaderNodeValToRGB", ins={0: n.math("MINIMUM", inten, 1.0)})
els = cr.color_ramp.elements
# kept toward yellow: under this scene's view transform a bright pure red orange turns salmon pink
els[0].position, els[0].color = 0.0, (0.9, 0.14, 0.0, 1)
els[1].position, els[1].color = 1.0, (1.0, 0.8, 0.3, 1)
for pos, c_ in ((0.35, (1.0, 0.33, 0.02, 1)), (0.7, (1.0, 0.55, 0.08, 1))):
    e_ = els.new(pos)
    e_.color = c_
fl = n.noise(n.comb(n.math("MULTIPLY", t, 4.0), seed, 0.0), 1.0, detail=1.0)
bright = n.math("MULTIPLY", n.math("MULTIPLY", n.math("POWER", n.math("MAXIMUM", inten, 0.0), 1.3), G("FLAME_GAIN", 2.5)),
                n.math("ADD", 0.85, n.math("MULTIPLY", fl.outputs["Fac"], 0.3)))
bright = n.math("MULTIPLY", bright, oi.outputs["Alpha"])
fcol = n.mix(1.0, cr.outputs["Color"], oi.outputs["Color"], blend="MULTIPLY")        # each layer's own tint
em = n.node("ShaderNodeEmission", ins={"Color": fcol, "Strength": bright})
tp = n.node("ShaderNodeBsdfTransparent")
add = n.node("ShaderNodeAddShader")
n.link(tp.outputs[0], add.inputs[0])
n.link(em.outputs[0], add.inputs[1])
n.out(add.outputs[0])

# a soft glow in the air round each fire
gm = mat("Temple Fire Glow")
gm.surface_render_method = "BLENDED"
gm.use_backface_culling = False
n = NT(gm)
uv = n.sep(n.coord().outputs["UV"])
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "glow time")
rr = n.math("MULTIPLY", n.math("SQRT", n.math("ADD", n.math("POWER", n.math("SUBTRACT", uv[0], 0.5), 2.0), n.math("POWER", n.math("SUBTRACT", uv[1], 0.5), 2.0))), 2.0)
gl = n.math("POWER", n.math("MAXIMUM", n.math("SUBTRACT", 1.0, rr), 0.0), G("GLOW_FALLOFF", 2.6))
gf = n.noise(n.comb(n.math("MULTIPLY", t, 3.0), n.math("MULTIPLY", oi.outputs["Random"], 21.0), 0.0), 1.0, detail=1.0)
gs = n.math("MULTIPLY", n.math("MULTIPLY", gl, G("FIRE_GLOW", 0.28)), n.math("MULTIPLY", n.math("ADD", 0.8, n.math("MULTIPLY", gf.outputs["Fac"], 0.4)), oi.outputs["Alpha"]))
em = n.node("ShaderNodeEmission", ins={"Color": (1.0, 0.42, 0.09, 1), "Strength": gs})
tp = n.node("ShaderNodeBsdfTransparent")
add = n.node("ShaderNodeAddShader")
n.link(tp.outputs[0], add.inputs[0])
n.link(em.outputs[0], add.inputs[1])
n.out(add.outputs[0])

# ------------------------------------------------------------------ embers
EW, EH = 3.6, 9.5
emb = mat("Temple Embers")
emb.surface_render_method = "BLENDED"
emb.use_backface_culling = False
n = NT(emb)
uv = n.sep(n.coord().outputs["UV"])
u, v = uv[0], uv[1]
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "ember time")
seed = n.math("MULTIPLY", oi.outputs["Random"], 53.0)
x = n.math("MULTIPLY", n.math("SUBTRACT", u, 0.5), 2.0)
X = n.math("MULTIPLY", x, EW / 2)
Y = n.math("MULTIPLY", v, EH)
sway = n.math("ADD", n.math("MULTIPLY", n.math("SINE", n.math("ADD", n.math("MULTIPLY", Y, 0.9), n.math("ADD", seed, n.math("MULTIPLY", t, 1.1)))), 0.24),
              n.math("MULTIPLY", n.math("SINE", n.math("ADD", n.math("MULTIPLY", Y, 2.3), n.math("ADD", n.math("MULTIPLY", seed, 2.0), n.math("MULTIPLY", t, 0.7)))), 0.1))
K = G("EMBER_CELLS", 1.1)
pe = n.comb(n.math("MULTIPLY", n.math("ADD", X, n.math("MULTIPLY", sway, v)), K),
            n.math("MULTIPLY", n.math("SUBTRACT", Y, n.math("MULTIPLY", t, G("EMBER_RISE", 2.2))), K),
            n.math("ADD", seed, n.math("MULTIPLY", t, 0.12)))
vor = n.node("ShaderNodeTexVoronoi", ins={"Vector": pe, "Scale": 1.0}, feature="F1")
R = G("EMBER_RADIUS", 0.05)
dot = n.math("SUBTRACT", 1.0, sstep(n, vor.outputs["Distance"], R * 0.4, R))
cs = n.node("ShaderNodeSeparateColor", ins={0: vor.outputs["Color"]})
keep = n.math("GREATER_THAN", cs.outputs[0], G("EMBER_FEW", SHAPE["few"]))
fade = n.math("MULTIPLY", n.math("MULTIPLY", sstep(n, v, 0.1, 0.22), n.math("POWER", n.math("MAXIMUM", n.math("SUBTRACT", 1.0, v), 0.0), 1.3)),
              n.math("SUBTRACT", 1.0, n.math("MULTIPLY", x, x)))
b = n.math("MULTIPLY", n.math("MULTIPLY", dot, keep), n.math("MULTIPLY", fade, n.math("MINIMUM", oi.outputs["Alpha"], 1.0)))
ecol = n.mix(cs.outputs[1], (1.0, 0.4, 0.03, 1), (1.0, 0.58, 0.1, 1))
em = n.node("ShaderNodeEmission", ins={"Color": ecol, "Strength": n.math("MULTIPLY", b, G("EMBER_GLOW", 10.0))})
tp = n.node("ShaderNodeBsdfTransparent")
mx = n.node("ShaderNodeMixShader", ins={0: n.math("MINIMUM", b, 1.0), 1: tp.outputs[0], 2: em.outputs[0]})
n.out(mx.outputs[0])


def lamp(name, kind, loc, energy, color, g, recv, vol, flick, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
        TORCH.objects.link(o)
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    o.data.color = color
    o.data.volume_factor = vol
    for k_, val in kw.items():
        setattr(o.data, k_, val)
    o.light_linking.receiver_collection = recv
    ph = (sum(ord(ch) * (k_ + 1) for k_, ch in enumerate(name)) % 628) / 100.0      # each light its own flicker, the same every run
    if flick:
        expr = "%.1f * lit * (0.88 + 0.07 * sin(frame * 0.83 + %.2f) + 0.05 * sin(frame * 1.91 + %.2f))" % (energy, ph, ph * 2)
    else:
        expr = "%.1f * lit" % energy
    drive(o.data, "energy", expr, g=g)
    return o


def card(name, w, h, base, yaw, s, material, g, grow, tint=(1.0, 1.0, 1.0)):
    me = mesh_from(name, [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [(0, 1, 2, 3)],
                   uvs={"UVMap": [(0, 0), (1, 0), (1, 1), (0, 1)]})
    o = put(name, me, TORCH, [material], root)
    o.matrix_basis = Matrix.Translation(base) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Diagonal((s, s, s, 1.0))
    o.visible_shadow = False
    o.color = (tint[0], tint[1], tint[2], 1)
    for idx in (0, 2):
        try:
            o.driver_remove("scale", idx)
        except Exception:
            pass
    if grow:
        drive(o, "scale", "%.3f * lit" % s, index=2, g=g)
        drive(o, "scale", "%.3f * (0.35 + 0.65 * lit)" % s, index=0, g=g)
    drive(o, "color", "lit", index=3, g=g)
    return o


for i, g, s, S, top, coal, d in torches:
    to = CAM - top
    yaw = math.atan2(to.x, -to.y)
    fwd = Vector((to.x, to.y, 0)).normalized()
    card(f"Temple Flame Back {i:02d}", FW * 1.18, FH * 1.12, top - fwd * 0.12, yaw, S, fm, g, True, tint=(0.55, 0.47, 0.38))
    card(f"Temple Flame {i:02d}", FW, FH, top, yaw, S, fm, g, True)
    card(f"Temple Flame Core {i:02d}", FW * 0.66, FH * 0.72, top + fwd * 0.06, yaw, S, fm, g, True, tint=(1.0, 0.95, 0.8))
    card(f"Temple Fire Glow {i:02d}", 9.0, 9.0, top - Vector((0, 0, (4.5 - 0.45 * FH) * S)) - fwd * 0.2, yaw, S, gm, g, False)
    card(f"Temple Embers {i:02d}", EW, EH, top + fwd * 0.1, yaw, S, emb, g, False)
    n_c = 20
    cr_ = (SHAPE["coal"][0] if SHAPE["coal"] else 0.2) * S
    Vc = [(cr_ * math.cos(2 * math.pi * k_ / n_c), cr_ * math.sin(2 * math.pi * k_ / n_c), 0.0) for k_ in range(n_c)]
    co = put(f"Temple Coals {i:02d}", mesh_from(f"Temple Coals {i:02d}", Vc, [tuple(range(n_c))]), TORCH, [cm], root)
    co.matrix_basis = Matrix.Translation(coal if coal is not None else top)
    co.hide_render = coal is None
    co.visible_shadow = False
    co.color = (1, 1, 1, 1)
    drive(co, "color", "lit", index=3, g=g)
    lamp(f"Temple Torch Light {i:02d}", "POINT", top + Vector((0, 0, 1.5 * S)) + fwd * 0.35,
         G("TORCH_E", (2400.0, 1500.0, 700.0))[min(g, 2)], FIRE, g, RECV, G("TORCH_VOL", 2.0), True,
         shadow_soft_size=0.8, use_shadow=g == 0)
    if g <= 1:
        # the fire's sheen on the iron itself (reaches only the iron)
        lamp(f"Temple Torch Sheen {i:02d}", "POINT", top + fwd * 3.2 + Vector((0, 0, 0.7 * S)), G("SHEEN_E", 450.0), (1.0, 0.6, 0.28),
             g, IRON_ONLY, 0.0, True, shadow_soft_size=0.6, use_shadow=False)

# a soft glow for each bay of the long hall (a torch's own reach is short)
for k_, yb in enumerate((116.0, 145.0, 174.0, 203.0)):
    lamp(f"Temple Bay Glow {k_}", "POINT", (0.0, yb - 5.0, 15.0), G("BAY_E", 8500.0), FIRE, 2 + k_, RECV, G("BAY_VOL", 0.5), True,
         shadow_soft_size=4.0, use_shadow=False)

# the lights that already stood for firelight follow their pair
for nm, g in (("Temple Rim L", 0), ("Temple Rim R", 0), ("Temple Arch Warm", 0), ("Temple Arch Face", 1)):
    o = bpy.data.objects[nm]
    try:
        o.data.driver_remove("energy")
    except Exception:
        pass
    base_e = o.data.get("v11_base", o.data.energy)
    o.data["v11_base"] = base_e
    drive(o.data, "energy", "%.1f * lit" % base_e, g=g)

# the far doorway: faint cold moonlight instead of gold
MOON = (0.5, 0.66, 1.0)
for nm, e, vol in (("Temple Back Glow", G("MOON_E", 130000.0), 0.5), ("Temple Corridor Glow", 0.0, 0.0), ("Temple Back Floor", G("MOON_FLOOR_E", 45000.0), 0.0)):
    o = bpy.data.objects[nm]
    o.data.color = MOON
    o.data.energy = e
    o.data.volume_factor = vol
fg = bpy.data.materials["Temple Far Glow"]
emn = next(nd for nd in fg.node_tree.nodes if nd.bl_idname == "ShaderNodeEmission")
emn.inputs["Color"].default_value = (0.45, 0.62, 1.0, 1)
emn.inputs["Strength"].default_value = G("FAR_GLOW", 1.6)
for nm in ("Temple Cool L", "Temple Cool R"):
    bpy.data.objects[nm].data.energy = G("COOL_E", 8000.0)
result = {"torches": len(SPOTS)}
