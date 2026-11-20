"""Version 10 temple light: the look at the very end of the reveal (owner, 2026-11-19: "more epic, more
cinematic", the end first, the rest of the animation later). Run after v10_temple_geo.py and v10_temple_mat.py;
safe to run again. Every earlier temple light that is not in this script's list is switched to 0 (kept).

The idea: a dark hall lit from behind and above, so the stone shows as dark shapes with warm edges against
glowing air, and the chest in its golden beam is the brightest thing in the picture.
- Temple Back Glow: warm light deep in the corridor behind the arch. It lights the hall's air (a glow behind
  the badge) and the edges of the arch and the small pillars from behind.
- Temple Shaft L/R: two columns of light falling from above between the pillars, with their pools on the floor.
- Temple Rim L/R: warm light from behind on the big pillars' inner edges. Temple Arch Warm: the same under the
  big arch at the top.
- Temple High Light: a little soft warm light on the fronts so the stone keeps its detail.
- Temple Cool L/R/Top: faint blue light from the side aisles and above, so the shadows are cool against the gold.
- Temple Air: thin haze in the hall, thicker with distance (aerial depth). Only the back glow and the shafts
  light it; every other temple light has its volume share at 0 (in version 9 they lit the beam's haze too, which
  greyed the whole top of the picture).
- The beam from above (approved earlier, owner agreed to make it more golden with visible rays): a little more
  golden, and its haze gets streaks that fan out from the light, like rays through gaps in a roof.
The temple lights still reach only the temple (light linking); the chest and badge keep their own lights."""
import bpy, math
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = coll("Temple Light Receivers", TC)
FRONT = coll("Temple Front Receivers", TC)
FLOORS = coll("Temple Floor Receivers", TC)
for nm in ("Temple Pillar Front L", "Temple Pillar Front R", "Temple Pillar Arcade L", "Temple Pillar Arcade R",
           "Temple Pillar Apse L", "Temple Pillar Apse R", "Temple Pillar Cracks", "Temple Apse Arch", "Temple Nave Arch",
           "Temple Arcade Arches", "Temple Walls", "Temple Apse Wall", "Temple Vault", "Temple Floor", "Temple Floor Bed",
           "Temple Corridor Ribs", "Temple Corridor Pillars", "Temple Corridor End"):
    o = bpy.data.objects.get(nm)
    if o and o.name not in RECV.objects:
        RECV.objects.link(o)
BACK = coll("Temple Back Receivers", TC)          # everything the far light reaches except the floor
for o in RECV.objects:
    if o.name not in ("Temple Floor", "Temple Floor Bed") and o.name not in BACK.objects:
        BACK.objects.link(o)
USED = set()


def light(name, kind, loc, aim, energy, color, vol=0.0, recv=RECV, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
        TC.objects.link(o)
    if o.data.type != kind:
        o.data.type = kind
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.energy = energy
    o.data.color = color
    o.data.volume_factor = vol
    for k, v in kw.items():
        setattr(o.data, k, v)
    o.light_linking.receiver_collection = recv
    o.hide_render = False
    USED.add(name)
    return o


S = G("TEMPLE_LIGHT_SCALE", 1.0)
GOLD = (1.0, 0.70, 0.38)
WARM = (1.0, 0.78, 0.50)
COOL = G("COOL", (0.55, 0.68, 0.95))
# ---- behind: the glow in the corridor
# one strong light at the far doorway, shining down the corridor toward the camera: the ribs and pillars stand
# dark against glowing air, the arch and the big pillars catch it on their inner edges
light("Temple Back Glow", "SPOT", (0.0, 232.0, 9.0), (0.0, 60.0, 9.0), G("BACK_E", 750000) * S, GOLD, recv=BACK,
      vol=G("BACK_VOL", 1.0), spot_size=math.radians(16), spot_blend=0.3, shadow_soft_size=1.5, use_shadow=True)
# the same light on the floor, much weaker (at full strength every stone's far edge lit up as a bright bar)
light("Temple Back Floor", "SPOT", (0.0, 232.0, 9.0), (0.0, 60.0, 9.0), G("BACK_FLOOR_E", 110000) * S, GOLD, recv=FLOORS,
      spot_size=math.radians(16), spot_blend=0.3, shadow_soft_size=1.5, use_shadow=True)
# ---- from above: two columns of light between the pillars
for nm, x, y, deg, e in (("L", -10.0, 36.0, 7.0, 1.0), ("R", 11.5, 47.0, 6.0, 0.8)):
    light("Temple Shaft " + nm, "SPOT", (x, y - 1.0, 46.0), (x, y, FLOOR), G("SHAFT_E", 90000) * e * S, WARM,
          vol=G("SHAFT_VOL", 16.0), spot_size=math.radians(deg), spot_blend=1.0, shadow_soft_size=0.6, use_shadow=True,
          diffuse_factor=G("SHAFT_FLOOR", 0.45), specular_factor=G("SHAFT_FLOOR", 0.45))
# ---- warm edges
for sx, nm in ((-1, "L"), (1, "R")):
    light("Temple Rim " + nm, "SPOT", (-sx * 7.0, 68.0, 18.0), (sx * 17.2, 58.0, 14.0), G("RIM_E", 70000) * S, GOLD,
          spot_size=math.radians(46), spot_blend=0.8, shadow_soft_size=1.5, use_shadow=True)
light("Temple Arch Warm", "SPOT", (0.0, 61.5, 18.0), (0.0, 58.5, 44.0), G("ARCH_E", 30000) * S, GOLD,
      spot_size=math.radians(66), spot_blend=0.8, shadow_soft_size=2.0, use_shadow=True)
# ---- the beam's glow on the small arch and the wall round it (the mockup's arch is lit at its crown)
light("Temple Arch Face", "SPOT", (0.0, 40.0, 30.0), (0.0, 87.0, 31.0), G("FACE_E", 26000) * S, WARM,
      spot_size=math.radians(34), spot_blend=1.0, shadow_soft_size=2.0, use_shadow=True)
# ---- a little detail light on the fronts
light("Temple High Light", "SPOT", (0.0, 4.0, 40.0), (0.0, 54.0, 6.0), G("HIGH_E", 9000) * S, (1.0, 0.82, 0.62),
      spot_size=math.radians(100), spot_blend=0.5, shadow_soft_size=3.0, use_shadow=True)
# ---- cool shadows
for sx, nm in ((-1, "L"), (1, "R")):
    light("Temple Cool " + nm, "AREA", (sx * 27.0, 34.0, 26.0), (sx * 16.0, 58.0, 16.0), G("COOL_E", 2600) * S, COOL,
          shape="DISK", size=14.0, use_shadow=True)
light("Temple Cool Top", "AREA", (0.0, 26.0, 52.0), (0.0, 58.0, 42.0), G("COOL_TOP_E", 3000) * S, COOL,
      shape="DISK", size=16.0, use_shadow=True)
# ---- the floor and the dais
light("Temple Floor Light", "SPOT", (0.0, 26.0, 44.0), (0.0, 24.0, 0.0), G("FLOOR_E", 7000) * S, (0.75, 0.8, 0.95), recv=FLOORS,
      spot_size=math.radians(92), spot_blend=1.0, shadow_soft_size=4.0, use_shadow=True)
# the beam's warm spill on the floor round the dais, fading outward
light("Temple Beam Spill", "SPOT", (0.0, -1.4, 26.0), (0.0, -1.0, FLOOR), G("SPILL_E", 9000) * S, (1.0, 0.8, 0.54), recv=FLOORS,
      spot_size=math.radians(76), spot_blend=1.0, shadow_soft_size=2.0, use_shadow=True)
light("Temple Front Fill", "AREA", (0.0, -24.0, 5.0), (0.0, 10.0, -0.55), G("FRONT_E", 2200) * S, (1.0, 0.82, 0.6), recv=FRONT,
      vol=G("FRONT_VOL", 1.0), shape="RECTANGLE", size=24.0, size_y=6.0, use_shadow=True)
light("Temple Dais Key", "SPOT", (-13.0, -9.0, 20.0), (-0.5, 0.5, 0.0), G("DAIS_E", 2500) * S, (1.0, 0.72, 0.44), recv=FRONT,
      spot_size=math.radians(34), spot_blend=0.7, shadow_soft_size=1.0, use_shadow=True)
# ---- every other temple light from version 9 is off (kept in the file)
OFF = []
for o in TC.all_objects:
    if o.type == "LIGHT" and o.name.startswith("Temple ") and o.name not in USED:
        o.data.energy = 0.0
        OFF.append(o.name)

# ---- the air in the hall
am = mat("Temple Air")
n = NT(am)
tc = n.coord()
p = tc.outputs["Object"]
ps = n.sep(p)
prof = n.ramp(ps[1], (G("AIR_Y0", 20.0), G("AIR_Y1", 80.0)))
prof = n.math("ADD", G("AIR_NEAR", 0.35), n.math("MULTIPLY", prof, 1.0 - G("AIR_NEAR", 0.35)))
nz = n.node("ShaderNodeTexNoise", ins={"Vector": n.vmath("MULTIPLY", p, (0.05, 0.03, 0.08)), "Scale": 1.0, "Detail": 3.0,
                                      "Roughness": 0.55}, noise_dimensions="3D")
var = n.math("ADD", 0.7, n.math("MULTIPLY", nz.outputs["Fac"], 0.6))
# thicker inside the corridor beyond the arch: that is where the air should glow
var = n.math("MULTIPLY", var, n.math("ADD", 1.0, n.math("MULTIPLY", n.ramp(ps[1], (88.0, 100.0)), G("AIR_CORRIDOR", 1.6))))
dens = n.math("MULTIPLY", n.math("MULTIPLY", prof, var), G("AIR_DENSITY", 0.0016))
vol = n.node("ShaderNodeVolumePrincipled", ins={"Color": (0.92, 0.88, 0.82, 1), "Density": dens, "Anisotropy": G("AIR_ANISO", 0.45)})
o_ = n.node("ShaderNodeOutputMaterial")
n.link(vol.outputs[0], o_.inputs["Volume"])
x0, x1, y0, y1, z0, z1 = -15.2, 15.2, 16.0, 236.0, FLOOR, 58.0
V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
air = put("Temple Air", mesh_from("Temple Air", V, F), TC, [am], root)
air.visible_shadow = False
air.display_type = "WIRE"
if air.name not in RECV.objects:
    RECV.objects.link(air)

# ---- the beam from above: more golden, with rays
spot = bpy.data.objects["Reveal Overhead Light"]
spot.data.color = G("BEAM_COLOR", (1.0, 0.82, 0.56))
hm = bpy.data.materials["Reveal Ending Haze"]
ht = hm.node_tree
pv = next(nd for nd in ht.nodes if nd.bl_idname == "ShaderNodeVolumePrincipled")
pv.inputs["Color"].default_value = (1.0, 0.88, 0.66, 1)
if "v10 ray streaks" not in ht.nodes:
    src = pv.inputs["Density"].links[0].from_socket
    tcn = ht.nodes.new("ShaderNodeTexCoord")
    sep = ht.nodes.new("ShaderNodeSeparateXYZ")
    ht.links.new(tcn.outputs["Object"], sep.inputs[0])
    dz = ht.nodes.new("ShaderNodeMath"); dz.operation = "MULTIPLY"; dz.inputs[1].default_value = -1.0
    ht.links.new(sep.outputs["Z"], dz.inputs[0])                      # distance below the light
    dz2 = ht.nodes.new("ShaderNodeMath"); dz2.operation = "MAXIMUM"; dz2.inputs[1].default_value = 0.5
    ht.links.new(dz.outputs[0], dz2.inputs[0])
    ax = ht.nodes.new("ShaderNodeMath"); ax.operation = "DIVIDE"
    ay = ht.nodes.new("ShaderNodeMath"); ay.operation = "DIVIDE"
    ht.links.new(sep.outputs["X"], ax.inputs[0]); ht.links.new(dz2.outputs[0], ax.inputs[1])
    ht.links.new(sep.outputs["Y"], ay.inputs[0]); ht.links.new(dz2.outputs[0], ay.inputs[1])
    cmb = ht.nodes.new("ShaderNodeCombineXYZ")
    ht.links.new(ax.outputs[0], cmb.inputs["X"]); ht.links.new(ay.outputs[0], cmb.inputs["Y"])
    nzr = ht.nodes.new("ShaderNodeTexNoise"); nzr.name = "v10 ray noise"; nzr.noise_dimensions = "3D"
    ht.links.new(cmb.outputs[0], nzr.inputs["Vector"])
    rmp = ht.nodes.new("ShaderNodeMapRange"); rmp.name = "v10 ray range"; rmp.interpolation_type = "SMOOTHSTEP"
    ht.links.new(nzr.outputs["Fac"], rmp.inputs["Value"])
    mul = ht.nodes.new("ShaderNodeMath"); mul.name = "v10 ray streaks"; mul.operation = "MULTIPLY"
    ht.links.new(src, mul.inputs[0]); ht.links.new(rmp.outputs["Result"], mul.inputs[1])
    # a hot core: the haze is thickest down the middle of the beam and thins toward its edge
    r2 = ht.nodes.new("ShaderNodeVectorMath"); r2.operation = "LENGTH"
    ht.links.new(cmb.outputs[0], r2.inputs[0])
    core = ht.nodes.new("ShaderNodeMapRange"); core.name = "v10 beam core"; core.interpolation_type = "SMOOTHSTEP"
    ht.links.new(r2.outputs["Value"], core.inputs["Value"])
    mul2 = ht.nodes.new("ShaderNodeMath"); mul2.name = "v10 beam core mix"; mul2.operation = "MULTIPLY"
    ht.links.new(mul.outputs[0], mul2.inputs[0]); ht.links.new(core.outputs["Result"], mul2.inputs[1])
    ht.links.new(mul2.outputs[0], pv.inputs["Density"])
nzr = ht.nodes["v10 ray noise"]
nzr.inputs["Scale"].default_value = G("RAY_SCALE", 21.0)       # how many rays across the beam
nzr.inputs["Detail"].default_value = 1.5
nzr.inputs["Roughness"].default_value = 0.5
if "v10 beam core" not in ht.nodes:          # an earlier run of this script made the streaks without the core
    cmb_ = ht.nodes["v10 ray noise"].inputs["Vector"].links[0].from_node
    mul_ = ht.nodes["v10 ray streaks"]
    r2 = ht.nodes.new("ShaderNodeVectorMath"); r2.operation = "LENGTH"
    ht.links.new(cmb_.outputs[0], r2.inputs[0])
    core = ht.nodes.new("ShaderNodeMapRange"); core.name = "v10 beam core"; core.interpolation_type = "SMOOTHSTEP"
    ht.links.new(r2.outputs["Value"], core.inputs["Value"])
    mul2 = ht.nodes.new("ShaderNodeMath"); mul2.name = "v10 beam core mix"; mul2.operation = "MULTIPLY"
    ht.links.new(mul_.outputs[0], mul2.inputs[0]); ht.links.new(core.outputs["Result"], mul2.inputs[1])
    ht.links.new(mul2.outputs[0], pv.inputs["Density"])
core = ht.nodes["v10 beam core"]
core.inputs["From Min"].default_value, core.inputs["From Max"].default_value = 0.0, G("CORE_EDGE", 0.15)
core.inputs["To Min"].default_value, core.inputs["To Max"].default_value = G("CORE_MID", 2.4), G("CORE_OUT", 0.45)
rmp = ht.nodes["v10 ray range"]
rmp.inputs["From Min"].default_value, rmp.inputs["From Max"].default_value = 0.36, 0.66
rmp.inputs["To Min"].default_value, rmp.inputs["To Max"].default_value = G("RAY_MIN", 0.14), G("RAY_MAX", 2.7)
vault = bpy.data.objects.get("Temple Vault")
if vault:
    vault.visible_shadow = False
bpy.data.scenes["Chest Reveal"].eevee.shadow_pool_size = "1024"
result = {"lights": sorted(USED), "off": OFF}
