"""Version 5 smoke: a real Mantaflow gas simulation that fills the open chest, billows under the
lid, spills over the rim and slides down the outside like heavy mist, then thins out (behavior taken
from the owner's chest opening reference video; look and light from the owner's golden image).

Run inside Blender (safe to run again, no deletes). It builds:
  Reveal Smoke Domain  world aligned box around the chest (open sides, closed floor), gas, baked
                       cache in ../cache_smoke (deterministic: same file, same bake).
  Reveal Smoke Emitter (core) and Reveal Smoke Emitter Front, Left, Right: volume sources keyed with
                       the lid (density and push); a drifting cloud texture keeps the emission uneven.
                       The core billows up through the opening; the rim sources push the heavy mist
                       over the front and side edges, so it falls down the outside.
  Effectors            the body envelope, the inside frame, the lid envelope and the inside lid
                       frame collide with the smoke (the lid moves, so it pushes the smoke).
Tuning lives in the constants below; bake with tools/v5_bake_smoke.py in background Blender.
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
root = bpy.data.objects["Reveal Chest Root"]
FLOOR = -2.455
CACHE = globals().get("SMOKE_CACHE", "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/cache_smoke")

RES = globals().get("SMOKE_RES", 112)
NOISE = globals().get("SMOKE_NOISE", 0)          # noise upres factor, 0 = off
F0, F1 = 104, globals().get("SMOKE_END", 222)                                 # cache range
DOMAIN = ((-4.7, 4.7), (-4.5, 3.6), (FLOOR, FLOOR + 6.4))
ALPHA, BETA = globals().get("SMOKE_ALPHA", -3.5), 0.0                          # negative density buoyancy: the mist is heavy
VORT = globals().get("SMOKE_VORT", 0.2)
DISSOLVE = 70                                     # frames, logarithmic
# emitter keys: (frame, density, upward velocity). The lid starts lifting at 108, swings at 118.
EMIT = globals().get("SMOKE_EMIT", [(104, 0.0, 0.0), (110, 0.0, 0.0), (113, 0.9, 1.6), (122, 1.0, 2.2),
        (135, 0.9, 1.5), (150, 0.6, 0.8), (165, 0.25, 0.3), (175, 0.0, 0.0)])
SMOKE_COLOR = (0.86, 0.87, 0.89)


def box(bm, x, y, z0, z1):
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 2 * x, v.co.y * 2 * y, z0 + (v.co.z + 0.5) * (z1 - z0)))


def mesh_obj(name, build, coll=FXC):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me)
        coll.objects.link(o)
    else:
        old = o.data
        mats = list(old.materials)
        o.data = me
        for m in mats:
            me.materials.append(m)
        if old.users == 0:
            bpy.data.meshes.remove(old)
    return o


def fluid(o, kind):
    md = next((m for m in o.modifiers if m.type == "FLUID"), None) or o.modifiers.new("Fluid", "FLUID")
    md.fluid_type = kind
    return md


# ---------------------------------------------------------------- domain
(x0, x1), (y0, y1), (z0, z1) = DOMAIN
dom = mesh_obj("Reveal Smoke Domain", lambda bm: box(bm, (x1 - x0) / 2, (y1 - y0) / 2, z0, z1))
dom.location = ((x0 + x1) / 2, (y0 + y1) / 2, 0.0)
dm = fluid(dom, "DOMAIN")
ds = dm.domain_settings
ds.domain_type = "GAS"
ds.resolution_max = RES
ds.use_adaptive_domain = False
ds.alpha, ds.beta = ALPHA, BETA
ds.vorticity = VORT
ds.use_dissolve_smoke = True
ds.dissolve_speed = DISSOLVE
ds.use_dissolve_smoke_log = True
ds.use_collision_border_bottom = True
for side in ("front", "back", "left", "right", "top"):
    setattr(ds, f"use_collision_border_{side}", False)
ds.cache_directory = CACHE
ds.cache_type = "ALL"
ds.cache_data_format = "OPENVDB"
ds.cache_frame_start, ds.cache_frame_end = F0, F1
ds.use_noise = NOISE > 0
if NOISE:
    ds.noise_scale = NOISE
    ds.noise_strength = 1.2
    ds.noise_pos_scale = 2.0
ds.timesteps_max, ds.timesteps_min = 4, 1
ds.cfl_condition = 2.0
ds.time_scale = globals().get("SMOKE_TIME", 2.0)
dom.display_type = "WIRE"
dom.visible_shadow = False
# before its cache starts Blender renders the domain as a plain grey volume box: hidden until then
if dom.animation_data:
    dom.animation_data_clear()
for _f, _h in ((1, True), (F0, True), (F0 + 1, False)):
    dom.hide_render = _h
    dom.keyframe_insert("hide_render", frame=_f)

# volume look: pale grey white, a soft density curve so thin mist stays thin
mat = bpy.data.materials.get("Reveal Smoke") or bpy.data.materials.new("Reveal Smoke")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
pv = nt.nodes.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (*SMOKE_COLOR, 1)
pv.inputs["Anisotropy"].default_value = 0.35
attr = nt.nodes.new("ShaderNodeAttribute")
attr.attribute_name = "density"
curve = nt.nodes.new("ShaderNodeMath"); curve.operation = "POWER"; curve.inputs[1].default_value = 1.3
gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.name = "smoke density"
gain.inputs[1].default_value = globals().get("SMOKE_DENSITY", 10.0)
nt.links.new(attr.outputs["Fac"], curve.inputs[0])
nt.links.new(curve.outputs[0], gain.inputs[0])
nt.links.new(gain.outputs[0], pv.inputs["Density"])
# dissipation as seen: once the mist has spilled, it thins out (the pool on the floor never thickens
# into a blanket); keyed on the look, so it needs no rebake
DENSITY_KEYS = globals().get("SMOKE_DENSITY_KEYS", [(104, 1.0), (158, 1.0), (180, 0.62), (200, 0.36), (222, 0.22)])
if nt.animation_data:
    nt.animation_data_clear()
for f, k in DENSITY_KEYS:
    gain.inputs[1].default_value = globals().get("SMOKE_DENSITY", 10.0) * k
    gain.inputs[1].keyframe_insert("default_value", frame=f)
nt.links.new(pv.outputs[0], out.inputs["Volume"])
dom.data.materials.clear()
dom.data.materials.append(mat)

# ---------------------------------------------------------------- emitters
# Simulated smoke is a passive tracer: it does not take up room, so a filling chest never overflows
# by itself. The overflow comes from motion: a core source billows up through the opening (then its
# weight brings it back down), and thin sources along the front and side rims push the mist over the
# edge, where its weight carries it down the outside. Box = chest frame x, y half sizes, z range
# (above the floor); direction = chest frame (x, y, z) velocity; keys = (frame, density, speed).
tex = bpy.data.textures.get("Reveal Smoke Clouds") or bpy.data.textures.new("Reveal Smoke Clouds", "CLOUDS")
tex.noise_scale = 0.55
tex.noise_depth = 2
EMITTERS = globals().get("SMOKE_EMITTERS", [
    ("Reveal Smoke Emitter", (0.0, 0.0, 1.9, 1.0, 2.0, 2.7), (0.0, 0.0, 1.0), EMIT),
    ("Reveal Smoke Emitter Front", (0.0, -1.08, 1.9, 0.2, 2.55, 3.0), (0.0, -1.0, 0.35),
     [(104, 0.0, 0.0), (118, 0.0, 0.0), (124, 0.9, 1.9), (136, 1.0, 2.2), (152, 0.9, 1.8), (166, 0.5, 1.1),
      (178, 0.0, 0.0)]),
    ("Reveal Smoke Emitter Left", (-2.05, 0.0, 0.2, 0.85, 2.55, 3.0), (-1.0, 0.0, 0.35),
     [(104, 0.0, 0.0), (122, 0.0, 0.0), (128, 0.6, 1.0), (145, 0.7, 1.0), (160, 0.3, 0.6), (168, 0.0, 0.0)]),
    ("Reveal Smoke Emitter Right", (2.05, 0.0, 0.2, 0.85, 2.55, 3.0), (1.0, 0.0, 0.35),
     [(104, 0.0, 0.0), (122, 0.0, 0.0), (128, 0.6, 1.0), (145, 0.7, 1.0), (160, 0.3, 0.6), (168, 0.0, 0.0)]),
])
R3 = root.matrix_world.to_3x3().normalized()
for k_, (name, (cx_, cy_, hx, hy, za, zb), dirn, keys) in enumerate(EMITTERS):
    em = mesh_obj(name, lambda bm: box(bm, hx, hy, za, zb))
    em.parent = root
    em.matrix_parent_inverse = Matrix.Identity(4)
    em.location = (cx_, cy_, 0)
    em.display_type = "WIRE"
    em.hide_render = True
    fm = fluid(em, "FLOW")
    fs = fm.flow_settings
    fs.flow_type = "SMOKE"
    fs.flow_behavior = "INFLOW"
    fs.flow_source = "MESH"
    fs.volume_density = 1.0
    fs.surface_distance = 0.15
    fs.smoke_color = SMOKE_COLOR
    fs.temperature = 0.0
    fs.use_initial_velocity = True
    fs.velocity_factor = 0.0
    fs.velocity_normal = 0.0
    fs.use_texture = True
    fs.noise_texture = tex
    fs.texture_map_type = "AUTO"
    fs.texture_size = 1.0
    if em.animation_data:
        em.animation_data_clear()
    wdir = R3 @ Vector(dirn)                 # the flow's velocity is in world space
    path = fm.path_from_id("flow_settings")
    for f, d, sp_ in keys:
        fs.density = d
        fs.velocity_coord = tuple(wdir * sp_)
        fs.texture_offset = f * 0.02 + k_ * 0.37   # the cloudy pattern drifts: emission is never static
        for prop in ("density", "velocity_coord", "texture_offset"):
            em.keyframe_insert(f"{path}.{prop}", frame=f)

# ---------------------------------------------------------------- effectors
EFFECTORS = ["R Master Chest Body Envelope", "Inside Body Frame", "R Lab Chest Barrel Lid Envelope",
             "Inside Lid Frame", "R Lab Chest Upper Lid Rim"]
for n in EFFECTORS:
    o = bpy.data.objects.get(n)
    if o is None:
        continue
    md = fluid(o, "EFFECTOR")
    es = md.effector_settings
    es.effector_type = "COLLISION"
    es.use_effector = True
    es.surface_distance = 0.02
    es.subframes = 1
    es.use_plane_init = False

SMOKE = dict(domain=dom.name, res=RES, noise=NOISE, cache=CACHE, effectors=EFFECTORS)
print("smoke set", SMOKE)
