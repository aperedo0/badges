"""Version 9 temple materials (run inside Blender after v9_temple_geo.py; safe to run again).

Surface relief and fine colour come from three CC0 Poly Haven scans (temple/resources/SOURCES.json):
plastered_stone_wall (pillars, arches, walls), rock_surface (flagstones, dais), concrete_moss (moss).
The broad look is authored to the mockup: weathered grey green stone with lighter worn patches, dark
stains and vertical streaks; moss on the plinth ledges, low on the stone and in the floor joints; dark
damp flagstones with a soft sheen; a lighter dressed stone for the dais; gold inlay rings."""
import bpy

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
DAIS_A, DAIS_B = G("DAIS_AXES", (4.45, 3.6))
STONE = RES + "polyhaven_plastered_stone_wall/plastered_stone_wall_"
ROCK = RES + "polyhaven_rock_surface/rock_surface_"
MOSS = RES + "polyhaven_concrete_moss/concrete_moss_"


def principled(n, color, rough, normal=None, metallic=0.0, spec=0.5):
    p = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": color, "Roughness": rough, "Metallic": metallic,
                                               "Specular IOR Level": spec})
    if normal is not None:
        n.set(p.inputs["Normal"], normal)
    return p


def lum(n, color_socket):
    return n.node("ShaderNodeRGBToBW", ins={0: color_socket}).outputs[0]


def mul_col(n, col, val):
    return n.mix(1.0, col, val, blend="MULTIPLY")


def clamp01(n, x):
    return n.math("MAXIMUM", n.math("MINIMUM", x, 1.0), 0.0)


# ------------------------------------------------------------------ pillars, arches, walls
def stone_material(name, dark=1.0, contrast=1.5, tile=3.4, scan_colour=True, spall=False, moss_k=1.0):
    m = mat(name)
    n = NT(m)
    tc = n.coord()
    obj, onrm = tc.outputs["Object"], tc.outputs["Normal"]
    v = n.vmath("SCALE", obj, scale=1 / tile)
    d = n.image(STONE + "diff_2k.jpg", v, proj="BOX", blend=0.3)
    r = n.image(STONE + "rough_2k.jpg", v, color=False, proj="BOX", blend=0.3)
    detail = n.math("POWER", n.math("DIVIDE", lum(n, d.outputs[0]), 0.053), contrast) if scan_colour else 1.0
    # broad wear: lighter worn patches, dark stains, vertical run off streaks (soft, large)
    big = n.noise(obj, 0.05, detail=3, rough=0.55)
    mid = n.noise(obj, 0.22, detail=3, rough=0.55)
    sv = n.vmath("MULTIPLY", obj, (0.8, 0.8, 0.055))
    stk = n.noise(sv, 1.0, detail=3, rough=0.55)
    patch = n.ramp(big.outputs["Fac"], (0.36, 0.70))
    col = n.mix(patch, (0.100, 0.102, 0.088, 1), (0.150, 0.150, 0.126, 1))
    stain = n.ramp(mid.outputs["Fac"], (0.50, 0.74))
    col = n.mix(n.math("MULTIPLY", stain, 0.28), col, (0.05, 0.05, 0.043, 1))
    streak = n.ramp(stk.outputs["Fac"], (0.52, 0.75))
    col = n.mix(n.math("MULTIPLY", streak, 0.3), col, (0.05, 0.05, 0.043, 1))
    if scan_colour:
        col = mul_col(n, col, detail)
    z = n.sep(obj)[2]
    low = n.math("SUBTRACT", 1.0, n.ramp(z, (FLOOR + 0.6, FLOOR + 7.0)))
    col = mul_col(n, col, n.math("ADD", 0.62, n.math("MULTIPLY", 0.38, n.math("SUBTRACT", 1.0, low))))
    sp = 0.0
    if spall:                       # flaked, lighter worn patches with crisp edges (mockup: pale spalls on the shafts)
        sn = n.noise(obj, 0.55, detail=4, rough=0.6, distortion=0.4)
        sp = n.ramp(sn.outputs["Fac"], (0.61, 0.63))
        col = n.mix(n.math("MULTIPLY", sp, 0.8), col, mul_col(n, col, (1.42, 1.4, 1.32, 1)))
    # moss: patchy low on the stone, more on the plinth ledges
    up = n.ramp(n.sep(onrm)[2], (0.45, 0.85))
    mn = n.noise(obj, 0.95, detail=6, rough=0.66)
    m1 = n.math("MULTIPLY", low, n.ramp(mn.outputs["Fac"], (0.50 - 0.08 * (moss_k - 1), 0.60 - 0.06 * (moss_k - 1))))
    ledge = n.math("MULTIPLY", up, n.math("SUBTRACT", 1.0, n.ramp(z, (FLOOR + 6.6, FLOOR + 8.0))))
    m2 = n.math("MULTIPLY", ledge, n.ramp(mn.outputs["Fac"], (0.36 - 0.1 * (moss_k - 1), 0.48 - 0.1 * (moss_k - 1))))
    moss = clamp01(n, n.math("MAXIMUM", m1, m2))
    mv = n.vmath("SCALE", obj, scale=1 / 1.6)
    md = n.image(MOSS + "diff_2k.jpg", mv, proj="BOX", blend=0.3)
    mcol = mul_col(n, md.outputs[0], (0.85, 1.0, 0.55, 1))
    col = n.mix(moss, col, mcol)
    ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 1.4}, samples=12)
    col = mul_col(n, col, n.math("POWER", ao.outputs["AO"], 1.4))
    if dark != 1.0:
        col = mul_col(n, col, (dark, dark, dark, 1))
    rough = n.math("ADD", 0.72, n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.89), 4.0))
    if spall:
        rough = n.math("ADD", rough, n.math("MULTIPLY", sp, 0.12))
    rough = n.mix(moss, rough, 0.92, kind="FLOAT")
    h = n.math("ADD", n.math("ADD", lum(n, d.outputs[0]), n.math("MULTIPLY", moss, 0.03)), n.math("MULTIPLY", sp, 0.02))
    bump = n.node("ShaderNodeBump", ins={"Strength": 0.45 if scan_colour else 0.12, "Distance": 0.05, "Height": h})
    n.out(principled(n, col, rough, bump.outputs[0]).outputs[0])
    return m


stone_material("Temple Stone", spall=True, moss_k=2.3)
stone_material("Temple Stone Arch", 0.78, 1.2, 3.4)
stone_material("Temple Stone Wall", 0.32, 0.7, 7.0, False)     # the scan's block pattern repeated as a grid on big walls
stone_material("Temple Stone Dark", 0.3, 0.7, 7.0, False)

# ------------------------------------------------------------------ flagstones
m = mat("Temple Floor Slab")
n = NT(m)
w = n.uv("UVMap")
rnd = n.uv("SlabRand")
suv = n.uv("SlabUV")
half = n.uv("SlabHalf")
rs = n.sep(rnd)
off = n.comb(n.math("MULTIPLY", rs[0], 13.7), n.math("MULTIPLY", rs[1], 7.3), 0.0)
v = n.vmath("ADD", n.vmath("SCALE", w, scale=1 / 2.6), off)
d = n.image(ROCK + "diff_2k.jpg", v)
r = n.image(ROCK + "rough_2k.jpg", v, color=False)
nm = n.image(ROCK + "nor_gl_2k.jpg", v, color=False)
nmap = n.node("ShaderNodeNormalMap", ins={"Strength": 0.14, "Color": nm.outputs[0]}, space="TANGENT", uv_map="UVMap")
detail = n.math("POWER", n.math("DIVIDE", lum(n, d.outputs[0]), 0.12), 1.8)
tint = n.math("ADD", 0.62, n.math("MULTIPLY", rs[0], 0.76))
hue = n.mix(rs[1], (0.88, 0.97, 1.06, 1), (1.06, 1.0, 0.9, 1))
big = n.noise(w, 0.06, detail=3, rough=0.5)
broad = n.math("ADD", 0.8, n.math("MULTIPLY", big.outputs["Fac"], 0.4))
col = mul_col(n, (0.0175, 0.018, 0.018, 1), n.math("MULTIPLY", n.math("MULTIPLY", tint, detail), broad))
wn = n.noise(n.vmath("ADD", w, off), 0.7, detail=4, rough=0.6)      # worn lighter and stained darker areas in each stone
col = mul_col(n, col, n.math("ADD", 0.7, n.math("MULTIPLY", n.ramp(wn.outputs["Fac"], (0.35, 0.68)), 0.6)))
col = mul_col(n, col, hue)
ss, hh = n.sep(suv), n.sep(half)
ex = n.math("SUBTRACT", hh[0], n.math("ABSOLUTE", ss[0]))
ey = n.math("SUBTRACT", hh[1], n.math("ABSOLUTE", ss[1]))
e = n.math("MINIMUM", ex, ey)
en = n.noise(n.vmath("SCALE", w, scale=1.0), 3.0, detail=3, rough=0.6)
e2 = n.math("ADD", e, n.math("MULTIPLY", n.math("SUBTRACT", en.outputs["Fac"], 0.5), 0.16))
edge = n.math("SUBTRACT", 1.0, n.ramp(e2, (0.0, 0.2)))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", edge, 0.72)))
mz = n.noise(w, 0.8, detail=4, rough=0.6)
band = n.math("SUBTRACT", 1.0, n.ramp(e2, (0.0, 0.07)))       # moss creeps out of the joints in patches
moss = n.math("MULTIPLY", band, n.ramp(mz.outputs["Fac"], (0.42, 0.56)))
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", w, scale=1 / 1.4))
mcol = mul_col(n, md.outputs[0], (0.16, 0.24, 0.09, 1))
col = n.mix(clamp01(n, moss), col, mcol)
wet = n.ramp(n.noise(w, 0.11, detail=3, rough=0.5).outputs["Fac"], (0.48, 0.62))
rough = n.math("ADD", 0.52, n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.84), 2.0))
rough = n.math("SUBTRACT", rough, n.math("MULTIPLY", wet, 0.12))
rough = n.math("ADD", rough, n.math("MULTIPLY", edge, 0.25))      # worn, dusty edges do not shine
dctr = n.vmath("LENGTH", w)                                          # dustier, duller round the dais
near = n.math("SUBTRACT", 1.0, n.ramp(dctr, (7.0, 20.0)))
rough = n.math("ADD", rough, n.math("MULTIPLY", near, 0.3))
rough = n.mix(clamp01(n, moss), rough, 0.9, kind="FLOAT")
n.out(principled(n, col, clamp01(n, rough), nmap.outputs[0], spec=n.math("SUBTRACT", 0.5, n.math("MULTIPLY", near, 0.3))).outputs[0])

# ------------------------------------------------------------------ mossy bed in the joints
m = mat("Temple Floor Bed")
n = NT(m)
w = n.uv("UVMap")
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", w, scale=1 / 1.3))
sn = n.noise(w, 1.7, detail=4, rough=0.6)
col = n.mix(n.ramp(sn.outputs["Fac"], (0.47, 0.62)), (0.005, 0.0045, 0.004, 1), mul_col(n, md.outputs[0], (0.17, 0.25, 0.085, 1)))
n.out(principled(n, col, 0.95).outputs[0])

# ------------------------------------------------------------------ dais stone
m = mat("Temple Dais Stone")
n = NT(m)
tc = n.coord()
obj, onrm = tc.outputs["Object"], tc.outputs["Normal"]
v = n.vmath("SCALE", obj, scale=1 / 1.7)
d = n.image(ROCK + "diff_2k.jpg", v, proj="BOX", blend=0.3)
r = n.image(ROCK + "rough_2k.jpg", v, color=False, proj="BOX", blend=0.3)
detail = n.math("POWER", n.math("DIVIDE", lum(n, d.outputs[0]), 0.12), 2.6)
big = n.noise(obj, 0.35, detail=4, rough=0.6)
wear = n.noise(obj, 1.3, detail=5, rough=0.62)          # darker weathered blotches
col = n.mix(n.ramp(big.outputs["Fac"], (0.38, 0.66)), (0.040, 0.030, 0.019, 1), (0.076, 0.057, 0.035, 1))
col = mul_col(n, col, detail)
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", n.ramp(wear.outputs["Fac"], (0.5, 0.68)), 0.45)))
p = n.sep(obj)
q = n.math("ADD", n.math("POWER", n.math("DIVIDE", p[0], DAIS_A), 2.0), n.math("POWER", n.math("DIVIDE", p[1], DAIS_B), 2.0))
nz = n.sep(onrm)[2]
side = n.math("SUBTRACT", 1.0, n.ramp(nz, (0.25, 0.6)))
lowz = n.math("SUBTRACT", 1.0, n.ramp(p[2], (FLOOR + 0.05, -0.05)))
mn = n.noise(obj, 1.6, detail=6, rough=0.66)
pn = n.noise(obj, 0.5, detail=3, rough=0.5)
patches = n.ramp(pn.outputs["Fac"], (0.53, 0.61))
m_side = n.math("MULTIPLY", side, n.math("MULTIPLY", n.math("MAXIMUM", n.math("MULTIPLY", lowz, 0.9), patches),
                                                 n.ramp(mn.outputs["Fac"], (0.40, 0.54))))
rim = n.ramp(q, (0.84, 0.97))
m_top = n.math("MULTIPLY", n.math("MULTIPLY", rim, patches), n.ramp(mn.outputs["Fac"], (0.42, 0.55)))
moss = clamp01(n, n.math("MAXIMUM", m_side, m_top))
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", n.ramp(q, (0.5, 1.0)), 0.65)))   # weathered toward the rim
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", obj, scale=1 / 1.2), proj="BOX", blend=0.3)
col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", lowz, n.math("MULTIPLY", side, 0.2))))
col = n.mix(moss, col, mul_col(n, md.outputs[0], (0.55, 0.62, 0.32, 1)))
ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.3}, samples=12)
col = mul_col(n, col, n.math("POWER", ao.outputs["AO"], 1.2))
rough = n.math("ADD", 0.78, n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.84), 2.0))
rough = n.mix(moss, rough, 0.9, kind="FLOAT")
bump = n.node("ShaderNodeBump", ins={"Strength": 0.35, "Distance": 0.02,
                                    "Height": n.math("ADD", lum(n, d.outputs[0]), n.math("MULTIPLY", moss, 0.02))})
n.out(principled(n, col, rough, bump.outputs[0]).outputs[0])

# ------------------------------------------------------------------ gold inlay, groove, crack
m = mat("Temple Gold Inlay")
n = NT(m)
n.out(principled(n, (1.0, 0.72, 0.36, 1), 0.42, metallic=1.0).outputs[0])      # satin, so it catches the light all round
m = mat("Temple Inlay Groove")
n = NT(m)
n.out(principled(n, (0.008, 0.007, 0.006, 1), 0.85).outputs[0])
m = mat("Temple Crack")
n = NT(m)
n.out(principled(n, (0.004, 0.0035, 0.003, 1), 0.95).outputs[0])

result = {"materials": "ok"}
