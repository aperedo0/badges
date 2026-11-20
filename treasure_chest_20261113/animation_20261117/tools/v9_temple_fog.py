"""Version 9 temple ground fog: thin, see through wisps lying on the floor where the mockup has them (around
the far pillar bases, along the back of the hall, beside the dais). Run after the other v9 scripts; safe to
run again; nothing to bake.

Each wisp is a soft card facing the resting camera. It has no glow of its own: it is lit like a thin layer
of mist on the floor (its shading normal points up), so it shows only where light falls on it. Its shape
drifts very slowly. Strength per card is the object's colour alpha; the whole layer scales with FOG_GAIN.
The far cards are lit by the temple's lights, the near ones by the chest's lights and the front fill."""
import bpy, math
from mathutils import Vector, Matrix

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
GAIN = G("FOG_GAIN", 2.2)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
FC = coll("Temple Fog", TC)
RECV = bpy.data.collections["Temple Light Receivers"]
FRONT = bpy.data.collections["Temple Front Receivers"]

# ------------------------------------------------------------------ material
def fog_material(name, beam=False):
    """beam=True: the wisp shows as the light from above comes up (it follows Reveal Overhead Light's
    energy, 0 before frame 132, full at 186), so it never sits beside the chest during the landing dust."""
    m = mat(name)
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    m.use_transparency_overlap = True
    n = NT(m)
    tc = n.coord()
    oi = n.node("ShaderNodeObjectInfo")
    t = n.node("ShaderNodeValue", label="fog time")
    fc = t.outputs[0].driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "frame / 300"
    v = n.vmath("MULTIPLY", tc.outputs["Object"], (0.62, 0.62, 1.1))
    n1 = n.node("ShaderNodeTexNoise", ins={"Vector": v, "W": t.outputs[0], "Scale": 0.8, "Detail": 2.5, "Roughness": 0.5,
                                          "Distortion": 0.15}, noise_dimensions="4D")
    v2 = n.vmath("SCALE", v, scale=2.4)
    n2 = n.node("ShaderNodeTexNoise", ins={"Vector": v2, "W": n.math("MULTIPLY", t.outputs[0], 1.6), "Scale": 1.0,
                                          "Detail": 2.0, "Roughness": 0.5}, noise_dimensions="4D")
    dens = n.math("MULTIPLY", n.ramp(n1.outputs["Fac"], (0.34, 0.82)), n.math("ADD", 0.6, n.math("MULTIPLY", n2.outputs["Fac"], 0.4)))
    uv = n.sep(tc.outputs["UV"])
    vprof = n.math("MULTIPLY", n.ramp(uv[1], (0.03, 0.2)), n.math("SUBTRACT", 1.0, n.ramp(uv[1], (0.25, 1.0))))
    hprof = n.math("MULTIPLY", n.ramp(uv[0], (0.0, 0.28)), n.math("SUBTRACT", 1.0, n.ramp(uv[0], (0.72, 1.0))))
    k = n.math("MULTIPLY", oi.outputs["Alpha"], GAIN)
    if beam:
        b = n.node("ShaderNodeValue", label="beam light")
        fb = b.outputs[0].driver_add("default_value")
        fb.driver.type = "SCRIPTED"
        var = fb.driver.variables.new()
        var.name = "e"
        var.type = "SINGLE_PROP"
        var.targets[0].id_type = "LIGHT"
        var.targets[0].id = bpy.data.objects["Reveal Overhead Light"].data
        var.targets[0].data_path = "energy"
        fb.driver.expression = "min(e / 60000.0, 1.0)"
        k = n.math("MULTIPLY", k, b.outputs[0])
    alpha = n.math("MULTIPLY", n.math("MULTIPLY", dens, n.math("MULTIPLY", vprof, hprof)), k)
    alpha = n.math("MINIMUM", alpha, 1.0)
    up = n.comb(0.0, 0.0, 1.0)
    tint = oi.outputs["Color"]
    dif = n.node("ShaderNodeBsdfDiffuse", ins={"Color": tint, "Normal": up})
    tr = n.node("ShaderNodeBsdfTranslucent", ins={"Color": tint, "Normal": up})
    lit = n.node("ShaderNodeMixShader", ins={0: 0.5, 1: dif.outputs[0], 2: tr.outputs[0]})
    tp = n.node("ShaderNodeBsdfTransparent")
    fin = n.node("ShaderNodeMixShader", ins={0: alpha, 1: tp.outputs[0], 2: lit.outputs[0]})
    n.out(fin.outputs[0])
    return m


M_FAR = fog_material("Temple Ground Fog")
M_NEAR = fog_material("Temple Ground Fog Near", beam=True)

# ------------------------------------------------------------------ cards: (x, y, width, height, strength, near)
CARDS = G("FOG_CARDS", [
    # far wisps hugging the pillar bases (beyond EEVEE's volume range, so they are soft cards)
    ("Far L", -17.2, 52.6, 13.0, 4.5, 0.5, False),
    ("Far R", 17.2, 52.6, 13.0, 4.5, 0.5, False),
    ("Far LL", -27.5, 57.0, 11.0, 5.0, 0.45, False),
    ("Far RR", 27.5, 57.0, 11.0, 5.0, 0.45, False),
    ("Back L", -17.5, 82.0, 9.0, 4.0, 0.4, False),
    ("Back R", 17.5, 82.0, 9.0, 4.0, 0.4, False),
    # replaced by the ground mist volume near the dais (cards showed straight edges there); kept hidden
    ("Far Back", 0.0, 72.0, 44.0, 4.0, 0.0, False),
    ("Mid L", -8.5, 15.0, 8.0, 3.2, 0.0, False),
    ("Mid R", 8.8, 17.0, 8.0, 3.4, 0.0, False),
    ("Near L", -6.4, 5.0, 5.5, 2.6, 0.0, True),
    ("Near R", 6.6, 6.0, 5.5, 2.8, 0.0, True),
    ("Front L", -4.9, -3.4, 3.6, 1.5, 0.0, True),
    ("Front R", 5.0, -3.0, 3.6, 1.6, 0.0, True),
])
cam = SCN.camera
keep = SCN.frame_current
SCN.frame_set(213)
cpos = root.matrix_world.inverted() @ cam.matrix_world.translation
SCN.frame_set(keep)
for name, x, y, w, h, k, near in CARDS:
    nm = "Temple Fog " + name
    V = [(-w / 2, 0, FLOOR - 0.05), (w / 2, 0, FLOOR - 0.05), (w / 2, 0, FLOOR + h), (-w / 2, 0, FLOOR + h)]
    me = mesh_from(nm, V, [(0, 1, 2, 3)], uvs={"UVMap": [(0, 0), (1, 0), (1, 1), (0, 1)]})
    o = put(nm, me, FC, [M_NEAR if near else M_FAR], root)
    o.hide_render = k <= 0.0
    yaw = math.atan2(-(cpos.x - x), (cpos.y - y)) + math.pi
    o.matrix_basis = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(yaw, 4, "Z")
    o.color = (0.78, 0.78, 0.76, k)
    o.visible_shadow = False
    tgt = FRONT if near else RECV
    if o.name not in tgt.objects:
        tgt.objects.link(o)

# ------------------------------------------------------------------ ground mist volume near the dais
# A thin layer lying on the floor beside and behind the dais, thickest low down and toward the picture's
# sides, clear of the chest. It has no glow of its own: it shows where light falls on it (the beam, the
# warm pools, the front fill). It comes up with the light from above, so it never mixes with the landing dust.
GM = G("GROUND_MIST", 0.36)
mm = mat("Temple Ground Mist")
n = NT(mm)
tc = n.coord()
p = tc.outputs["Object"]
t = n.node("ShaderNodeValue", label="mist time")
fc = t.outputs[0].driver_add("default_value")
fc.driver.type = "SCRIPTED"
fc.driver.expression = "frame / 260"
b = n.node("ShaderNodeValue", label="beam light")
fb = b.outputs[0].driver_add("default_value")
fb.driver.type = "SCRIPTED"
var = fb.driver.variables.new()
var.name = "e"
var.targets[0].id_type = "LIGHT"
var.targets[0].id = bpy.data.objects["Reveal Overhead Light"].data
var.targets[0].data_path = "energy"
fb.driver.expression = "min(e / 60000.0, 1.0)"
ps = n.sep(p)
v = n.vmath("MULTIPLY", p, (0.32, 0.32, 0.9))
n1 = n.node("ShaderNodeTexNoise", ins={"Vector": v, "W": t.outputs[0], "Scale": 1.0, "Detail": 3.0, "Roughness": 0.55,
                                      "Distortion": 0.5}, noise_dimensions="4D")
patch = n.ramp(n1.outputs["Fac"], (0.42, 0.72))
hgt = n.math("SUBTRACT", 1.0, n.ramp(ps[2], (FLOOR, FLOOR + 2.6)))
hgt = n.math("MULTIPLY", hgt, hgt)
rad = n.math("SQRT", n.math("ADD", n.math("MULTIPLY", ps[0], ps[0]), n.math("MULTIPLY", n.math("MULTIPLY", ps[1], ps[1]), 1.6)))
clear = n.ramp(rad, (4.4, 7.5))
sides = n.ramp(n.math("DIVIDE", n.math("ABSOLUTE", ps[0]), n.math("ADD", ps[1], 16.5)), (0.09, 0.2))   # toward the picture's edges
dens = n.math("MULTIPLY", n.math("MULTIPLY", patch, hgt), n.math("MULTIPLY", n.math("MULTIPLY", clear, sides), b.outputs[0]))
dens = n.math("MULTIPLY", dens, GM)
vol = n.node("ShaderNodeVolumePrincipled", ins={"Color": (0.86, 0.86, 0.84, 1), "Density": dens, "Anisotropy": 0.3})
o_ = n.node("ShaderNodeOutputMaterial")
n.link(vol.outputs[0], o_.inputs["Volume"])
V, F = [], []
x0, x1, y0, y1, z0, z1 = -15.0, 15.0, -9.0, 26.0, FLOOR - 0.05, FLOOR + 3.0
V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
gm = put("Temple Ground Mist", mesh_from("Temple Ground Mist", V, F), FC, [mm], root)
gm.visible_shadow = False
for c in (FRONT, bpy.data.collections.get("Temple Floor Receivers")):
    if c and gm.name not in c.objects:
        c.objects.link(gm)
result = {"cards": len(CARDS)}
