"""Version 12: the two shafts of night light through the roof, and dust that falls in them when the chest lands
(owner, 2026-11-20: "the one before had like two light streaks, almost as if ... parts of the roof were missing
... The night light was shining through, and I like that. And then in those same areas ... dust came and fell
... I feel like the dust that you had before that came down looked a little low quality, so I want it to be
higher quality dust ... almost as if like the chest falling kind of made some of the dust from above come
down. It's like something shifted ... add that back in").
Run inside chest_reveal_v12_full.blend after v12_story.py and v12_dark.py; safe to run again; nothing is deleted.

- The two shafts stand straight again where they were (v12_story.py places them; v12_dark.py had slanted them
  out of the hall's air, which made them vanish).
- The old falling dust was six flat cards with scrolling streaks (kept in the file, switched off). The new dust
  falls only in the two shafts and is made of two real things, both lit by nothing but the shaft's own light:
  * grit: five thin trickles per shaft, each a few hundred very fine grains pouring from one point just after the
    impact, heavy at first and thinning out, falling under gravity with air drag. Each grain is a real sphere
    far smaller than a pixel, pale and lit from every side. In a render each is drawn as a short streak the
    length it would blur to (`streak` 1, set by v12_render.py, which also steps `dustfall` by hand so the
    renderer's own motion blur does not smear the grains away in some frames and not in others).
  * a dust cloud: a thin plume of fine dust that comes down slower behind the grit, spreads, and thins away.
  Everything follows `dustfall` on Temple Story (seconds since the first impact at frame 17) and is over by 2.5
  seconds, before the arrival clip ends."""
import bpy, math, random
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
SC = coll("Temple Story", TC)
RECV = bpy.data.collections["Temple Light Receivers"]
story = bpy.data.objects["Temple Story"]
SHAFTS = (("L", -10.0, 36.0), ("R", 11.5, 47.0))
ZC = G("DUST_TOP", 56.0)                          # where it lets go: the vault above the picture's top
GRAV = 79.0                                       # gravity in this scene's units (the chest is 0.7 m wide)
END_T = 2.5                                       # all dust from above is gone by then


def drive(sock, expr, **vs):
    try:
        sock.driver_remove("default_value")
    except Exception:
        pass
    d = sock.driver_add("default_value").driver
    d.type = "SCRIPTED"
    for nm, path in vs.items():
        v = d.variables.new()
        v.name = nm
        v.type = "SINGLE_PROP"
        v.targets[0].id = story
        v.targets[0].data_path = path
    d.expression = expr


story.update_tag()                                # so numbers added to the story in this session can be read by new drivers
bpy.context.view_layer.update()
for i in range(6):                                # the old cards
    o = bpy.data.objects.get(f"Temple Dust Fall {i}")
    if o:
        o.hide_render = True
        o.hide_viewport = True
for nm, x, y in SHAFTS:                           # nothing but the hall itself stands in the shafts' way
    pass                                          # (what shapes the shafts is set in v12_hall.py)

# ------------------------------------------------------------------ the dust cloud
cm = mat("Temple Dust Cloud")
n = NT(cm)
p = n.coord().outputs["Object"]
ps = n.sep(p)
tv = n.node("ShaderNodeValue", label="fall time")
drive(tv.outputs[0], "t", t='["dustfall"]')
oi = n.node("ShaderNodeObjectInfo")
t = n.math("MAXIMUM", n.math("SUBTRACT", tv.outputs[0], 0.12), 0.0)
fallen = n.math("MULTIPLY", n.math("SUBTRACT", 1.0, n.math("EXPONENT", n.math("MULTIPLY", t, -1.0 / 1.2))), G("CLOUD_FALL", 34.0))
zh = n.math("SUBTRACT", ZC, fallen)                                  # the plume's lower end
length = n.math("ADD", 6.0, n.math("MULTIPLY", t, 8.0))
lo = n.node("ShaderNodeMapRange", ins={0: n.math("SUBTRACT", ps[2], zh), 1: -1.5, 2: 1.5, 3: 0.0, 4: 1.0}, interpolation_type="SMOOTHSTEP")
hi = n.node("ShaderNodeMapRange", ins={0: n.math("SUBTRACT", n.math("SUBTRACT", ps[2], zh), length), 1: -4.0, 2: 0.0, 3: 1.0, 4: 0.0},
            interpolation_type="SMOOTHSTEP")
band = n.math("MULTIPLY", lo.outputs[0], hi.outputs[0])
sig = n.math("ADD", 0.7, n.math("MULTIPLY", t, 0.5))                  # it spreads as it comes down
rr = n.math("DIVIDE", n.math("SQRT", n.math("ADD", n.math("MULTIPLY", ps[0], ps[0]), n.math("MULTIPLY", ps[1], ps[1]))), sig)
radial = n.math("EXPONENT", n.math("MULTIPLY", n.math("MULTIPLY", rr, rr), -1.0))
# fine veils that hang long and thin, and travel down with the dust
adv = n.comb(n.math("MULTIPLY", ps[0], 1.1), n.math("ADD", n.math("MULTIPLY", ps[1], 1.1), n.math("MULTIPLY", oi.outputs["Random"], 9.0)),
             n.math("MULTIPLY", n.math("ADD", ps[2], n.math("MULTIPLY", fallen, 0.8)), 0.09))
nz = n.node("ShaderNodeTexNoise", ins={"Vector": adv, "W": n.math("MULTIPLY", t, 0.35), "Scale": 1.0, "Detail": 4.0, "Roughness": 0.6,
                                      "Distortion": 0.5}, noise_dimensions="4D")
wisp = n.ramp(nz.outputs["Fac"], (0.3, 0.75), interp="SMOOTH")
amp = n.math("MULTIPLY", n.ramp(t, (0.0, 0.25), interp="SMOOTH"), n.math("SUBTRACT", 1.0, n.ramp(t, (1.3, END_T - 0.15), interp="SMOOTH")))
dens = n.math("MULTIPLY", n.math("MULTIPLY", n.math("MULTIPLY", radial, band), n.math("MULTIPLY", wisp, amp)), G("DUST_CLOUD", 0.007))
vol = n.node("ShaderNodeVolumePrincipled", ins={"Color": G("DUST_COLOR", (0.62, 0.58, 0.52, 1)), "Density": dens, "Anisotropy": 0.35})
om = n.node("ShaderNodeOutputMaterial")
n.link(vol.outputs[0], om.inputs["Volume"])

# ------------------------------------------------------------------ the grit
gm = mat("Temple Dust Grit")
n = NT(gm)
# Pale, and lit from every side: a grain in a beam of light is bright whichever way you look at it. (As a plain
# solid lit only on top, the camera saw the grains' dark sides and they read as brown blocks.)
# The colour of the stone it fell from (owner, 2026-11-20: "maybe don't make the sand so white ... It'd probably
# be the color of the stone"); it was near white.
SAND = G("SAND_COLOR", (0.56, 0.54, 0.50, 1))
df = n.node("ShaderNodeBsdfDiffuse", ins={"Color": SAND})
tr = n.node("ShaderNodeBsdfTranslucent", ins={"Color": SAND})
mx = n.node("ShaderNodeMixShader", ins={0: 0.5, 1: df.outputs[0], 2: tr.outputs[0]})
# Fine dust in a beam throws most of the light onward, toward whoever looks into the beam: it shines far brighter
# than a solid surface in the same light (the air in the shaft is boosted the same way). This stands in for that.
# The grains only ever exist inside the two shafts, in the dark part of the story.
em = n.node("ShaderNodeEmission", ins={"Color": (0.56, 0.55, 0.53, 1), "Strength": G("GRIT_SHINE", 0.13)})
ad = n.node("ShaderNodeAddShader", ins={0: mx.outputs[0], 1: em.outputs[0]})
n.out(ad.outputs[0])

ng = bpy.data.node_groups.get("Temple Dust Grit")
if ng is None:
    ng = bpy.data.node_groups.new("Temple Dust Grit", "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
ng.nodes.clear()
N, Lk = ng.nodes, ng.links


def M(op, a, b=None):
    nd = N.new("ShaderNodeMath")
    nd.operation = op
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, bpy.types.NodeSocket):
            Lk.new(v, nd.inputs[i])
        else:
            nd.inputs[i].default_value = v
    return nd.outputs[0]


def attr(name, kind="FLOAT"):
    nd = N.new("GeometryNodeInputNamedAttribute")
    nd.data_type = kind
    nd.inputs["Name"].default_value = name
    return nd.outputs["Attribute"]


gin, gout = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
tn = N.new("ShaderNodeValue"); tn.name = tn.label = "fall time"
sn = N.new("ShaderNodeValue"); sn.name = sn.label = "streak"
T = tn.outputs[0]
t0, vt, size = attr("t0"), attr("vt"), attr("size")
drift = attr("drift", "FLOAT_VECTOR")
tau = M("MAXIMUM", M("SUBTRACT", T, t0), 0.0)
k = M("DIVIDE", vt, GRAV)                                            # how long it takes a grain to reach its top speed
ex = M("EXPONENT", M("MULTIPLY", M("DIVIDE", tau, k), -1.0))
fall = M("MULTIPLY", vt, M("SUBTRACT", tau, M("MULTIPLY", k, M("SUBTRACT", 1.0, ex))))
speed = M("MULTIPLY", vt, M("SUBTRACT", 1.0, ex))
sx = N.new("ShaderNodeSeparateXYZ"); Lk.new(drift, sx.inputs[0])
off = N.new("ShaderNodeCombineXYZ")
Lk.new(M("MULTIPLY", sx.outputs[0], tau), off.inputs[0])
Lk.new(M("MULTIPLY", sx.outputs[1], tau), off.inputs[1])
Lk.new(M("MULTIPLY", fall, -1.0), off.inputs[2])
sp = N.new("GeometryNodeSetPosition")
Lk.new(gin.outputs[0], sp.inputs["Geometry"]); Lk.new(off.outputs[0], sp.inputs["Offset"])
# shown only while falling: after it lets go, above the floor, and before the end
alive = M("MULTIPLY", M("GREATER_THAN", tau, 0.0), M("GREATER_THAN", (ZC - FLOOR) - 0.05, fall))
# No fading in the air (owner, 2026-11-20: "it comes down and then it opacities out ... I just don't like that
# look"): every grain falls until it reaches the floor. This only clears anything left at the very end.
fade = M("SUBTRACT", 1.0, M("MINIMUM", 1.0, M("MAXIMUM", M("DIVIDE", M("SUBTRACT", T, END_T - 0.08), 0.06), 0.0)))
r = M("MULTIPLY", M("MULTIPLY", size, alive), fade)
half = M("MULTIPLY", M("MULTIPLY", speed, 1.0 / 120.0), sn.outputs[0])     # half the streak: speed times half a shutter
sc = N.new("ShaderNodeCombineXYZ")
Lk.new(r, sc.inputs[0]); Lk.new(r, sc.inputs[1])
Lk.new(M("MULTIPLY", M("ADD", size, half), M("MULTIPLY", alive, fade)), sc.inputs[2])
ico = N.new("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 1.0; ico.inputs["Subdivisions"].default_value = 1
iop = N.new("GeometryNodeInstanceOnPoints")
Lk.new(sp.outputs[0], iop.inputs["Points"]); Lk.new(ico.outputs[0], iop.inputs["Instance"]); Lk.new(sc.outputs[0], iop.inputs["Scale"])
rl = N.new("GeometryNodeRealizeInstances"); Lk.new(iop.outputs[0], rl.inputs[0])
sm = N.new("GeometryNodeSetMaterial"); Lk.new(rl.outputs[0], sm.inputs["Geometry"]); sm.inputs["Material"].default_value = gm
Lk.new(sm.outputs[0], gout.inputs[0])
drive(T, "t", t='["dustfall"]')
drive(sn.outputs[0], "s", s='["streak"]')

rng = random.Random(G("DUST_SEED", 5))
for nm, x, y in SHAFTS:
    # the cloud
    R, zt = 3.4, ZC + 2.0
    V = [(-R, -R, FLOOR), (R, -R, FLOOR), (R, R, FLOOR), (-R, R, FLOOR), (-R, -R, zt), (R, -R, zt), (R, R, zt), (-R, R, zt)]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    co = put("Temple Dust Cloud " + nm, mesh_from("Temple Dust Cloud " + nm, V, F), SC, [cm], root)
    co.hide_render = G("DUST_VEIL", 0) <= 0        # the soft veil behind the sand is off: it came down and faded in the air
    co.location = (x, y, 0.0)
    co.visible_shadow = False
    co.display_type = "WIRE"
    # the grit: a few trickles, each a small cluster of grains with its own start
    pts, a_t0, a_vt, a_size, a_drift = [], [], [], [], []
    # Each trickle pours from one crack: a thin stream of very fine grains, heavy at first and thinning out, like
    # sand from an hourglass. Hundreds of grains far smaller than a pixel add up to a soft pale line.
    # Owner, 2026-11-20: "it's too much sand. It is way too much sand ... just a little bit of sand, enough to be
    # noticeable ... like 20% of the current amount". Three thin trickles of about 180 grains (it was five of
    # about 550), and the veil of fine dust behind them at a third.
    for c in range(G("DUST_TRICKLES", 3)):
        ang, rad = rng.uniform(0, 2 * math.pi), rng.uniform(0.15, 1.1)
        cx_, cy_ = rad * math.cos(ang), rad * math.sin(ang)
        # A short spill (owner, 2026-11-20: "when I say shrink it, I mean shrink it in terms of length ... just a
        # little bit of sand, very short ... looks like it comes like almost all the way down"): each trickle lets
        # go within a tenth of a second and its grains fall at nearly one speed, so it stays a short clump, a few
        # units long, all the way to the floor (the last grain lands 2.1 s after the impact).
        start, dur = rng.uniform(0.03, 0.15), rng.uniform(0.05, 0.10)
        wide, v0 = rng.uniform(0.05, 0.12), rng.uniform(47.0, 57.0)
        for _ in range(int(G("DUST_GRAINS", 230) * rng.uniform(0.4, 1.2))):
            pts.append((x + cx_ + rng.gauss(0, wide), y + cy_ + rng.gauss(0, wide), ZC))
            a_t0.append(start + dur * rng.random() ** 1.3)
            a_vt.append(v0 * rng.uniform(0.96, 1.04))
            a_size.append(rng.uniform(0.008, 0.017))
            a_drift += [rng.gauss(0, 0.1), rng.gauss(0, 0.1), 0.0]
    me = bpy.data.meshes.new("Temple Dust Grit " + nm)
    me.from_pydata(pts, [], [])
    for an, vals, kind in (("t0", a_t0, "FLOAT"), ("vt", a_vt, "FLOAT"), ("size", a_size, "FLOAT")):
        me.attributes.new(an, kind, "POINT").data.foreach_set("value", vals)
    me.attributes.new("drift", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", a_drift)
    go = put("Temple Dust Grit " + nm, me, SC, [gm], root)
    md = go.modifiers.get("Grit") or go.modifiers.new("Grit", "NODES")
    md.node_group = ng
    go.visible_shadow = False
    if go.name not in RECV.objects:
        RECV.objects.link(go)
bpy.context.view_layer.update()
bad = []
for idb in (ng, cm.node_tree):                    # a driver that failed once stays switched off until it is set again
    for fc in idb.animation_data.drivers:
        fc.driver.expression = fc.driver.expression
        if not fc.driver.is_valid:
            bad.append(fc.data_path)
result = {"dust": "ok", "grains_per_shaft": len(pts), "invalid_drivers": bad}
