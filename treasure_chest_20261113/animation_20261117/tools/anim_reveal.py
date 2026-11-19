"""Sections 02 Mystery, 03 Unlock, 04 Opening, 05 Badge Reveal (v2, badge and light v5), run after anim_landing.py.

Every channel continues from the value the previous section ended on, so each section can later be
triggered on its own. Signs: lid and hasp open with negative rotation x; the bolt retracts with
negative location x; FX Controls properties drive every glow (build_fx.py).
Measured limits on this chest: the hasp tongue is held by the bolt (it touches the bolt beyond about
3 degrees until the bolt retracts) and, once free, can swing up to about 128 degrees before it
meets its own mount; the lid is clear of the body to beyond 125 degrees."""
import bpy, math, sys
from mathutils import Vector
sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools")
import importlib, anim_lib
importlib.reload(anim_lib)
from anim_lib import Keys, build, DEG, damped, markers

K = globals().get("ANIM_K") or Keys()   # shared when run from anim_all.py
FX = "Reveal FX Controls"
LID, HASP, BOLT = "Reveal Lid Hinge", "Reveal Hasp Pivot", "Reveal Lock Bolt"
BADGE, DOLLY, GLINT = "Reveal Badge Root", "Reveal Camera Dolly", "Reveal Badge Glint"

T = dict(glow=40, pulse1=52, rattle1=56, push=62, pulse2=72, rattle2=75, flare=82,
         click=86, pop=87, swing=94, seat=102, open0=108, whoosh=118, stop=135,
         badge0=128, peak=176, climax=179, hold=197, end=222)
HASP_SEAT = -124 * DEG         # resting against its mount (contact begins near -130)

# ------------------------------------------------------------------ 02 Mystery
S = "02 Mystery"
K.add(S, FX, '["keyhole_glow"]', 0, [
    (T["glow"], 0.0, 0.0, 0.0), (T["glow"] + 10, 0.16), (T["pulse1"], 0.42, 0.0, 0.0),
    (T["pulse1"] + 5, 0.24), (T["push"] + 4, 0.34), (T["pulse2"], 0.95, 0.0, 0.0),
    (T["pulse2"] + 4, 0.62), (T["flare"], 0.75)])
K.add(S, FX, '["seam_glow"]', 0, [
    (T["push"], 0.0), (T["push"] + 5, 0.55), (T["push"] + 8, 0.45), (T["pulse2"], 0.8),
    (T["rattle2"] + 1, 1.0), (T["flare"], 0.8)])
K.add(S, FX, '["interior_glow"]', 0, [
    (T["glow"], 0.0), (T["push"], 0.08), (T["push"] + 5, 0.22), (T["flare"], 0.4)])
r1, r2 = T["rattle1"], T["rattle2"]
# the tongue is captured by the bolt: only its small play (under 3 degrees) shows
K.add(S, HASP, "rotation_euler", 0, [
    (r1 - 1, 0.0), (r1, -1.9 * DEG), (r1 + 1, -0.2 * DEG), (r1 + 2, -1.1 * DEG), (r1 + 4, 0.0),
    (r2 - 1, 0.0), (r2, -2.5 * DEG), (r2 + 1, -0.3 * DEG), (r2 + 2, -1.6 * DEG), (r2 + 3, -0.4 * DEG),
    (r2 + 5, 0.0), (T["flare"], 0.0)])
K.add(S, BOLT, "location", 0, [(r2 - 1, 0.0), (r2, -0.012), (r2 + 1, 0.004), (r2 + 2, -0.006), (r2 + 4, 0.0),
                               (T["flare"], 0.0)])
p = T["push"]
K.add(S, LID, "rotation_euler", 0, [
    (p - 1, 0.0, 0.0, 0.0), (p + 5, -2.2 * DEG, None, 0.0), (p + 9, -1.55 * DEG), (r2 - 1, -1.65 * DEG),
    (r2 + 1, -2.7 * DEG), (r2 + 3, -1.45 * DEG), (r2 + 5, -1.8 * DEG), (T["flare"], -1.7 * DEG)])

# ------------------------------------------------------------------ 03 Unlock
S = "03 Unlock"
fl, ck, pp, sw, st = T["flare"], T["click"], T["pop"], T["swing"], T["seat"]
# 1) the lock strains: keyhole flares, bolt creeps
K.add(S, FX, '["keyhole_glow"]', 0, [(fl, 0.75), (ck - 1, 1.25), (ck, 1.9, 0.0, 0.0), (ck + 4, 1.0),
                                    (st, 0.55), (T["open0"], 0.4)])
K.add(S, BOLT, "location", 0, [(fl, 0.0, None, 0.0), (ck - 1, -0.018), (ck, -0.022, None, -0.07),
                               (ck + 1, -0.158, -0.05, 0.0), (ck + 2, -0.142), (ck + 4, -0.147),
                               (T["open0"], -0.147)])
# 2) click: the clasp drops a hair as the bolt leaves, then pops out of the catch
# 3) it swings up and over, slows, and lands against its mount with a small bounce
K.add(S, HASP, "rotation_euler", 0, [
    (fl, 0.0), (ck - 1, -0.6 * DEG), (ck, 0.0, 0.0, 0.0),
    # the freed clasp kicks clear of the lock face (a dark gap opens) and hangs open for a beat
    (pp + 1, -14.0 * DEG, -9.0 * DEG, -8.0 * DEG), (pp + 2, -26.0 * DEG, -5.0 * DEG, 0.0),
    (pp + 4, -18.0 * DEG, 0.0, 0.0), (pp + 6, -21.0 * DEG, 0.0, 0.0),
    (sw, -20.0 * DEG, 0.0, -4.0 * DEG),
    # then it swings up and over, slows, and lands against its mount with a small bounce
    (sw + 2, -44 * DEG, -16 * DEG, -17 * DEG),
    (sw + 5, -95 * DEG, -15 * DEG, -12 * DEG),
    (st, HASP_SEAT, -6.0 * DEG, 2.0 * DEG),
    (st + 2, HASP_SEAT + 5 * DEG, 0.0, 0.0),
    (st + 4, HASP_SEAT, -1.5 * DEG, 0.8 * DEG),
    (st + 6, HASP_SEAT + 1.0 * DEG, 0.0, 0.0), (T["open0"], HASP_SEAT)])
K.add(S, FX, '["seam_glow"]', 0, [(fl, 0.8), (ck, 1.0), (ck + 3, 1.3), (st, 1.25), (T["open0"], 1.6)])
K.add(S, FX, '["interior_glow"]', 0, [(fl, 0.4), (ck + 3, 0.55), (T["open0"], 0.75)])
# the freed lid lifts a little on the pressure and waits, trembling once
K.add(S, LID, "rotation_euler", 0, [
    (fl, -1.7 * DEG), (ck, -1.8 * DEG, None, -0.5 * DEG), (ck + 3, -3.2 * DEG, 0.0, 0.0),
    (st, -2.6 * DEG), (st + 3, -3.3 * DEG), (st + 4, -2.9 * DEG), (T["open0"], -3.0 * DEG, 0.0, None)])

# ------------------------------------------------------------------ 04 Opening
S = "04 Opening"
o0, wh, sp = T["open0"], T["whoosh"], T["stop"]
STOP = -108 * DEG
K.add(S, LID, "rotation_euler", 0, [
    (o0, -3.0 * DEG, None, -0.25 * DEG),           # heavy: it barely moves at first
    (o0 + 5, -5.5 * DEG, -0.7 * DEG, -0.7 * DEG),
    (wh, -10.0 * DEG, -1.3 * DEG, -2.2 * DEG),      # resistance gives way, the push takes over
    (wh + 4, -24 * DEG, -6.0 * DEG, -6.0 * DEG),
    (wh + 8, -55 * DEG, -9.0 * DEG, -9.0 * DEG),
    (wh + 12, -90 * DEG, -7.5 * DEG, -7.5 * DEG),
    (wh + 15, -105.5 * DEG, -3.5 * DEG, -3.5 * DEG),  # natural deceleration
    (sp, STOP - 0.5 * DEG, -0.6 * DEG, 0.3 * DEG),    # comes to the stop gently
    (sp + 3, STOP + 1.2 * DEG, 0.0, 0.0),
    (sp + 6, STOP - 0.1 * DEG, 0.0, 0.0), (sp + 10, STOP, 0.0, 0.0)])
K.add(S, HASP, "rotation_euler", 0, [(o0, HASP_SEAT), (sp + 10, HASP_SEAT)])
K.add(S, FX, '["keyhole_glow"]', 0, [(o0, 0.4), (wh + 4, 0.15), (sp, 0.0)])
K.add(S, FX, '["seam_glow"]', 0, [(o0, 1.6), (o0 + 6, 1.9), (wh + 4, 0.5), (wh + 8, 0.0)])
K.add(S, FX, '["interior_glow"]', 0, [
    (o0, 0.75), (o0 + 6, 0.95), (wh + 4, 1.3), (wh + 10, 1.55, 0.0, 0.0), (sp + 8, 1.15), (sp + 14, 1.05)])
K.add(S, FX, '["beam"]', 0, [
    (wh - 2, 0.0, 0.0, 0.0), (wh + 4, 0.25), (wh + 10, 0.75), (sp + 2, 0.95, 0.0, 0.0), (sp + 14, 0.8)])

# ------------------------------------------------------------------ 05 Badge Reveal
# Version 5 (owner, 2026-11-17): the badge rises out of the smoke slowly, turning a little over half
# a turn and easing into the front facing pose, then a small controlled bounce: up past its rest,
# gently down, a much smaller correction, settled. The overhead light comes up with it.
S = "05 Badge Reveal"
cam = bpy.data.objects[DOLLY]
CAM_LOC = Vector(cam["rest_loc"])                            # stored by build_stage.py
CAM_ROT = cam["rest_rot"]
facing = math.atan2(CAM_LOC.x, -CAM_LOC.y)                  # badge front (-y) toward the camera
b0, pk, cx, hd, end = T["badge0"], T["peak"], T["climax"], T["hold"], T["end"]
ZTOP = 6.15
K.add(S, BADGE, "location", 0, [(b0, 0.0), (end, 0.0)])
K.add(S, BADGE, "location", 1, [(b0, 0.0), (end, 0.0)])
K.add(S, BADGE, "location", 2, [
    (b0, -1.25, None, 0.03), (b0 + 15, 0.3, 0.16, 0.17),       # emerges from the smoke, unhurried
    (b0 + 30, 3.2, 0.21, 0.2), (b0 + 42, 5.65, 0.12, 0.11),     # deliberate rise, easing off
    (pk, ZTOP + 0.15, 0.0, 0.0),                                # carries a little past its rest
    (pk + 7, ZTOP - 0.06, 0.0, 0.0),                            # gently down
    (pk + 14, ZTOP + 0.015, 0.0, 0.0),                          # a much smaller correction
    (hd, ZTOP, 0.0, 0.0),                                       # settled
    (hd + 13, ZTOP + 0.025, 0.0, 0.0), (end, ZTOP + 0.005, 0.0, 0.0)])   # barely floating
# a little over half a turn, slow, easing all the way into the front
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
# light: the overhead light comes up through the opening and with the badge, a soft highlight
# sweeps the face as it turns to the front, then everything settles to a steady presentation
# (the overhead light's keys live in the 04 Opening strip, so they never cover the earlier sections:
#  one NLA strip per object and section starts at its earliest key)
K.add("04 Opening", FX, '["overhead"]', 0, [(T["whoosh"] - 4, 0.0, 0.0, 0.0), (T["stop"], 0.32),
                                            (b0 + 22, 0.62), (cx, 1.0, 0.0, 0.0), (hd, 0.94, 0.0, 0.0), (end, 0.94)])
K.add(S, FX, '["flash"]', 0, [(cx - 4, 0.0, 0.0, 0.0), (cx + 1, 0.3, 0.0, 0.0), (cx + 16, 0.0, 0.0, 0.0)])
K.add(S, FX, '["beam"]', 0, [(cx - 8, 0.8), (cx + 1, 0.95, 0.0, 0.0), (cx + 16, 0.7), (end, 0.6)])
K.add(S, FX, '["interior_glow"]', 0, [(cx - 8, 1.05), (cx + 1, 1.2, 0.0, 0.0), (cx + 16, 1.0), (end, 0.95)])
K.add(S, FX, '["glint"]', 0, [(cx - 5, 0.0, 0.0, 0.0), (cx + 1, 0.55, 0.0, 0.0), (cx + 11, 0.0, 0.0, 0.0)])
K.add(S, GLINT, "location", 0, [(cx - 5, -4.5, None, 0.6), (cx + 11, 4.5, 0.5, None)])

# camera: landing framing, then a gentle push in and tilt up from the unlock to the hero pose
start_loc = CAM_LOC.copy()
start_rot = list(CAM_ROT)
end_loc = Vector(cam["hero_loc"])
end_rot = list(cam["hero_rot"])
mid_loc = Vector(cam["mid_loc"])
mid_rot = list(cam["mid_rot"])
for i in range(3):
    # after the landing the camera eases from the wider landing framing to a centred closer one,
    K.add("02 Mystery", DOLLY, "location", i, [(32, start_loc[i], None, 0.0), (80, mid_loc[i], 0.0, None)])
    K.add("02 Mystery", DOLLY, "rotation_euler", i, [(32, start_rot[i], None, 0.0), (80, mid_rot[i], 0.0, None)])
    # then pushes in gently and tilts up to the hero framing from the unlock to the hold
    K.add(S, DOLLY, "location", i, [(T["click"] - 2, mid_loc[i], None, 0.0), (hd, end_loc[i], 0.0, None)])
    K.add(S, DOLLY, "rotation_euler", i, [(T["click"] - 2, mid_rot[i], None, 0.0), (hd, end_rot[i], 0.0, None)])

# badge waits hidden inside the chest at the size it starts rising with
bo = bpy.data.objects[BADGE]
bo.location = (0, 0, -1.25)
bo.rotation_euler = (-10 * DEG, 0, facing)
bo.scale = (0.0, 0.0, 0.0)

made = [] if globals().get("ANIM_DEFER") else build(K, ["02 Mystery", "03 Unlock", "04 Opening", "05 Badge Reveal"])

scn = bpy.data.scenes["Chest Reveal"]
LD = globals().get("LANDING", {})
imp = [im for im in LD.get("impacts", []) if im["strength"] > 0.2]
mk = [("Landing: fall", 1)]
for name, im in zip(("BOOM 1", "BOOM 2", "boom 3"), imp):
    mk.append((name, round(im["frame"])))
if LD.get("settle"):
    mk.append(("Settled", round(LD["settle"])))
mk += [("Mystery: keyhole glow", T["glow"]), ("Rattle 1", T["rattle1"]), ("Lid pressure", T["push"]),
       ("Rattle 2", T["rattle2"]), ("Unlock: flare", T["flare"]), ("Unlock: click", T["click"]),
       ("Clasp swings up", T["swing"]), ("Clasp seated", T["seat"]), ("Opening: heavy start", T["open0"]),
       ("Opening: push", T["whoosh"]), ("Lid open", T["stop"]), ("Badge rises", T["badge0"]),
       ("Badge peak", T["peak"]), ("Badge faces front", T["climax"]), ("Bounce settled", T["hold"]), ("End", T["end"])]
markers(scn, mk)
scn.frame_end = T["end"]
print("reveal v2 timeline", T)
