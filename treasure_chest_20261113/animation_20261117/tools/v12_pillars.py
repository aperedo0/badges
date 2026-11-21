"""Version 12: pillars that look like carved stone (owner, 2026-11-20, after the arches were redone: "it looks
like stone, and then now the pillars look kind of like Play-Doh. So now you got to improve the pillars").
Run inside chest_reveal_v12_full.blend after v12_dark.py; safe to run again; nothing is deleted (objects are
reused by name and get new mesh data).

Why they looked like modelling clay: the grooves were only shading painted onto a smooth cylinder (no real
edges, no real shadow), the colour was soft blotches, and nothing said "built from blocks".
- Real grooves: 16 concave flutes cut into each shaft with sharp ridges between them, fading out at the top
  and bottom of the shaft. The ridges stand where the old painted ones were, so every torch still sits in the
  flat middle of a flute.
- One solid shaft. (A first try stacked each shaft from three round blocks with seams; the owner: "I don't like
  the drums. Just make it look like real stone.")
- Real stone: colour, relief and roughness all come from the same scan of a weathered stone wall (Poly Haven
  plastered_stone_wall), so the light and dark agree with the bumps the way they do on a real surface. On the
  shaft the scan is wrapped round the pillar (two repeats, no smear); on the square blocks it is projected flat.
  Matte, with faint stains that run down the shaft, a little dirt in the grooves and pits, quiet moss low down
  and on the plinth ledges. Crisper edges on the plinths and capitals.
- The pillars of the long hall behind the small arch become plain round shafts with a simple base and band.
  Their stepped plinths and flared capitals stacked up into a jagged outline in the distance (owner: "this
  pattern in the back ... does not look good ... so jaggedy"). The long hall's air is thicker, so the far bays
  melt into haze, and the far light sits beyond the air (inside it, it made a bright dot in the doorway)."""
import bpy, bmesh, math, random
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
ROCK = RES + "polyhaven_rock_surface/rock_surface_"
ROCKF = RES + "polyhaven_rock_face_04/rock_face_04_"
MOSS = RES + "polyhaven_concrete_moss/concrete_moss_"
FRONT_Y, FRONT_X, ARCADE_Y = 58.0, 17.2, 22.0
INNER_Y, INNER_X, INNER_S = 87.0, 17.5, 0.88
CA = 15.3
BAYS = (116.0, 145.0, 174.0, 203.0)
SEED = G("TEMPLE_SEED", 7)
NF = G("FLUTES", 16)
NA = NF * 8                                       # points round the pillar: 8 per flute, one exactly on every ridge
FL = G("FLUTE_DEPTH_GEO", 0.085)
TURNS = 2                                         # repeats of the stone scan round a shaft
TILE = 2 * math.pi * 2.0 / TURNS                  # so one repeat is this wide (shaft radius 2)
CH = 0.3
K = 1.0 - CH


def unit_c(th):
    """How far the chamfered square reaches in direction th (half width 1)."""
    c, s_ = abs(math.cos(th)), abs(math.sin(th))
    return min(1.0 / max(c, 1e-9), 1.0 / max(s_, 1e-9), (1.0 + K) / (c + s_))


def torus_ring(ac, hc, r, n=8):
    return [("r", ac + r * math.cos(t), hc + r * math.sin(t), 0.0) for t in [math.radians(-90 + 180 * i / n) for i in range(1, n + 1)]]


def shaft_a(h):
    t = (h - 6.8) / 17.55
    return 2.06 + (1.9 - 2.06) * t ** 1.6 + 0.035 * math.sin(math.pi * t)


def shaft_rows():
    """One solid shaft: no seams."""
    out = []
    for i in range(19):
        h = 6.8 + 17.55 * i / 18
        fade = min(1.0, (h - 6.8) / 1.3, (24.35 - h) / 1.3)          # flutes die out toward the ends of the shaft
        out.append(("r", shaft_a(h), h, max(fade, 0.0)))
    return out


BASE = ([("c", 3.55, 0.0, 0), ("c", 3.55, 0.88, 0), ("c", 3.45, 0.98, 0),
         ("c", 3.25, 0.98, 0), ("c", 3.25, 4.35, 0), ("c", 3.0, 4.6, 0),
         ("c", 2.72, 4.6, 0), ("c", 2.72, 5.62, 0), ("c", 2.58, 5.8, 0),
         ("r", 2.12, 5.8, 0)] + torus_ring(2.12, 6.22, 0.42) + [("r", 2.06, 6.79, 0)])
TOP = (torus_ring(1.9, 24.57, 0.22, 6) + [("r", 1.9, 25.45, 0)] +
       [("r", 1.9 + 0.55 * (1 - math.cos(t)), 25.45 + 0.85 * math.sin(t), 0) for t in [math.radians(15 * i) for i in range(1, 7)]] +
       [("c", 2.45, 26.3, 0), ("c", 2.45, 27.35, 0), ("c", 2.58, 27.35, 0), ("c", 2.84, 27.62, 0), ("c", 2.84, 28.95, 0)])
PROFILE = BASE + shaft_rows() + TOP
# the long hall's pillars: a plain shaft with a simple base and a simple band (no steps, no flare)
PLAIN = ([("r", 2.5, 0.0, 0), ("r", 2.5, 1.1, 0), ("r", 2.3, 1.3, 0), ("r", 2.06, 1.5, 0)] +
         [("r", shaft_a(6.8 + 17.55 * i / 6), 1.5 + (26.9 - 1.5) * i / 6, 0) for i in range(1, 7)] +
         [("r", 2.2, 27.1, 0), ("r", 2.2, 28.95, 0)])
CHIP_EDGES = [(0.95, 3.5, 1), (4.5, 3.1, 1), (5.7, 2.65, 1), (26.3, 2.45, -1), (27.5, 2.7, -1)]


def pillar(cx, cy, s=1.0, seed=None, chips=0, profile=PROFILE):
    """Points, faces and per point: its direction round the pillar, (on the fluted shaft?, height), and where
    the stone scan sits on it (round the pillar, up). The first column of points is repeated at the end so the
    scan can wrap; weld() joins the two columns again."""
    verts, faces, dirs, marks, wrap, starts = [], [], [], [], [], []
    for kind, a, h, flute in profile:
        starts.append(len(verts))
        for i in range(NA + 1):
            th = 2 * math.pi * (i % NA) / NA
            c, s_ = math.cos(th), math.sin(th)
            r = a * (unit_c(th) if kind == "c" else 1.0)
            if flute:
                ph = ((i % NA) * NF / float(NA)) % 1.0               # 0 on a ridge, 0.5 in the middle of a flute
                r -= FL * flute * math.sin(math.pi * ph)
            verts.append([cx + s * r * c, cy + s * r * s_, FLOOR + s * h])
            dirs.append((c, s_))
            marks.append((1.0 if flute else 0.0, h / 29.0))
            wrap.append((TURNS * i / float(NA), s * h / TILE))
    for j in range(len(profile) - 1):
        for i in range(NA):
            a, b = starts[j] + i, starts[j] + i + 1
            faces.append((a, b, starts[j + 1] + i + 1, starts[j + 1] + i))
    faces.append(tuple(starts[0] + i for i in reversed(range(NA))))
    faces.append(tuple(starts[-1] + i for i in range(NA)))
    rng = random.Random(seed)
    for _ in range(chips):                       # worn, broken corners: mostly on the sides the camera sees
        h, a, sgn = rng.choice(CHIP_EDGES)
        corner = math.radians(rng.choice((-45.0, -135.0, -45.0, -135.0, 45.0, 135.0)) + rng.uniform(-16, 16))
        c = Vector((cx + s * a * unit_c(corner) * math.cos(corner), cy + s * a * unit_c(corner) * math.sin(corner), FLOOR + s * h))
        rad, depth = rng.uniform(0.55, 1.15) * s, rng.uniform(0.14, 0.36) * s
        for v in verts:
            dd = (Vector(v) - c).length
            if dd < rad:
                w = (1.0 - dd / rad) ** 2
                ax = Vector((cx - v[0], cy - v[1], 0.0))
                if ax.length > 1e-6:
                    ax.normalize()
                v[0] += ax.x * depth * w
                v[1] += ax.y * depth * w
                v[2] -= sgn * 0.6 * depth * w
    return [tuple(v) for v in verts], faces, dirs, marks, wrap


def weld(me, sharp_deg):
    """Join the repeated column of points (each face corner keeps its own place on the scan)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(me)
    bm.free()
    me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    me.update()
    return me


# ------------------------------------------------------------------ the stone
PW = RES + "polyhaven_plastered_stone_wall/plastered_stone_wall_"
PW_LUM, PW_RGB, PW_ROUGH, PW_H = 0.0535, (0.0587, 0.0534, 0.0395), 0.89, 0.426     # the scan's averages (measured)


def pillar_stone(name):
    m = mat(name)
    n = NT(m)
    obj = n.coord().outputs["Object"]
    ps = n.sep(obj)
    rnd = n.node("ShaderNodeObjectInfo").outputs["Random"]
    mk = n.sep(n.uv("PillarShaft"))                                  # on the fluted shaft?, height / 29
    uvc = n.uv("PillarUV")
    us = n.sep(uvc)
    dr = n.sep(n.uv("PillarDir"))
    off = n.comb(n.math("MULTIPLY", rnd, 7.3), n.math("MULTIPLY", rnd, 3.1), 0.0)        # every pillar its own piece of the scan
    on_shaft = n.vmath("ADD", uvc, off)
    on_block = n.vmath("ADD", n.vmath("SCALE", obj, scale=1.0 / TILE), off)

    def scan(suffix, color):
        a = n.image(PW + suffix, on_shaft, color=color)
        b = n.image(PW + suffix, on_block, color=color, proj="BOX", blend=0.25)
        return n.mix(mk[0], b.outputs[0], a.outputs[0])

    d, hgt, rgh = scan("diff_2k.jpg", True), scan("disp_2k.png", False), scan("rough_2k.jpg", False)
    lum = n.node("ShaderNodeRGBToBW", ins={0: d}).outputs[0]
    detail = n.math("POWER", n.math("DIVIDE", lum, PW_LUM), G("PILLAR_CONTRAST", 0.55))
    # the scan's own slight shifts of hue, round a neutral average (the stone's colour stays the hall's grey)
    hue = n.vmath("DIVIDE", n.vmath("DIVIDE", d, n.comb(lum, lum, lum)), tuple(c / PW_LUM for c in PW_RGB))
    hue = n.mix(G("PILLAR_HUE", 0.5), (1, 1, 1, 1), hue)
    k = n.math("MULTIPLY", n.math("ADD", 0.95, n.math("MULTIPLY", rnd, 0.1)), detail)
    # faint stains that run down the shaft
    st = n.noise(n.comb(n.math("MULTIPLY", dr[0], 2.4), n.math("MULTIPLY", dr[1], 2.4),
                        n.math("ADD", n.math("MULTIPLY", mk[1], 1.74), n.math("MULTIPLY", rnd, 20.0))), 1.0, detail=3, rough=0.6)
    streak = n.math("MULTIPLY", n.ramp(st.outputs["Fac"], (0.42, 0.72), interp="SMOOTH"), mk[0])
    k = n.math("MULTIPLY", k, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", streak, G("PILLAR_STREAK", 0.22))))
    # a little dirt in the grooves and in the pits
    ph = n.math("FRACT", n.math("MULTIPLY", us[0], NF / float(TURNS)))
    groove = n.math("MULTIPLY", n.math("SINE", n.math("MULTIPLY", ph, math.pi)), mk[0])
    k = n.math("MULTIPLY", k, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", groove, 0.1)))
    pit = n.ramp(hgt, (PW_H - 0.2, PW_H + 0.05), interp="SMOOTH")
    k = n.math("MULTIPLY", k, n.math("ADD", 0.72, n.math("MULTIPLY", pit, 0.28)))
    low = n.math("SUBTRACT", 1.0, n.ramp(ps[2], (FLOOR + 0.6, FLOOR + 7.0)))
    k = n.math("MULTIPLY", k, n.math("ADD", 0.7, n.math("MULTIPLY", 0.3, n.math("SUBTRACT", 1.0, low))))                    # darker toward the floor
    ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 1.0}, samples=12)
    k = n.math("MULTIPLY", k, n.math("POWER", ao.outputs["AO"], 1.3))
    col = n.mix(1.0, G("STONE_BASE", (0.128, 0.128, 0.118, 1)), n.comb(k, k, k), blend="MULTIPLY")
    col = n.mix(1.0, col, hue, blend="MULTIPLY")
    # quiet moss low on the stone and on the plinth ledges
    up = n.ramp(n.sep(n.coord().outputs["Normal"])[2], (0.45, 0.85))
    mn = n.noise(obj, 0.95, detail=6, rough=0.66)
    m1 = n.math("MULTIPLY", low, n.ramp(mn.outputs["Fac"], (0.46, 0.58)))
    m2 = n.math("MULTIPLY", n.math("MULTIPLY", up, n.math("SUBTRACT", 1.0, n.ramp(ps[2], (FLOOR + 6.6, FLOOR + 8.0)))), n.ramp(mn.outputs["Fac"], (0.3, 0.44)))
    moss = n.math("MINIMUM", n.math("MAXIMUM", m1, m2), 1.0)
    md = n.image(MOSS + "diff_2k.jpg", n.vmath("SCALE", obj, scale=1 / 1.6), proj="BOX", blend=0.3)
    col = n.mix(moss, col, n.mix(1.0, md.outputs[0], G("MOSS_TINT", (0.4, 0.5, 0.24, 1)), blend="MULTIPLY"))
    # matte, the way weathered stone is (at 0.6 the ridges drew glossy lines)
    rough = n.math("ADD", G("PILLAR_ROUGH", 0.86), n.math("MULTIPLY", n.math("SUBTRACT", rgh, PW_ROUGH), 1.2))
    b1 = n.node("ShaderNodeBump", ins={"Strength": G("PILLAR_RELIEF", 0.55), "Distance": G("PILLAR_RELIEF_DEPTH", 0.14),
                                      "Height": n.math("ADD", hgt, n.math("MULTIPLY", moss, 0.1))})
    pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": rough, "Normal": b1.outputs[0], "Specular IOR Level": 0.3})
    n.out(pb.outputs[0])
    return m


M_PIL = pillar_stone("Temple Pillar Stone")
SHARP = G("PILLAR_SHARP", 28)
for sx in (-1, 1):
    side = "L" if sx < 0 else "R"
    for name, (cx, cy, s), chips in (("Temple Pillar Front " + side, (sx * FRONT_X, FRONT_Y, 1.0), 9),
                                     ("Temple Pillar Arcade " + side, (sx * FRONT_X, ARCADE_Y, 1.0), 0),
                                     ("Temple Pillar Apse " + side, (sx * INNER_X, INNER_Y, INNER_S), 6)):
        v, f, dr, mk, wr = pillar(cx, cy, s, seed=SEED * 31 + sx + len(name), chips=chips)
        me = weld(mesh_from(name, v, f, uvs={"PillarDir": dr, "PillarShaft": mk, "PillarUV": wr}, smooth=True, sharp_deg=SHARP), SHARP)
        o = put(name, me, TC, [M_PIL], root)
        bevel(o, 0.035, 2, 40)
V, F, DR, MK, WR = [], [], [], [], []
for yb in BAYS:
    for sx in (-1, 1):
        v_, f_, dr_, mk_, wr_ = pillar(sx * (CA - 0.9), yb, INNER_S, profile=PLAIN)
        o_ = len(V)
        V += v_
        F += [tuple(i + o_ for i in ff) for ff in f_]
        DR += dr_
        MK += mk_
        WR += wr_
put("Temple Corridor Pillars", weld(mesh_from("Temple Corridor Pillars", V, F, uvs={"PillarDir": DR, "PillarShaft": MK, "PillarUV": WR},
                                              smooth=True, sharp_deg=40), 40), TC, [M_PIL], root)
fb = bpy.data.objects.get("Temple Fallen Blocks")
if fb:
    fb.data.materials.clear()
    fb.data.materials.append(M_PIL)

# ------------------------------------------------------------------ the long hall melts into haze
am = bpy.data.materials["Temple Air"]
for nd in am.node_tree.nodes:                     # thicker air beyond the small arch (set in v10_temple_light.py as 1 + ramp * 1.6)
    if nd.bl_idname == "ShaderNodeMath" and nd.operation == "MULTIPLY" and not nd.inputs[1].is_linked and abs(nd.inputs[1].default_value - 1.6) < 1e-4:
        nd.inputs[1].default_value = G("AIR_CORRIDOR", 3.2)
        nd.label = "v12 corridor air"
    elif nd.label == "v12 corridor air":
        nd.inputs[1].default_value = G("AIR_CORRIDOR", 3.2)
for nm in ("Temple Back Glow", "Temple Back Floor", "Temple Corridor Glow"):
    o = bpy.data.objects.get(nm)
    if o:
        o.location.y = 252.0                      # beyond the air's box (it ends at 236): no bright dot at the light itself
        o.rotation_euler = (Vector((0.0, 60.0, 9.0)) - Vector(o.location)).to_track_quat("-Z", "Y").to_euler()
result = {"pillars": "ok", "points_round": NA}
