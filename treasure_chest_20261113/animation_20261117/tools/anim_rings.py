"""Side rings: physical pendulum driven by the chest's real motion, baked into section 01 Landing.
Run inside Blender after anim_landing.py (it samples the evaluated rig).

Each ring hangs from its rolled cover and swings about the chest's depth axis. The apparent
gravity at the pivot (gravity minus the pivot's acceleration) and the chest's own angular
acceleration drive it; the end wall stops the inward swing with a soft clack."""
import bpy, math, sys
from mathutils import Vector, Matrix
sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools")
import importlib, anim_lib
importlib.reload(anim_lib)
from anim_lib import Keys, build

S = "01 Landing"
scn = bpy.data.scenes["Chest Reveal"]
G = 77.9                   # real gravity for a 0.7 m chest (same as the landing physics)
SUB = 4                     # samples per frame
INNER = 0.0                 # the ring rests against its mount plate: it cannot swing toward the wall
OUTER = math.radians(globals().get("RING_OUTER_DEG", 14.0))  # outward stop: v2 to v6 the curved cover (14 deg);
                            # v7 the straight hinge barrel: 170 (rivets above), see v7_rings.py
REST = 0.3                  # bounce off the wall
DAMP = 1.6                  # hinge friction (1/s): rings keep swinging a little after the chest settles
D_COM, I_PIV = 0.481, 0.346 # pivot to ring centre, inertia per unit mass about the top bar
if globals().get("RING_PIVOT_UP"):  # v7: pivot raised onto the hinge barrel's axis (v7_rings.py)
    _icm = I_PIV - D_COM ** 2
    D_COM += RING_PIVOT_UP
    I_PIV = _icm + D_COM ** 2
F_END = globals().get("RING_F_END", 95)

shake = bpy.data.objects["Reveal Chest Shake"]
piv = {"L": bpy.data.objects["Reveal Ring Pivot L"], "R": bpy.data.objects["Reveal Ring Pivot R"]}
for p in piv.values():      # sample with the rings at rest so their own keys never matter
    if p.animation_data:
        for t in p.animation_data.nla_tracks:
            t.mute = True

samples = []
for f in range(1, F_END + 1):
    for s in range(SUB):
        scn.frame_set(f, subframe=s / SUB)
        R = shake.matrix_world.to_3x3()
        samples.append((f + s / SUB, R.copy(), {k: (shake.matrix_world @ p.location) for k, p in piv.items()}))
h = 1.0 / 30.0 / SUB

K = globals().get("ANIM_K") or Keys()   # shared when run from anim_all.py
report = {}
for side in ("L", "R"):
    out = 1.0 if side == "L" else -1.0       # sign of phi that swings the bottom outward
    pos = [smp[2][side] for smp in samples]
    beta = []
    for _, R, _ in samples:
        xa = R.col[0]
        beta.append(-math.asin(max(-1, min(1, xa.z))))
    phi = None
    phid = 0.0
    keys = []
    peak = 0.0
    for i in range(len(samples)):
        if i == 0:
            acc = Vector((0, 0, 0))
        else:
            j0, j1, j2 = max(i - 2, 0), i - 1, i
            acc = (pos[j2] - 2 * pos[j1] + pos[j0]) / (h * h) if i >= 2 else Vector((0, 0, 0))
        R = samples[i][1]
        gapp = Vector((0, 0, -G)) - acc
        gb = R.transposed() @ gapp
        if phi is None:
            phi = -beta[0]                     # hangs plumb when the clip starts
            if globals().get("RING_START_STILL"):
                # v7: the toss spun the chest, not the loose ring: the ring starts still in the world,
                # hanging plumb (or resting on its plate), so relative to the chest it turns backward
                lo, hi = (-INNER, OUTER) if out > 0 else (-OUTER, INNER)
                phi = max(lo, min(hi, phi))
                phid = -(beta[1] - beta[0]) / h
        bdd = 0.0 if i < 2 else (beta[i] - 2 * beta[i - 1] + beta[i - 2]) / (h * h)
        n = 8
        for _ in range(n):
            phidd = (D_COM / I_PIV) * (-math.cos(phi) * gb.x + math.sin(phi) * gb.z) - bdd - DAMP * phid
            phid += phidd * h / n
            phi += phid * h / n
            if out * phi < -INNER:             # bottom swings back onto the mount plate
                phi = -INNER * out
                if out * phid < 0:
                    phid = -phid * REST
            if out * phi > OUTER:              # top bar hits the cover lip
                phi = OUTER * out
                if out * phid > 0:
                    phid = -phid * REST
        if i % SUB == 0:
            keys.append((samples[i][0], phi))
            if samples[i][0] > 14:
                peak = max(peak, abs(phi))
    # ease the tail to exact rest
    f_last = keys[-1][0]
    keys.append((f_last + 12, 0.0))
    K.add(S, piv[side].name, "rotation_euler", 1, keys)
    report[side] = (round(math.degrees(peak), 1), [round(math.degrees(v), 1) for f, v in keys[14:60:3]])

for p in piv.values():
    if p.animation_data:
        for t in p.animation_data.nla_tracks:
            t.mute = False
if not globals().get("ANIM_DEFER"):
    build(K, [S])
print("rings", report)
