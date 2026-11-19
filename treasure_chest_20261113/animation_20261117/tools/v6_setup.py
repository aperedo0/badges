"""Version 6 setup (owner's review of version 5, 2026-11-18). Run inside Blender on chest_reveal_v6.blend,
before anim_all.py with REVEAL="anim_reveal_v6.py". Safe to run again; nothing is deleted.

0. Badge: the app's 3 Days Total model replaces Star Ascent (imported once; Star Ascent kept, excluded).
1. Effects off: smoke (domain, emitters, collision modifiers), every glow, light beam, haze, the
   overhead light, rays and backdrop, the keyhole and inner lights, flash and glint. Objects are hidden
   from render and viewport and their fluid modifiers disabled, so they can come back later.
   Dust and sparkles are switched off by anim_fx.py (FX_PARTICLES = False). Compositor glow off.
2. Ordinary lighting only: the studio lights as they are, and the badge's key, rake and rim lights at
   fixed neutral strengths (no longer driven by the effects).
3. Camera: straight on (0 degrees off frontal). Opening shot low, looking up at the chest (35 mm,
   camera 0.8 units above the floor); the zoom out rises and tilts down to 10 degrees above. Two framings
   solved by projecting the real geometry: CLOSE, the closed chest centred and about 88% of the frame
   width (side rings included); WIDE, the open chest and the risen badge inside the frame with a margin and
   the chest at about 72% of the width, so the zoom out reads. Stored on the dolly as v6_close_loc, v6_wide_loc, v6_rot; the animation only translates.
"""
import bpy, math
import numpy as np
from mathutils import Vector, Matrix

scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn

# ---------------------------------------------------------------- badge: the app's 3 Days Total model
# badge/sprout_badge_mobile.usdz is an exact copy of the app's Badge3DModelEmeraldSprout file (the model the
# app shows for 3 Days Total). Star Ascent is parked in an excluded collection (kept, not deleted).
BADGE_USDZ = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/badge/sprout_badge_mobile.usdz"
_bm = bpy.data.objects["Reveal Badge Model"]
_rb = bpy.data.collections["Reveal Badge"]
if not any(o.name.startswith("ReliefFront_0_emerald") for o in _rb.objects):
    _off = bpy.data.collections.get("Reveal Badge Star Ascent (off)") or bpy.data.collections.new("Reveal Badge Star Ascent (off)")
    if _off.name not in scn.collection.children:
        scn.collection.children.link(_off)
    for o in list(_bm.children):
        if o.name in _rb.objects:
            _off.objects.link(o)
            _rb.objects.unlink(o)
            if not o.name.startswith("StarAscent "):
                o.name = "StarAscent " + o.name

    def _lc(lc, name):
        if lc.collection.name == name:
            return lc
        for c in lc.children:
            r = _lc(c, name)
            if r:
                return r
    _lc(bpy.context.view_layer.layer_collection, _off.name).exclude = True
    bpy.context.view_layer.active_layer_collection = _lc(bpy.context.view_layer.layer_collection, _rb.name)
    bpy.ops.wm.usd_import(filepath=BADGE_USDZ)
    for o in _rb.objects:
        if o is not _bm and o.parent is None:
            o.parent = _bm
            o.matrix_parent_inverse = Matrix.Identity(4)

EFFECTS = ["Reveal Smoke Domain", "Reveal Smoke Emitter", "Reveal Smoke Emitter Front", "Reveal Smoke Emitter Left",
           "Reveal Smoke Emitter Right", "Reveal Keyhole Glow Card", "Reveal Keyhole Light",
           "Reveal Keyhole Inner Light", "Reveal Magic Core", "Reveal Interior Light", "Reveal Spill Light",
           "Reveal Seam Glow", "Reveal Light Beam", "Reveal Light Beam Outer", "Reveal Light Haze",
           "Reveal Flash Light", "Reveal Badge Glint", "Reveal Overhead Light", "Reveal Overhead Rays",
           "Reveal Backdrop"]
hidden = []
for n in EFFECTS:
    o = bpy.data.objects.get(n)
    if o is None:
        continue
    if o.animation_data and o.animation_data.action and n == "Reveal Smoke Domain":
        o.animation_data_clear()                    # its keyed hide_render would show it again
    o.hide_render = True
    o.hide_viewport = True
    hidden.append(n)
for o in scn.objects:                              # no fluid simulation runs or reads its cache
    for m in o.modifiers:
        if m.type == "FLUID":
            m.show_viewport = False
            m.show_render = False
scn.render.use_compositing = False
for o in bpy.data.collections["Reveal FX"].objects:   # dust puffs and sparkles: no animation, never shown
    if o.name.startswith(("Reveal Dust ", "Reveal Spark ")):
        if o.animation_data:
            for t in list(o.animation_data.nla_tracks):
                o.animation_data.nla_tracks.remove(t)
            o.animation_data.action = None
        o.hide_render = True
        o.hide_viewport = True

BADGE_LIGHTS = {"Reveal Badge Key": (520.0, (1.0, 0.96, 0.9)), "Reveal Badge Rake": (300.0, (1.0, 0.95, 0.88)),
                "Reveal Badge Rim": (260.0, (0.9, 0.93, 1.0))}
for n, (e, col) in BADGE_LIGHTS.items():
    d = bpy.data.objects[n].data
    try:
        d.driver_remove("energy")
    except Exception:
        pass
    d.energy, d.color = e, col

# ---------------------------------------------------------------- camera framings
# Owner, 2026-11-18 (second review): the opening shot looks UP at the chest from low, as if it were a
# little bigger than the viewer, whole chest in frame; the zoom out then rises and tilts gently down
# to the elevated wide view that sees into the open chest and frames the badge.
NF = Vector((0.529919175863294, -0.8480481513760686, 0.0))   # chest front normal (world)
UF = Vector((0.8480481513760686, 0.529919175863294, 0.0))    # chest +x (world)
FLOOR = -2.455
AZ = 0.0
LENS = globals().get("CAM_LENS", 35.0)    # a little wider than 50 mm: closer camera, stronger low angle
CLOSE_HEIGHT = globals().get("CLOSE_HEIGHT", 0.8)   # opening camera height above the floor (units)
WIDE_EL = 10.0                            # wide view: 10 degrees above
CLOSE_WIDTH = 0.88               # share of the frame width the closed chest fills
WIDE_WIDTH = 0.72                # after the zoom out the chest is clearly smaller (a real pull back)
WIDE_MARGIN = 0.06               # and the open chest and badge keep at least this border
cam = scn.camera
cam.data.lens = LENS
TAN_V = (cam.data.sensor_width / 2) / cam.data.lens          # AUTO fit: the sensor spans the long (vertical) side
TAN_H = TAN_V * scn.render.resolution_x / scn.render.resolution_y


def basis(el):
    d_ = (math.cos(math.radians(el)) * (math.cos(math.radians(AZ)) * NF + math.sin(math.radians(AZ)) * UF)
          + math.sin(math.radians(el)) * Vector((0, 0, 1)))
    rot = (-d_).to_track_quat("-Z", "Y")
    R = rot.to_matrix()
    return rot, np.array(R.col[0]), np.array(R.col[1]), -np.array(R.col[2])


def points(colls, frame, step=25):
    scn.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    P = []
    for cn in colls:
        for o in bpy.data.collections[cn].all_objects:
            if o.type != "MESH" or o.hide_render:
                continue
            oe = o.evaluated_get(dg)
            mw = np.array(oe.matrix_world)
            vs = oe.data.vertices
            co = np.zeros(len(vs) * 3)
            vs.foreach_get("co", co)
            co = co.reshape(-1, 3)[::step]
            P.append((mw[:3, :3] @ co.T).T + mw[:3, 3])
    return np.vstack(P)


def screen(P, C, B):
    _, right, up, fwd = B
    q = P - C
    z = q @ fwd
    return (q @ right) / (z * TAN_H), (q @ up) / (z * TAN_V)    # -1..1 across the frame


def solve(P, fit, B):
    """camera position (orientation B fixed) that centres P and scales it by fit(sx, sy) -> factor."""
    _, right, up, fwd = B
    c = P.mean(0)
    C = c - fwd * 30.0
    for _ in range(60):
        sx, sy = screen(P, C, B)
        cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2
        depth = (c - C) @ fwd
        C = C + right * cx * depth * TAN_H + up * cy * depth * TAN_V        # centre
        sx, sy = screen(P, C, B)
        k = fit(sx, sy)                                                      # >1: too big, back off
        depth = (c - C) @ fwd
        C = C - fwd * depth * (k - 1.0) * 0.8
    sx, sy = screen(P, C, B)
    return C, (sx.min(), sx.max(), sy.min(), sy.max())


CHEST = ["Reveal Chest Body", "Reveal Chest Lid", "Reveal Lock And Hasp", "Reveal Rings"]
P_close = points(CHEST, globals().get("CLOSE_FRAME", 40))
fit_close = lambda sx, sy: (sx.max() - sx.min()) / 2 / CLOSE_WIDTH
# the look up angle: the (negative) elevation whose solved camera sits CLOSE_HEIGHT above the floor
lo, hi = -30.0, 0.0
for _ in range(30):
    el = (lo + hi) / 2
    C_try, _ = solve(P_close, fit_close, basis(el))
    if C_try[2] > FLOOR + CLOSE_HEIGHT:
        hi = el
    else:
        lo = el
CLOSE_EL = (lo + hi) / 2
B_close = basis(CLOSE_EL)
C_close, ext_close = solve(P_close, fit_close, B_close)
B_wide = basis(WIDE_EL)
P_wide = np.vstack([points(CHEST, globals().get("OPEN_FRAME", 150)), points(["Reveal Badge"], globals().get("BADGE_FRAME", 200), 40)])
lim = 1.0 - 2 * WIDE_MARGIN
C_wide, ext_wide = solve(P_wide, lambda sx, sy: max((sx.max() - sx.min()) / 2 / WIDE_WIDTH, (sy.max() - sy.min()) / 2 / lim), B_wide)
dolly = bpy.data.objects["Reveal Camera Dolly"]
dolly["v6_close_loc"] = [float(v) for v in C_close]
dolly["v6_wide_loc"] = [float(v) for v in C_wide]
dolly["v6_close_rot"] = list(B_close[0].to_euler())
dolly["v6_wide_rot"] = list(B_wide[0].to_euler())
dolly["v6_rot"] = list(B_wide[0].to_euler())
V6 = dict(hidden=hidden, close_el=round(CLOSE_EL, 2), lens=LENS, close=[round(float(v), 3) for v in C_close],
          wide=[round(float(v), 3) for v in C_wide],
          ext_close=[round(float(v), 3) for v in ext_close], ext_wide=[round(float(v), 3) for v in ext_wide])
print("v6 setup", V6)
