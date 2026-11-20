"""Version 11: the stone of the platform under the chest, in three styles (owner, 2026-11-19, about the pitted
stone: "something about the texture beneath the badge, the circle object it rests on that I do not like.. idk
what it is"). Run inside Blender; v11_stone.py runs it too. DAIS_STYLE chooses:
- "pitted": the rock_3 scan (pits, dirt in the pits, cracks). What the owner did not like: it is speckled and
  blotchy, reads like rough concrete, and is paler than the floor.
- "dressed": a dark, smooth, honed stone like the owner's first mockup: soft large variation and no speckle,
  a few thin cracks, a darker worn rim, and a soft sheen so the beam's warm light pools on it.
- "carved": the dressed stone with a carved band inside the gold rings (two fine grooves with short radial
  marks between them, like a dial), so the platform looks made for the chest.
- "marble": a dark polished stone with pale veins and the same carved band; it mirrors the chest and the
  light softly, worn duller toward the rim.
- "carved_dark": the carved stone in the marble's near black colour, matte and without veins (owner,
  2026-11-20: "show me B with C's color").
temple/tools/dais_style.py renders a style for one picture without saving it."""
import bpy, math

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
DAIS_A, DAIS_B = G("DAIS_AXES", (4.45, 3.6))
STYLE = G("DAIS_STYLE", "pitted")
ROCKD = RES + "polyhaven_rock_3/rock_3_"
ROCKS = RES + "polyhaven_rock_surface/rock_surface_"
MOSS = RES + "polyhaven_concrete_moss/concrete_moss_"


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


m = mat("Temple Dais Stone")
n = NT(m)
tc = n.coord()
obj, onrm = tc.outputs["Object"], tc.outputs["Normal"]
p = n.sep(obj)
q = n.math("ADD", n.math("POWER", n.math("DIVIDE", p[0], DAIS_A), 2.0), n.math("POWER", n.math("DIVIDE", p[1], DAIS_B), 2.0))
nz = n.sep(onrm)[2]
top = sstep(n, nz, 0.4, 0.8)
side = n.math("SUBTRACT", 1.0, n.ramp(nz, (0.25, 0.6)))
lowz = n.math("SUBTRACT", 1.0, n.ramp(p[2], (FLOOR + 0.05, -0.05)))
# a few long cracks across the top, broken along their length
cw = n.vmath("ADD", n.vmath("SCALE", obj, scale=G("CRACK_SCALE", 0.17)),
             n.vmath("SCALE", n.vmath("SUBTRACT", n.noise(obj, 0.5, detail=4, rough=0.6).outputs["Color"], (0.5, 0.5, 0.5)), scale=0.22))
cv = n.node("ShaderNodeTexVoronoi", ins={"Vector": cw, "Scale": 1.0}, feature="DISTANCE_TO_EDGE")
crack = n.math("SUBTRACT", 1.0, sstep(n, cv.outputs["Distance"], 0.0, G("CRACK_WIDTH", 0.012 if STYLE == "pitted" else 0.007)))
crack = n.math("MULTIPLY", n.math("MULTIPLY", crack, top), sstep(n, n.noise(obj, 0.9, detail=2, rough=0.5).outputs["Fac"], 0.38, 0.5))
# moss: low on the side and in a few patches on the rim
mn = n.noise(obj, 1.6, detail=6, rough=0.66)
pn = n.noise(obj, 0.5, detail=3, rough=0.5)
patches = n.ramp(pn.outputs["Fac"], (0.53, 0.61))
m_side = n.math("MULTIPLY", side, n.math("MULTIPLY", n.math("MAXIMUM", n.math("MULTIPLY", lowz, 0.9), patches), n.ramp(mn.outputs["Fac"], (0.40, 0.54))))
m_top = n.math("MULTIPLY", n.math("MULTIPLY", n.ramp(q, (0.84, 0.97)), patches), n.ramp(mn.outputs["Fac"], (0.42, 0.55)))
moss = clamp01(n, n.math("MAXIMUM", m_side, m_top))
md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", obj, scale=1 / 1.2), proj="BOX", blend=0.3)
mcol = mul_col(n, md.outputs[0], G("DAIS_MOSS", (0.30, 0.36, 0.17, 1)))
ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.3}, samples=12)
aok = n.math("POWER", ao.outputs["AO"], 1.2)

if STYLE == "pitted":
    v = n.vmath("SCALE", obj, scale=1 / G("DAIS_TILE", 3.6))
    d = n.image(ROCKD + "diff_2k.jpg", v, proj="BOX", blend=0.25)
    r = n.image(ROCKD + "rough_2k.jpg", v, color=False, proj="BOX", blend=0.25)
    dp = n.image(ROCKD + "disp_2k.png", v, color=False, proj="BOX", blend=0.25)
    h = sstep(n, dp.outputs[0], 0.30, 0.68)
    col = desat(n, d.outputs[0], 0.3)
    big = n.noise(obj, 0.35, detail=4, rough=0.6)
    col = mul_col(n, col, n.math("MULTIPLY", n.math("ADD", 0.75, n.math("MULTIPLY", big.outputs["Fac"], 0.5)), 0.7))
    col = mul_col(n, col, n.math("ADD", 0.28, n.math("MULTIPLY", sstep(n, h, 0.0, 0.5), 0.72)))        # dirt in the pits
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", crack, 0.85)))
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", n.ramp(q, (0.5, 1.0)), 0.38)))
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", lowz, n.math("MULTIPLY", side, 0.3))))
    col = mul_col(n, n.mix(moss, col, mcol), aok)
    rough = n.math("ADD", 0.74, n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.52), 1.2))
    rough = n.mix(moss, rough, 0.9, kind="FLOAT")
    hb = n.math("SUBTRACT", n.math("ADD", n.math("MULTIPLY", h, 0.9), n.math("MULTIPLY", moss, 0.05)), n.math("MULTIPLY", crack, 0.7))
    nrm = n.node("ShaderNodeBump", ins={"Strength": 0.7, "Distance": 0.07, "Height": hb}).outputs[0]
    spec = 0.25
else:
    v = n.vmath("SCALE", obj, scale=1 / 3.2)
    d = n.image(ROCKS + "diff_2k.jpg", v, proj="BOX", blend=0.3)
    r = n.image(ROCKS + "rough_2k.jpg", v, color=False, proj="BOX", blend=0.3)
    detail = n.math("POWER", n.math("DIVIDE", lum(n, d.outputs[0]), 0.12), G("DRESSED_GRAIN", 0.7))      # soft: no speckle
    big = n.noise(obj, 0.3, detail=3, rough=0.55)
    if STYLE == "carved_dark":
        col = n.mix(n.ramp(big.outputs["Fac"], (0.35, 0.7)), G("CHARCOAL_DARK", (0.016, 0.016, 0.018, 1)), G("CHARCOAL_LIGHT", (0.030, 0.028, 0.027, 1)))
    else:
        col = n.mix(n.ramp(big.outputs["Fac"], (0.35, 0.7)), G("DRESSED_DARK", (0.032, 0.028, 0.024, 1)), G("DRESSED_LIGHT", (0.052, 0.044, 0.036, 1)))
    col = mul_col(n, col, detail)
    mott = n.noise(obj, 1.1, detail=4, rough=0.6)                  # soft clouding, so the smooth stone is not one flat tone
    col = mul_col(n, col, n.math("ADD", 0.82, n.math("MULTIPLY", mott.outputs["Fac"], 0.36)))
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", crack, 0.8)))
    worn = n.ramp(q, (0.7, 1.0))
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", worn, 0.4)))
    col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", lowz, n.math("MULTIPLY", side, 0.3))))
    if STYLE == "marble":
        # dark stone with pale veins: two sizes of the same broken web
        col = n.mix(n.ramp(big.outputs["Fac"], (0.35, 0.7)), (0.016, 0.016, 0.018, 1), (0.03, 0.028, 0.027, 1))
        for vs, vw, vk in ((0.33, 0.014, 0.6), (0.8, 0.007, 0.3)):
            vw_ = n.vmath("ADD", n.vmath("SCALE", obj, scale=vs),
                          n.vmath("SCALE", n.vmath("SUBTRACT", n.noise(obj, 0.7, detail=4, rough=0.6).outputs["Color"], (0.5, 0.5, 0.5)), scale=0.5))
            vd = n.node("ShaderNodeTexVoronoi", ins={"Vector": vw_, "Scale": 1.0}, feature="DISTANCE_TO_EDGE")
            vein = n.math("MULTIPLY", n.math("SUBTRACT", 1.0, sstep(n, vd.outputs["Distance"], 0.0, vw)),
                          sstep(n, n.noise(obj, 0.6 + vs, detail=2, rough=0.5).outputs["Fac"], 0.4, 0.6))
            col = n.mix(n.math("MULTIPLY", vein, vk), col, (0.10, 0.085, 0.065, 1))
        col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", worn, 0.25)))
        col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", lowz, n.math("MULTIPLY", side, 0.3))))
    carve = 0.0
    if STYLE in ("carved", "marble", "carved_dark"):
        # distance in from the edge, so the band runs parallel to the gold rings
        rxy = n.math("SQRT", n.math("ADD", n.math("MULTIPLY", p[0], p[0]), n.math("MULTIPLY", p[1], p[1])))
        rad = n.math("DIVIDE", n.math("MULTIPLY", rxy, DAIS_A * DAIS_B),
                     n.math("MAXIMUM", n.math("SQRT", n.math("ADD", n.math("POWER", n.math("MULTIPLY", p[0], DAIS_B), 2.0),
                                                              n.math("POWER", n.math("MULTIPLY", p[1], DAIS_A), 2.0))), 0.001))
        inset = n.math("MULTIPLY", n.math("SUBTRACT", 1.0, n.math("SQRT", q)), rad)
        B0, B1 = G("CARVE_BAND", (0.64, 1.04))
        g1 = n.math("SUBTRACT", 1.0, sstep(n, n.math("ABSOLUTE", n.math("SUBTRACT", inset, B0)), 0.012, 0.03))
        g2 = n.math("SUBTRACT", 1.0, sstep(n, n.math("ABSOLUTE", n.math("SUBTRACT", inset, B1)), 0.012, 0.03))
        theta = n.math("ARCTAN2", n.math("DIVIDE", p[1], DAIS_B), n.math("DIVIDE", p[0], DAIS_A))
        NT_ = G("CARVE_MARKS", 64)
        tick = n.math("SUBTRACT", 1.0, sstep(n, n.math("ABSOLUTE", n.math("SINE", n.math("MULTIPLY", theta, NT_ / 2.0))), 0.14, 0.26))
        tick = n.math("MULTIPLY", tick, n.math("MULTIPLY", sstep(n, inset, B0 + 0.05, B0 + 0.09), n.math("SUBTRACT", 1.0, sstep(n, inset, B1 - 0.09, B1 - 0.05))))
        carve = n.math("MULTIPLY", n.math("MAXIMUM", n.math("MAXIMUM", g1, g2), tick), top)
        col = mul_col(n, col, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", carve, 0.6)))
    col = mul_col(n, n.mix(moss, col, mcol), aok)
    fine = n.noise(obj, 7.0, detail=2, rough=0.5)
    rough = n.math("ADD", G("DRESSED_ROUGH", 0.5), n.math("MULTIPLY", n.math("SUBTRACT", r.outputs[0], 0.84), 1.5))
    rough = n.math("ADD", rough, n.math("MULTIPLY", n.math("SUBTRACT", fine.outputs["Fac"], 0.5), 0.14))    # the sheen varies, the colour does not
    rough = n.math("ADD", rough, n.math("ADD", n.math("MULTIPLY", worn, 0.22), n.math("MULTIPLY", side, 0.25)))
    if STYLE == "marble":
        rough = n.math("ADD", n.math("ADD", G("MARBLE_ROUGH", 0.3), n.math("MULTIPLY", n.math("SUBTRACT", fine.outputs["Fac"], 0.5), 0.1)),
                       n.math("ADD", n.math("MULTIPLY", worn, 0.3), n.math("MULTIPLY", side, 0.3)))
    if STYLE in ("carved", "marble", "carved_dark"):
        rough = n.math("ADD", rough, n.math("MULTIPLY", carve, 0.2))
    rough = n.mix(moss, rough, 0.9, kind="FLOAT")
    hb = n.math("SUBTRACT", n.math("ADD", n.math("MULTIPLY", lum(n, d.outputs[0]), 0.5), n.math("MULTIPLY", moss, 0.04)), n.math("MULTIPLY", crack, 0.5))
    nrm = n.node("ShaderNodeBump", ins={"Strength": 0.1 if STYLE == "marble" else 0.3, "Distance": 0.06, "Height": hb}).outputs[0]
    if STYLE in ("carved", "marble", "carved_dark"):
        nrm = n.node("ShaderNodeBump", ins={"Strength": 0.9, "Distance": 0.05, "Height": n.math("SUBTRACT", 1.0, carve), "Normal": nrm}).outputs[0]
    spec = 0.5
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": clamp01(n, rough), "Normal": nrm, "Specular IOR Level": spec})
n.out(pb.outputs[0])
result = {"dais": STYLE}
