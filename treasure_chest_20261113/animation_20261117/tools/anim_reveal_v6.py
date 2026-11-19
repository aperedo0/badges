"""Version 6 sections 03 Unlock, 04 Opening, 05 Badge Reveal (owner's review of version 5, 2026-11-18).
Run from anim_all.py with REVEAL = "anim_reveal_v6.py", after tools/v6_setup.py stored the camera framings.

Sequence: the chest lands (physics, 01 Landing) and settles large and centred; a short hold; the gold
clasp unlocks as a clear two step action (bolt clicks back, clasp kicks free and hangs, then swings
up and over onto its mount); a pause; only then the lid opens (it stays shut until then, no pressure
lift); as the lid starts the camera pulls straight back and up (translation only, no rotation) to
the wide framing; the badge rises, turns into the front pose and settles with a small bounce.
No glows, smoke or particle effects (switched off in v6_setup.py). The mystery beat of version 5
(keyhole glow and rattles) is left out: the owner's sequence goes from the landing to the unlock.
"""
import bpy, math, sys
from mathutils import Vector
sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools")
import importlib, anim_lib
importlib.reload(anim_lib)
from anim_lib import Keys, build, DEG, markers

K = globals().get("ANIM_K") or Keys()
LID, HASP, BOLT = "Reveal Lid Hinge", "Reveal Hasp Pivot", "Reveal Lock Bolt"
BADGE, DOLLY = "Reveal Badge Root", "Reveal Camera Dolly"

T6 = dict(strain=44, click=50, pop=50, swing=60, seat=68, open0=84, whoosh=94, stop=111,
          zoom=(84, 136), badge0=110, peak=158, front=161, hold=179, end=207)
# the landing starts at the top of the drop (LANDING_T0 = 0) so the chest begins out of view under the
# low camera; everything after it moves later by the same 6 frames
SHIFT = globals().get("T6_SHIFT", 6)
T6 = {k: (tuple(x + SHIFT for x in v) if isinstance(v, tuple) else v + SHIFT) for k, v in T6.items()}
HASP_SEAT = -124 * DEG         # resting against its mount (contact begins near -130)
STOP = -108 * DEG

# ------------------------------------------------------------------ 03 Unlock
S = "03 Unlock"
sn, ck, pp, sw, st, o0 = T6["strain"], T6["click"], T6["pop"], T6["swing"], T6["seat"], T6["open0"]
# 1) the bolt creeps, clicks back and the freed clasp kicks clear of the lock face and hangs a beat.
#    With the lid shut the tongue grazes the bolt's slider between about 1 and 8 degrees out (measured),
#    so the release passes that range in one frame (0 at the click, 14 degrees the next frame).
K.add(S, BOLT, "location", 0, [(sn, 0.0, None, 0.0), (ck - 1, -0.018), (ck, -0.022, None, -0.07),
                               (ck + 1, -0.158, -0.05, 0.0), (ck + 2, -0.142), (ck + 4, -0.147), (o0, -0.147)])
K.add(S, HASP, "rotation_euler", 0, [
    (sn, 0.0), (ck, 0.0, 0.0, 0.0),                   # still while locked (any tilt touches the slider)
    (pp + 1, -14.0 * DEG, -9.0 * DEG, -8.0 * DEG), (pp + 2, -26.0 * DEG, -5.0 * DEG, 0.0),
    (pp + 4, -18.0 * DEG, 0.0, 0.0), (pp + 6, -21.0 * DEG, 0.0, 0.0),
    (sw, -20.0 * DEG, 0.0, -4.0 * DEG),
    # 2) it swings up and over, slows, and lands against its mount with a small bounce
    (sw + 2, -44 * DEG, -16 * DEG, -17 * DEG),
    (sw + 5, -95 * DEG, -15 * DEG, -12 * DEG),
    (st, HASP_SEAT, -6.0 * DEG, 2.0 * DEG),
    (st + 2, HASP_SEAT + 5 * DEG, 0.0, 0.0),
    (st + 4, HASP_SEAT, -1.5 * DEG, 0.8 * DEG),
    (st + 6, HASP_SEAT + 1.0 * DEG, 0.0, 0.0), (o0, HASP_SEAT)])
# the lid stays shut the whole time the clasp is engaged, and through the pause after it
K.add(S, LID, "rotation_euler", 0, [(sn, 0.0), (o0, 0.0)])

# ------------------------------------------------------------------ 04 Opening
S = "04 Opening"
wh, sp = T6["whoosh"], T6["stop"]
K.add(S, LID, "rotation_euler", 0, [
    (o0, 0.0, None, -0.15 * DEG),                     # heavy: it barely moves at first
    (o0 + 5, -2.0 * DEG, -0.55 * DEG, -0.6 * DEG),
    (wh, -8.5 * DEG, -1.4 * DEG, -2.2 * DEG),         # resistance gives way, the push takes over
    (wh + 4, -24 * DEG, -6.0 * DEG, -6.0 * DEG),
    (wh + 8, -55 * DEG, -9.0 * DEG, -9.0 * DEG),
    (wh + 12, -90 * DEG, -7.5 * DEG, -7.5 * DEG),
    (wh + 15, -105.5 * DEG, -3.5 * DEG, -3.5 * DEG),  # natural deceleration
    (sp, STOP - 0.5 * DEG, -0.6 * DEG, 0.3 * DEG),    # comes to the stop gently
    (sp + 3, STOP + 1.2 * DEG, 0.0, 0.0),
    (sp + 6, STOP - 0.1 * DEG, 0.0, 0.0), (sp + 10, STOP, 0.0, 0.0)])
K.add(S, HASP, "rotation_euler", 0, [(o0, HASP_SEAT), (sp + 10, HASP_SEAT)])
# camera: a still, straight on, low view looking up; as the lid starts it pulls back and up (eased both ends)
cam = bpy.data.objects[DOLLY]
CL, CW = Vector(cam["v6_close_loc"]), Vector(cam["v6_wide_loc"])
RC, RW = list(cam["v6_close_rot"]), list(cam["v6_wide_rot"])
z0, z1 = T6["zoom"]
for i in range(3):
    # low, looking up, until the lid starts; then up and back while it tilts down to the wide view
    K.add(S, DOLLY, "location", i, [(z0, CL[i], None, 0.0), (z1, CW[i], 0.0, None)])
    K.add(S, DOLLY, "rotation_euler", i, [(z0, RC[i], None, 0.0), (z1, RW[i], 0.0, None)])

# ------------------------------------------------------------------ 05 Badge Reveal
S = "05 Badge Reveal"
facing = math.atan2(CL.x, -CL.y)                     # badge front (-y) toward the camera
b0, pk, cx, hd, end = T6["badge0"], T6["peak"], T6["front"], T6["hold"], T6["end"]
ZTOP = 6.15
K.add(S, BADGE, "location", 0, [(b0, 0.0), (end, 0.0)])
K.add(S, BADGE, "location", 1, [(b0, 0.0), (end, 0.0)])
K.add(S, BADGE, "location", 2, [
    (b0, -1.25, None, 0.03), (b0 + 15, 0.3, 0.16, 0.17),
    (b0 + 30, 3.2, 0.21, 0.2), (b0 + 42, 5.65, 0.12, 0.11),
    (pk, ZTOP + 0.15, 0.0, 0.0), (pk + 7, ZTOP - 0.06, 0.0, 0.0), (pk + 14, ZTOP + 0.015, 0.0, 0.0),
    (hd, ZTOP, 0.0, 0.0), (hd + 13, ZTOP + 0.025, 0.0, 0.0), (end, ZTOP + 0.005, 0.0, 0.0)])
K.add(S, BADGE, "rotation_euler", 2, [
    (b0, facing + 200 * DEG, None, -3.0 * DEG),
    (b0 + 17, facing + 140 * DEG, -5.0 * DEG, -5.0 * DEG),
    (b0 + 32, facing + 55 * DEG, -4.5 * DEG, -4.5 * DEG),
    (b0 + 44, facing + 8 * DEG, -1.6 * DEG, -1.6 * DEG),
    (cx, facing, -0.2 * DEG, 0.0),
    (cx + 7, facing - 0.7 * DEG, 0.0, 0.0), (cx + 15, facing + 0.15 * DEG, 0.0, 0.0),
    (hd + 6, facing, 0.0, 0.0), (end, facing + 0.3 * DEG, 0.0, 0.0)])
K.add(S, BADGE, "rotation_euler", 0, [
    (b0, -10 * DEG), (b0 + 30, -3 * DEG), (pk, 1.0 * DEG, 0.0, 0.0), (pk + 7, -0.5 * DEG, 0.0, 0.0),
    (hd, 0.0, 0.0, 0.0), (hd + 13, 0.4 * DEG, 0.0, 0.0), (end, 0.0, 0.0, 0.0)])
K.add(S, BADGE, "scale", 0, [(1, 0.0, "CONST"), (b0 - 2, 0.26, None, 0.0), (b0, 0.26, None, 0.0),
                             (b0 + 30, 0.92), (b0 + 42, 1.0, 0.003, 0.0), (end, 1.0)])
for i in (1, 2):
    K.k[(S, BADGE)][("scale", i)] = K.k[(S, BADGE)][("scale", 0)]

bo = bpy.data.objects[BADGE]
bo.location = (0, 0, -1.25)
bo.rotation_euler = (-10 * DEG, 0, facing)
bo.scale = (0.0, 0.0, 0.0)

made = [] if globals().get("ANIM_DEFER") else build(K, ["03 Unlock", "04 Opening", "05 Badge Reveal"])

scn = bpy.data.scenes["Chest Reveal"]
LD = globals().get("LANDING", {})
imp = [im for im in LD.get("impacts", []) if im["strength"] > 0.2]
mk = [("Empty frame", 1)]
for name, im in zip(("Impact 1", "Impact 2", "Impact 3"), imp):
    mk.append((name, round(im["frame"])))
if LD.get("settle"):
    mk.append(("Settled", round(LD["settle"])))
mk += [("Unlock: bolt strains", sn), ("Unlock: click", ck), ("Clasp swings up", sw), ("Clasp seated", st),
       ("Lid opens, zoom out", o0), ("Lid open", sp), ("Badge rises", b0), ("Zoom out done", z1),
       ("Badge faces front", cx), ("Bounce settled", hd), ("End", end)]
markers(scn, mk)
scn.frame_end = end
print("reveal v6 timeline", T6)
