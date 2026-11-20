"""Version 8 specks in the beam: replaces the version 7 specks (owner, 2026-11-19: "horribly scattered
... should be pretty faint, the opacity should be determined by the light, pretty much evenly
scattered, and there should be less, it should be tasteful").

What is different:
- Fewer (about 150 instead of 900) and laid out evenly as the camera sees them: no clumps, no bare
  patches. Each has its own depth inside the beam, so they still sit in space, not on a sheet.
- A speck adds light and nothing else, and how much it adds follows the beam: brightest in the middle
  of the beam, fading at its edge, nothing outside it, nothing before the beam comes up (it follows the
  beam light's own fade in). An unlit speck is invisible (the old ones showed as dark dots over the fog).
- None in front of the badge's face, so the badge stays clean.
- They drift slowly together, like dust carried on the same slow air.

Run inside Blender in chest_reveal_v8_mist.blend after v7_ending.py; safe to run again, no deletes,
nothing to bake. Numbers can be overridden with MOTE_* globals set before the script runs.
"""
import bpy, bmesh, math, random
from mathutils import Vector

G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
spot = bpy.data.objects["Reveal Overhead Light"]
haze = bpy.data.objects["Reveal Ending Haze"]
cam = scn.camera
SPACING = G("MOTE_SPACING", 0.062)      # smallest gap between two specks, as a share of the picture's width
# True radius range. Owner, 2026-11-19: first "HUGE", then "a tenth of their size ... much, much smaller".
# These are far smaller than a pixel, and a dot cannot be drawn smaller than a pixel, so each speck is
# drawn one pixel wide (PIXEL_RADIUS, set for the render size by v8_render.py) and dimmed by how much
# smaller than a pixel it really is. Smaller specks are fainter points, never bigger ones.
SIZE = G("MOTE_SIZE", (0.00035, 0.0008))
PIXEL_RADIUS = G("MOTE_PIXEL_RADIUS", 0.5 * (36.0 / 35.0) / 1920.0)   # half a pixel per unit of distance at 1080 by 1920
GAIN = G("MOTE_GAIN", 3.2)              # brightness of the biggest specks at the beam's middle
Z_LOW, Z_HIGH = G("MOTE_Z", (3.5, 13.5))
CONE = G("MOTE_CONE", 0.74)             # share of the beam's radius they fill
DRIFT = G("MOTE_DRIFT", 0.55)           # how far a speck wanders
SEED = G("MOTE_SEED", 11)
TINT = (1.0, 0.94, 0.84)

# ---------------------------------------------------------------- the old specks stop rendering (kept in the file)
old = bpy.data.objects.get("Reveal Ending Mote Volume")
if old:
    if old.animation_data:
        old.animation_data_clear()
    old.hide_render = True
    old.hide_viewport = True
    for m in old.modifiers:
        if m.type == "PARTICLE_SYSTEM":
            m.show_render = False
            m.show_viewport = False

# ---------------------------------------------------------------- where they go: even on screen, each at its own depth
keep = scn.frame_current
scn.frame_set(213)                       # the camera's resting place
bpy.context.view_layer.update()
cm = cam.matrix_world.copy()
frame = [cm @ v for v in cam.data.view_frame(scene=scn)]      # the four corners of the picture, one unit ahead
tr, br, bl, tl = frame
origin = cm.translation.copy()
apex = spot.matrix_world.translation.copy()
axis = (spot.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
tan_half = math.tan(spot.data.spot_size / 2.0)
casing = bpy.data.objects["Casing___smooth_rounded_outer_edge_mobile_geometry"]
bb = [casing.matrix_world @ Vector(c) for c in casing.bound_box]
bc = sum(bb, Vector()) / 8.0
brad = max((p - bc).length for p in bb) * 0.75 + 0.25        # the badge's face plus a margin
aspect = scn.render.resolution_y / scn.render.resolution_x
rng = random.Random(SEED)


def inside(p):
    if not (Z_LOW <= p.z <= Z_HIGH):
        return False
    d = (p - apex).dot(axis)
    if d <= 0:
        return False
    r = ((p - apex) - axis * d).length
    if r > d * tan_half * CONE:
        return False
    # nothing in front of the badge's face
    if p.y < bc.y + 0.5 and (Vector((p.x, 0, p.z)) - Vector((bc.x, 0, bc.z))).length < brad:
        return False
    return True


pts, screen = [], []
for _ in range(60000):
    u, v = rng.random(), rng.random()
    if any((u - a) ** 2 + ((v - b) * aspect) ** 2 < SPACING ** 2 for a, b in screen):
        continue
    target = bl + (br - bl) * u + (tl - bl) * v
    ray = (target - origin).normalized()
    ok = [t for t in (9.0 + 0.1 * i for i in range(190)) if inside(origin + ray * t)]
    if not ok:
        continue
    pts.append(origin + ray * rng.choice(ok))
    screen.append((u, v))
scn.frame_set(keep)

me = bpy.data.meshes.get("Reveal Beam Specks") or bpy.data.meshes.new("Reveal Beam Specks")
me.clear_geometry()
me.from_pydata([tuple(p) for p in pts], [], [])
for name in ("size", "glint"):
    if name not in me.attributes:
        me.attributes.new(name, "FLOAT", "POINT")
me.attributes["size"].data.foreach_set("value", [SIZE[0] + (SIZE[1] - SIZE[0]) * rng.random() ** 1.6 for _ in pts])
me.attributes["glint"].data.foreach_set("value", [0.3 + 0.9 * rng.random() ** 1.8 for _ in pts])   # most are faint, a few catch more light
me.update()
ob = bpy.data.objects.get("Reveal Beam Specks")
if ob is None:
    ob = bpy.data.objects.new("Reveal Beam Specks", me)
    FXC.objects.link(ob)
ob.data = me
ob.visible_shadow = False
ob.hide_render = False

# ---------------------------------------------------------------- material: adds exactly the light that reaches it
mat = bpy.data.materials.get("Reveal Beam Speck") or bpy.data.materials.new("Reveal Beam Speck")
mat.use_nodes = True
mat.surface_render_method = "BLENDED"
nt = mat.node_tree
nt.nodes.clear()
N, L = nt.nodes, nt.links.new
out = N.new("ShaderNodeOutputMaterial")
# how far up the beam is, 0 to 1: the beam light's own fade in, frame by frame
lvl = N.new("ShaderNodeValue"); lvl.name = "beam level"
if nt.animation_data:
    nt.animation_data_clear()
full = max(1e-6, G("MOTE_FULL_LIGHT", 60000.0))
for f_ in range(scn.frame_start, scn.frame_end + 1):
    scn.frame_set(f_)
    lvl.outputs[0].default_value = spot.data.energy / full
    lvl.outputs[0].keyframe_insert("default_value", frame=f_)
scn.frame_set(keep)
# soft dot: brightest in its middle, fading to nothing at its rim
lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
soft = N.new("ShaderNodeMath"); soft.operation = "SUBTRACT"; soft.inputs[0].default_value = 1.0
soft2 = N.new("ShaderNodeMath"); soft2.operation = "POWER"; soft2.inputs[1].default_value = 1.5
L(lw.outputs["Facing"], soft.inputs[1]); L(soft.outputs[0], soft2.inputs[0])
att = N.new("ShaderNodeAttribute"); att.attribute_name = "glint"
# only where the beam is visible: same cone and height fades as the haze that shows the beam
tc = N.new("ShaderNodeTexCoord"); tc.object = haze
sep = N.new("ShaderNodeSeparateXYZ")
xy = N.new("ShaderNodeCombineXYZ")
ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
depth = N.new("ShaderNodeMath"); depth.operation = "MULTIPLY"; depth.inputs[1].default_value = -tan_half
rn = N.new("ShaderNodeMath"); rn.operation = "DIVIDE"
cone = N.new("ShaderNodeMapRange"); cone.interpolation_type = "SMOOTHSTEP"
cone.inputs["From Min"].default_value, cone.inputs["From Max"].default_value = G("MOTE_EDGE", (0.3, 0.85))
cone.inputs["To Min"].default_value, cone.inputs["To Max"].default_value = 1.0, 0.0
geo = N.new("ShaderNodeNewGeometry")
sepw = N.new("ShaderNodeSeparateXYZ")
above = N.new("ShaderNodeMapRange"); above.interpolation_type = "SMOOTHSTEP"
above.inputs["From Min"].default_value, above.inputs["From Max"].default_value = 3.2, 5.0
above.inputs["To Min"].default_value, above.inputs["To Max"].default_value = 0.0, 1.0
m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"
gain = N.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.name = "speck brightness"
gain.inputs[1].default_value = GAIN
em = N.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (*TINT, 1)
clear = N.new("ShaderNodeBsdfTransparent")
add = N.new("ShaderNodeAddShader")
L(tc.outputs["Object"], sep.inputs[0])
L(sep.outputs["X"], xy.inputs["X"]); L(sep.outputs["Y"], xy.inputs["Y"])
L(xy.outputs[0], ln.inputs[0])
L(sep.outputs["Z"], depth.inputs[0])
L(ln.outputs["Value"], rn.inputs[0]); L(depth.outputs[0], rn.inputs[1])
L(rn.outputs[0], cone.inputs["Value"])
L(geo.outputs["Position"], sepw.inputs[0]); L(sepw.outputs["Z"], above.inputs["Value"])
L(lvl.outputs[0], m1.inputs[0]); L(att.outputs["Fac"], m1.inputs[1])
L(cone.outputs[0], m2.inputs[0]); L(above.outputs[0], m2.inputs[1])
L(m1.outputs[0], m3.inputs[0]); L(m2.outputs[0], m3.inputs[1])
m4 = N.new("ShaderNodeMath"); m4.operation = "MULTIPLY"
L(m3.outputs[0], m4.inputs[0]); L(soft2.outputs[0], m4.inputs[1])
dim = N.new("ShaderNodeAttribute"); dim.attribute_name = "dim"          # how much of its drawn dot the speck really fills
m5 = N.new("ShaderNodeMath"); m5.operation = "MULTIPLY"
L(m4.outputs[0], m5.inputs[0]); L(dim.outputs["Fac"], m5.inputs[1])
L(m5.outputs[0], gain.inputs[0]); L(gain.outputs[0], em.inputs["Strength"])
L(clear.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1])
L(add.outputs[0], out.inputs["Surface"])

# ---------------------------------------------------------------- geometry: tiny spheres on the points, drifting on slow shared air
ng = bpy.data.node_groups.get("Reveal Beam Specks")
if ng is None:
    ng = bpy.data.node_groups.new("Reveal Beam Specks", "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
ng.nodes.clear()
N, L = ng.nodes, ng.links.new
gin = N.new("NodeGroupInput"); gout = N.new("NodeGroupOutput")
pos = N.new("GeometryNodeInputPosition")
tm = N.new("GeometryNodeInputSceneTime")
spd = N.new("ShaderNodeMath"); spd.operation = "MULTIPLY"; spd.inputs[1].default_value = G("MOTE_SPEED", 0.085)
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
nz.inputs["Scale"].default_value = 0.16; nz.inputs["Detail"].default_value = 1.0
sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0.5)
amp = N.new("ShaderNodeVectorMath"); amp.operation = "SCALE"; amp.inputs["Scale"].default_value = DRIFT * 2.0
rise = N.new("ShaderNodeCombineXYZ")
risez = N.new("ShaderNodeMath"); risez.operation = "MULTIPLY"; risez.inputs[1].default_value = G("MOTE_RISE", 0.04)   # a slow lift
addv = N.new("ShaderNodeVectorMath"); addv.operation = "ADD"
setp = N.new("GeometryNodeSetPosition")
ico = N.new("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 1.0; ico.inputs["Subdivisions"].default_value = 2
size = N.new("GeometryNodeInputNamedAttribute"); size.data_type = "FLOAT"; size.inputs["Name"].default_value = "size"
# never drawn narrower than a pixel: radius = the larger of its true radius and half a pixel at its distance;
# "dim" keeps its light true to its real size (area ratio, 1 for the biggest speck at 15 units)
camn = N.new("GeometryNodeInputActiveCamera")
cinfo = N.new("GeometryNodeObjectInfo"); cinfo.transform_space = "RELATIVE"
pos2 = N.new("GeometryNodeInputPosition")
dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"
pix = N.new("ShaderNodeMath"); pix.operation = "MULTIPLY"; pix.name = "pixel radius"; pix.inputs[1].default_value = PIXEL_RADIUS
rad = N.new("ShaderNodeMath"); rad.operation = "MAXIMUM"
ratio = N.new("ShaderNodeMath"); ratio.operation = "DIVIDE"
area = N.new("ShaderNodeMath"); area.operation = "POWER"; area.inputs[1].default_value = 2.0
norm = N.new("ShaderNodeMath"); norm.operation = "MULTIPLY"; norm.name = "dim scale"
norm.inputs[1].default_value = (PIXEL_RADIUS * 15.0 / SIZE[1]) ** 2 if SIZE[1] < PIXEL_RADIUS * 15.0 else 1.0
store = N.new("GeometryNodeStoreNamedAttribute"); store.data_type = "FLOAT"; store.domain = "POINT"
store.inputs["Name"].default_value = "dim"
inst = N.new("GeometryNodeInstanceOnPoints")
real = N.new("GeometryNodeRealizeInstances")
setm = N.new("GeometryNodeSetMaterial"); setm.inputs["Material"].default_value = mat
L(tm.outputs["Seconds"], spd.inputs[0]); L(spd.outputs[0], nz.inputs["W"])
L(pos.outputs[0], nz.inputs["Vector"])
L(nz.outputs[1], sub.inputs[0]); L(sub.outputs[0], amp.inputs[0])
L(tm.outputs["Seconds"], risez.inputs[0]); L(risez.outputs[0], rise.inputs["Z"])
L(amp.outputs[0], addv.inputs[0]); L(rise.outputs[0], addv.inputs[1])
L(gin.outputs[0], setp.inputs["Geometry"]); L(addv.outputs[0], setp.inputs["Offset"])
L(camn.outputs[0], cinfo.inputs["Object"])
L(pos2.outputs[0], dist.inputs[0]); L(cinfo.outputs["Location"], dist.inputs[1])
L(dist.outputs["Value"], pix.inputs[0])
L(size.outputs[0], rad.inputs[0]); L(pix.outputs[0], rad.inputs[1])
L(size.outputs[0], ratio.inputs[0]); L(rad.outputs[0], ratio.inputs[1])
L(ratio.outputs[0], area.inputs[0]); L(area.outputs[0], norm.inputs[0])
L(setp.outputs[0], store.inputs["Geometry"]); L(norm.outputs[0], store.inputs["Value"])
L(store.outputs[0], inst.inputs["Points"]); L(ico.outputs["Mesh"], inst.inputs["Instance"])
L(rad.outputs[0], inst.inputs["Scale"])
L(inst.outputs[0], real.inputs[0]); L(real.outputs[0], setm.inputs["Geometry"])
L(setm.outputs[0], gout.inputs[0])
md = ob.modifiers.get("Specks") or ob.modifiers.new("Specks", "NODES")
md.node_group = ng

V8_MOTES = dict(count=len(pts), spacing=SPACING, gain=GAIN, badge_radius=round(brad, 2))
print("v8 motes", V8_MOTES)
