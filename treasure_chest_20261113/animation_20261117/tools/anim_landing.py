"""01 Landing (v2): the chest's fall and landing come from a real rigid body simulation.

physics/landing.json is made by rigid2d.py (Newton impacts with restitution 0.2, Coulomb friction
0.6, real gravity for a 0.7 m chest, the chest's real footprint and centre of mass), dropped tilted
20 degrees with a gentle tumble (1.5 rad/s) and a slight sideways drift (3 units/s):
    python3 tools/rigid2d.py physics/landing.json w0=1.5 vx0=-3 roll=20 e=0.2 mu=0.6 drop=11 seconds=2.0
It gives: corner hit (43.5 units/s), far side slam (18.7), rock back (13.0), tiny tap (2.5).

The simulated motion is baked onto 'Reveal Chest Drop' at 4 samples per frame with straight
segments (exact physics, no curve smoothing). Rock and Shake stay at zero during the landing.
Lid, hasp, camera shake and dust are timed and scaled from the simulated impacts, which are also
written to physics/landing_events.json for anim_fx.py."""
import bpy, math, sys, json
sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools")
import importlib, anim_lib
importlib.reload(anim_lib)
from anim_lib import Keys, build, DEG, damped

S = "01 Landing"
K = globals().get("ANIM_K") or Keys()   # shared when run from anim_all.py
ROOT = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/"
sim = json.load(open(ROOT + "physics/landing.json"))
H = sim["params"]["com"]
T0 = globals().get("LANDING_T0", 0.20)   # simulation time shown on frame 1 (v6: 0, the top of the drop, out of view)
F0 = 1
fin = sim["frames"][-1]["loc"]
DX = -fin[0]                 # shift so the chest comes to rest exactly at its home position


def frame_of(t):
    return F0 + (t - T0) * 30.0


# ---- bake the rigid body onto Drop (bottom centre pose in the chest frame) ----
lx, lz, ry = [], [], []
settle = None
for f in sim["frames"]:
    t = f["t"]
    if t < T0 - 1e-6:
        continue
    w, qx, qy, qz = f["quat"]
    roll = 2 * math.atan2(qy, w)
    X, Z = f["loc"][0] + DX, f["loc"][2]
    bx = X - H * math.sin(roll)
    bz = Z - H * math.cos(roll)
    fr = frame_of(t)
    lx.append((fr, bx, "LIN")); lz.append((fr, bz, "LIN")); ry.append((fr, roll, "LIN"))
    if settle is None and t > 0.9 and abs(roll) < 1e-4 and abs(bz) < 1e-4:
        settle = fr
    if settle is not None and fr > settle + 2:
        break
K.add(S, "Reveal Chest Drop", "location", 0, lx)
K.add(S, "Reveal Chest Drop", "location", 2, lz)
K.add(S, "Reveal Chest Drop", "rotation_euler", 1, ry)
K.add(S, "Reveal Chest Drop", "rotation_euler", 2, [(F0, 0.0)])
for i in (0, 1):
    K.add(S, "Reveal Chest Rock", "rotation_euler", i, [(F0, 0.0)])
    K.add(S, "Reveal Chest Shake", "rotation_euler", i, [(F0, 0.0)])

# ---- impacts (strong ones drive the secondary motion) ----
imps = [dict(frame=frame_of(im["t"]), edge=im["edge"], speed=im["speed"]) for im in sim["impacts"]]
top = imps[0]["speed"]
for im in imps:
    im["strength"] = im["speed"] / top
json.dump({"impacts": imps, "settle": settle, "T0": T0, "DX": DX}, open(ROOT + "physics/landing_events.json", "w"), indent=1)
LANDING = dict(impacts=imps, settle=settle)
strong = [im for im in imps if im["strength"] > 0.2]

# ---- lid: inertia lifts it a hair off the rim at each impact, then it clacks back ----
lid = [(F0, 0.0)]
hp = [(F0, 0.0)]
for im in strong:
    f, a = round(im["frame"]), im["strength"]
    if f <= lid[-1][0]:
        continue
    la = a * globals().get("LID_RATTLE", 1.0)    # v6: 0, the latched lid stays shut on impact
    lid += [(f, 0.0, 0.0, 0.0), (f + 1, -0.9 * DEG * la), (f + 2, -0.3 * DEG * la), (f + 3, 0.0, 0.0, 0.0)]
    ha = a * globals().get("HASP_RATTLE", 1.0)   # v6: 0, the locked clasp stays still (no overlap with the bolt)
    hp += [(f, 0.0), (f + 1, -1.6 * DEG * ha), (f + 2, -0.5 * DEG * ha), (f + 3, 0.0)]
lid.append((settle + 6, 0.0)); hp.append((settle + 6, 0.0))
K.add(S, "Reveal Lid Hinge", "rotation_euler", 0, lid)
K.add(S, "Reveal Hasp Pivot", "rotation_euler", 0, hp)

# ---- camera: a short jolt on the heavy first impact, much less after ----
cz, cx, cr = [(F0, 0.0)], [(F0, 0.0)], [(F0, 0.0)]
for im in strong:
    f, a = round(im["frame"]), im["strength"] ** 1.5 * globals().get("CAM_SHAKE", 1.0)   # v6: 0, a still camera
    for lst, amp, per, ph in ((cz, 0.06, 2.6, 0.0), (cx, 0.025, 3.3, 0.9), (cr, 0.15 * DEG, 2.9, 0.4)):
        lst += [p for p in damped(f, amp * a, per, 2.3, 7, phase=ph) if p[0] > lst[-1][0]]
K.add(S, "Reveal Camera Shake", "location", 1, cz)
K.add(S, "Reveal Camera Shake", "location", 0, cx)
K.add(S, "Reveal Camera Shake", "rotation_euler", 2, cr)

made = [] if globals().get("ANIM_DEFER") else build(K, [S])
print("landing (physics): impacts", [(round(im["frame"], 1), im["edge"], round(im["strength"], 2)) for im in imps],
      "settled f", round(settle, 1))
