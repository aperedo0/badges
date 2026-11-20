"""Version 11 stone: real character for the floor and for the platform under the chest (owner, 2026-11-19:
"do you think we can make some genuine enhancements to the texture beneath the badge and the concrete
floor?"; the floor read as smooth concrete pavers, the platform as a plain sandy disc).
Run inside chest_reveal_v11_torches.blend after v10_temple_mat.py and v11_torches.py (it rebuilds two of that
script's materials, so run it again after v10_temple_mat.py); safe to run again. Version 10 keeps the old stone.

Two more CC0 Poly Haven scans carry the look (temple/resources/SOURCES.json):
- Flagstones: rock_face_04, a dark cracked rock with grit in its cracks, laid large (one repeat is 4.2 units,
  each stone takes its own piece). Its height map darkens the cracks and hollows, its normal map gives the
  relief. Joints are grimy, edges are bitten here and there, moss sits in the joints, and in the damp areas
  water lies only in the hollows of the stone (so wet reads as wet stone, not as shiny blotches).
- Platform: rock_3, a pitted worn stone, with dirt in its pits, a few long cracks across the top, a darker
  weathered rim and quieter moss (it glowed yellow green from the low opening camera).
- Light that shows the relief: the two big torches' light reaches the floor at a low angle
  (`Temple Floor Firelight L/R`, floor only, follow lit_0), and the platform's key light sits lower."""
import bpy, math
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
DAIS_A, DAIS_B = G("DAIS_AXES", (4.45, 3.6))
ROCKF = RES + "polyhaven_rock_face_04/rock_face_04_"
ROCKD = RES + "polyhaven_rock_3/rock_3_"
MOSS = RES + "polyhaven_concrete_moss/concrete_moss_"
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]


def lum(n, c):
    return n.node("ShaderNodeRGBToBW", ins={0: c}).outputs[0]


def mul_col(n, col, val):
    return n.mix(1.0, col, val, blend="MULTIPLY")


def clamp01(n, x):
    return n.math("MAXIMUM", n.math("MINIMUM", x, 1.0), 0.0)


def sstep(n, x, lo, hi):
    return n.ramp(x, (lo, hi), interp="SMOOTH")


def desat(n, col, k):
    l = lum(n, col)
    return n.mix(k, col, n.comb(l, l, l))


# ------------------------------------------------------------------ flagstones
m = mat("Temple Floor Slab")
n = NT(m)
w = n.uv("UVMap")
rs = n.sep(n.uv("SlabRand"))
ss, hh = n.sep(n.uv("SlabUV")), n.sep(n.uv("SlabHalf"))
off = n.comb(n.math("MULTIPLY", rs[0], 13.7), n.math("MULTIPLY", rs[1], 7.3), 0.0)
TILE = G("FLOOR_TILE", 4.2)
v = n.vmath("ADD", n.vmath("SCALE", w, scale=1 / TILE), off)
d = n.image(ROCKF + "diff_2k.jpg", v)
r = n.image(ROCKF + "rough_2k.jpg", v, color=False)
nm = n.image(ROCKF + "nor_gl_2k.jpg", v, color=False)
dp = n.image(ROCKF + "disp_2k.png", v, color=False)
h = sstep(n, dp.outputs[0], 0.50, 0.82)                       # 0 in the cracks and hollows, 1 on the high spots
# colour: the scan's own, pulled toward a dark slate, each stone a little different
col = desat(n, d.outputs[0], G("FLOOR_GREY", 0.5))
# the scan's pale grit would show as light specks at phone size: bring the brightest bits down
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", sstep(n, lum(n, d.outputs[0]), 0.15, 0.3), 0.55)))
tint = n.math("ADD", 0.62, n.math("MULTIPLY", rs[0], 0.76))
hue = n.mix(rs[1], (0.86, 0.97, 1.08, 1), (1.1, 1.0, 0.88, 1))
big = n.noise(w, 0.06, detail=3, rough=0.5)
broad = n.math("ADD", 0.8, n.math("MULTIPLY", big.outputs["Fac"], 0.4))
col = mul_col(n, col, n.math("MULTIPLY", n.math("MULTIPLY", tint, broad), G("FLOOR_VALUE", 0.55)))
col = mul_col(n, col, hue)
col = mul_col(n, col, n.math("ADD", 0.3, n.math("MULTIPLY", sstep(n, h, 0.0, 0.5), 0.7)))          # dirt in the cracks
# the edge of each stone
ex = n.math("SUBTRACT", hh[0], n.math("ABSOLUTE", ss[0]))
ey = n.math("SUBTRACT", hh[1], n.math("ABSOLUTE", ss[1]))
e = n.math("MINIMUM", ex, ey)
en = n.noise(w, 3.0, detail=3, rough=0.6)
e2 = n.math("ADD", e, n.math("MULTIPLY", n.math("SUBTRACT", en.outputs["Fac"], 0.5), 0.16))
grime = n.math("SUBTRACT", 1.0, sstep(n, e2, 0.0, 0.2))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", grime, 0.7)))
bn = n.noise(n.vmath("ADD", w, off), 1.3, detail=2, rough=0.5)
bite = n.math("MULTIPLY", sstep(n, bn.outputs["Fac"], 0.57, 0.64), n.math("SUBTRACT", 1.0, sstep(n, e, 0.02, 0.4)))   # broken bits of edge
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", bite, 0.45)))
mz = n.noise(w, 0.8, detail=4, rough=0.6)
moss = clamp01(n, n.math("MULTIPLY", n.math("SUBTRACT", 1.0, sstep(n, e2, 0.0, 0.07)), sstep(n, mz.outputs["Fac"], 0.42, 0.56)))
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", w, scale=1 / 1.4))
col = n.mix(moss, col, mul_col(n, md.outputs[0], (0.11, 0.16, 0.06, 1)))
# damp: water lies in the hollows of the damp areas, away from the platform (the beam would mirror in it)
near = n.math("SUBTRACT", 1.0, n.ramp(n.vmath("LENGTH", w), (7.0, 20.0)))
zone = n.math("MULTIPLY", sstep(n, n.noise(w, 0.11, detail=3, rough=0.5).outputs["Fac"], 0.40, 0.58), n.math("SUBTRACT", 1.0, near))
damp = n.math("MULTIPLY", zone, n.math("SUBTRACT", 1.0, grime))
puddle = n.math("MULTIPLY", damp, n.math("SUBTRACT", 1.0, sstep(n, h, 0.3, 0.62)))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", damp, 0.3)))
rough = n.math("ADD", G("FLOOR_ROUGH", 0.66), n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.958), 2.0))
rough = n.math("ADD", rough, n.math("ADD", n.math("MULTIPLY", near, 0.2), n.math("MULTIPLY", grime, 0.2)))
rough = n.math("SUBTRACT", rough, n.math("MULTIPLY", damp, 0.22))
rough = n.mix(puddle, rough, G("PUDDLE_ROUGH", 0.2), kind="FLOAT")
rough = n.mix(moss, rough, 0.9, kind="FLOAT")
nmap = n.node("ShaderNodeNormalMap", ins={"Strength": G("FLOOR_RELIEF", 0.9), "Color": nm.outputs[0]}, space="TANGENT", uv_map="UVMap")
hb = n.math("SUBTRACT", n.math("MULTIPLY", h, 0.5), n.math("ADD", n.math("MULTIPLY", bite, 0.6), n.math("MULTIPLY", grime, 0.25)))
bump = n.node("ShaderNodeBump", ins={"Strength": 0.45, "Distance": 0.09, "Height": hb, "Normal": nmap.outputs[0]})
geo = n.node("ShaderNodeNewGeometry")
nrm = n.mix(n.math("MULTIPLY", puddle, 0.85), bump.outputs[0], geo.outputs["Normal"], kind="VECTOR")      # still water is flat
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": clamp01(n, rough), "Normal": nrm,
                                            "Specular IOR Level": n.math("SUBTRACT", 0.5, n.math("MULTIPLY", near, 0.25))})
n.out(pb.outputs[0])

# the bed seen in the joints: quieter moss (it turned yellow green under the firelight)
bed = mat("Temple Floor Bed")
nb = NT(bed)
wb = nb.uv("UVMap")
mdb = nb.image(MOSS + "diff_2k.jpg", nb.vmath("SCALE", wb, scale=1 / 1.3))
snb = nb.noise(wb, 1.7, detail=4, rough=0.6)
colb = nb.mix(nb.ramp(snb.outputs["Fac"], (0.47, 0.62)), (0.005, 0.0045, 0.004, 1), mul_col(nb, mdb.outputs[0], (0.09, 0.13, 0.05, 1)))
pbb = nb.node("ShaderNodeBsdfPrincipled", ins={"Base Color": colb, "Roughness": 0.95})
nb.out(pbb.outputs[0])

# ------------------------------------------------------------------ platform under the chest
m = mat("Temple Dais Stone")
n = NT(m)
tc = n.coord()
obj, onrm = tc.outputs["Object"], tc.outputs["Normal"]
TD = G("DAIS_TILE", 3.6)
v = n.vmath("SCALE", obj, scale=1 / TD)
d = n.image(ROCKD + "diff_2k.jpg", v, proj="BOX", blend=0.25)
r = n.image(ROCKD + "rough_2k.jpg", v, color=False, proj="BOX", blend=0.25)
dp = n.image(ROCKD + "disp_2k.png", v, color=False, proj="BOX", blend=0.25)
h = sstep(n, dp.outputs[0], 0.30, 0.68)
p = n.sep(obj)
q = n.math("ADD", n.math("POWER", n.math("DIVIDE", p[0], DAIS_A), 2.0), n.math("POWER", n.math("DIVIDE", p[1], DAIS_B), 2.0))
nz = n.sep(onrm)[2]
top = sstep(n, nz, 0.4, 0.8)
side = n.math("SUBTRACT", 1.0, n.ramp(nz, (0.25, 0.6)))
lowz = n.math("SUBTRACT", 1.0, n.ramp(p[2], (FLOOR + 0.05, -0.05)))
col = desat(n, d.outputs[0], G("DAIS_GREY", 0.3))
big = n.noise(obj, 0.35, detail=4, rough=0.6)
col = mul_col(n, col, n.math("MULTIPLY", n.math("ADD", 0.75, n.math("MULTIPLY", big.outputs["Fac"], 0.5)), G("DAIS_VALUE", 0.7)))
col = mul_col(n, col, n.math("ADD", 0.28, n.math("MULTIPLY", sstep(n, h, 0.0, 0.5), 0.72)))        # dirt in the pits
# a few long cracks across the top, broken along their length
cw = n.vmath("ADD", n.vmath("SCALE", obj, scale=G("CRACK_SCALE", 0.17)),
             n.vmath("SCALE", n.vmath("SUBTRACT", n.noise(obj, 0.5, detail=4, rough=0.6).outputs["Color"], (0.5, 0.5, 0.5)), scale=0.22))
cv = n.node("ShaderNodeTexVoronoi", ins={"Vector": cw, "Scale": 1.0}, feature="DISTANCE_TO_EDGE")
crack = n.math("SUBTRACT", 1.0, sstep(n, cv.outputs["Distance"], 0.0, G("CRACK_WIDTH", 0.012)))
crack = n.math("MULTIPLY", n.math("MULTIPLY", crack, top), sstep(n, n.noise(obj, 0.9, detail=2, rough=0.5).outputs["Fac"], 0.38, 0.5))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", crack, 0.85)))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", n.ramp(q, (0.5, 1.0)), 0.38)))      # weathered toward the rim
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", lowz, n.math("MULTIPLY", side, 0.3))))
mn = n.noise(obj, 1.6, detail=6, rough=0.66)
pn = n.noise(obj, 0.5, detail=3, rough=0.5)
patches = n.ramp(pn.outputs["Fac"], (0.53, 0.61))
m_side = n.math("MULTIPLY", side, n.math("MULTIPLY", n.math("MAXIMUM", n.math("MULTIPLY", lowz, 0.9), patches), n.ramp(mn.outputs["Fac"], (0.40, 0.54))))
m_top = n.math("MULTIPLY", n.math("MULTIPLY", n.ramp(q, (0.84, 0.97)), patches), n.ramp(mn.outputs["Fac"], (0.42, 0.55)))
moss = clamp01(n, n.math("MAXIMUM", m_side, m_top))
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", obj, scale=1 / 1.2), proj="BOX", blend=0.3)
col = n.mix(moss, col, mul_col(n, md.outputs[0], G("DAIS_MOSS", (0.30, 0.36, 0.17, 1))))
ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.3}, samples=12)
col = mul_col(n, col, n.math("POWER", ao.outputs["AO"], 1.2))
rough = n.math("ADD", G("DAIS_ROUGH", 0.74), n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.52), 1.2))
rough = n.mix(moss, rough, 0.9, kind="FLOAT")
hb = n.math("SUBTRACT", n.math("ADD", n.math("MULTIPLY", h, 0.9), n.math("MULTIPLY", moss, 0.05)), n.math("MULTIPLY", crack, 0.7))
bump = n.node("ShaderNodeBump", ins={"Strength": G("DAIS_RELIEF", 0.7), "Distance": 0.07, "Height": hb})
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": clamp01(n, rough), "Normal": bump.outputs[0],
                                            "Specular IOR Level": 0.25})
n.out(pb.outputs[0])

# ------------------------------------------------------------------ light that shows the relief
FLOORS = bpy.data.collections["Temple Floor Receivers"]
ctrl = bpy.data.objects["Temple Torch Control"]
for sx, nm, e in ((-1, "L", 1.0), (1, "R", 0.7)):
    name = "Temple Floor Firelight " + nm
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, "SPOT"))
        TC.objects.link(o)
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = (sx * 15.0, 54.0, 17.0)
    o.rotation_euler = (Vector((-sx * 2.0, -3.0, FLOOR)) - Vector(o.location)).to_track_quat("-Z", "Y").to_euler()
    L = o.data
    L.color = (1.0, 0.55, 0.22)
    L.spot_size = math.radians(34)
    L.spot_blend = 0.9
    L.shadow_soft_size = 1.0
    L.use_shadow = False                  # a help light for the stone's relief: the chest must not throw a long shadow at the camera
    L.volume_factor = 0.0
    o.light_linking.receiver_collection = FLOORS
    try:
        L.driver_remove("energy")
    except Exception:
        pass
    dr = L.driver_add("energy").driver
    dr.type = "SCRIPTED"
    var = dr.variables.new()
    var.name = "lit"
    var.type = "SINGLE_PROP"
    var.targets[0].id = ctrl
    var.targets[0].data_path = '["lit_0"]'
    dr.expression = "%.1f * lit" % (G("FIRELIGHT_E", 80000.0) * e)
key = bpy.data.objects["Temple Dais Key"]
key.location = G("DAIS_KEY_AT", (-14.0, -8.0, 11.0))
key.rotation_euler = (Vector((-0.5, 0.5, 0.0)) - Vector(key.location)).to_track_quat("-Z", "Y").to_euler()
key.data.energy = G("DAIS_KEY_E", 2600.0)
result = {"stone": "ok"}
