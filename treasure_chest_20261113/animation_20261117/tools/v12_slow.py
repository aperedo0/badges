"""Version 12: slower camera, slower lights, and smoke that plays all the way out (owner's notes, 2026-11-20:
"the camera animation is a little too fast ... slow and cinematic, smooth and cinematic", "the lights come on
very fast", "the smoke animation should animate the entire way out ... if you have to, extend the clip").
Run inside chest_reveal_v12_full.blend after v12_story.py; safe to run again; nothing is deleted.

- Camera: the rise and pull back as the lid opens follows the same path as before, but takes 3.8 seconds
  (frames 90 to 205, was 90 to 142) with one long gentle ease. The original motion is sampled once into
  temple/v12_camera_original.json and never read from the scene again. The dolly gets its own action on top of
  its old NLA tracks (which stay); the camera's distance keys are rewritten in place.
- Lights: everything that came up between frames 132 and 186 (the beam from above, its haze, the studio lights
  dimming round it) now takes frames 130 to 228.
- Mist from the chest: its simulation runs to frame 286 (bake with tools/v12_bake_mist.py); how thick it reads
  fades smoothly to nothing between frames 190 and 272 while it keeps moving, so it thins away by itself.
  Nothing is left in the chest at the end (owner, 2026-11-20: "none left at the end"; on 2026-11-19 they had
  chosen a thin layer that stays, and changed that after seeing it). `CHEST_HAZE` above 0 would bring one back."""
import bpy, json, math, os
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
story = bpy.data.objects["Temple Story"]
END = int(story["end"])
dolly = bpy.data.objects["Reveal Camera Dolly"]
cam = bpy.data.objects["Reveal Camera"]
C0, C1 = 90, G("CAM_END", 205)
ORIG = bpy.path.abspath("//temple/v12_camera_original.json")
SLOW = "v12 Camera Dolly Slow"

# ------------------------------------------------------------------ the camera's original move, sampled once
if not os.path.exists(ORIG):
    assert not (dolly.animation_data.action and dolly.animation_data.action.name == SLOW), "the original move is already replaced"
    keep = scn.frame_current
    scn.frame_set(88)
    rest = list(dolly.location) + list(dolly.rotation_euler)
    scn.frame_set(keep)
    strip = dolly.animation_data.nla_tracks["04 Opening"].strips[0]
    curves = {}
    for layer in strip.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path in ("location", "rotation_euler"):
                        curves[(fc.data_path, fc.array_index)] = fc
    camz = None
    for layer in cam.animation_data.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves:
                    if fc.data_path == "location" and fc.array_index == 2:
                        camz = fc
    rows = []
    t = 88.0
    while t <= 144.01:
        ta = strip.action_frame_start + (min(max(t, strip.frame_start), strip.frame_end) - strip.frame_start) / strip.scale
        row = [t]
        for j, key in enumerate([("location", 0), ("location", 1), ("location", 2), ("rotation_euler", 0), ("rotation_euler", 1), ("rotation_euler", 2)]):
            row.append(curves[key].evaluate(ta) if key in curves else rest[j])
        row.append(camz.evaluate(t))
        rows.append(row)
        t += 0.25
    json.dump({"note": "dolly location xyz, rotation xyz and the camera's own z, every quarter frame, before version 12 slowed the move",
               "rows": rows}, open(ORIG, "w"))
rows = json.load(open(ORIG))["rows"]
z0, z1 = rows[0][3], rows[-1][3]
prog = [(r[3] - z0) / (z1 - z0) for r in rows]             # how far along the move (the dolly's height: it only rises)


def pose(q):
    """The original pose at share q of the move."""
    q = min(max(q, 0.0), 1.0)
    for i in range(len(rows) - 1):
        if prog[i] <= q <= prog[i + 1] and prog[i + 1] > prog[i]:
            k = (q - prog[i]) / (prog[i + 1] - prog[i])
            return [rows[i][j] + (rows[i + 1][j] - rows[i][j]) * k for j in range(1, 8)]
    return rows[-1][1:] if q > 0.5 else rows[0][1:]


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (u * (u * 6 - 15) + 10)               # starts and stops with no jolt in speed or in its change


def at(f):
    return pose(ease((f - C0) / float(C1 - C0)))


# the dolly: its own action over the old tracks
ad = dolly.animation_data
if ad.action and ad.action.name == SLOW:
    for layer in ad.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    cb.fcurves.remove(fc)
else:
    ad.action = None
for f in [C0 - 2, C0 - 1] + list(range(C0, C1 + 1)) + [C1 + 1, C1 + 2]:
    p = at(f)
    dolly.location = p[0:3]
    dolly.rotation_euler = p[3:6]
    dolly.keyframe_insert("location", frame=f)
    dolly.keyframe_insert("rotation_euler", frame=f)
ad.action.name = SLOW
ad.action_extrapolation = "HOLD"
ad.action_blend_type = "REPLACE"
ad.action_influence = 1.0
# the camera's own distance (the 10 percent pull back from version 7) follows the same timing
for layer in cam.animation_data.action.layers:
    for st in layer.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                if fc.data_path == "location" and fc.array_index == 2:
                    for kp in fc.keyframe_points:
                        kp.co.y = at(kp.co.x)[6]
                        kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
                    fc.update()

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
GAIN = G("MIST_GAIN", 13.0)
for f, v in ((G("MIST_OUT_START", 190), GAIN), (G("MIST_OUT_END", END - 8), 0.0)):
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
