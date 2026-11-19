"""Stage for the 'Chest Reveal' scene: world, lights, floor, portrait camera rig, render settings.
Run inside Blender after build_scene.py. Safe to run again (updates settings in place, no deletes)."""
import bpy, math
from mathutils import Vector, Matrix

scn = bpy.data.scenes["Chest Reveal"]
src = bpy.data.scenes["Full chest material evaluation"]
stage = bpy.data.collections["Reveal Stage"]
FLOOR = -2.455
NF = Vector((0.529919175863294, -0.8480481513760686, 0.0))   # chest front normal (world)
UF = Vector((0.8480481513760686, 0.529919175863294, 0.0))    # chest +x (world)


def obj(name, data, coll=stage):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, data)
        coll.objects.link(o)
    return o


# ---------- world: dark backdrop for the camera, neutral studio for reflections ----------
w = bpy.data.worlds.get("Reveal World")
if w is None:
    w = src.world.copy()
    w.name = "Reveal World"
scn.world = w
nt = w.node_tree
for n in nt.nodes:
    if n.bl_idname == "ShaderNodeMixRGB":            # reflection tint: near neutral, faintly warm
        n.inputs["Color2"].default_value = (1.0, 0.96, 0.9, 1.0)
    if n.name == "Background":
        n.inputs["Strength"].default_value = 0.30
    if n.name in ("Background.001", "Rollout camera background"):
        n.inputs["Color"].default_value = (0.0045, 0.0042, 0.0055, 1.0)

# ---------- lights ----------
def area(name, loc, target, energy, color, size, spread=None):
    d = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
    d.type = "AREA"
    d.energy, d.color, d.size = energy, color, size
    d.use_shadow = True
    if spread:
        d.spread = math.radians(spread)
    o = obj(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o

# key: upper left of camera, warm white; fill: low right, dim; rim: behind, cool, separates the
# silhouette from the dark backdrop; top: soft overhead so the lid arch reads.
area("Reveal Key", (-6.5, -9.0, 8.0), (0, 0, -0.5), 1300, (1.0, 0.93, 0.84), 3.0)
area("Reveal Fill", (8.0, -6.0, 1.5), (0, 0, -0.5), 260, (0.92, 0.95, 1.0), 4.0)
area("Reveal Rim", (-2.0, 9.0, 6.0), (0, 0, 0.5), 1600, (0.62, 0.74, 1.0), 2.5)
area("Reveal Rim Right", (7.5, 5.0, 4.0), (0, 0, 0.0), 650, (0.75, 0.82, 1.0), 2.0)
area("Reveal Top", (0.0, -1.0, 11.0), (0, 0, 0), 160, (1.0, 0.97, 0.92), 6.0)

# ---------- floor ----------
fm = bpy.data.materials.get("Reveal Floor") or bpy.data.materials.new("Reveal Floor")
fm.use_nodes = True
ft = fm.node_tree
ft.nodes.clear()
# Diffuse plus a weak glossy layer of fixed strength. A Principled floor seen at this grazing
# camera angle turns into a mirror of the bright studio (Fresnel), so the reflection strength
# is set directly here instead. Both fade to black away from the chest.
out = ft.nodes.new("ShaderNodeOutputMaterial"); out.location = (700, 0)
add = ft.nodes.new("ShaderNodeAddShader"); add.location = (500, 0)
dif = ft.nodes.new("ShaderNodeBsdfDiffuse"); dif.location = (250, 120)
glo = ft.nodes.new("ShaderNodeBsdfGlossy"); glo.location = (250, -120)
tc = ft.nodes.new("ShaderNodeTexCoord"); tc.location = (-700, 0)
ln = ft.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; ln.location = (-500, 0)
mr = ft.nodes.new("ShaderNodeMapRange"); mr.location = (-300, 0)
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 3.5, 15.0
mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.0
mr.interpolation_type = "SMOOTHERSTEP"
dc = ft.nodes.new("ShaderNodeMath"); dc.operation = "MULTIPLY"; dc.location = (0, 150)
dc.inputs[1].default_value = 0.010          # diffuse albedo near the chest
gc = ft.nodes.new("ShaderNodeMath"); gc.operation = "MULTIPLY"; gc.location = (0, -100)
gc.inputs[1].default_value = 0.05           # reflection strength near the chest
noise = ft.nodes.new("ShaderNodeTexNoise"); noise.location = (-500, -300)
noise.inputs["Scale"].default_value = 1.6
noise.inputs["Detail"].default_value = 6
rr = ft.nodes.new("ShaderNodeMapRange"); rr.location = (-300, -300)
rr.inputs["To Min"].default_value, rr.inputs["To Max"].default_value = 0.09, 0.16
L = ft.links.new
L(tc.outputs["Object"], ln.inputs[0]); L(ln.outputs["Value"], mr.inputs["Value"])
L(mr.outputs["Result"], dc.inputs[0]); L(dc.outputs["Value"], dif.inputs["Color"])
L(mr.outputs["Result"], gc.inputs[0]); L(gc.outputs["Value"], glo.inputs["Color"])
L(tc.outputs["Object"], noise.inputs["Vector"]); L(noise.outputs["Fac"], rr.inputs["Value"])
L(rr.outputs["Result"], glo.inputs["Roughness"])
L(dif.outputs[0], add.inputs[0]); L(glo.outputs[0], add.inputs[1]); L(add.outputs[0], out.inputs["Surface"])
me = bpy.data.meshes.get("Reveal Floor")
if me is None:
    me = bpy.data.meshes.new("Reveal Floor")
    s = 60.0
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    me.materials.append(fm)
floor = obj("Reveal Floor", me)
floor.location = (0, 0, FLOOR)

# ---------- camera rig: Dolly (placement + push) > Shake (impact shake) > Camera ----------
# Two framings on the same three quarter view: the landing framing (closer than v1, chest about
# 20% larger) and the hero framing the camera pushes to during the reveal.
# Head-on cinematic camera (owner, 2026-11-17): 5 degrees off frontal toward the near ring, 15 degrees
# above, 50 mm. Chosen from frontal candidates rendered side by side (previews/camcmp/grid.png).
# landing: wide enough for the real sideways tip over the corner; mystery: a slow push toward the
# lock; hero: tilted up and pulled back a touch so the risen badge is centred and dominant.
# Version 5 (owner's golden reference, 2026-11-17): straight on, 2 degrees off frontal so the gold
# lock sits in the horizontal centre while a sliver of the near end keeps the box solid.
CAM_AZ = -2.0
CAM_REST = dict(az=CAM_AZ, el=15.0, dist=25.6, aim_z=1.2, off=-0.42)
CAM_MID = dict(az=CAM_AZ, el=14.0, dist=19.6, aim_z=0.55, off=0.0)
CAM_HERO = dict(az=CAM_AZ, el=12.0, dist=21.0, aim_z=3.4, off=0.0)


def cam_pose(az, el, dist, aim_z, off=0.0):
    d = (math.cos(math.radians(el)) * (math.cos(math.radians(az)) * NF + math.sin(math.radians(az)) * UF)
         + math.sin(math.radians(el)) * Vector((0, 0, 1)))
    loc = Vector((0, 0, aim_z)) + UF * off + d * dist
    return loc, (-d).to_track_quat("-Z", "Y").to_euler()


dolly = obj("Reveal Camera Dolly", None)
dolly.empty_display_type = "ARROWS"
dolly.location, dolly.rotation_euler = cam_pose(**CAM_REST)
dolly["rest_loc"] = list(dolly.location)          # the animation starts the camera here
dolly["rest_rot"] = list(dolly.rotation_euler)
hl, hr = cam_pose(**CAM_HERO)
ml, mr = cam_pose(**CAM_MID)
dolly["mid_loc"] = list(ml)
dolly["mid_rot"] = list(mr)
dolly["hero_loc"] = list(hl)
dolly["hero_rot"] = list(hr)
shk = obj("Reveal Camera Shake", None)
shk.empty_display_size = 0.3
shk.parent = dolly
shk.matrix_parent_inverse = Matrix.Identity(4)
camd = bpy.data.cameras.get("Reveal Camera") or bpy.data.cameras.new("Reveal Camera")
camd.lens = 50
camd.sensor_fit = "AUTO"
camd.sensor_width = 36
camd.clip_start, camd.clip_end = 0.5, 300
cam = obj("Reveal Camera", camd)
cam.parent = shk
cam.matrix_parent_inverse = Matrix.Identity(4)
cam.location = (0, 0, 0)
cam.rotation_euler = (0, 0, 0)
scn.camera = cam

# ---------- render ----------
e = scn.eevee
e.taa_render_samples = 64
e.use_raytracing = True
e.ray_tracing_options.resolution_scale = "2"
e.use_shadows = True
e.shadow_ray_count = 2
e.shadow_step_count = 8
scn.render.use_motion_blur = True
scn.render.motion_blur_shutter = 0.35
scn.render.image_settings.file_format = "PNG"
# underside board: the chest's flat bottom was never meant to be seen; while the chest falls the
# camera looks up at it, so a thin dark wood board (moves with the chest) covers it.
bm_ = bpy.data.materials.get("Reveal Underside Wood") or bpy.data.materials.new("Reveal Underside Wood")
bm_.use_nodes = True
_b = bm_.node_tree.nodes.get("Principled BSDF")
_b.inputs["Base Color"].default_value = (0.09, 0.045, 0.022, 1)
_b.inputs["Roughness"].default_value = 0.75
_um = bpy.data.meshes.get("Reveal Underside") or bpy.data.meshes.new("Reveal Underside")
if not _um.polygons:
    _um.from_pydata([(-2.6, -1.66, 0), (2.6, -1.66, 0), (2.6, 1.66, 0), (-2.6, 1.66, 0)], [], [(3, 2, 1, 0)])
    _um.materials.append(bm_)
_uo = bpy.data.objects.get("Reveal Underside") or bpy.data.objects.new("Reveal Underside", _um)
if _uo.name not in bpy.data.collections["Reveal Chest Body"].objects:
    bpy.data.collections["Reveal Chest Body"].objects.link(_uo)
_uo.parent = bpy.data.objects["Reveal Chest Shake"]
_uo.matrix_parent_inverse = Matrix.Identity(4)
_uo.location = (0, 0, -2.217 + 2.455 - 0.004)
# the badge model's size (the reveal's scale keys multiply this): 0.68 makes it dominant in the hero pose
_bm = bpy.data.objects.get("Reveal Badge Model")
if _bm:
    _bm.scale = (0.68, 0.68, 0.68)
print("stage ok", tuple(round(v, 2) for v in dolly.location))

# ---------- light linking: the cool rim lights light the chest and badge only ----------
# (otherwise the floor mirrors them as bright rectangles while the chest is in the air)
rc = bpy.data.collections.get("Reveal Rim Light Receivers") or bpy.data.collections.new("Reveal Rim Light Receivers")
for cn in ("Reveal Chest Body", "Reveal Chest Lid", "Reveal Lock And Hasp", "Reveal Rings", "Reveal Badge"):
    c = bpy.data.collections[cn]
    if c.name not in rc.children:
        rc.children.link(c)
for ln in ("Reveal Rim", "Reveal Rim Right"):
    bpy.data.objects[ln].light_linking.receiver_collection = rc
