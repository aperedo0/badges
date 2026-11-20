"""Version 11: torches whose fire wakes the hall (owner, 2026-11-19: "we can put some torches ... on each hall ...
the fire can wake up the hall"; on the pillars and down the hall, none beside the platform).
Run inside chest_reveal_v11_torches.blend after the version 10 scripts (geo, mat, light, lens, motion); safe to
run again; nothing is deleted. Version 10 keeps the look without torches.

Second design, after the owner's picture (~/Downloads/Flaming Iron Torch on Stone Wall.png: "maybe we can do
even better on the fire ... you can make the flame bigger, change up the shape of the thing that holds the
flame"): the first torches were thin brackets with a candle sized flame.
- Six pairs: the two big pillars, the two small pillars under the arch, and the four bays of the long hall.
  Each is a forged iron sconce: an oval back plate with four bolts, a square arm, a socket with a collar and
  a goblet shaped cup with a thick rim, turned three quarters toward the camera so the arm and the cup read.
- The fire is a card that faces the camera, drawn by a shader: a body as wide as the cup that leans and
  splits into tongues (three layers of noise streaming upward), a pale yellow heart, orange then deep red at
  the edges. A bed of glowing coals sits inside the cup. A second card carries a few tiny embers that rise,
  drift sideways and die out.
- Each flame has its own light (a pool on its pillar, a halo in the hall's air). Each pair of the long hall
  also has a soft glow light for its bay, because a torch's own reach is short and the hall has to be seen.
- "Temple Torch Control" carries one number per pair, lit_0 (big pillars) to lit_5 (far end of the hall), 0 to
  1. Flame size and brightness, coals, embers and every torch light follow it, so lighting the hall pair after
  pair later is six keyed numbers. All are 1 for now (the ending).
- The far doorway no longer lights the hall in gold (that showed the hall before anything woke it): it is
  faint cold moonlight now. The warm edge lights on the big pillars and under the big arch follow lit_0, the
  pool on the small arch follows lit_1."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
TORCH = coll("Temple Torches", TC)
CAM = Vector((0.0, -16.0, 8.0))                 # where the resting camera stands, in the chest's frame
FIRE = (1.0, 0.50, 0.17)
TS = G("TORCH_SIZE", 1.0)
TURN = math.radians(G("TORCH_TURN", 35.0))      # 0 = seen exactly from the side, 90 = pointing at the camera
L = 1.3                                         # arm: from the plate to the socket
AX = L + 0.34                                   # the cup's axis, out from the pillar's surface
RIM = 2.1                                       # top of the cup above the plate's middle

ctrl = bpy.data.objects.get("Temple Torch Control")
if ctrl is None:
    ctrl = bpy.data.objects.new("Temple Torch Control", None)
    TORCH.objects.link(ctrl)
ctrl.parent = root
ctrl.matrix_parent_inverse.identity()
ctrl.location = (0.0, 40.0, 30.0)
for g in range(6):
    if f"lit_{g}" not in ctrl:
        ctrl[f"lit_{g}"] = 1.0
    ctrl.id_properties_ui(f"lit_{g}").update(min=0.0, max=1.5, soft_min=0.0, soft_max=1.0)

# pair number, pillar centre x and y, pillar scale, height of the plate's middle on the pillar
SPOTS = []
for sx in (-1, 1):
    SPOTS.append((0, sx * 17.2, 58.0, 1.0, 14.5))
    SPOTS.append((1, sx * 17.5, 87.0, 0.88, 14.5))
    for k, yb in enumerate((116.0, 145.0, 174.0, 203.0)):
        SPOTS.append((2 + k, sx * 14.4, yb, 0.88, 13.5))


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


def extrude(poly, t0, t1, mapf):
    n = len(poly)
    V = [mapf(a, b, t0) for a, b in poly] + [mapf(a, b, t1) for a, b in poly]
    F = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return finish(V, F)


def lathe(profile, mapf, n=24):
    V, F = [], []
    for r, h in profile:
        for i in range(n):
            t = 2 * math.pi * i / n
            V.append(mapf(r * math.cos(t), r * math.sin(t), h))
    for j in range(len(profile) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            F.append((a, b, b + n, a + n))
    F.append(tuple(reversed(range(n))))
    F.append(tuple(range((len(profile) - 1) * n, len(profile) * n)))
    return finish(V, F)


STADIUM = ([(0.5 * math.cos(t), 0.62 + 0.5 * math.sin(t)) for t in [math.pi * i / 10 for i in range(11)]] +
           [(0.5 * math.cos(t), -0.62 + 0.5 * math.sin(t)) for t in [math.pi + math.pi * i / 10 for i in range(11)]])
HEX = [(0.115 * math.cos(math.pi / 6 + math.pi * i / 3), 0.115 * math.sin(math.pi / 6 + math.pi * i / 3)) for i in range(6)]
CUP = [(0.30, -0.52), (0.34, -0.46), (0.34, 0.10), (0.47, 0.10), (0.47, 0.30), (0.37, 0.30),        # socket and collar
       (0.40, 0.36), (0.52, 0.62), (0.67, 1.0), (0.78, 1.4), (0.84, 1.8),                           # the goblet
       (0.93, 1.8), (0.96, 1.86), (0.96, 2.04), (0.93, RIM), (0.83, RIM), (0.79, 1.97)]             # rim band, lip, inner floor

iron, torches = [], []
for i, (g, cx, cy, s, h) in enumerate(SPOTS):
    S = s * TS
    C = Vector((cx, cy, FLOOR + h * s))
    to_cam = Vector((CAM.x - cx, CAM.y - cy, 0.0)).normalized()
    side = Vector((-to_cam.y, to_cam.x, 0.0))
    if side.x * cx > 0:                       # toward the middle of the hall
        side = -side
    d = (side * math.cos(TURN) + to_cam * math.sin(TURN)).normalized()
    sd = Vector((-d.y, d.x, 0.0))
    r_s = 1.99 * s

    def P(out, sdv, up, C=C, d=d, sd=sd, S=S, r_s=r_s):
        return tuple(C + d * (r_s + out * S) + sd * (sdv * S) + Vector((0, 0, up * S)))

    iron.append(extrude(STADIUM, -0.12, 0.1, lambda a, b, t: P(t, a, b)))
    for bx in (-0.25, 0.25):
        for bz in (-0.74, 0.74):
            iron.append(extrude([(bx + hx, bz + hz) for hx, hz in HEX], 0.1, 0.2, lambda a, b, t: P(t, a, b)))
    iron.append(extrude([(-0.16, -0.22), (0.16, -0.22), (0.16, 0.1), (-0.16, 0.1)], 0.05, L + 0.12, lambda a, b, t: P(t, a, b)))
    iron.append(lathe(CUP, lambda rx, ry, up: P(AX + rx, ry, up)))
    torches.append((i, g, s, S, Vector(P(AX, 0, 0)), d))

# ------------------------------------------------------------------ hammered, rusted iron
m_iron = mat("Temple Torch Iron")
n = NT(m_iron)
tc = n.coord()
p = tc.outputs["Object"]
dents = n.node("ShaderNodeTexVoronoi", ins={"Vector": p, "Scale": 5.5}, feature="SMOOTH_F1")
fine = n.noise(p, 26.0, detail=3, rough=0.6)
rustn = n.noise(p, 1.4, detail=5, rough=0.65)
rust = n.ramp(rustn.outputs["Fac"], (0.42, 0.68))
col = n.mix(rust, (0.026, 0.024, 0.022, 1), (0.10, 0.042, 0.018, 1))
col = n.mix(n.math("MULTIPLY", n.ramp(fine.outputs["Fac"], (0.55, 0.8)), 0.4), col, (0.17, 0.07, 0.028, 1))
hgt = n.math("ADD", n.math("MULTIPLY", dents.outputs["Distance"], 0.6), n.math("MULTIPLY", fine.outputs["Fac"], 0.12))
bump = n.node("ShaderNodeBump", ins={"Strength": 0.55, "Distance": 0.06, "Height": hgt})
rough = n.math("ADD", 0.36, n.math("MULTIPLY", rust, 0.34))
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": col, "Roughness": rough, "Metallic": n.math("SUBTRACT", 0.75, n.math("MULTIPLY", rust, 0.5)),
                                            "Normal": bump.outputs[0]})
n.out(pb.outputs[0])
V, F = join(iron)
o = put("Temple Torch Iron", mesh_from("Temple Torch Iron", V, F, smooth=True, sharp_deg=38), TORCH, [m_iron], root)
if o.name not in RECV.objects:
    RECV.objects.link(o)
old = bpy.data.objects.get("Temple Torch Heads")          # from the first design: kept, not rendered
if old:
    old.hide_render = True
    old.hide_viewport = True


def drive(idb, path, expr, index=-1, g=0):
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except Exception:
        pass
    fcu = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    dr = fcu.driver
    dr.type = "SCRIPTED"
    var = dr.variables.new()
    var.name = "lit"
    var.type = "SINGLE_PROP"
    var.targets[0].id = ctrl
    var.targets[0].data_path = f'["lit_{g}"]'
    dr.expression = expr


def time_node(n, name):
    tv = n.node("ShaderNodeValue", label=name)
    fc = tv.outputs[0].driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "frame / 30"
    return tv.outputs[0]


def sstep(n, x, lo, hi):
    return n.ramp(x, (lo, hi), interp="SMOOTH")


# ------------------------------------------------------------------ coals in the cup
cm = mat("Temple Coals")
n = NT(cm)
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "coal time")
pc = n.coord().outputs["Object"]
cell = n.node("ShaderNodeTexVoronoi", ins={"Vector": pc, "Scale": 4.5}, feature="DISTANCE_TO_EDGE")
glow = n.math("SUBTRACT", 1.0, sstep(n, cell.outputs["Distance"], 0.0, 0.22))
pulse = n.noise(n.comb(n.math("MULTIPLY", t, 0.9), n.math("MULTIPLY", oi.outputs["Random"], 9.0), 0.0), 1.0, detail=1.0)
k = n.math("MULTIPLY", n.math("MULTIPLY", n.math("ADD", 0.25, glow), n.math("ADD", 0.7, n.math("MULTIPLY", pulse.outputs["Fac"], 0.6))),
           oi.outputs["Alpha"])
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": (0.012, 0.008, 0.006, 1), "Roughness": 0.9})
pb.inputs["Emission Color"].default_value = (1.0, 0.36, 0.05, 1)
n.set(pb.inputs["Emission Strength"], n.math("MULTIPLY", k, G("COAL_GLOW", 9.0)))
n.out(pb.outputs[0])

# ------------------------------------------------------------------ the flame
FW, FH = 3.8, 4.4
fm = mat("Temple Flame")
fm.surface_render_method = "BLENDED"
fm.use_backface_culling = False
n = NT(fm)
tc = n.coord()
uv = n.sep(tc.outputs["UV"])
u, v = uv[0], uv[1]
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "flame time")
seed = n.math("MULTIPLY", oi.outputs["Random"], 37.0)
x = n.math("MULTIPLY", n.math("SUBTRACT", u, 0.5), 2.0)
S1, S2, S3 = G("FLAME_SPEEDS", (0.9, 1.5, 1.9))


def flow(n, fx, fy, speed, zk, zt, src, detail=2.0, rough=0.5):
    """Noise that streams upward: fx across, fy along the height."""
    return n.noise(n.comb(n.math("MULTIPLY", src, fx), n.math("SUBTRACT", n.math("MULTIPLY", v, fy), n.math("MULTIPLY", t, speed)),
                          n.math("ADD", n.math("MULTIPLY", seed, zk), n.math("MULTIPLY", t, zt))), 1.0, detail=detail, rough=rough).outputs["Fac"]


w1 = flow(n, 1.1, 1.6, S1, 1.0, 0.21, x, detail=1.0)             # the whole fire leaning
w2 = flow(n, 2.6, 3.2, S2, 1.37, 0.45, x)                        # licks
lean = n.math("ADD", 0.06, n.math("POWER", v, 1.2))
xs = n.math("ADD", x, n.math("ADD", n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", w1, 0.5), G("FLAME_SWAY", 0.9)), lean),
                             n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", w2, 0.5), 0.6), lean)))
# a bulb: a little narrower than the cup at the very bottom, fullest just above the rim, closing toward the tip
wv = n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", 1.0, n.math("POWER", v, 1.5)), G("FLAME_WIDTH", 0.52)),
            n.math("MINIMUM", n.math("ADD", 0.7, n.math("MULTIPLY", v, 2.2)), 1.0))
across = n.math("SUBTRACT", 1.0, n.math("POWER", n.math("DIVIDE", n.math("ABSOLUTE", xs), n.math("MAXIMUM", wv, 0.001)), 1.6))
tn = flow(n, 4.2, 1.1, S3, 2.1, 0.3, xs)                         # long upright streaks: they split the top into tongues
tn = n.math("MINIMUM", n.math("MAXIMUM", n.math("ADD", n.math("MULTIPLY", n.math("SUBTRACT", tn, 0.5), G("FLAME_SPLIT", 2.6)), 0.5), 0.0), 1.0)
tn2 = flow(n, 7.0, 3.0, S3 * 1.5, 3.3, 0.5, xs)                  # fine veins
cut = n.math("ADD", 0.02, n.math("MULTIPLY", n.math("POWER", v, 0.8), G("FLAME_TONGUES", 1.5)))
eaten = n.math("SUBTRACT", n.math("SUBTRACT", across, n.math("MULTIPLY", tn, cut)),
               n.math("MULTIPLY", n.math("MULTIPLY", n.math("SUBTRACT", tn2, 0.5), 0.25), n.math("ADD", 0.3, v)))
alpha = n.math("MULTIPLY", sstep(n, eaten, 0.0, 0.07), n.math("MINIMUM", oi.outputs["Alpha"], 1.0))
# heat: deep orange at the edges and in the tongues, yellow only low in the middle
heat = n.math("MULTIPLY", n.math("MULTIPLY", n.math("POWER", n.math("MAXIMUM", n.math("MINIMUM", eaten, 1.0), 0.0), 1.3),
                                 n.math("SUBTRACT", 1.0, n.math("MULTIPLY", v, 0.55))),
              n.math("ADD", 0.7, n.math("MULTIPLY", tn2, 0.5)))
core = n.math("MULTIPLY", sstep(n, across, 0.55, 1.0), n.math("POWER", n.math("MAXIMUM", n.math("SUBTRACT", 1.0, v), 0.0), 3.0))
heat = n.math("MINIMUM", n.math("ADD", heat, n.math("MULTIPLY", core, 0.35)), 1.0)
cr = n.node("ShaderNodeValToRGB", ins={0: heat})
els = cr.color_ramp.elements
# kept toward yellow: under this scene's view transform a bright pure red orange turns salmon pink
els[0].position, els[0].color = 0.0, (0.7, 0.16, 0.0, 1)
els[1].position, els[1].color = 1.0, (1.0, 0.9, 0.5, 1)
for pos, c_ in ((0.28, (1.0, 0.36, 0.02, 1)), (0.55, (1.0, 0.52, 0.05, 1)), (0.8, (1.0, 0.72, 0.16, 1))):
    e_ = els.new(pos)
    e_.color = c_
fl = n.noise(n.comb(n.math("MULTIPLY", t, 4.0), seed, 0.0), 1.0, detail=1.0)
bright = n.math("MULTIPLY", n.math("ADD", G("FLAME_LOW", 0.9), n.math("MULTIPLY", n.math("POWER", heat, 1.5), G("FLAME_HOT", 4.2))),
                n.math("ADD", 0.85, n.math("MULTIPLY", fl.outputs["Fac"], 0.3)))
bright = n.math("MULTIPLY", bright, oi.outputs["Alpha"])
fcol = n.mix(1.0, cr.outputs["Color"], oi.outputs["Color"], blend="MULTIPLY")        # the back layer of each fire is tinted deeper
em = n.node("ShaderNodeEmission", ins={"Color": fcol, "Strength": bright})
tp = n.node("ShaderNodeBsdfTransparent")
mx = n.node("ShaderNodeMixShader", ins={0: alpha, 1: tp.outputs[0], 2: em.outputs[0]})
n.out(mx.outputs[0])

# ------------------------------------------------------------------ embers
EW, EH = 3.6, 9.5
emb = mat("Temple Embers")
emb.surface_render_method = "BLENDED"
emb.use_backface_culling = False
n = NT(emb)
uv = n.sep(n.coord().outputs["UV"])
u, v = uv[0], uv[1]
oi = n.node("ShaderNodeObjectInfo")
t = time_node(n, "ember time")
seed = n.math("MULTIPLY", oi.outputs["Random"], 53.0)
x = n.math("MULTIPLY", n.math("SUBTRACT", u, 0.5), 2.0)
X = n.math("MULTIPLY", x, EW / 2)
Y = n.math("MULTIPLY", v, EH)
sway = n.math("ADD", n.math("MULTIPLY", n.math("SINE", n.math("ADD", n.math("MULTIPLY", Y, 0.9), n.math("ADD", seed, n.math("MULTIPLY", t, 1.1)))), 0.24),
              n.math("MULTIPLY", n.math("SINE", n.math("ADD", n.math("MULTIPLY", Y, 2.3), n.math("ADD", n.math("MULTIPLY", seed, 2.0), n.math("MULTIPLY", t, 0.7)))), 0.1))
K = G("EMBER_CELLS", 1.1)
pe = n.comb(n.math("MULTIPLY", n.math("ADD", X, n.math("MULTIPLY", sway, v)), K),
            n.math("MULTIPLY", n.math("SUBTRACT", Y, n.math("MULTIPLY", t, G("EMBER_RISE", 2.2))), K),
            n.math("ADD", seed, n.math("MULTIPLY", t, 0.12)))
vor = n.node("ShaderNodeTexVoronoi", ins={"Vector": pe, "Scale": 1.0}, feature="F1")
R = G("EMBER_RADIUS", 0.05)
dot = n.math("SUBTRACT", 1.0, sstep(n, vor.outputs["Distance"], R * 0.4, R))
cs = n.node("ShaderNodeSeparateColor", ins={0: vor.outputs["Color"]})
keep = n.math("GREATER_THAN", cs.outputs[0], G("EMBER_FEW", 0.62))
fade = n.math("MULTIPLY", n.math("MULTIPLY", sstep(n, v, 0.1, 0.22), n.math("POWER", n.math("MAXIMUM", n.math("SUBTRACT", 1.0, v), 0.0), 1.3)),
              n.math("SUBTRACT", 1.0, n.math("MULTIPLY", x, x)))
b = n.math("MULTIPLY", n.math("MULTIPLY", dot, keep), n.math("MULTIPLY", fade, n.math("MINIMUM", oi.outputs["Alpha"], 1.0)))
ecol = n.mix(cs.outputs[1], (1.0, 0.36, 0.03, 1), (1.0, 0.6, 0.12, 1))
em = n.node("ShaderNodeEmission", ins={"Color": ecol, "Strength": n.math("MULTIPLY", b, G("EMBER_GLOW", 7.0))})
tp = n.node("ShaderNodeBsdfTransparent")
mx = n.node("ShaderNodeMixShader", ins={0: n.math("MINIMUM", b, 1.0), 1: tp.outputs[0], 2: em.outputs[0]})
n.out(mx.outputs[0])


def lamp(name, kind, loc, energy, color, g, recv, vol, flick, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
        TORCH.objects.link(o)
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    o.data.color = color
    o.data.volume_factor = vol
    for k_, val in kw.items():
        setattr(o.data, k_, val)
    o.light_linking.receiver_collection = recv
    ph = (sum(ord(ch) * (k_ + 1) for k_, ch in enumerate(name)) % 628) / 100.0      # each light its own flicker, the same every run
    if flick:
        expr = "%.1f * lit * (0.88 + 0.07 * sin(frame * 0.83 + %.2f) + 0.05 * sin(frame * 1.91 + %.2f))" % (energy, ph, ph * 2)
    else:
        expr = "%.1f * lit" % energy
    drive(o.data, "energy", expr, g=g)
    return o


def card(name, w, h, base, yaw, s, material, g, grow, tint=(1.0, 1.0, 1.0)):
    me = mesh_from(name, [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [(0, 1, 2, 3)],
                   uvs={"UVMap": [(0, 0), (1, 0), (1, 1), (0, 1)]})
    o = put(name, me, TORCH, [material], root)
    o.matrix_basis = Matrix.Translation(base) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Diagonal((s, s, s, 1.0))
    o.visible_shadow = False
    o.color = (tint[0], tint[1], tint[2], 1)
    for idx in (0, 2):
        try:
            o.driver_remove("scale", idx)
        except Exception:
            pass
    if grow:
        drive(o, "scale", "%.3f * lit" % s, index=2, g=g)
        drive(o, "scale", "%.3f * (0.35 + 0.65 * lit)" % s, index=0, g=g)
    drive(o, "color", "lit", index=3, g=g)
    return o


for i, g, s, S, axis, d in torches:
    top = axis + Vector((0, 0, 1.9 * S))
    to = CAM - top
    yaw = math.atan2(to.x, -to.y)
    fwd = Vector((to.x, to.y, 0)).normalized()
    # two layers with their own shapes: a larger, deeper orange fire behind a brighter one
    card(f"Temple Flame Back {i:02d}", FW * 1.12, FH * 1.12, top - fwd * 0.12, yaw, S, fm, g, True, tint=(0.62, 0.54, 0.4))
    card(f"Temple Flame {i:02d}", FW, FH, top, yaw, S, fm, g, True)
    card(f"Temple Embers {i:02d}", EW, EH, top + fwd * 0.05, yaw, S, emb, g, False)
    n_c = 20
    Vc = [(0.8 * S * math.cos(2 * math.pi * k_ / n_c), 0.8 * S * math.sin(2 * math.pi * k_ / n_c), 0.0) for k_ in range(n_c)]
    co = put(f"Temple Coals {i:02d}", mesh_from(f"Temple Coals {i:02d}", Vc, [tuple(range(n_c))]), TORCH, [cm], root)
    co.matrix_basis = Matrix.Translation(axis + Vector((0, 0, 1.99 * S)))
    co.visible_shadow = False
    co.color = (1, 1, 1, 1)
    drive(co, "color", "lit", index=3, g=g)
    lamp(f"Temple Torch Light {i:02d}", "POINT", top + Vector((0, 0, 1.5 * S)) + fwd * 0.35,
         G("TORCH_E", (1300.0, 950.0, 700.0))[min(g, 2)], FIRE, g, RECV, G("TORCH_VOL", 2.0), True,
         shadow_soft_size=0.8, use_shadow=g == 0)

# a soft glow for each bay of the long hall (a torch's own reach is short)
for k_, yb in enumerate((116.0, 145.0, 174.0, 203.0)):
    lamp(f"Temple Bay Glow {k_}", "POINT", (0.0, yb - 5.0, 15.0), G("BAY_E", 8500.0), FIRE, 2 + k_, RECV, G("BAY_VOL", 0.5), True,
         shadow_soft_size=4.0, use_shadow=False)

# the lights that already stood for firelight follow their pair
for nm, g in (("Temple Rim L", 0), ("Temple Rim R", 0), ("Temple Arch Warm", 0), ("Temple Arch Face", 1)):
    o = bpy.data.objects[nm]
    try:
        o.data.driver_remove("energy")
    except Exception:
        pass
    base_e = o.data.get("v11_base", o.data.energy)
    o.data["v11_base"] = base_e
    drive(o.data, "energy", "%.1f * lit" % base_e, g=g)

# the far doorway: faint cold moonlight instead of gold
MOON = (0.5, 0.66, 1.0)
for nm, e, vol in (("Temple Back Glow", G("MOON_E", 130000.0), 0.5), ("Temple Corridor Glow", 0.0, 0.0), ("Temple Back Floor", G("MOON_FLOOR_E", 45000.0), 0.0)):
    o = bpy.data.objects[nm]
    o.data.color = MOON
    o.data.energy = e
    o.data.volume_factor = vol
fg = bpy.data.materials["Temple Far Glow"]
emn = next(nd for nd in fg.node_tree.nodes if nd.bl_idname == "ShaderNodeEmission")
emn.inputs["Color"].default_value = (0.45, 0.62, 1.0, 1)
emn.inputs["Strength"].default_value = G("FAR_GLOW", 1.6)
for nm in ("Temple Cool L", "Temple Cool R"):
    bpy.data.objects[nm].data.energy = G("COOL_E", 8000.0)
result = {"torches": len(SPOTS)}
