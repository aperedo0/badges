"""Version 12: the whole reveal's story, keyed on the real timeline (scene frames -23 to 213) so it plays in the
open Blender. Run inside chest_reveal_v12_full.blend after the version 10 and 11 scripts; safe to run again;
nothing is deleted. tools/v12_render.py renders the four pieces (it adds the holds, the rattles and the loops).

What the owner agreed to (2026-11-19 and 20), and where it lives here:
- A dark, cool start that warms to gold: `Temple Story["gold"]` (0 moonlight, 1 the gold ending) drives the
  temple's lights; the torches start unlit.
- The camera is level through the whole movie (the lens shifts), so pillars are upright at the start too, and at
  the start the chest sits lower in the tall picture with the hall towering above it.
- Landing (f17, f22): dust falls from above through the shafts (`dustfall`). The platform's rings never light up
  (owner, 2026-11-20); `rings` stays at 0.
- Waiting for the swipe: the keyhole glows (`keyhole`), a line of light shows at the lid's seam on each rattle
  (`seam`). The rattles themselves are added by the render script.
- Swipe (f50): the lock clicks at f56 (the keyhole flashes and dies). The camera never moves toward the chest.
- The lid cracks (f90): cold light bursts from the chest across the floor and up the pillars (`burst`), with rays
  in the air (`rays`, gone by f136, before the gold beam).
- The badge rises (f116): the torches catch pair after pair into the distance (`lit_0` to `lit_5` on Temple
  Torch Control, each with a small flare).
- The badge settles (f185); the gold beam and the warm light keep coming up slowly until about f238.
- The mist from the chest plays all the way out by about f272 and the reveal ends at f280 (v12_slow.py)."""
import bpy, math
from mathutils import Vector, Matrix

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
scn = bpy.data.scenes["Chest Reveal"]
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
FLOORS = bpy.data.collections["Temple Floor Receivers"]
FRONT = bpy.data.collections["Temple Front Receivers"]
SC = coll("Temple Story", TC)
F0 = G("STORY_START", -28)                       # one second of empty temple before the chest drops into the picture (about f2)
END = G("STORY_END", 290)                        # the reveal's last frame; the ending loop starts here (was 213: the owner
                                                 # asked for slower lights, a slower camera and smoke that plays all the way out)
scn.frame_end = END
scn.frame_start = max(F0, 0)                    # Blender keeps a scene's first frame at 0 or later; the story still starts at F0


def drv(idb, path, expr, index=-1, **vs):
    """A driver with named variables: name=(datablock, data path)."""
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except Exception:
        pass
    fc = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for nm, (tid, tpath) in vs.items():
        v = d.variables.new()
        v.name = nm
        v.type = "SINGLE_PROP"
        v.targets[0].id_type = tid.id_type
        v.targets[0].id = tid
        v.targets[0].data_path = tpath
    d.expression = expr
    return fc


# ------------------------------------------------------------------ the story's controls
story = bpy.data.objects.get("Temple Story")
if story is None:
    story = bpy.data.objects.new("Temple Story", None)
    SC.objects.link(story)
story.parent = root
story.matrix_parent_inverse.identity()
story.location = (0.0, 40.0, 34.0)
story.animation_data_clear()
story["start"] = F0                              # the render script reads the story's first and last frames from here
story["end"] = END
PROPS = ("gold", "rings", "burst", "rays", "keyhole", "seam", "dustfall", "drift", "streak")
for k in PROPS:
    story[k] = 0.0
    story.id_properties_ui(k).update(min=-100.0, max=100.0)


def keys(obj, prop, pts, linear=False):
    for f, v in pts:
        obj[prop] = float(v)
        obj.keyframe_insert(f'["{prop}"]', frame=f)
    if linear:
        for layer in obj.animation_data.action.layers:
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        if fc.data_path == f'["{prop}"]':
                            for kp in fc.keyframe_points:
                                kp.interpolation = "LINEAR"
                            fc.extrapolation = "LINEAR" if prop == "dustfall" else "CONSTANT"


S = lambda k: (story, f'["{k}"]')
# Owner, 2026-11-20: "the lights come on very fast ... dark scene and suddenly it's like a light scene. I want
# them to come on a little slower ... they could appreciate the lights coming on and what it does to the
# environment". The warm up now takes about 3.8 seconds (was about 2).
keys(story, "gold", [(F0, 0), (122, 0), (176, 0.42), (238, 1.0), (END, 1.0)])
# Owner, 2026-11-20: "the gold ones. I don't want them to light up ... They're just colored that way". The rings
# are plain gold metal now and never glow, flash or pulse.
keys(story, "rings", [(F0, 0), (END, 0)])
# rises with the lid (it opens f90 to f117), then fades slowly; gone before the gold light is full
keys(story, "burst", [(F0, 0), (89, 0), (114, 1.0), (134, 0.8), (184, 0.3), (228, 0.0), (END, 0.0)])
keys(story, "rays", [(F0, 0), (89, 0), (112, 1.0), (140, 0.6), (172, 0.0), (END, 0.0)])
keys(story, "keyhole", [(F0, 0), (34, 0), (49, 0.5), (50, 0.5), (55, 1.5), (56, 3.0), (59, 0.5), (66, 0.15), (88, 0.15), (92, 0.0), (213, 0)], linear=True)
keys(story, "seam", [(F0, 0), (213, 0)])
keys(story, "dustfall", [(17, 0.0), (213, 196 / 30.0)], linear=True)
story["streak"] = 0.0                                    # not keyed: v12_render.py sets it to 1 (the falling grit's stand in for motion blur)
keys(story, "drift", [(F0, 0), (END, 0)])              # not used any more: the mist plays out by itself (v12_slow.py)
ctrl = bpy.data.objects["Temple Torch Control"]
ctrl.animation_data_clear()
for g in range(6):                               # each pair catches, flares, then settles
    a = G("TORCH_FIRST", 126) + G("TORCH_STEP", 15) * g
    keys(ctrl, f"lit_{g}", [(F0, 0), (a, 0), (a + 14, 1.15), (a + 34, 1.0), (END, 1.0)])

# ------------------------------------------------------------------ the camera: level always, chest low at the start
cam = bpy.data.objects["Reveal Camera"]
dolly = bpy.data.objects["Reveal Camera Dolly"]
cd = cam.data
OFF = G("END_SHIFT", 0.03)
S0 = G("START_SHIFT", 0.17)                      # how far the picture's contents move down at the start (share of its height)
RX = (dolly, "rotation_euler[0]")
drv(cam, "rotation_euler", "1.5707963 - rx", index=0, rx=RX)
# (the lens is written in as a number: a driver on the camera that reads the same camera makes a dependency cycle)
drv(cd, "shift_y", "-%.6f * tan(1.5707963 - rx) + %.4f * clamp((1.5707963 - rx) / 0.1745329, 0.0, 1.0)"
                   " + %.4f * clamp((rx - 1.5707963) / 0.1243, 0.0, 1.0)" % (cd.lens / 36.0, OFF, S0), rx=RX)
# the slow push toward the lock, from the swipe until the lid opens (in the dolly's space; the view is level)
if cam.animation_data and cam.animation_data.action:
    for layer in cam.animation_data.action.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                for fc in list(cb.fcurves):
                    if fc.data_path == "delta_location":
                        cb.fcurves.remove(fc)
# Owner, 2026-11-20: "I don't ever want the camera to pull in." The push toward the lock is gone (its keys are
# removed above); the only camera move left is the rise and pull back as the lid opens (slowed in v12_slow.py).
cam.delta_location = (0, 0, 0)

# The taller, lower picture showed the chest hanging at the top before it fell (it starts at rest at f1, 12 units
# up). It now comes from 9 units higher and joins its own fall by f8, turning as it comes: it enters at about f2.
drop = bpy.data.objects["Reveal Chest Drop"]
if drop.animation_data and drop.animation_data.action:
    for layer in drop.animation_data.action.layers:
        for st_ in layer.strips:
            for cb in st_.channelbags:
                for fc in list(cb.fcurves):
                    if fc.data_path.startswith("delta_"):
                        cb.fcurves.remove(fc)
FA, FB, HIGH = -4, 8, G("DROP_FROM", 9.0)
for f in range(FA, FB + 1):
    s_ = (f - FA) / (FB - FA)
    drop.delta_location = (0.0, 0.0, HIGH * (1.0 - s_) ** 2)
    drop.delta_rotation_euler = (0.0, 0.05 * max(1 - f, 0), 0.0)
    drop.keyframe_insert("delta_location", frame=f)
    drop.keyframe_insert("delta_rotation_euler", frame=f)
drop.delta_location = (0, 0, 0)
drop.delta_rotation_euler = (0, 0, 0)

# ------------------------------------------------------------------ the temple's lights follow the story
beam = bpy.data.objects["Reveal Overhead Light"].data
BEAM = (beam, "energy")


def L(name):
    return bpy.data.objects[name].data


drv(L("Temple High Light"), "energy", "9000.0 * (0.06 + 0.94 * gold)", gold=S("gold"))
for nm in ("Temple Cool L", "Temple Cool R"):
    drv(L(nm), "energy", "%.1f * (1.0 + %.2f * (1.0 - gold))" % (G("COOL_E", 8000.0), G("MOON_BOOST", 0.35)), gold=S("gold"))
drv(L("Temple Cool Top"), "energy", "3000.0 * (1.0 + %.2f * (1.0 - gold))" % G("MOON_BOOST", 0.35), gold=S("gold"))
drv(L("Temple Floor Light"), "energy", "7000.0 * (0.8 + 0.2 * gold)", gold=S("gold"))
drv(L("Temple Back Glow"), "energy", "130000.0 * (1.15 - 0.15 * gold)", gold=S("gold"))
drv(L("Temple Beam Spill"), "energy", "20000.0 * min(e / 60000.0, 1.0)", e=BEAM)
drv(L("Temple Mist Rim"), "energy", "2500.0 * min(e / 60000.0, 1.0)", e=BEAM)
drv(L("Temple Front Fill"), "energy", "2200.0 * (0.4 + 0.6 * gold)", gold=S("gold"))
drv(L("Temple Dais Key"), "energy", "2600.0 * (0.4 + 0.6 * gold)", gold=S("gold"))
# Moonlight through the roof, warming to gold. From the low opening camera the old shafts showed their own
# beginning in mid air and read as thin poles: they now start far above the picture and are softer.
for nm, e, deg, sx_, sy_ in (("Temple Shaft L", 1.0, 4.4, -10.0, 36.0), ("Temple Shaft R", 0.8, 3.8, 11.5, 47.0)):
    so = bpy.data.objects[nm]
    aim = Vector((sx_, sy_, FLOOR))                    # straight down through the roof, where the owner liked them
    # From very high up, so the light is as strong at the floor as under the roof (from z 90 the streak was seven
    # times dimmer at the bottom and faded out half way down). Same width and same light on the floor as before.
    HI = 330.0
    so.location = (sx_, sy_ - 1.0, HI)
    so.rotation_euler = (aim - Vector(so.location)).to_track_quat("-Z", "Y").to_euler()
    so.data.spot_size = 2.0 * math.atan(90.55 * math.tan(math.radians(deg) / 2.0) / (HI - FLOOR))
    so.data.spot_blend = 0.9
    so.data.volume_factor = G("SHAFT_AIR", 40.0)
    drv(L(nm), "energy", "%.1f * (2.0 - 1.0 * gold)" % (90000.0 * e * 1.5 * ((HI - FLOOR) / 90.55) ** 2), gold=S("gold"))
    for i, (c0, c1) in enumerate(((0.62, 1.0), (0.76, 0.78), (1.0, 0.5))):
        drv(L(nm), "color", "%.3f + %.3f * gold" % (c0, c1 - c0), index=i, gold=S("gold"))
airo = bpy.data.objects.get("Temple Air")           # the hall's air reaches higher, so the shafts have no visible top
if airo:
    for v_ in airo.data.vertices:
        if v_.co.z > 50.0:
            v_.co.z = 82.0
    airo.data.update()
# the studio surroundings that lit the chest evenly are dimmer from the start (they flattened the dark temple)
wn = bpy.data.worlds["Reveal World"].node_tree
if wn.animation_data and wn.animation_data.action:
    for layer in wn.animation_data.action.layers:
        for st_ in layer.strips:
            for cb in st_.channelbags:
                for fc in cb.fcurves:
                    if 'nodes["Background"]' in fc.data_path:
                        ks = fc.keyframe_points
                        base = wn.get("v12_world_start", ks[0].co.y)
                        wn["v12_world_start"] = base
                        ks[0].co.y = base * G("WORLD_START", 0.3)       # the same dim level as the ending
                        ks[0].handle_left.y = ks[0].handle_right.y = ks[0].co.y
bpy.data.objects["Temple Back Glow"].data.volume_factor = 0.12      # less of a halo round the far doorway
fgm = bpy.data.materials["Temple Far Glow"]         # the far doorway: a faint pale slit (bright, it sat on the lid like a glowing pill)
next(nd for nd in fgm.node_tree.nodes if nd.bl_idname == "ShaderNodeEmission").inputs["Strength"].default_value = G("FAR_GLOW", 0.1)
# the platform's rings
gm = bpy.data.materials["Temple Gold Inlay"]
pb = next(n for n in gm.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
try:
    pb.inputs["Emission Strength"].driver_remove("default_value")
except Exception:
    pass
pb.inputs["Emission Strength"].default_value = 0.0     # plain gold metal: no light of its own, ever

# ------------------------------------------------------------------ the cold burst from the chest
BR = coll("Temple Burst Receivers", TC)
for c in (RECV, FLOORS, FRONT):
    for o in c.objects:
        if o.name not in BR.objects and o.name not in ("Temple Ground Mist",):
            BR.objects.link(o)
BB = coll("Temple Burst Blockers", TC)           # what throws shadows in the burst: the chest's body and the temple, not the lid
for o in list(bpy.data.collections["Reveal Chest Body"].objects) + [o for o in TC.all_objects if o.type == "MESH"]:
    if o.type == "MESH" and o.name not in BB.objects and not o.name.startswith(("Temple Fog", "Temple Flame", "Temple Fire", "Temple Embers",
                                                                                 "Temple Ground", "Temple Air", "Temple Burst", "Temple Dust")):
        BB.objects.link(o)
bl = bpy.data.objects.get("Temple Chest Burst")
if bl is None:
    bl = bpy.data.objects.new("Temple Chest Burst", bpy.data.lights.new("Temple Chest Burst", "POINT"))
    SC.objects.link(bl)
bl.parent = root
bl.matrix_parent_inverse.identity()
# Just above the rim and a little back, so the chest's own walls shade the floor all round it (out to about 28
# units in front, past the camera) and the light goes up and out to the far floor, the pillars and the arches.
# Higher (3.4), the floor at the bottom of the picture flashed white.
bl.location = G("BURST_AT", (0.0, 0.2, 3.1))
bl.data.color = (0.74, 0.88, 1.0)
bl.data.shadow_soft_size = 0.8
bl.data.use_shadow = True
# No part in the air: a light's reach into mist and haze cannot be limited to chosen things, and this one sits in
# the chest's own mist (the first try was a white out).
bl.data.volume_factor = 0.0
bl.light_linking.receiver_collection = BR
bl.light_linking.blocker_collection = BB
drv(bl.data, "energy", "%.1f * burst" % G("BURST_E", 60000.0), burst=S("burst"))
# thin air round the chest that only exists while the rays do
hm = mat("Temple Burst Haze")
n = NT(hm)
p = n.coord().outputs["Object"]
nz = n.node("ShaderNodeTexNoise", ins={"Vector": n.vmath("MULTIPLY", p, (0.08, 0.08, 0.12)), "Scale": 1.0, "Detail": 3.0, "Roughness": 0.55})
rv = n.node("ShaderNodeValue", label="rays")
drv(rv.outputs[0], "default_value", "rays", rays=S("rays"))
dens = n.math("MULTIPLY", n.math("MULTIPLY", n.math("ADD", 0.6, n.math("MULTIPLY", nz.outputs["Fac"], 0.8)), rv.outputs[0]), G("RAYS_DENSITY", 0.004))
vol = n.node("ShaderNodeVolumePrincipled", ins={"Color": (0.9, 0.93, 1.0, 1), "Density": dens, "Anisotropy": 0.5})
om = n.node("ShaderNodeOutputMaterial")
n.link(vol.outputs[0], om.inputs["Volume"])
x0, x1, y0, y1, z0, z1 = -13.0, 13.0, -10.0, 16.0, FLOOR, 30.0
V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
Fb = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
bh = put("Temple Burst Haze", mesh_from("Temple Burst Haze", V, Fb), SC, [hm], root)
bh.visible_shadow = False
bh.display_type = "WIRE"
bh.hide_render = True                             # kept, not used: it fogged the whole picture
# the rays: a light behind the chest that looks down the hall and touches only the air there
rl = bpy.data.objects.get("Temple Burst Rays")
if rl is None:
    rl = bpy.data.objects.new("Temple Burst Rays", bpy.data.lights.new("Temple Burst Rays", "SPOT"))
    SC.objects.link(rl)
rl.parent = root
rl.matrix_parent_inverse.identity()
rl.location = (0.0, 7.0, 5.0)
rl.rotation_euler = (Vector((0.0, 60.0, 16.0)) - Vector(rl.location)).to_track_quat("-Z", "Y").to_euler()
rl.data.color = (0.74, 0.88, 1.0)
rl.data.spot_size = math.radians(80)
rl.data.spot_blend = 0.6
rl.data.shadow_soft_size = 0.6
rl.data.use_shadow = True
rl.data.diffuse_factor = 0.0
rl.data.specular_factor = 0.0
rl.data.volume_factor = 1.0
drv(rl.data, "energy", "%.1f * rays" % G("RAYS_E", 180000.0), rays=S("rays"))
# the torches' low light on the floor, gentler now that the floor is calm (it lit the middle of the floor in patches)
for nm_, e_ in (("Temple Floor Firelight L", 1.0), ("Temple Floor Firelight R", 0.7)):
    drv(L(nm_), "energy", "%.1f * lit" % (G("FIRELIGHT_E", 24000.0) * e_), lit=(ctrl, '["lit_0"]'))
if bh.name not in BR.objects:
    BR.objects.link(bh)
air = bpy.data.objects.get("Temple Air")
if air and air.name not in BR.objects:
    BR.objects.link(air)

# ------------------------------------------------------------------ keyhole glow and the line of light at the lid's seam
shake = bpy.data.objects["Reveal Chest Shake"]
keep = scn.frame_current
scn.frame_set(49)
bpy.context.view_layer.update()


def glow_card(name, corners, prop, strength, color):
    m = mat(name)
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    nn = NT(m)
    val = nn.node("ShaderNodeValue", label="level")
    drv(val.outputs[0], "default_value", prop, **{prop: S(prop)})
    em = nn.node("ShaderNodeEmission", ins={"Color": color, "Strength": nn.math("MULTIPLY", val.outputs[0], strength)})
    tp = nn.node("ShaderNodeBsdfTransparent")
    add = nn.node("ShaderNodeAddShader")
    nn.link(tp.outputs[0], add.inputs[0])
    nn.link(em.outputs[0], add.inputs[1])
    nn.out(add.outputs[0])
    o = put(name, mesh_from(name, corners, [(0, 1, 2, 3)]), SC, [m])
    o.parent = shake                              # it moves with the chest when the chest rattles
    o.matrix_world = root.matrix_world.copy()
    o.visible_shadow = False
    return o


KY = G("KEYHOLE_Y", -1.98)                       # just behind the lock plate (its face is at -2.11): seen only through the keyhole
glow_card("Temple Keyhole Glow", [(-0.3, KY, 1.35), (0.3, KY, 1.35), (0.3, KY, 2.15), (-0.3, KY, 2.15)], "keyhole", G("KEYHOLE_GLOW", 1.7), (0.6, 0.82, 1.0, 1))
SY = G("SEAM_Y", -1.6)                           # inside the front wall: seen only when the lid lifts a hair
glow_card("Temple Seam Glow", [(-2.35, SY, 2.62), (2.35, SY, 2.62), (2.35, SY, 3.1), (-2.35, SY, 3.1)], "seam", G("SEAM_GLOW", 5.0), (0.6, 0.84, 1.0, 1))
scn.frame_set(keep)

# ------------------------------------------------------------------ dust shaken loose from above
dm = mat("Temple Dust Fall")
dm.surface_render_method = "BLENDED"
dm.use_backface_culling = False
dm.use_transparency_overlap = True
n = NT(dm)
tc = n.coord()
uv = n.sep(tc.outputs["UV"])
oi = n.node("ShaderNodeObjectInfo")
tv = n.node("ShaderNodeValue", label="fall time")
drv(tv.outputs[0], "default_value", "dustfall", dustfall=S("dustfall"))
HC = 30.0                                         # the card's height
t = n.math("SUBTRACT", tv.outputs[0], n.math("MULTIPLY", oi.outputs["Random"], 0.4))       # each stream starts a little apart
fall = n.math("MULTIPLY", n.math("MAXIMUM", t, 0.0), G("DUST_SPEED", 8.0))                 # how far the first grains have dropped
down = n.math("MULTIPLY", n.math("SUBTRACT", 1.0, uv[1]), HC)                              # distance below the card's top
head = n.math("SUBTRACT", 1.0, n.ramp(n.math("SUBTRACT", down, fall), (-2.5, 0.5)))        # nothing below the first grains
tail = n.ramp(n.math("SUBTRACT", down, n.math("MULTIPLY", n.math("MAXIMUM", n.math("SUBTRACT", t, 0.7), 0.0), G("DUST_SPEED", 8.0))), (-1.0, 4.0))
x = n.math("MULTIPLY", n.math("SUBTRACT", uv[0], 0.5), 2.0)
sx = n.math("ADD", n.math("MULTIPLY", x, 1.3), n.math("MULTIPLY", oi.outputs["Random"], 17.0))
st1 = n.noise(n.comb(sx, n.math("MULTIPLY", n.math("SUBTRACT", down, fall), 0.12), 0.0), 1.0, detail=3.0, rough=0.6)
st2 = n.noise(n.comb(n.math("MULTIPLY", sx, 3.1), n.math("MULTIPLY", n.math("SUBTRACT", down, n.math("MULTIPLY", fall, 1.15)), 0.4), 3.0), 1.0, detail=2.0)
streak = n.math("MULTIPLY", n.ramp(st1.outputs["Fac"], (0.36, 0.8)), n.math("ADD", 0.6, n.math("MULTIPLY", st2.outputs["Fac"], 0.5)))
sides = n.math("SUBTRACT", 1.0, n.math("POWER", n.math("ABSOLUTE", x), 2.5))
life = n.math("MULTIPLY", n.ramp(t, (0.0, 0.15)), n.math("SUBTRACT", 1.0, n.ramp(t, (1.2, 2.5))))
alpha = n.math("MULTIPLY", n.math("MULTIPLY", n.math("MULTIPLY", streak, sides), n.math("MULTIPLY", head, tail)), n.math("MULTIPLY", life, G("DUST_FALL", 0.3)))
alpha = n.math("MINIMUM", n.math("MAXIMUM", alpha, 0.0), 1.0)
up = n.comb(0.0, 0.0, 1.0)
dif = n.node("ShaderNodeBsdfDiffuse", ins={"Color": (0.8, 0.78, 0.74, 1), "Normal": up})
tr = n.node("ShaderNodeBsdfTranslucent", ins={"Color": (0.8, 0.78, 0.74, 1), "Normal": up})
lit_ = n.node("ShaderNodeMixShader", ins={0: 0.5, 1: dif.outputs[0], 2: tr.outputs[0]})
tp = n.node("ShaderNodeBsdfTransparent")
fin = n.node("ShaderNodeMixShader", ins={0: alpha, 1: tp.outputs[0], 2: lit_.outputs[0]})
n.out(fin.outputs[0])
CAMP = Vector((0.0, -14.2, 0.6))
for i, (x_, y_, w_, ztop) in enumerate(G("DUST_SPOTS", [(-10.0, 36.0, 5.0, 46.0), (11.5, 47.0, 5.0, 46.0), (-3.5, 30.0, 4.0, 48.0),
                                                        (5.0, 60.0, 6.0, 44.0), (-12.5, 66.0, 5.0, 42.0), (12.0, 26.0, 4.0, 46.0)])):
    nm = f"Temple Dust Fall {i}"
    me = mesh_from(nm, [(-w_ / 2, 0, -HC), (w_ / 2, 0, -HC), (w_ / 2, 0, 0), (-w_ / 2, 0, 0)], [(0, 1, 2, 3)],
                   uvs={"UVMap": [(0, 0), (1, 0), (1, 1), (0, 1)]})
    o = put(nm, me, SC, [dm], root)
    yaw = math.atan2(CAMP.x - x_, -(CAMP.y - y_))
    o.matrix_basis = Matrix.Translation((x_, y_, ztop)) @ Matrix.Rotation(yaw, 4, "Z")
    o.visible_shadow = False
    if o.name not in RECV.objects:
        RECV.objects.link(o)

# ------------------------------------------------------------------ the mist in the chest keeps drifting at the end
mm = bpy.data.materials["Reveal Opening Mist"]
mt = mm.node_tree
if "v12 drift" not in mt.nodes:
    src = mt.nodes["mist density"].outputs[0]
    pv = next(nd for nd in mt.nodes if nd.bl_idname == "ShaderNodeVolumePrincipled")
    tcn = mt.nodes.new("ShaderNodeTexCoord")
    nzn = mt.nodes.new("ShaderNodeTexNoise")
    nzn.name = "v12 drift noise"
    nzn.noise_dimensions = "4D"
    nzn.inputs["Scale"].default_value = 0.55
    nzn.inputs["Detail"].default_value = 2.0
    mt.links.new(tcn.outputs["Object"], nzn.inputs["Vector"])
    dv = mt.nodes.new("ShaderNodeValue")
    dv.name = dv.label = "v12 drift amount"
    a1 = mt.nodes.new("ShaderNodeMath"); a1.operation = "SUBTRACT"; a1.inputs[1].default_value = 0.5
    mt.links.new(nzn.outputs["Fac"], a1.inputs[0])
    a2 = mt.nodes.new("ShaderNodeMath"); a2.operation = "MULTIPLY"
    mt.links.new(a1.outputs[0], a2.inputs[0]); mt.links.new(dv.outputs[0], a2.inputs[1])
    a3 = mt.nodes.new("ShaderNodeMath"); a3.operation = "ADD"; a3.inputs[1].default_value = 1.0
    mt.links.new(a2.outputs[0], a3.inputs[0])
    mul = mt.nodes.new("ShaderNodeMath"); mul.name = "v12 drift"; mul.operation = "MULTIPLY"
    mt.links.new(src, mul.inputs[0]); mt.links.new(a3.outputs[0], mul.inputs[1])
    mt.links.new(mul.outputs[0], pv.inputs["Density"])
drv(mt.nodes["v12 drift amount"].outputs[0], "default_value", "drift * %.2f" % G("MIST_DRIFT", 1.3), drift=S("drift"))
drv(mt.nodes["v12 drift noise"].inputs["W"], "default_value", "frame / 70.0")
result = {"story": "ok", "start": F0}
