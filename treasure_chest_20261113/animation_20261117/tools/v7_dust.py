"""Version 7 landing dust: a real air simulation (Mantaflow gas) instead of keyed puff spheres
(owner, 2026-11-18: the old dust was ok but did not follow real physics and could look much better;
the settling dust must be high quality).

What is physical here:
- The chest itself pushes the air. Its body, boots, rims and lid are collision objects that move
  with the baked landing, so the falling edge squeezes air out from under it and drags air behind it.
- Dust starts on the floor. At each impact, floor dust on every side of the chest is thrown out as
  many small clumps (short lived particles, strongest at the edge that hits, amount from the impact
  speed in physics/landing_events.json) carried by the air squeezed from under that edge (the gap
  under the chest is only about 2 cells, too thin for the grid to resolve that jet by itself). Air
  drag stops the clumps within a few frames; the dust they release stays in the simulated air.
- Dust is heavier than air (negative density buoyancy): it rolls out along the floor, curls up,
  hangs, then sinks and thins out.
- Fine grit: a few hundred specks thrown up at each impact, carried by the simulated air (fluid flow
  force field), pulled down by real gravity for a 0.7 m chest, and settling on the floor.

Built in the separate dust file (chest_reveal_v7_dust.blend): effects stay out of the core file.
Run inside Blender; safe to run again. Bake with tools/v7_bake_dust.py in background Blender."""
import bpy, bmesh, math, json
from mathutils import Vector, Matrix

ROOT = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117"
scn = bpy.data.scenes["Chest Reveal"]
FXC = bpy.data.collections["Reveal FX"]
shake = bpy.data.objects["Reveal Chest Shake"]
FLOOR = -2.455
G = 77.9                                   # gravity for a 0.7 m chest in scene units per second squared
CACHE = globals().get("DUST_CACHE", ROOT + "/cache_dust")
RES = globals().get("DUST_RES", 160)
NOISE = globals().get("DUST_NOISE", 2)
F0, F1 = 12, globals().get("DUST_END", 213)
DOMAIN = ((-6.0, 5.5), (-6.0, 5.0), (FLOOR, FLOOR + globals().get("DUST_TOP", 4.6)))   # what the camera sees of the floor, so the cells stay small
ALPHA, VORT = -0.01, 0.22                   # heavy dust that still curls as the jet meets still air
DISSOLVE = 130                             # frames, logarithmic: thins as it settles out (150 before the owner asked for 15% faster)
DUST_COLOR = (0.68, 0.62, 0.54)            # pale dry dust
B, D = 2.775, 1.865                        # chest half width and half depth (chest frame)
OUT_SPEED = 7.0                            # squeezed air from under the falling edge, units per second at full strength
UP_SPEED = 2.0
EV = json.load(open(ROOT + "/physics/landing_events.json"))
IMPACTS = [(im["frame"], im["strength"], im["edge"]) for im in EV["impacts"] if im["strength"] > 0.04]
GRIT_PER_HIT = 160
PUFFS_PER_HIT = 170                       # dust clumps thrown out per side at full strength

COLLIDERS = ["R Master Chest Body Envelope", "R Lab Chest Barrel Lid Envelope", "R Lab Chest Upper Lid Rim",
             "R Lab Chest Lower Rim", "R Lab Chest Central Lower Cuff", "Reveal Underside",
             "R Lab Chest Angular Boot -1 -1", "R Lab Chest Angular Boot -1 1",
             "R Lab Chest Angular Boot 1 -1", "R Lab Chest Angular Boot 1 1"]


def set_interp(idb, mode):
    """Set every key of an ID's action to one interpolation. Blender 5.2 ignored the 'new keyframe
    interpolation' preference when keys were added from Python: parked openings slid down through
    the whole domain within a frame while releasing dust (a column of dust in one frame, the flash)."""
    ad = idb.animation_data
    act = ad.action if ad else None
    if act is None:
        return 0
    curves = []
    if hasattr(act, "layers") and act.layers:
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    curves.extend(cb.fcurves)
    elif hasattr(act, "fcurves"):
        curves = list(act.fcurves)
    n = 0
    for fc in curves:
        for kp in fc.keyframe_points:
            kp.interpolation = mode
            n += 1
    return n


def box(bm, x0, x1, y0, y1, z0, z1):
    for v in bmesh.ops.create_cube(bm, size=1.0)["verts"]:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))


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
    md.show_viewport = md.show_render = True
    return md


# ---------------------------------------------------------------- the old smoke stays off
for n in ("Reveal Smoke Domain", "Reveal Smoke Emitter", "Reveal Smoke Emitter Front",
          "Reveal Smoke Emitter Left", "Reveal Smoke Emitter Right"):
    o = bpy.data.objects.get(n)
    if o:
        for m in o.modifiers:
            if m.type == "FLUID":
                m.show_viewport = m.show_render = False
for n in ("Inside Body Frame", "Inside Lid Frame"):     # inside parts do not matter for floor dust
    o = bpy.data.objects.get(n)
    if o:
        for m in o.modifiers:
            if m.type == "FLUID":
                m.show_viewport = m.show_render = False

# ---------------------------------------------------------------- domain
(x0, x1), (y0, y1), (z0, z1) = DOMAIN
dom = mesh_obj("Reveal Dust Domain", lambda bm: box(bm, x0, x1, y0, y1, z0, z1))
dom.location = (0, 0, 0)
dm = fluid(dom, "DOMAIN")
ds = dm.domain_settings
# The cache folder first: changing a domain setting clears the cache in the folder the domain points at
# (a test setup once wiped the full detail bake this way).
ds.cache_directory = CACHE
ds.domain_type = "GAS"
ds.resolution_max = RES
ds.use_adaptive_domain = False
ds.alpha, ds.beta = ALPHA, 0.0
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
    ds.noise_strength = 1.4
    ds.noise_pos_scale = 2.5
    ds.noise_time_anim = 0.12
# (Tried 40 steps per frame at CFL 1 against the flash: no change, 12 times the bake time. The flash was
# the openings sliding through the domain, fixed by set_interp below.)
ds.timesteps_max, ds.timesteps_min = globals().get("DUST_TSTEPS", 16), 2
ds.cfl_condition = globals().get("DUST_CFL", 3.0)
ds.time_scale = 1.0                        # real time
dom.display_type = "WIRE"
dom.visible_shadow = False
if dom.animation_data:
    dom.animation_data_clear()
for _f, _h in ((1, True), (F0, True), (F0 + 1, False)):
    dom.hide_render = _h
    dom.keyframe_insert("hide_render", frame=_f)

# look: pale dust, soft forward scattering, fine breakup so the edges are wispy, never a smooth blob
mat = bpy.data.materials.get("Reveal Dust Volume") or bpy.data.materials.new("Reveal Dust Volume")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
N, L = nt.nodes, nt.links.new
out = N.new("ShaderNodeOutputMaterial")
pv = N.new("ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (*DUST_COLOR, 1)
pv.inputs["Anisotropy"].default_value = 0.45
attr = N.new("ShaderNodeAttribute"); attr.attribute_name = "density"
tc = N.new("ShaderNodeTexCoord")
nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 6.0
nz.inputs["Roughness"].default_value = 0.6
nz.inputs["W"].default_value = 0.0
nr = N.new("ShaderNodeMapRange")
nr.inputs["From Min"].default_value, nr.inputs["From Max"].default_value = 0.3, 0.75
nr.inputs["To Min"].default_value, nr.inputs["To Max"].default_value = 0.12, 1.3
curve = N.new("ShaderNodeMath"); curve.operation = "POWER"; curve.inputs[1].default_value = 1.0   # density from the solved dust amounts as it is
mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
gain = N.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.name = "dust density"
gain.inputs[1].default_value = globals().get("DUST_DENSITY", 110.0)   # retuned after the flash fix (the false dust column had inflated it)
L(tc.outputs["Object"], nz.inputs["Vector"])
L(nz.outputs["Fac"], nr.inputs["Value"])
L(attr.outputs["Fac"], curve.inputs[0])
L(curve.outputs[0], mul.inputs[0]); L(nr.outputs[0], mul.inputs[1])
L(mul.outputs[0], gain.inputs[0])
# Settling (plan section E): 25 micrometre mineral dust falls at 0.37 units/s. The gas grid has one
# shared density, so one shared falling top from the first strong release, with a soft 0.3 band.
geo = N.new("ShaderNodeNewGeometry")
sep = N.new("ShaderNodeSeparateXYZ")
top = N.new("ShaderNodeValue"); top.name = "settling top"
dz = N.new("ShaderNodeMath"); dz.operation = "SUBTRACT"
band = N.new("ShaderNodeMath"); band.operation = "DIVIDE"; band.inputs[1].default_value = 0.3; band.use_clamp = True
fade = N.new("ShaderNodeMath"); fade.operation = "MULTIPLY"
L(geo.outputs["Position"], sep.inputs[0])
L(top.outputs[0], dz.inputs[0]); L(sep.outputs["Z"], dz.inputs[1])
L(dz.outputs[0], band.inputs[0])
L(gain.outputs[0], fade.inputs[0]); L(band.outputs[0], fade.inputs[1])
L(fade.outputs[0], pv.inputs["Density"])
L(pv.outputs[0], out.inputs["Volume"])
if nt.animation_data:
    nt.animation_data_clear()
nz.inputs["W"].default_value = 0.0
nz.inputs["W"].keyframe_insert("default_value", frame=F0)
nz.inputs["W"].default_value = (F1 - F0) * 0.012
nz.inputs["W"].keyframe_insert("default_value", frame=F1)
T_SETTLE, V_SETTLE, Z_TOP0 = 16.8, 0.37 * 1.15, 2.6   # owner: settle 15% faster (about 27 micrometre dust)     # first strong release (frame), settling speed, top above the floor
_ip = bpy.context.preferences.edit.keyframe_new_interpolation_type
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
for fr_ in (F0, T_SETTLE, F1):
    top.outputs[0].default_value = FLOOR + Z_TOP0 - V_SETTLE * max(0.0, fr_ - T_SETTLE) / 30.0
    top.outputs[0].keyframe_insert("default_value", frame=fr_)
bpy.context.preferences.edit.keyframe_new_interpolation_type = _ip
set_interp(nt, "LINEAR")
dom.data.materials.clear()
dom.data.materials.append(mat)

# ---------------------------------------------------------------- collider: the moving chest
# One low poly stand in that moves with the chest: body and closed lid as one block, plus the four
# boots it lands on. The real parts (one rim alone has 66,000 faces) were rebuilt as obstacles many
# times per frame (35 s per frame at the test size); at this grid size the stand in moves the same air.
for n in COLLIDERS:                        # earlier tries put the obstacle on the real parts: off
    o = bpy.data.objects.get(n)
    if o:
        for m in o.modifiers:
            if m.type == "FLUID":
                m.show_viewport = m.show_render = False


def proxy_build(bm):
    box(bm, -2.75, 2.75, -1.80, 1.80, 0.237, 4.60)
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * 1.887, sx * 2.775))
            ya, yb = sorted((sy * 0.85, sy * 1.865))
            box(bm, xa, xb, ya, yb, 0.0, 0.883)


proxy = mesh_obj("Reveal Dust Chest Collider", proxy_build)
proxy.parent = shake
proxy.matrix_parent_inverse = Matrix.Identity(4)
proxy.location = (0, 0, 0)
proxy.rotation_euler = (0, 0, 0)
proxy.display_type = "WIRE"
proxy.hide_render = True
es = fluid(proxy, "EFFECTOR").effector_settings
es.effector_type = "COLLISION"
es.use_effector = True
es.subframes = globals().get("DUST_EFFECTOR_SUB", 3)   # the chest's position sampled finely within each frame
es.surface_distance = 0.0
es.use_plane_init = False


# ---------------------------------------------------------------- dust sources from the air solve
def chest_at(f):
    scn.frame_set(int(math.floor(f)), subframe=f - math.floor(f))
    M = shake.matrix_world
    yaw = math.atan2(M.col[0].y, M.col[0].x)
    return Matrix.Translation((M.translation.x, M.translation.y, 0)) @ Matrix.Rotation(yaw, 4, "Z"), yaw


tex = bpy.data.textures.get("Reveal Dust Clumps") or bpy.data.textures.new("Reveal Dust Clumps", "CLOUDS")
tex.noise_scale = 0.25
tex.noise_depth = 3
tex.contrast = 1.6
# Every earlier source (four sided strips, dust clumps, single strips) is switched off: all names.
for o in [o for o in bpy.data.objects if o.name.startswith("Reveal Dust Source ")]:
    for m in o.modifiers:
        m.show_viewport = m.show_render = False
    o.hide_render = True
    if o.name in FXC.objects:
        FXC.objects.unlink(o)
# One emitter per opening under the chest (tools/v7_squeeze.py, physics/dust_sources.json): placed
# just outside it, moving with the chest. Each frame it releases the dust the solve says left there,
# with the solved jet (world direction, keyed per frame) where the gap is too thin for the grid.
SRC = json.load(open(ROOT + "/physics/dust_sources.json"))
_prefs = bpy.context.preferences.edit
_interp = _prefs.keyframe_new_interpolation_type
_prefs.keyframe_new_interpolation_type = "CONSTANT"     # each frame's value holds for the whole frame
YAW = math.radians(32.0)
SOURCES = []
for sg in SRC["segments"]:
    if sg["dust"] <= 0 and not any(k["speed"] > 0 for k in sg["keys"]):
        continue
    name = f"Reveal Dust Opening {sg['name']}"
    x0, x1, y0, y1, z0, z1 = sg["box"]
    xm, ym = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    # a loose cluster of small round puffs inside the opening's box, not the box itself: a full box
    # showed as a white rectangle on the frame it fired
    def puffs(bm, seed=len(SOURCES)):
        import random
        rnd = random.Random(1000 + seed)
        hx, hy, hz = 0.5 * (x1 - x0), 0.5 * (y1 - y0), z1 - z0
        for _ in range(max(5, int(4 * hx * hy / 0.01))):
            rad = rnd.uniform(0.08, 0.14)
            c = Vector((rnd.uniform(-hx, hx), rnd.uniform(-hy, hy), rnd.uniform(0.3, 0.7) * hz))
            for v in bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rad)["verts"]:
                v.co = v.co + c
    em = mesh_obj(name, puffs)
    em.parent = None
    em.rotation_euler = (0.0, 0.0, YAW)   # the chest only rolls about its depth axis: yaw stays 32
    em.display_type = "WIRE"
    em.hide_render = True
    fm = fluid(em, "FLOW")
    fs = fm.flow_settings
    fs.flow_type = "SMOKE"
    fs.flow_behavior = "INFLOW"
    fs.flow_source = "MESH"
    fs.volume_density = 1.0
    fs.surface_distance = 0.0
    fs.smoke_color = DUST_COLOR
    fs.temperature = 0.0
    fs.subframes = 2
    fs.velocity_factor = 0.0               # the emitter's own motion is not added (audit)
    fs.velocity_normal = 0.0
    fs.use_texture = True
    fs.noise_texture = tex
    fs.texture_map_type = "AUTO"
    fs.texture_size = 0.25
    fs.texture_offset = 0.013 * len(SOURCES)
    if em.animation_data:
        em.animation_data_clear()
    path = fm.path_from_id("flow_settings")
    nx, ny = sg["normal"]
    d = Vector((math.cos(YAW) * nx - math.sin(YAW) * ny, math.sin(YAW) * nx + math.cos(YAW) * ny, 0.05))
    # Initial velocity stays on for the whole bake (switching it during a bake crashes Blender 5.2).
    # An opening with nothing to release this frame is parked far above the domain instead, so its
    # box never holds the air still. Active frames: the solved jet, or the air's own exit speed.
    # No injected jets: two bakes with initial velocity on and off came out identical (it has no
    # effect here), so the air is moved by the grid itself, the chest pushing it out from underneath.
    JETS = globals().get("DUST_JETS", False)
    fs.use_initial_velocity = JETS
    def put(frame, active, dens, speed):
        # on the floor under its opening: the dust is lifted from the floor, wherever the chest is
        scn.frame_set(frame)
        p = shake.matrix_world @ Vector((xm, ym, 0.0))
        fs.density = dens
        fs.velocity_coord = tuple(d * speed)
        em.location = (p.x, p.y, FLOOR if active else FLOOR + 60.0)
        em.keyframe_insert(f"{path}.density", frame=frame)
        em.keyframe_insert(f"{path}.velocity_coord", frame=frame)
        em.keyframe_insert("location", frame=frame)
    put(F0, False, 0.0, 0.0)
    for k in sg["keys"]:
        active = k["density"] > 0 or k["jet"]
        put(k["frame"], active, k["density"], k["speed"] if k["jet"] else max(k["air_speed"], 2.0))
    assert set_interp(em, "CONSTANT") > 0       # jump to the floor and back, never slide through the domain
    SOURCES.append((name, sg["side"], round(sg["dust"], 2)))
_prefs.keyframe_new_interpolation_type = _interp

# the stage's lights were set to skip volumes (no haze in the core file): the dust needs them
for n in ("Reveal Key", "Reveal Fill", "Reveal Rim", "Reveal Rim Right", "Reveal Top"):
    bpy.data.objects[n].data.volume_factor = 1.0

# ---------------------------------------------------------------- fine grit: real gravity, carried by the air, settles
floor = bpy.data.objects["Reveal Floor"]
col = next((m for m in floor.modifiers if m.type == "COLLISION"), None) or floor.modifiers.new("Collision", "COLLISION")
cs = floor.collision
cs.damping_factor = 0.85
cs.damping_random = 0.1
cs.friction_factor = 0.9
cs.friction_random = 0.1
cs.use_particle_kill = False

flowfield = bpy.data.objects.get("Reveal Dust Air")
if flowfield is None:
    flowfield = bpy.data.objects.new("Reveal Dust Air", None)
    FXC.objects.link(flowfield)
if flowfield.field is None:                # an empty has no field until one is switched on
    with bpy.context.temp_override(object=flowfield, active_object=flowfield):
        bpy.ops.object.forcefield_toggle()
flowfield.field.type = "FLUID_FLOW"
bpy.context.view_layer.update()
flowfield.field.source_object = dom
flowfield.field.strength = 1.0
flowfield.field.flow = 0.6                 # how strongly the grit follows the air

grain_me = bpy.data.meshes.get("Reveal Dust Grain")
if grain_me is None:
    grain_me = bpy.data.meshes.new("Reveal Dust Grain")
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0); bm.to_mesh(grain_me); bm.free()
grain = bpy.data.objects.get("Reveal Dust Grain") or bpy.data.objects.new("Reveal Dust Grain", grain_me)
if grain.name not in FXC.objects:
    FXC.objects.link(grain)
grain.hide_render = True
grain.hide_viewport = True
gm = bpy.data.materials.get("Reveal Dust Grain") or bpy.data.materials.new("Reveal Dust Grain")
gm.use_nodes = True
bs = gm.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value = (0.74, 0.68, 0.6, 1)
bs.inputs["Roughness"].default_value = 0.85
grain_me.materials.clear(); grain_me.materials.append(gm)

for k, (f, s, edge) in enumerate(IMPACTS):
    if s < 0.2:
        continue
    W, yaw = chest_at(f)
    for sy in (-1, 1):
      gname = f"Reveal Dust Grit Boot {k + 1} {'L' if edge < 0 else 'R'}{'F' if sy < 0 else 'B'}"
      bx0, bx1 = sorted((edge * 1.887, edge * 2.775 + edge * 0.15))
      by0, by1 = sorted((sy * 0.85, sy * 1.865 + sy * 0.15))
      em = mesh_obj(gname, lambda bm: box(bm, bx0, bx1, by0, by1, 0.0, 0.12))
      em.parent = None
      em.matrix_world = Matrix.Translation((0, 0, FLOOR + 0.005)) @ W
      em.display_type = "WIRE"
      psname = f"Reveal Dust Grit {k + 1} {'F' if sy < 0 else 'B'}"
      pset = bpy.data.particles.get(psname) or bpy.data.particles.new(psname)
      if not any(m.type == "PARTICLE_SYSTEM" and m.particle_system.settings == pset for m in em.modifiers):
          em.modifiers.new(psname, "PARTICLE_SYSTEM")
          em.particle_systems[-1].settings = pset
      em.hide_render = False                 # the grit renders; the box itself does not
      em.show_instancer_for_render = False
      em.show_instancer_for_viewport = False
      pset.count = int(GRIT_PER_HIT * s / 2)
      pset.frame_start, pset.frame_end = f, f + 2.0
      pset.lifetime = 400
      pset.emit_from = "VOLUME"
      pset.physics_type = "NEWTON"
      pset.normal_factor = 0.0
      # emitter space (the source box is already turned with the chest): outward along x, and up
      pset.object_align_factor = (edge * 5.0 * math.sqrt(s), sy * 2.0 * math.sqrt(s), 9.0 * math.sqrt(s))   # out from that boot
      pset.factor_random = 4.0 * math.sqrt(s)
      pset.mass = 0.002
      pset.drag_factor = 0.6
      pset.damping = 0.02
      pset.brownian_factor = 0.15
      pset.effector_weights.gravity = G / 9.81
      pset.effector_weights.all = 1.0
      pset.use_rotations = True
      pset.angular_velocity_mode = "RAND"
      pset.render_type = "OBJECT"
      pset.instance_object = grain
      pset.particle_size = 0.008
      pset.size_random = 0.75
      pset.collision_collection = None
      pset.use_die_on_collision = False
      pset.timestep = 1.0 / 30.0
      pset.subframes = 4
      pset.use_adaptive_subframes = True
      pset.effector_weights.collection = None
      pset.display_size = 0.02
      ps = next(m.particle_system for m in em.modifiers if m.type == "PARTICLE_SYSTEM" and m.particle_system.settings == pset)
      ps.seed = 17 + 2 * k + (sy > 0)
      pc = ps.point_cache
      pc.frame_start, pc.frame_end = F0, F1

# ---------------------------------------------------------------- volume quality in EEVEE
ee = scn.eevee
ee.volumetric_tile_size = "2"
ee.volumetric_samples = 96
ee.volumetric_sample_distribution = 0.85
ee.use_volumetric_shadows = True
ee.volumetric_shadow_samples = 32
ee.volumetric_end = 40.0

V7_DUST = dict(domain=(RES, NOISE, F0, F1), sources=SOURCES)
print("v7 dust", V7_DUST)
