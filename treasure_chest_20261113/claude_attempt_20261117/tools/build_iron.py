"""Give every structural iron piece my forged iron: chipped worn edges in real geometry
plus a procedural dark hammered surface that matches the approved bottom rim.

Run: blender -b chest_claude.blend --python tools/build_iron.py -- [object name filter]
Works in place and can be run again: Codex's meshes stay as "Codex backup ..." datablocks.
"""
import math
import sys

import bpy
import bmesh
import numpy as np
from mathutils import kdtree

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FILTER = args[0] if args else ""
SRC_MAT = "Chest forged iron shared varied surface"
MAT = "Claude forged iron pieces"
THIN = 0.011           # a face region this narrow (area / sharp border length) is a bevel strip
ANGLE = math.radians(12.0)

# ---- periodic 3D value noise ------------------------------------------------
_rng = np.random.default_rng(1234)
_LAT = _rng.random((48, 48, 48)).astype(np.float32)


def vnoise(p, freq, off=0.0):
    q = p * freq + off
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * _LAT[(i[:, 0] + dx) % 48, (i[:, 1] + dy) % 48, (i[:, 2] + dz) % 48]
    return out


def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---- material ------------------------------------------------------------------
def build_material():
    m = bpy.data.materials.get(MAT) or bpy.data.materials.new(MAT)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes
    L = nt.links

    def val(x):
        return x

    def link(src, dst):
        if isinstance(src, (int, float)):
            dst.default_value = src
        else:
            L.new(src, dst)

    def mth(op, a, b=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        link(a, n.inputs[0])
        if b is not None:
            link(b, n.inputs[1])
        return n.outputs[0]

    def mrange(v, f0, f1, t0, t1, smooth=True):
        n = N.new("ShaderNodeMapRange")
        n.interpolation_type = "SMOOTHSTEP" if smooth else "LINEAR"
        link(v, n.inputs["Value"])
        n.inputs["From Min"].default_value = f0; n.inputs["From Max"].default_value = f1
        n.inputs["To Min"].default_value = t0; n.inputs["To Max"].default_value = t1
        return n.outputs["Result"]

    def mixc(fac, a, b):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"
        link(fac, n.inputs["Factor"])
        for sock, v in ((n.inputs["A"], a), (n.inputs["B"], b)):
            if isinstance(v, tuple):
                sock.default_value = v + (1.0,)
            else:
                L.new(v, sock)
        return n.outputs["Result"]

    tc = N.new("ShaderNodeTexCoord")
    oi = N.new("ShaderNodeObjectInfo")
    offs = N.new("ShaderNodeVectorMath"); offs.operation = "SCALE"; offs.inputs[0].default_value = (37.0, 53.0, 71.0)
    L.new(oi.outputs["Random"], offs.inputs["Scale"])
    pos = N.new("ShaderNodeVectorMath"); pos.operation = "ADD"
    L.new(tc.outputs["Object"], pos.inputs[0]); L.new(offs.outputs["Vector"], pos.inputs[1])
    P = pos.outputs["Vector"]

    def noise(scale, detail, rough=0.55):
        n = N.new("ShaderNodeTexNoise"); L.new(P, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        return n.outputs["Fac"]

    def voro(scale, feature, smooth=0.7):
        n = N.new("ShaderNodeTexVoronoi"); n.feature = feature; L.new(P, n.inputs["Vector"])
        n.inputs["Scale"].default_value = scale
        if feature == "SMOOTH_F1":
            n.inputs["Smoothness"].default_value = smooth
        return n

    mott = noise(9.0, 3.0)
    brk = noise(35.0, 2.0)
    rustn = noise(4.5, 2.0)
    micro = noise(110.0, 2.0)
    d1 = voro(6.0, "SMOOTH_F1").outputs["Distance"]
    d2 = voro(13.0, "SMOOTH_F1").outputs["Distance"]
    vp = voro(60.0, "F1")
    sep = N.new("ShaderNodeSeparateColor"); L.new(vp.outputs["Color"], sep.inputs["Color"])
    pm = mth("MULTIPLY", mrange(vp.outputs["Distance"], 0.0, 0.22, 1.0, 0.0), mth("GREATER_THAN", sep.outputs["Red"], 0.85))

    attr = N.new("ShaderNodeAttribute"); attr.attribute_name = "claude_wear"
    # sharp edges without a modelled bevel (the boots): rounded and worn by the Cycles bevel node
    bev = N.new("ShaderNodeBevel"); bev.samples = 4; bev.inputs["Radius"].default_value = 0.022
    geo = N.new("ShaderNodeNewGeometry")
    dotn = N.new("ShaderNodeVectorMath"); dotn.operation = "DOT_PRODUCT"
    L.new(bev.outputs["Normal"], dotn.inputs[0]); L.new(geo.outputs["Normal"], dotn.inputs[1])
    bevmask = mrange(dotn.outputs["Value"], 0.80, 0.985, 1.0, 0.0)
    E = mth("MULTIPLY", mth("MAXIMUM", attr.outputs["Fac"], bevmask), mrange(brk, 0.25, 0.75, 0.45, 1.0), clamp=True)

    # height in scene units: hammer bowls, pits, fine scale
    bowl1 = mrange(d1, 0.0, 0.5, 0.0, 0.0030)
    bowl2 = mrange(d2, 0.0, 0.5, 0.0, 0.0012)
    h = mth("ADD", bowl1, bowl2)
    h = mth("SUBTRACT", h, mth("MULTIPLY", pm, 0.008))
    h = mth("ADD", h, mth("MULTIPLY", micro, 0.0006))
    h = mth("ADD", h, mth("MULTIPLY", mott, 0.0020))
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 1.0
    L.new(h, bump.inputs["Height"]); L.new(bev.outputs["Normal"], bump.inputs["Normal"])

    rust = mth("ADD", mrange(rustn, 0.58, 0.74, 0.0, 0.15), mth("MULTIPLY", pm, 0.25))
    tone = mrange(mott, 0.30, 0.70, 0.68, 1.32, smooth=False)
    ox = N.new("ShaderNodeVectorMath"); ox.operation = "SCALE"; ox.inputs[0].default_value = (0.040, 0.042, 0.047)
    L.new(tone, ox.inputs["Scale"])
    c = mixc(rust, ox.outputs["Vector"], (0.070, 0.042, 0.027))
    dark = N.new("ShaderNodeVectorMath"); dark.operation = "SCALE"
    L.new(c, dark.inputs[0]); L.new(mth("SUBTRACT", 1.0, mth("MULTIPLY", pm, 0.6)), dark.inputs["Scale"])
    col = mixc(E, dark.outputs["Vector"], (0.42, 0.38, 0.33))

    r = mth("ADD", 0.41, mth("MULTIPLY", mott, 0.12))
    r = mth("SUBTRACT", r, mrange(d1, 0.0, 0.35, 0.10, 0.0))
    r = mth("ADD", r, mth("MULTIPLY", pm, 0.25))
    r = mth("ADD", r, mth("MULTIPLY", rust, 0.10))
    rmix = N.new("ShaderNodeMix"); rmix.data_type = "FLOAT"
    L.new(E, rmix.inputs["Factor"]); L.new(r, rmix.inputs["A"]); rmix.inputs["B"].default_value = 0.36
    met = mth("ADD", 0.90, mth("MULTIPLY", E, 0.10))
    met = mth("SUBTRACT", met, mth("MULTIPLY", pm, 0.5))
    met = mth("SUBTRACT", met, mth("MULTIPLY", rust, 0.35), clamp=True)

    bsdf = N.new("ShaderNodeBsdfPrincipled")
    out = N.new("ShaderNodeOutputMaterial")
    L.new(col, bsdf.inputs["Base Color"]); L.new(rmix.outputs["Result"], bsdf.inputs["Roughness"])
    L.new(met, bsdf.inputs["Metallic"]); L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


# ---- geometry ------------------------------------------------------------------
def process(ob, mat):
    """Keep the piece's shape. Mark its narrow bevel strips (the worn edges) with a face attribute."""
    bkname = "Codex backup " + ob.name
    src = bpy.data.meshes.get(bkname)
    if src is None:
        src = ob.data
        src.name = bkname
        src.use_fake_user = True
    name = "Claude " + ob.name
    old = bpy.data.meshes.get(name)
    if old:
        old.name = name + " old"
    me = src.copy()
    me.name = name
    me.use_fake_user = False

    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    c0 = co - co.mean(0)
    thin = float(np.sqrt(np.linalg.eigvalsh(c0.T @ c0 / len(co)).min())) < 0.012   # washers stay dark
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.normal_update()

    def is_feature(e):
        if len(e.link_faces) != 2:
            return True
        return e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) >= ANGLE

    feat = {e.index: is_feature(e) for e in bm.edges}
    region = [-1] * len(bm.faces)
    worn = np.zeros(len(bm.faces), np.float32)
    for f0 in bm.faces:
        if region[f0.index] != -1:
            continue
        stack, members = [f0], []
        region[f0.index] = f0.index
        area = 0.0
        blen = 0.0
        while stack:
            f = stack.pop()
            members.append(f.index)
            area += f.calc_area()
            for e in f.edges:
                if feat[e.index]:
                    blen += e.calc_length()
                    continue
                for g in e.link_faces:
                    if region[g.index] == -1:
                        region[g.index] = f0.index
                        stack.append(g)
        if blen > 0 and area / blen < THIN and not thin:
            worn[members] = 1.0
    bm.free()
    att = me.attributes.get("claude_wear") or me.attributes.new("claude_wear", "FLOAT", "FACE")
    att.data.foreach_set("value", worn)
    me.materials.clear()
    me.materials.append(mat)
    me.update()
    ob.data = me
    if old:
        bpy.data.meshes.remove(old)
    return int(worn.sum()), len(worn)


mat = build_material()
total = 0
for ob in bpy.data.scenes["Full chest material evaluation"].objects:
    if ob.type != "MESH" or FILTER not in ob.name:
        continue
    names = [s.material.name for s in ob.material_slots if s.material]
    if names == [SRC_MAT] or names == [MAT]:
        n, nf = process(ob, mat)
        total += n
        print("IRON", ob.name, "worn faces", n, "of", nf, flush=True)
bpy.ops.wm.save_mainfile(compress=True)
print("IRON done", total)
