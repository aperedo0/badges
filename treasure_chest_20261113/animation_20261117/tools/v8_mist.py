"""Version 8 mist: replaces the version 7 opening fog (owner, 2026-11-19: "the smoke is just horrible").

The version 7 fog was a thick, cold, cotton wool cloud that sat on the rim. This is the opposite:
a thin, see through mist that the light inside the chest makes visible (owner's reference: a chest
opening with a bright light and soft glowing vapour). It wafts up out of the chest in soft wisps
when the lid swings, thins out as it rises and is nearly gone when the badge settles. Nothing pushes it: see CORE below.

Built in chest_reveal_v8_mist.blend (a copy of chest_reveal_v7_dust.blend). Run inside Blender, safe
to run again, no deletes. Bake with tools/v8_bake.py. It never touches the landing dust domain, and it
writes to its own cache folder (the version 7 fog cache is left alone).

Every number can be overridden by a MIST_* global set before the script runs.
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

G = globals().get
scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
shake = bpy.data.objects["Reveal Chest Shake"]
hinge = bpy.data.objects["Reveal Lid Hinge"]
FLOOR = -2.455
ROOT = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117"
CACHE = G("MIST_CACHE", ROOT + "/cache_smoke_mist")
RES = G("MIST_RES", 96)
NOISE = G("MIST_NOISE", 2)                     # 0 = no detail pass
F0, F1 = 80, 213
DOMAIN = ((-4.8, 4.8), (-4.4, 4.8), (FLOOR, FLOOR + 10.4))
ALPHA, BETA = G("MIST_ALPHA", 0.0), G("MIST_BETA", 1.0)    # lifted gently by its warmth, not by its weight
TEMP = G("MIST_TEMP", 1.0)
VORT = G("MIST_VORT", 0.12)
DISSOLVE = G("MIST_DISSOLVE", 68)              # frames: it thins out as it rises
MIST_COLOR = (0.93, 0.96, 1.0)                 # faintly cool white
LIGHT_COLOR = (0.84, 0.93, 1.0)                # the light inside: cool white (owner's reference)
CLOSED = 85                                    # a frame with the lid shut and the chest at rest
# keys (frame, value). The lid starts lifting at 95 and is fully open at 117; the badge rises from 116.
# Real physics only (owner, 2026-11-19: "if a real chest is opening ... is there going to be smoke pushed up
# like how it is now? how would real smoke react?"). The chest holds one fill of slightly warm smoke, made
# while the lid is shut; nothing makes more once it opens and nothing pushes it. It moves because the
# swinging lid drags it, its warmth lifts it and the rising badge shoves through it.
CORE = G("MIST_CORE", [(81, 0.0), (83, 0.8), (94, 0.8), (96, 0.0)])
# The light inside is at full strength before the lid moves and fades once it is open (owner, 2026-11-19:
# "it starts bright and then fades, does not start low then grow", like the reference chest). Two lights,
# because one light on the chest floor skimmed the lid at a shallow angle (every bump of the wood grain
# sparkled) and leaked through the plank seams as bright dashes on the front:
# - LIGHT: lights the mist only, nothing solid;
# - GLOW: a soft light on the wood and the badge, no mirror glints, placed so it meets the lid squarely.
LIGHT = G("MIST_LIGHT", [(86, 0.0), (90, 9000.0), (104, 9000.0), (116, 5400.0), (135, 3200.0), (186, 1900.0), (213, 1500.0)])
GLOW = G("MIST_GLOW", [(86, 0.0), (90, 4500.0), (104, 4500.0), (118, 1800.0), (140, 800.0), (213, 450.0)])
GAIN = G("MIST_GAIN", 13.0)                    # how thick the mist reads; low = see through
CURVE = G("MIST_CURVE", 0.7)                   # below 1 lifts the thin wisps and holds back the thick middle


def set_interp(idb, mode):
    ad = idb.animation_data
    act = ad.action if ad else None
    if act is None:
        return 0
    curves = []
    if getattr(act, "layers", None):
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    curves.extend(cb.fcurves)
    else:
        curves = list(act.fcurves)
    n = 0
    for fc in curves:
        for kp in fc.keyframe_points:
            kp.interpolation = mode
            n += 1
    return n


def boxes(bm, specs):
    for x0, x1, y0, y1, z0, z1 in specs:
        for v in bmesh.ops.create_cube(bm, size=1.0)["verts"]:
            v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))


def mesh_obj(name, specs, coll):
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm = bmesh.new(); boxes(bm, specs); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me)
    o.data = me
    if o.name not in coll.objects:
        coll.objects.link(o)
    return o


def fluid(o, kind):
    md = next((m for m in o.modifiers if m.type == "FLUID"), None) or o.modifiers.new("Fluid", "FLUID")
    md.fluid_type = kind
    md.show_viewport = md.show_render = True
    return md


def attach(o, parent, at_frame):
    """parent o so that its mesh, built in the chest frame, sits on the chest at at_frame"""
    scn.frame_set(at_frame)
    bpy.context.view_layer.update()
    o.parent = parent
    o.matrix_parent_inverse = parent.matrix_world.inverted() @ shake.matrix_world
    o.location = (0, 0, 0); o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1)


SRC = bpy.data.collections["Reveal Opening Sources"]
COL = bpy.data.collections["Reveal Opening Colliders"]

# ---------------------------------------------------------------- domain
(x0, x1), (y0, y1), (z0, z1) = DOMAIN
dom = mesh_obj("Reveal Opening Domain", [(x0, x1, y0, y1, z0, z1)], FXC)
dom.parent = None
dom.matrix_world = Matrix.Identity(4)
dm = fluid(dom, "DOMAIN")
ds = dm.domain_settings
ds.cache_directory = CACHE                    # first: nothing below may clear the version 7 cache
ds.domain_type = "GAS"
ds.resolution_max = RES
ds.use_adaptive_domain = False
ds.alpha, ds.beta = ALPHA, BETA
ds.vorticity = VORT
ds.use_dissolve_smoke = True
ds.dissolve_speed = DISSOLVE
ds.use_dissolve_smoke_log = True              # fades evenly, so the edges stay soft
ds.use_collision_border_bottom = True
for side in ("front", "back", "left", "right", "top"):
    setattr(ds, f"use_collision_border_{side}", False)
ds.cache_type = "ALL"
ds.cache_data_format = "OPENVDB"
ds.cache_frame_start, ds.cache_frame_end = F0, F1
ds.use_noise = NOISE > 0
if NOISE:
    ds.noise_scale = NOISE
    ds.noise_strength = G("MIST_NOISE_STRENGTH", 0.8)
    ds.noise_pos_scale = 1.5
    ds.noise_time_anim = 0.1
ds.timesteps_max, ds.timesteps_min = 8, 1
ds.cfl_condition = 3.0
ds.time_scale = 1.0
ds.fluid_group = SRC
ds.effector_group = COL
dom.display_type = "WIRE"
dom.visible_shadow = False
if dom.animation_data:
    dom.animation_data_clear()
for f_, h_ in ((1, True), (F0, True), (F0 + 1, False)):
    dom.hide_render = h_
    dom.keyframe_insert("hide_render", frame=f_)

# ---------------------------------------------------------------- look: thin mist, shown by the light
mat = bpy.data.materials.get("Reveal Opening Mist") or bpy.data.materials.new("Reveal Opening Mist")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
if nt.animation_data:
    nt.animation_data_clear()
N, L = nt.nodes, nt.links.new
out = N.new("ShaderNodeOutputMaterial")
pv = N.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (*MIST_COLOR, 1)
pv.inputs["Anisotropy"].default_value = G("MIST_ANISO", 0.2)
pv.inputs["Emission Strength"].default_value = 0.0      # no glow of its own: only light shows it
dens = N.new("ShaderNodeAttribute"); dens.attribute_name = "density"
tc = N.new("ShaderNodeTexCoord")
# a soft, slow, large breakup so it reads as drifting veils, not one even slab
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 4.0; nz.inputs["Roughness"].default_value = 0.55
mr = N.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.3, 0.72
mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.45, 1.15
mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
# fades out before the top and sides of the simulated space, so it never shows a cut edge
sep = N.new("ShaderNodeSeparateXYZ")
top = N.new("ShaderNodeMapRange"); top.interpolation_type = "SMOOTHSTEP"
top.inputs["From Min"].default_value, top.inputs["From Max"].default_value = z1 - 2.4, z1 - 0.3
top.inputs["To Min"].default_value, top.inputs["To Max"].default_value = 1.0, 0.0
ax = N.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"
side = N.new("ShaderNodeMapRange"); side.interpolation_type = "SMOOTHSTEP"
side.inputs["From Min"].default_value, side.inputs["From Max"].default_value = x1 - 1.4, x1 - 0.2
side.inputs["To Min"].default_value, side.inputs["To Max"].default_value = 1.0, 0.0
fade = N.new("ShaderNodeMath"); fade.operation = "MULTIPLY"
mul2 = N.new("ShaderNodeMath"); mul2.operation = "MULTIPLY"
gain = N.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.name = "mist density"
gain.inputs[1].default_value = GAIN
L(tc.outputs["Object"], nz.inputs["Vector"]); L(nz.outputs[0], mr.inputs["Value"])
crv = N.new("ShaderNodeMath"); crv.operation = "POWER"; crv.name = "mist curve"
crv.inputs[1].default_value = CURVE
L(dens.outputs["Fac"], crv.inputs[0])
L(crv.outputs[0], mul.inputs[0]); L(mr.outputs[0], mul.inputs[1])
L(tc.outputs["Object"], sep.inputs[0])
L(sep.outputs["Z"], top.inputs["Value"])
L(sep.outputs["X"], ax.inputs[0]); L(ax.outputs[0], side.inputs["Value"])
L(top.outputs[0], fade.inputs[0]); L(side.outputs[0], fade.inputs[1])
L(mul.outputs[0], mul2.inputs[0]); L(fade.outputs[0], mul2.inputs[1])
L(mul2.outputs[0], gain.inputs[0]); L(gain.outputs[0], pv.inputs["Density"])
L(pv.outputs[0], out.inputs["Volume"])
nz.inputs["W"].default_value = 0.0
nz.inputs["W"].keyframe_insert("default_value", frame=F0)
nz.inputs["W"].default_value = 0.8
nz.inputs["W"].keyframe_insert("default_value", frame=F1)
set_interp(nt, "LINEAR")
dom.data.materials.clear()
dom.data.materials.append(mat)

# ---------------------------------------------------------------- stand ins the mist flows around
BO, DO, BI, DI = 2.78, 1.86, 2.50, 1.58         # outer and inner half sizes of the body
ZF, ZR = 0.45, 2.80                              # inside floor and rim height
body = mesh_obj("Reveal Opening Body Collider", [
    (-BO, BO, -DO, DO, 0.24, ZF),
    (-BO, -BI, -DO, DO, 0.24, ZR), (BI, BO, -DO, DO, 0.24, ZR),
    (-BI, BI, -DO, -DI, 0.24, ZR), (-BI, BI, DI, DO, 0.24, ZR)], COL)
attach(body, shake, CLOSED)
lid = mesh_obj("Reveal Opening Lid Collider", [
    (-BO, BO, -DO, DO, 4.50, 4.74),
    (-BO, -BO + 0.2, -DO, DO, 2.84, 4.50), (BO - 0.2, BO, -DO, DO, 2.84, 4.50),
    (-BO + 0.2, BO - 0.2, -DO, -DO + 0.2, 2.84, 4.50), (-BO + 0.2, BO - 0.2, DO - 0.2, DO, 2.84, 4.50)], COL)
attach(lid, hinge, CLOSED)
casing = bpy.data.objects["Casing___smooth_rounded_outer_edge_mobile_geometry"]   # the badge's outer shell
if casing.name not in COL.objects:
    COL.objects.link(casing)
for o in (body, lid, casing):
    es = fluid(o, "EFFECTOR").effector_settings
    es.effector_type = "COLLISION"; es.use_effector = True; es.subframes = 2; es.surface_distance = 0.0
for o in (body, lid):
    o.display_type = "WIRE"; o.hide_render = True

# ---------------------------------------------------------------- sources (inside the chest)
tex = bpy.data.textures.get("Reveal Opening Mist Veil") or bpy.data.textures.new("Reveal Opening Mist Veil", "CLOUDS")
tex.noise_scale = 0.9; tex.noise_depth = 2; tex.contrast = 1.0


def source(name, spec, keys, temp):
    o = mesh_obj(name, [spec], SRC)
    attach(o, shake, CLOSED)
    o.display_type = "WIRE"; o.hide_render = True
    fm = fluid(o, "FLOW")
    fs = fm.flow_settings
    fs.flow_type = "SMOKE"; fs.flow_behavior = "INFLOW"; fs.flow_source = "MESH"
    fs.volume_density = 1.0; fs.surface_distance = 0.0
    fs.smoke_color = MIST_COLOR
    fs.temperature = temp
    fs.subframes = 2
    fs.use_initial_velocity = False            # nothing pushes the smoke
    fs.use_texture = True; fs.noise_texture = tex; fs.texture_map_type = "AUTO"; fs.texture_size = 1.2
    if o.animation_data:
        o.animation_data_clear()
    path = fm.path_from_id("flow_settings")
    for f_, v in keys:
        fs.density = v
        o.keyframe_insert(f"{path}.density", frame=f_)
    set_interp(o, "LINEAR")
    return o


core = source("Reveal Opening Core", (-2.3, 2.3, -1.35, 1.35, 0.6, 2.6), CORE, TEMP)
for name in ("Reveal Opening Rim Mist", "Reveal Opening Seep"):   # earlier sources: out of the simulation, kept in the file
    old = bpy.data.objects.get(name)
    if old:
        if old.name in SRC.objects:
            SRC.objects.unlink(old)
        if old.name not in FXC.objects:
            FXC.objects.link(old)
        old.hide_render = True; old.hide_viewport = True
        for m in old.modifiers:
            if m.type == "FLUID":
                m.show_viewport = m.show_render = False

# ---------------------------------------------------------------- the light inside the chest
lo = bpy.data.objects["Reveal Opening Light"]          # on the chest floor, facing up: the mist only
ld = lo.data
ld.color = LIGHT_COLOR
ld.volume_factor = G("MIST_LIGHT_VOLUME", 1.0)
ld.diffuse_factor = 0.0
ld.specular_factor = 0.0
if ld.animation_data:
    ld.animation_data_clear()
for f_, e in LIGHT:
    ld.energy = e
    ld.keyframe_insert("energy", frame=f_)
set_interp(ld, "LINEAR")

go = bpy.data.objects.get("Reveal Opening Glow")       # the wood and the badge: soft, no glints
if go is None:
    go = bpy.data.objects.new("Reveal Opening Glow", bpy.data.lights.new("Reveal Opening Glow", "POINT"))
    FXC.objects.link(go)
gd = go.data
gd.type = "POINT"
gd.color = LIGHT_COLOR
gd.shadow_soft_size = 0.8
gd.use_shadow = True
gd.specular_factor = 0.0
gd.diffuse_factor = 1.0
gd.volume_factor = 0.0
gpos = Matrix.Translation(G("MIST_GLOW_AT", (0.0, -0.7, 1.35)))   # chest frame: low, toward the front, so it faces the open lid
go.parent = None
scn.frame_set(CLOSED); bpy.context.view_layer.update()
go.matrix_world = shake.matrix_world @ gpos
go.parent = shake
go.matrix_parent_inverse = shake.matrix_world.inverted()
go.matrix_world = shake.matrix_world @ gpos
if gd.animation_data:
    gd.animation_data_clear()
for f_, e in GLOW:
    gd.energy = e
    gd.keyframe_insert("energy", frame=f_)
set_interp(gd, "LINEAR")

# a shadow only wall inside the body's walls and floor: nothing from inside leaks out through the seams
blk = mesh_obj("Reveal Opening Light Blocker", [
    (-BO + 0.08, BO - 0.08, -DO + 0.08, DO - 0.08, 0.29, 0.40),
    (-BO + 0.08, -BI - 0.08, -DO + 0.08, DO - 0.08, 0.29, ZR - 0.12), (BI + 0.08, BO - 0.08, -DO + 0.08, DO - 0.08, 0.29, ZR - 0.12),
    (-BI - 0.08, BI + 0.08, -DO + 0.08, -DI - 0.08, 0.29, ZR - 0.12), (-BI - 0.08, BI + 0.08, DI + 0.08, DO - 0.08, 0.29, ZR - 0.12)], FXC)
attach(blk, shake, CLOSED)
blk.display_type = "WIRE"
blk.hide_render = False
blk.visible_camera = False
blk.visible_shadow = True
for flag in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
    setattr(blk, flag, False)
for flag in ("hide_probe_volume", "hide_probe_sphere", "hide_probe_plane"):
    if hasattr(blk, flag):
        setattr(blk, flag, True)
bm_ = bpy.data.materials.get("Reveal Opening Light Blocker") or bpy.data.materials.new("Reveal Opening Light Blocker")
blk.data.materials.clear(); blk.data.materials.append(bm_)

V8_MIST = dict(res=RES, noise=NOISE, cache=CACHE, sources=[o.name for o in SRC.objects],
               colliders=[o.name for o in COL.objects], gain=GAIN)
print("v8 mist", V8_MIST)
