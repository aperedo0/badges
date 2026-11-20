"""Version 12: the temple in the dark (owner, 2026-11-20, about an arch in the dark start: "when it's dark, that
texture unfortunately looks a little, it looks a little cheap. I want it to look better. I'm not sure how").
Run inside chest_reveal_v12_full.blend after v12_story.py; safe to run again; nothing is deleted.

Why it looked cheap: each arch was one smooth band with soft blotches painted on, lit flat from the front by a
dim blue fill, against a pure black hole. No joints, no carved edges, no direction in the light, no depth behind.
What this does:
- Arches built of stones: every arch gets real joints between its stones (cut into the surface as relief and
  darkened with old dirt), each stone a slightly different tone, a raised roll along its inner edge, a hood
  along its outer edge and a keystone at the crown. The back wall and the long hall's walls become coursed
  masonry with thin irregular joints. The stone's relief comes from a real height map (cracks and pits), not
  from its colour.
- Moonlight with direction: one cool light from high on the left that rakes across the arch faces, so the
  joints and carved edges catch light and throw small shadows, and the pillars' left sides are lit. The flat
  blue fill from the front is turned far down while it is dark.
- Depth: two faint shafts of moonlight fall into the long hall behind the small arch, lighting its floor and
  its air, so the arches stand as dark shapes against a faint blue haze and no longer against black.
All of it fades as the gold light comes up (`gold` on Temple Story), so the ending keeps its look."""
import bpy, bmesh, math
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
BACK = bpy.data.collections["Temple Back Receivers"]
story = bpy.data.objects["Temple Story"]
ROCK = RES + "polyhaven_rock_surface/rock_surface_"
ROCKF = RES + "polyhaven_rock_face_04/rock_face_04_"
ZN = FLOOR + 28.95                                # springing height of the big arch over the front pillars
ZA = FLOOR + 0.88 * 28.95                         # of the arch behind the chest and of the long hall's ribs
NAVE = dict(r0=17.2 - 2.84, r1=17.2 - 2.84 + 2.6, y=58.0 - 2.84, zc=ZN, n=25)
APSE = dict(r0=15.3, r1=15.3 + 2.3, y=87.0 - 2.2, zc=ZA, n=25)
BAYS = (116.0, 145.0, 174.0, 203.0)
RIB = dict(r0=13.7, r1=13.7 + 1.7, zc=ZA, n=23)


def drv(idb, path, expr, index=-1, **vs):
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except Exception:
        pass
    fc = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    d = fc.driver
    d.type = "SCRIPTED"
    for nm, (tid, tpath) in vs.items():
        v = d.variables.new()
        v.name = nm
        v.type = "SINGLE_PROP"
        v.targets[0].id_type = tid.id_type
        v.targets[0].id = tid
        v.targets[0].data_path = tpath
    d.expression = expr


GOLD = (story, '["gold"]')


def finish(V, F):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = [tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return out


def join(parts):
    V, F = [], []
    for v, f in parts:
        o_ = len(V)
        V += v
        F += [tuple(i + o_ for i in ff) for ff in f]
    return V, F


def band(r0, r1, y0, y1, zc, th0=0.0, th1=math.pi, n=96):
    """A bar of rectangular section bent along an arc (in the plane across the hall)."""
    V, F = [], []
    for i in range(n + 1):
        th = th0 + (th1 - th0) * i / n
        c, s_ = math.cos(th), math.sin(th)
        for r, y in ((r0, y0), (r1, y0), (r1, y1), (r0, y1)):
            V.append((r * c, y, zc + r * s_))
    for i in range(n):
        for q in range(4):
            a, b = 4 * i + q, 4 * i + (q + 1) % 4
            F.append((a, b, b + 4, a + 4))
    F.append((0, 1, 2, 3))
    F.append((4 * n + 3, 4 * n + 2, 4 * n + 1, 4 * n))
    return finish(V, F)


# ------------------------------------------------------------------ carved edges and keystones
def trim(A, key=True):
    r0, r1, y, zc = A["r0"], A["r1"], A["y"], A["zc"]
    parts = [band(r0 - 0.12, r0 + 0.42, y - 0.32, y + 0.1, zc),            # a roll along the inner edge
             band(r1 - 0.36, r1 + 0.2, y - 0.24, y + 0.1, zc)]            # a hood along the outer edge
    if key:
        parts.append(band(r0 - 0.34, r1 + 0.46, y - 0.5, y + 0.15, zc, math.pi / 2 - 0.056, math.pi / 2 + 0.056, n=6))
    return join(parts)


def stone(name, zc, n_st, mid_r, dark=1.0, masonry=False):
    """Dressed stone built of blocks: joints as relief and old dirt, each block its own tone, relief from a height map."""
    m = mat(name)
    n = NT(m)
    obj = n.coord().outputs["Object"]
    ps = n.sep(obj)
    if masonry:                                   # courses on walls: along the wall and up
        bt = n.node("ShaderNodeTexBrick", ins={"Vector": n.comb(n.math("ADD", ps[0], ps[1]), ps[2], 0.0), "Color1": (0.82, 0.82, 0.82, 1),
                                              "Color2": (1.16, 1.16, 1.16, 1), "Mortar": (1, 1, 1, 1), "Scale": 1.0, "Mortar Size": 0.035,
                                              "Mortar Smooth": 0.35, "Bias": 0.0, "Brick Width": 4.6, "Row Height": 2.3})
        bt.offset = 0.5
        groove = bt.outputs["Fac"]
        tone = n.node("ShaderNodeRGBToBW", ins={0: bt.outputs["Color"]}).outputs[0]
        idx = n.math("FLOOR", n.math("DIVIDE", ps[2], 2.3))
    else:                                         # voussoirs round an arch
        dz = n.math("SUBTRACT", ps[2], zc)
        th = n.math("ARCTAN2", dz, ps[0])
        u = n.math("MULTIPLY", th, n_st / math.pi)
        fr = n.math("FRACT", u)
        idx = n.math("FLOOR", u)
        r = n.math("SQRT", n.math("ADD", n.math("MULTIPLY", ps[0], ps[0]), n.math("MULTIPLY", dz, dz)))
        dj = n.math("MULTIPLY", n.math("MINIMUM", fr, n.math("SUBTRACT", 1.0, fr)), n.math("MULTIPLY", r, math.pi / n_st))
        groove = n.math("SUBTRACT", 1.0, n.ramp(dj, (0.012, 0.07), interp="SMOOTH"))
        wn = n.node("ShaderNodeTexWhiteNoise", ins={"W": n.math("ADD", idx, 11.3)}, noise_dimensions="1D")
        tone = n.math("ADD", 0.84, n.math("MULTIPLY", wn.outputs["Value"], 0.32))
    shift = n.comb(n.math("MULTIPLY", idx, 0.37), n.math("MULTIPLY", idx, 0.61), 0.0)      # cracks do not run across joints
    d = n.image(ROCK + "diff_2k.jpg", n.vmath("ADD", n.vmath("SCALE", obj, scale=1 / 3.2), shift), proj="BOX", blend=0.3)
    hp = n.image(ROCKF + "disp_2k.png", n.vmath("ADD", n.vmath("SCALE", obj, scale=1 / 5.0), shift), color=False, proj="BOX", blend=0.3)
    h = n.ramp(hp.outputs[0], (0.5, 0.82), interp="SMOOTH")
    lum = n.node("ShaderNodeRGBToBW", ins={0: d.outputs[0]}).outputs[0]
    detail = n.math("POWER", n.math("DIVIDE", lum, 0.12), 1.1)
    big = n.noise(obj, 0.09, detail=3, rough=0.55)
    k = n.math("MULTIPLY", n.math("MULTIPLY", tone, detail), n.math("ADD", 0.9, n.math("MULTIPLY", big.outputs["Fac"], 0.2)))
    k = n.math("MULTIPLY", k, n.math("ADD", 0.5, n.math("MULTIPLY", n.ramp(h, (0.0, 0.5), interp="SMOOTH"), 0.5)))       # dirt in cracks
    k = n.math("MULTIPLY", k, n.math("SUBTRACT", 1.0, n.math("MULTIPLY", groove, 0.92)))                                   # dirt in joints
    ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 1.2}, samples=12)
    k = n.math("MULTIPLY", k, n.math("POWER", ao.outputs["AO"], 1.3))
    col = n.mix(1.0, G("STONE_BASE", (0.128, 0.128, 0.118, 1)), n.comb(n.math("MULTIPLY", k, dark), n.math("MULTIPLY", k, dark), n.math("MULTIPLY", k, dark)),
                blend="MULTIPLY")
    rough = n.math("ADD", n.math("SUBTRACT", G("STONE_ROUGH", 0.6), n.math("MULTIPLY", h, 0.1)), n.math("MULTIPLY", groove, 0.3))
    b1 = n.node("ShaderNodeBump", ins={"Strength": G("STONE_RELIEF", 0.2), "Distance": 0.05, "Height": h})      # low: raking light exaggerates relief
    b2 = n.node("ShaderNodeBump", ins={"Strength": 1.0, "Distance": G("JOINT_DEPTH", 0.035), "Height": n.math("SUBTRACT", 1.0, groove), "Normal": b1.outputs[0]})
    pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": rough, "Normal": b2.outputs[0], "Specular IOR Level": 0.5})
    n.out(pb.outputs[0])
    return m


M_NAVE = stone("Temple Arch Stone High", ZN, NAVE["n"], 15.6, dark=G("ARCH_DARK", 0.8))
M_APSE = stone("Temple Arch Stone", ZA, APSE["n"], 16.4, dark=G("ARCH_DARK", 0.8))
M_RIB = stone("Temple Arch Stone Ribs", ZA, RIB["n"], 14.5, dark=G("ARCH_DARK", 0.8))
M_WALL = stone("Temple Wall Masonry", 0.0, 1, 1.0, dark=G("WALL_DARK", 0.3), masonry=True)

for name, m in (("Temple Nave Arch", M_NAVE), ("Temple Apse Arch", M_APSE), ("Temple Corridor Ribs", M_RIB),
                ("Temple Walls", M_WALL), ("Temple Apse Wall", M_WALL), ("Temple Corridor End", M_WALL)):
    o = bpy.data.objects[name]
    o.data.materials.clear()
    o.data.materials.append(m)

V, F = trim(NAVE)
o = put("Temple Nave Arch Trim", mesh_from("Temple Nave Arch Trim", V, F, smooth=True, sharp_deg=30), TC, [M_NAVE], root)
bevel(o, 0.05, 2, 30)
V, F = trim(APSE)
o = put("Temple Apse Arch Trim", mesh_from("Temple Apse Arch Trim", V, F, smooth=True, sharp_deg=30), TC, [M_APSE], root)
bevel(o, 0.05, 2, 30)
V, F = join([band(RIB["r0"] - 0.1, RIB["r0"] + 0.36, yb - 1.3 - 0.26, yb - 1.3 + 0.1, RIB["zc"], n=64) for yb in BAYS])
o = put("Temple Corridor Rib Trim", mesh_from("Temple Corridor Rib Trim", V, F, smooth=True, sharp_deg=30), TC, [M_RIB], root)
NEW = ("Temple Nave Arch Trim", "Temple Apse Arch Trim", "Temple Corridor Rib Trim")
for nm in NEW:
    for c in (RECV, BACK):
        if nm not in c.objects:
            c.objects.link(bpy.data.objects[nm])
for cn in ("Temple Burst Receivers", "Temple Burst Blockers"):
    c = bpy.data.collections.get(cn)
    if c:
        for nm in NEW:
            if nm not in c.objects:
                c.objects.link(bpy.data.objects[nm])

# ------------------------------------------------------------------ moonlight
MOON = (0.60, 0.75, 1.0)
MB = coll("Temple Moon Blockers", TC)                # what throws shadows in the moonlight: pillars and arches, not walls or roof
for o in TC.all_objects:
    if o.type == "MESH" and (o.name.startswith(("Temple Pillar", "Temple Corridor Pillars", "Temple Fallen", "Temple Torch Iron")) or "Arch" in o.name
                             or o.name.startswith("Temple Corridor Rib")) and o.name not in MB.objects:
        MB.objects.link(o)


def light(name, loc, aim, color, recv, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, "SPOT"))
        TC.objects.link(o)
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.color = color
    for k, v in kw.items():
        setattr(o.data, k, v)
    o.light_linking.receiver_collection = recv
    o.light_linking.blocker_collection = MB
    return o


mk = light("Temple Moon Key", G("MOON_AT", (-46.0, 44.0, 80.0)), G("MOON_AIM", (2.0, 64.0, 22.0)), MOON, BACK,
           spot_size=math.radians(34), spot_blend=0.6, shadow_soft_size=1.2, use_shadow=True, volume_factor=G("MOON_VOL", 0.0))
drv(mk.data, "energy", "%.1f * (1.0 - 0.9 * gold)" % G("MOON_E", 420000.0), gold=GOLD)
MDIR = (Vector(G("MOON_AIM", (2.0, 64.0, 22.0))) - Vector(G("MOON_AT", (-46.0, 44.0, 80.0)))).normalized()
# Two faint shafts into the long hall behind the small arch. They slant the way the moonlight falls: straight
# down they read as pale poles standing in the hall.
for nm, x, y, deg, e in (("A", -3.0, 128.0, 7.0, 1.0), ("B", 5.0, 187.0, 6.0, 0.8)):
    tgt = Vector((x, y, FLOOR))
    so = light("Temple Moon Shaft " + nm, tuple(tgt - MDIR * 95.0), tuple(tgt), MOON, RECV,
               spot_size=math.radians(deg), spot_blend=1.0, shadow_soft_size=1.5, use_shadow=True, volume_factor=G("HALL_SHAFT_VOL", 7.0))
    drv(so.data, "energy", "%.1f * (1.0 - 0.75 * gold)" % (G("HALL_SHAFT_E", 220000.0) * e), gold=GOLD)
# the two shafts in the front hall slant the same way (they keep their pools on the floor where they were)
for nm, x, y, deg, e in (("L", -10.0, 36.0, 5.5, 1.0), ("R", 11.5, 47.0, 5.0, 0.8)):
    so = bpy.data.objects["Temple Shaft " + nm]
    tgt = Vector((x, y, FLOOR))
    so.location = tuple(tgt - MDIR * 100.0)
    so.rotation_euler = (tgt - Vector(so.location)).to_track_quat("-Z", "Y").to_euler()
    so.data.spot_size = math.radians(deg)
    so.data.spot_blend = 1.0
    so.light_linking.blocker_collection = MB
    drv(so.data, "energy", "%.1f * (%.2f + %.2f * gold)" % (135000.0 * e, G("SHAFT_DARK", 0.7), 1.0 - G("SHAFT_DARK", 0.7)), gold=GOLD)
# the flat blue fill from the front: far down while it is dark, as before once the gold light is up
drv(bpy.data.objects["Temple Cool Top"].data, "energy", "3000.0 * (%.2f + %.2f * gold)" % (G("TOP_DARK", 0.25), 1.0 - G("TOP_DARK", 0.25)), gold=GOLD)
# the moss tufts on the pillar bases: quieter (in the moonlight they turned bright yellow green)
mm_ = mat("Temple Moss")
nn = NT(mm_)
MOSS = RES + "polyhaven_concrete_moss/concrete_moss_"
md = nn.image(MOSS + "diff_2k.jpg", nn.vmath("SCALE", nn.uv("UVMap"), scale=1 / 1.1))
mn_ = nn.noise(nn.coord().outputs["Object"], 6.0, detail=3, rough=0.6)
mc = nn.mix(1.0, md.outputs[0], G("MOSS_TINT", (0.4, 0.5, 0.24, 1)), blend="MULTIPLY")
mk_ = nn.math("ADD", 0.6, nn.math("MULTIPLY", mn_.outputs["Fac"], 0.8))
mc = nn.mix(1.0, mc, nn.comb(mk_, mk_, mk_), blend="MULTIPLY")
mb = nn.node("ShaderNodeBump", ins={"Strength": 0.8, "Distance": 0.06, "Height": mn_.outputs["Fac"]})
mp = nn.node("ShaderNodeBsdfPrincipled", ins={"Base Color": mc, "Roughness": 0.95, "Normal": mb.outputs[0], "Specular IOR Level": 0.2})
nn.out(mp.outputs[0])
result = {"dark": "ok", "trim_tris": sum(len(p.vertices) - 2 for nm in NEW for p in bpy.data.objects[nm].data.polygons)}
