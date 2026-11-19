"""Dust puffs and magic sparkles, keyed per object (run from anim_all.py, which supplies ANIM_K).

Deterministic (fixed seed). Each puff or sparkle is a small object parented to the chest Root,
keyed in chest-frame coordinates (z measured from the floor). Its opacity or glow is the alpha of
its Object Color (Object Info > Alpha in the material), so 0 means invisible.
Settings: DUST_* and SPARK_* below."""
import bpy, math, random, bmesh, sys
from mathutils import Vector, Matrix
sys.path.insert(0, "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools")
from anim_lib import Keys

K = globals().get("ANIM_K") or Keys()
root = bpy.data.objects["Reveal Chest Root"]
FXC = bpy.data.collections["Reveal FX"]
FPS = 30.0
B, D = 2.775, 1.865

# impacts come from the physics landing (anim_landing.py writes physics/landing_events.json):
# frame, edge (-1 = -x side, +1 = +x side) and strength (speed relative to the first hit)
import json as _json
_ev = _json.load(open("/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/physics/landing_events.json"))
DUST_IMPACTS = [(im["frame"], im["strength"], im["edge"]) for im in _ev["impacts"] if im["strength"] > 0.2]
DUST_PER_BOOT = 14             # puffs per touching boot on the strongest hit (scaled by strength)
BOOT = (2.33, 1.36)            # boot centres (the boots are the only parts that touch the floor)
SPARK_STREAM = dict(count=24, start=122, end=205, dense_until=150)
SPARK_BURST = dict(count=10, frame=179, centre=(0.0, 0.0, 6.21 + 2.455))   # v5: a soft few, not a burst
SPARK_AMBIENT = dict(count=14, start=180, end=222, centre=(0.0, 0.0, 6.15 + 2.455))


# ------------------------------------------------------------------ materials and meshes
def dust_material():
    m = bpy.data.materials.get("Reveal Dust") or bpy.data.materials.new("Reveal Dust")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value = (0.42, 0.36, 0.29, 1)
    bs.inputs["Emission Color"].default_value = (0.42, 0.36, 0.29, 1)   # lifts the shadow side:
    bs.inputs["Emission Strength"].default_value = 0.4                 # no dark rims on the puffs
    bs.inputs["Roughness"].default_value = 1.0
    bs.inputs["Specular IOR Level"].default_value = 0.0
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.2
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.3
    nz.inputs["Detail"].default_value = 4
    nr = nt.nodes.new("ShaderNodeMapRange")
    nr.inputs["From Min"].default_value, nr.inputs["From Max"].default_value = 0.3, 0.75
    nr.inputs["To Min"].default_value, nr.inputs["To Max"].default_value = 0.45, 1.0
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    L = nt.links.new
    L(lw.outputs["Facing"], inv.inputs[1]); L(inv.outputs[0], pw.inputs[0])
    rn = nt.nodes.new("ShaderNodeMath"); rn.operation = "MULTIPLY"; rn.inputs[1].default_value = 37.0
    va = nt.nodes.new("ShaderNodeVectorMath"); va.operation = "ADD"      # each puff its own pattern
    L(oi.outputs["Random"], rn.inputs[0]); L(tc.outputs["Object"], va.inputs[0]); L(rn.outputs[0], va.inputs[1])
    L(va.outputs[0], nz.inputs["Vector"]); L(nz.outputs["Fac"], nr.inputs["Value"])
    L(pw.outputs[0], m1.inputs[0]); L(nr.outputs["Result"], m1.inputs[1])
    L(m1.outputs[0], m2.inputs[0]); L(oi.outputs["Alpha"], m2.inputs[1])
    L(m2.outputs[0], bs.inputs["Alpha"]); L(bs.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = True
    return m


def spark_material():
    m = bpy.data.materials.get("Reveal Sparkle") or bpy.data.materials.new("Reveal Sparkle")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    add = nt.nodes.new("ShaderNodeAddShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    g = nt.nodes.new("ShaderNodeMath"); g.operation = "MULTIPLY"; g.inputs[1].default_value = 28.0
    L = nt.links.new
    L(oi.outputs["Color"], em.inputs["Color"]); L(oi.outputs["Alpha"], g.inputs[0])
    L(g.outputs[0], em.inputs["Strength"])
    L(tr.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1]); L(add.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    return m


def shared_mesh(name, maker):
    me = bpy.data.meshes.get(name)
    if me is None:
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        maker(bm)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
    return me


dust_me = shared_mesh("Reveal Dust Puff", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0))
spark_me = shared_mesh("Reveal Sparkle", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0))
dm, sm = dust_material(), spark_material()
for me, mt in ((dust_me, dm), (spark_me, sm)):
    if not me.materials:
        me.materials.append(mt)


def objs(prefix, n, me):
    out = []
    for i in range(n):
        name = f"{prefix} {i:02d}"
        o = bpy.data.objects.get(name)
        if o is None:
            o = bpy.data.objects.new(name, me)
            FXC.objects.link(o)
        o.parent = root
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.visible_shadow = False
        out.append(o)
    return out


def key_track(sec, o, samples, rgb):
    """samples: list of (frame, (x,y,z), scale, alpha)."""
    for i in range(3):
        K.add(sec, o.name, "location", i, [(f, p[i]) for f, p, s, a in samples])
        K.add(sec, o.name, "scale", i, [(f, s) for f, p, s, a in samples])
    K.add(sec, o.name, "color", 3, [(f, a) for f, p, s, a in samples])
    for i in range(3):
        K.add(sec, o.name, "color", i, [(samples[0][0], rgb[i])])


rnd = random.Random(20261117)

# ------------------------------------------------------------------ dust
counts = [max(2, round(DUST_PER_BOOT * st)) for f0, st, ed in DUST_IMPACTS]
dust_objs = objs("Reveal Dust", 2 * sum(counts), dust_me)
di = 0
for (f0, s, edge), cnt in zip(DUST_IMPACTS, counts):
    for boot_y in (-1, 1):                         # front and back boot on the touching edge
        bx, by = edge * BOOT[0], boot_y * BOOT[1]
        for n in range(cnt):
            # kicked outward from under the boot, mostly away from the chest, low along the floor
            base = math.atan2(boot_y * 0.55, edge * 1.0)
            ang = base + rnd.uniform(-1.25, 1.25)
            dirv = Vector((math.cos(ang), math.sin(ang), 0.0))
            p0 = Vector((bx + edge * rnd.uniform(0.2, 0.5), by + rnd.uniform(-0.4, 0.4), 0.0))
            v0 = rnd.uniform(4.0, 9.0) * math.sqrt(s)
            tau = rnd.uniform(0.18, 0.32)
            rise = rnd.uniform(0.05, 0.35) * s
            size = rnd.uniform(0.36, 0.8) * (0.5 + 0.5 * s)
            peak = rnd.uniform(0.35, 0.6) * (0.4 + 0.6 * s)
            life = int(rnd.uniform(18, 34) * (0.55 + 0.45 * s))
            delay = rnd.choice((0, 0, 1))
            f_start = round(f0) + delay
            samples = [(f_start - 1, (p0.x, p0.y, 0.05), 0.01, 0.0)]
            for k in range(0, life + 1, 2):
                tt = k / FPS
                pos = p0 + dirv * v0 * tau * (1 - math.exp(-tt / tau))
                z = 0.08 + rise * (1 - math.exp(-tt / 0.5)) + 0.3 * size * (1 - math.exp(-tt / 0.15))
                sc = size * (0.3 + 0.7 * (1 - math.exp(-tt / 0.15))) * (1 + 0.7 * tt)
                al = peak * min(1.0, k / 2.0 + 0.4) * math.exp(-max(0, k - 2) / (life * 0.4))
                samples.append((f_start + k, (pos.x, pos.y, z), sc, al if k < life else 0.0))
            samples.append((samples[-1][0] + 1, samples[-1][1], 0.01, 0.0))
            o = dust_objs[di]
            key_track("01 Landing", o, samples, (1, 1, 1))
            o.scale = (0.01, 0.01, 0.01)
            o["flat"] = 0.5
            di += 1
# puffs hug the floor: flatten every dust puff (z scale is half the xy scale)
for (sec, oname), chans in list(K.k.items()):
    if oname.startswith("Reveal Dust") and ("scale", 2) in chans:
        chans[("scale", 2)] = [tuple([k[0], k[1] * 0.5] + list(k[2:])) for k in chans[("scale", 2)]]

# ------------------------------------------------------------------ sparkles
def spark_rgb():
    w = rnd.random()
    return (1.0, 0.62 + 0.25 * w, 0.25 + 0.4 * w * w)


def twinkle(k, ph, fr):
    return 0.72 + 0.28 * math.sin(k * fr + ph)


st = objs("Reveal Spark Stream", SPARK_STREAM["count"], spark_me)
for i, o in enumerate(st):
    if i < SPARK_STREAM["count"] * 0.65:
        b0 = int(rnd.uniform(SPARK_STREAM["start"], SPARK_STREAM["dense_until"]))
    else:
        b0 = int(rnd.uniform(SPARK_STREAM["dense_until"], SPARK_STREAM["end"]))
    p0 = Vector((rnd.uniform(-2.1, 2.1), rnd.uniform(-1.2, 1.2), rnd.uniform(2.3, 2.8)))
    vz = rnd.uniform(2.2, 5.5)
    vxy = Vector((p0.x, p0.y, 0)) * rnd.uniform(0.05, 0.25)
    life = int(rnd.uniform(26, 52))
    size = rnd.uniform(0.028, 0.06)
    ph, fr = rnd.uniform(0, 6.28), rnd.uniform(0.6, 1.4)
    sway = rnd.uniform(0.15, 0.45)
    samples = [(b0 - 1, tuple(p0), 0.001, 0.0)]
    for k in range(0, life + 1, 2):
        tt = k / FPS
        z = p0.z + vz * 0.9 * (1 - math.exp(-tt / 0.9))
        x = p0.x + vxy.x * tt + sway * math.sin(tt * 3.0 + ph)
        y = p0.y + vxy.y * tt + sway * 0.6 * math.cos(tt * 2.6 + ph)
        al = min(1.0, k / 4.0) * (1 - (k / life) ** 2) * twinkle(k, ph, fr)
        samples.append((b0 + k, (x, y, z), size * (1 - 0.4 * k / life), al if k < life else 0.0))
    samples.append((samples[-1][0] + 1, samples[-1][1], 0.001, 0.0))
    key_track("04 Opening", o, samples, spark_rgb())

bu = objs("Reveal Spark Burst", SPARK_BURST["count"], spark_me)
c = Vector(SPARK_BURST["centre"])
cam_dir = Vector((0.0, -1.0, 0.0))
for i, o in enumerate(bu):
    th = 2 * math.pi * (i + rnd.uniform(-0.3, 0.3)) / SPARK_BURST["count"]
    # radial in the plane facing the camera (world x/z), expressed in the chest frame
    yaw = math.atan2(0.5299192070960999, 0.8480481505393982)
    wdir = Vector((math.cos(th), rnd.uniform(-0.35, 0.35), math.sin(th))).normalized()
    ldir = Matrix.Rotation(-yaw, 3, "Z") @ wdir
    v0 = rnd.uniform(5.0, 11.0)
    tau = rnd.uniform(0.18, 0.3)
    life = int(rnd.uniform(16, 30))
    size = rnd.uniform(0.03, 0.065)
    f0 = SPARK_BURST["frame"] + rnd.choice((0, 0, 1))
    p0 = c + ldir * 2.05
    samples = [(f0 - 1, tuple(p0), 0.001, 0.0)]
    for k in range(0, life + 1, 2):
        tt = k / FPS
        pos = p0 + ldir * v0 * tau * (1 - math.exp(-tt / tau)) + Vector((0, 0, -0.6 * tt * tt))
        al = (1 - k / life) ** 1.5 * twinkle(k, i, 1.1)
        samples.append((f0 + k, tuple(pos), size, al if k < life else 0.0))
    samples.append((samples[-1][0] + 1, samples[-1][1], 0.001, 0.0))
    key_track("05 Badge Reveal", o, samples, spark_rgb())

am = objs("Reveal Spark Ambient", SPARK_AMBIENT["count"], spark_me)
c = Vector(SPARK_AMBIENT["centre"])
for i, o in enumerate(am):
    b0 = int(rnd.uniform(SPARK_AMBIENT["start"], SPARK_AMBIENT["end"] - 20))
    ang = rnd.uniform(0, 2 * math.pi)
    r = rnd.uniform(1.9, 2.9)
    p0 = c + Vector((r * math.cos(ang), r * 0.5 * math.sin(ang), rnd.uniform(-1.6, 1.4)))
    life = min(int(rnd.uniform(28, 50)), SPARK_AMBIENT["end"] - b0)
    size = rnd.uniform(0.022, 0.045)
    samples = [(b0 - 1, tuple(p0), 0.001, 0.0)]
    for k in range(0, life + 1, 2):
        tt = k / FPS
        pos = p0 + Vector((0.15 * math.sin(tt * 2 + i), 0, 0.55 * tt))
        al = math.sin(math.pi * k / life) * twinkle(k, i, 0.9) * 0.8
        samples.append((b0 + k, tuple(pos), size, al if k < life else 0.0))
    samples.append((samples[-1][0] + 1, samples[-1][1], 0.001, 0.0))
    key_track("05 Badge Reveal", o, samples, spark_rgb())
print("fx particles:", len(dust_objs), "dust,", len(st) + len(bu) + len(am), "sparkles")

# objects left over from earlier versions with larger counts: no animation, never rendered
used = {o.name for o in dust_objs + st + bu + am}
for o in list(FXC.objects):
    if o.name.startswith(("Reveal Dust ", "Reveal Spark ")) and o.name not in used:
        if o.animation_data:
            for t in list(o.animation_data.nla_tracks):
                o.animation_data.nla_tracks.remove(t)
            o.animation_data.action = None
        o.color = (1, 1, 1, 0)
        o.hide_render = True
        o.hide_viewport = True
    elif o.name in used:
        o.hide_render = False
        o.hide_viewport = False
