"""Version 12: slower camera, slower lights, and smoke that plays all the way out (owner's notes, 2026-11-20:
"the camera animation is a little too fast ... slow and cinematic, smooth and cinematic", "the lights come on
very fast", "the smoke animation should animate the entire way out ... if you have to, extend the clip").
Run inside chest_reveal_v12_full.blend after v12_story.py; safe to run again; nothing is deleted.

- Camera: one fluid arc round the chest from its low start to its high end, frames 90 to 232 (4.7 seconds;
  the original took 90 to 142), level all the way, the lens shift changing with it on the same easing. The
  dolly gets its own action on top of its old NLA tracks (which stay); the camera's own distance is constant.
  (temple/v12_camera_original.json holds the original move as a record.)
- Badge: its rise, turn and settle take 1.3 times as long (front at about frame 182, settled about 206), in its
  own action over its old NLA track.
- Lights: everything that came up between frames 132 and 186 (the beam from above, its haze, the studio lights
  dimming round it) now takes frames 130 to 228.
- Mist from the chest: its simulation runs to frame 286 (bake with tools/v12_bake_mist.py); how thick it reads
  fades smoothly to nothing between frames 190 and 272 while it keeps moving, so it thins away by itself.
  Nothing is left in the chest at the end (owner, 2026-11-20: "none left at the end"; on 2026-11-19 they had
  chosen a thin layer that stays, and changed that after seeing it). `CHEST_HAZE` above 0 would bring one back."""
import bpy, json, math, os
from mathutils import Vector, Euler

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
story = bpy.data.objects["Temple Story"]
END = int(story["end"])
dolly = bpy.data.objects["Reveal Camera Dolly"]
cam = bpy.data.objects["Reveal Camera"]
root = bpy.data.objects["Reveal Chest Root"]
C0, C1 = 90, G("CAM_END", 232)
SLOW = "v12 Camera Dolly Slow"

# ------------------------------------------------------------------ the camera: one fluid arc
# Owner, 2026-11-20, on the first slow version: "it goes back and then there's like a sharp up ... very quick.
# I want that to be like a fluid motion, like it should be like an arc". The old move was three things on their
# own timing (the dolly's path, its tilt turned into a lens shift by a formula with a kink, and the camera's own
# distance). Now it is one arc round the chest: the camera swings up and out from its low start to its high end
# while the lens shift changes with it, all on one share q of the way, eased once. The camera is level all the
# time. Start and end are exactly the old start and end framings.
A_POS, A_SHIFT = Vector((0.0, -14.235, 0.622)), 0.2695        # in the chest's frame: where the camera waits
B_POS, B_SHIFT = Vector((0.0, -16.07, 7.975)), -0.1107        # and where it ends (the approved end framing)
PIVOT = Vector(G("CAM_PIVOT", (0.0, 0.0, 3.0)))
ea, ra = math.atan2(A_POS.z - PIVOT.z, -(A_POS.y - PIVOT.y)), (A_POS - PIVOT).length
eb, rb = math.atan2(B_POS.z - PIVOT.z, -(B_POS.y - PIVOT.y)), (B_POS - PIVOT).length
RAMP = G("CAM_RAMP", 0.35)                     # share of the move spent speeding up, and again slowing down


def ease(u):
    """Speed rises smoothly, holds, falls smoothly: no jolt, and its top speed is only 1.54 times its average."""
    u = min(max(u, 0.0), 1.0)
    if u > 0.5:
        return 1.0 - ease(1.0 - u)
    vp = 1.0 / (1.0 - RAMP)
    if u < RAMP:
        return vp * (u / 2.0 - RAMP / (2.0 * math.pi) * math.sin(math.pi * u / RAMP))
    return vp * (RAMP / 2.0 + (u - RAMP))


def cam_at(f):
    q = ease((f - C0) / float(C1 - C0))
    e, r = ea + (eb - ea) * q, ra + (rb - ra) * q
    return PIVOT + Vector((0.0, -r * math.cos(e), r * math.sin(e))), A_SHIFT + (B_SHIFT - A_SHIFT) * q


CAMZ = 1.705                                   # the camera's own distance behind the dolly: constant now
level = Euler((math.pi / 2.0, 0.0, dolly.rotation_euler[2]))
back = level.to_matrix() @ Vector((0.0, 0.0, 1.0))
ad = dolly.animation_data
if ad.action and ad.action.name == SLOW:
    for layer in ad.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    cb.fcurves.remove(fc)
else:
    ad.action = None
cd = cam.data
try:
    cd.driver_remove("shift_y")                # the lens shift is keyed directly now (a driver through a new custom
except Exception:                              # number stayed invalid in the open session)
    pass
if cd.animation_data and cd.animation_data.action:
    for layer in cd.animation_data.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    if fc.data_path == "shift_y":
                        cb.fcurves.remove(fc)
for f in [C0 - 2, C0 - 1] + list(range(C0, C1 + 1)) + [C1 + 1, C1 + 2]:
    p, sh = cam_at(f)
    dolly.location = root.matrix_world @ p - back * CAMZ
    dolly.rotation_euler = level
    dolly.keyframe_insert("location", frame=f)
    dolly.keyframe_insert("rotation_euler", frame=f)
    cd.shift_y = sh
    cd.keyframe_insert("shift_y", frame=f)
ad.action.name = SLOW
ad.action_extrapolation = "HOLD"
ad.action_blend_type = "REPLACE"
ad.action_influence = 1.0
for layer in cam.animation_data.action.layers:
    for st in layer.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                if fc.data_path == "location" and fc.array_index == 2:
                    for kp in fc.keyframe_points:
                        kp.co.y = kp.handle_left.y = kp.handle_right.y = CAMZ
                    fc.update()

# ------------------------------------------------------------------ the badge comes out a little slower
# Owner: "you can also make the badge come out a little slower, so that ... it fits the fluid movement of the
# camera". Its rise, turn and settle keep their shape and take 1.3 times as long, starting at frame 116 as before.
BADGE_K = G("BADGE_SLOW", 1.3)
br = bpy.data.objects["Reveal Badge Root"]
bad = br.animation_data
BSLOW = "v12 Badge Slow"
strip = bad.nla_tracks["05 Badge Reveal"].strips[0]
curves = []
for layer in strip.action.layers:
    for st in layer.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                curves.append(fc)
if bad.action and bad.action.name == BSLOW:
    for layer in bad.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    cb.fcurves.remove(fc)
else:
    bad.action = None
last = int(116 + (213 - 116) * BADGE_K) + 2
for f in range(110, last + 1):
    t = f if f <= 116 else min(116 + (f - 116) / BADGE_K, 213.0)
    for fc in curves:
        cur = getattr(br, fc.data_path) if not fc.data_path.startswith("[") else None
        if cur is None:
            continue
        if hasattr(cur, "__len__"):
            cur[fc.array_index] = fc.evaluate(t)
        else:
            setattr(br, fc.data_path, fc.evaluate(t))
    for path in sorted({fc.data_path for fc in curves if not fc.data_path.startswith("[")}):
        br.keyframe_insert(path, frame=f)
bad.action.name = BSLOW
bad.action_extrapolation = "HOLD"
bad.action_blend_type = "REPLACE"
bad.action_influence = 1.0

# ------------------------------------------------------------------ the beam and the room's change come on slower
B0, B1 = G("BEAM_START", 130), G("BEAM_FULL", 228)
moved = 0
for act in bpy.data.actions:
    for layer in act.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    ks = fc.keyframe_points
                    if len(ks) == 2 and round(ks[0].co.x) in (130, 132) and round(ks[1].co.x) in (186, 228) and not act.name.startswith("Temple"):
                        ks[0].co.x, ks[1].co.x = B0, B1
                        for kp in ks:
                            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
                        fc.update()
                        moved += 1

# ------------------------------------------------------------------ the mist from the chest plays all the way out
dom = bpy.data.objects["Reveal Opening Domain"]
ds = next(m for m in dom.modifiers if m.type == "FLUID").domain_settings
if ds.cache_frame_end != END + 6:                # only when it differs (writing it clears the baked files)
    ds.cache_frame_end = END + 6
mm = bpy.data.materials["Reveal Opening Mist"]
mt = mm.node_tree
gain = mt.nodes["mist density"].inputs[1]
if mt.animation_data and mt.animation_data.action:
    for layer in mt.animation_data.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    if 'nodes["mist density"].inputs[1]' in fc.data_path:
                        cb.fcurves.remove(fc)
GAIN = G("MIST_GAIN", 10.0)                      # at 96 cells the smoke keeps more of its body; 13 read as thick
for f, v in ((G("MIST_OUT_START", 200), GAIN), (G("MIST_OUT_END", END - 8), 0.0)):
    gain.default_value = v
    gain.keyframe_insert("default_value", frame=f)
gain.default_value = GAIN

# ------------------------------------------------------------------ a faint layer that stays in the chest
# Owner, 2026-11-20: "I want the mist to drift all the way out, none left at the end." So no layer stays (0).
# The object is kept in the file, switched off; a value above 0 brings a faint layer back (0.16 was tried).
HAZE = G("CHEST_HAZE", 0.0)
shake = bpy.data.objects["Reveal Chest Shake"]
root = bpy.data.objects["Reveal Chest Root"]
hm = mat("Reveal Chest Haze")
n = NT(hm)
p = n.coord().outputs["Object"]
ps = n.sep(p)
tv = n.node("ShaderNodeValue", label="haze time")
d = tv.outputs[0].driver_add("default_value").driver
d.type = "SCRIPTED"
d.expression = "frame / 110.0"
lv = n.node("ShaderNodeValue", label="haze level")
nz = n.node("ShaderNodeTexNoise", ins={"Vector": n.vmath("MULTIPLY", p, (0.55, 0.55, 1.1)), "W": tv.outputs[0], "Scale": 1.0, "Detail": 3.0,
                                      "Roughness": 0.55, "Distortion": 0.4}, noise_dimensions="4D")
wisp = n.ramp(nz.outputs["Fac"], (0.44, 0.74))
# thickest just under the rim (z 2.8), thinning up over it and down into the chest
layer_ = n.math("MULTIPLY", n.ramp(ps[2], (0.5, 2.3)), n.math("SUBTRACT", 1.0, n.ramp(ps[2], (2.6, 3.5))))
# over the rim it stays inside the chest's outline, so the box that holds it never shows an edge
inx = n.math("SUBTRACT", 1.0, n.ramp(n.math("ABSOLUTE", ps[0]), (1.9, 2.5)))
iny = n.math("SUBTRACT", 1.0, n.ramp(n.math("ABSOLUTE", n.math("SUBTRACT", ps[1], 0.0)), (1.1, 1.6)))
dens = n.math("MULTIPLY", n.math("MULTIPLY", n.math("MULTIPLY", wisp, layer_), n.math("MULTIPLY", inx, iny)), lv.outputs[0])
vol = n.node("ShaderNodeVolumePrincipled", ins={"Color": (0.93, 0.96, 1.0, 1), "Density": dens, "Anisotropy": 0.2})
om = n.node("ShaderNodeOutputMaterial")
n.link(vol.outputs[0], om.inputs["Volume"])
x0, x1, y0, y1, zb, zt = -2.5, 2.5, -1.6, 1.6, 0.45, 3.5
V = [(x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb), (x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt)]
Fh = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
ho = put("Reveal Chest Haze", mesh_from("Reveal Chest Haze", V, Fh), bpy.data.collections["Reveal FX"], [hm])
keep = scn.frame_current
scn.frame_set(END)
bpy.context.view_layer.update()
ho.parent = shake
ho.matrix_world = root.matrix_world.copy()
scn.frame_set(keep)
ho.visible_shadow = False
ho.display_type = "WIRE"
ho.hide_render = HAZE <= 0.0
lvs = lv.outputs[0]
if hm.node_tree.animation_data:
    hm.node_tree.animation_data_clear()
    d = tv.outputs[0].driver_add("default_value").driver
    d.type = "SCRIPTED"
    d.expression = "frame / 110.0"
for f, v in ((G("HAZE_IN_START", 196), 0.0), (G("HAZE_IN_END", END - 10), HAZE)):
    lvs.default_value = v
    lvs.keyframe_insert("default_value", frame=f)
result = {"camera_end": C1, "beam_curves_moved": moved, "mist_cache_end": ds.cache_frame_end, "end": END}
