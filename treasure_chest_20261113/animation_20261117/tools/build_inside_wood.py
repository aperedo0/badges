"""Real wood boards on every inside surface of the chest (body walls, floor, rim tops, lid underside
and lid end caps). Run inside Blender: exec(open(PATH).read()). Safe to run again.

The inside used one plank picture box projected over the whole chest, so the floor and the lid's
underside showed one board stretched into flat orange streaks. This builds two materials from the
same plank pictures as the outside front (Simple plank01 to 03), laid as separate boards at the
outside's own scale: boards run along the chest's length on the long walls, floor and lid, along the
depth on the end walls, and follow the lid's arch. Each board picks its own plank picture, strip,
direction and slight tone, with a dark seam and rounded edges between boards.

Only the two envelope meshes' materials change (shared mesh data, so the original objects in the
other scenes of this file get the same inside). No geometry changes. The closing faces (wall tops,
lid bottom edge) keep the earlier material, see restore_closing_edges at the end.
"""
import bpy, math
import numpy as np

BOARD = 0.54          # board width, the outside middle plank's height
LENGTH = 5.1          # world units covered by one plank picture's length (the outside front)
SEAM = (0.003, 0.012)  # dark gap, then edge back to full tone (units from the seam)
ROUND = 0.025         # rounded board edge width
TONE = (0.86, 1.08)   # per board brightness range
ROUGH_ADD = 0.06      # inside a touch less glossy than the varnished outside
AO_DIST, AO_MIN = 0.6, 0.5
BUMP_STRENGTH, BUMP_DIST = 0.7, 0.03
PLANKS = [("Simple plank01", 816), ("Simple plank02", 432), ("Simple plank03", 784)]

BODY = "Master Chest Body Envelope"
LID = "Lab Chest Barrel Lid Envelope"


def chest_frame(o):
    M = np.array(o.matrix_parent_inverse)
    return M, -math.atan2(M[0][1], M[0][0])


def lid_arc(o):
    """Fit the lid underside arch (chest frame y, z) with a circle."""
    M, _ = chest_frame(o)
    R3 = M[:3, :3]
    pts = []
    for p in o.data.polygons:
        n = R3 @ np.array(p.normal[:])
        c = (M @ np.r_[np.array(p.center[:]), 1])[:3]
        if abs(n[0]) < 0.3 and n[2] < -0.2 and c[2] > 0.3:
            pts.append(c[1:])
    a = np.array(pts)
    A = np.c_[2 * a[:, 0], 2 * a[:, 1], np.ones(len(a))]
    yc, zc, k = np.linalg.lstsq(A, (a ** 2).sum(1), rcond=None)[0]
    return float(yc), float(zc), float(math.sqrt(k + yc * yc + zc * zc))


class G:
    def __init__(self, tree):
        self.t, self.n, self.l = tree, tree.nodes, tree.links
        self.x = 0

    def node(self, kind, **kw):
        n = self.n.new(kind)
        n.location = (self.x, 0)
        self.x += 30
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def link(self, a, b):
        self.l.new(a, b)

    def m(self, op, a, b=None, clamp=False):
        n = self.node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def mix(self, fac, a, b):
        n = self.node("ShaderNodeMix", data_type="RGBA")
        for sock, v in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            elif isinstance(v, tuple):
                sock.default_value = v
            else:
                self.link(v, sock)
        return n.outputs[2]

    def smooth(self, v, lo, hi):
        n = self.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP")
        self.link(v, n.inputs[0])
        n.inputs[1].default_value, n.inputs[2].default_value = lo, hi
        return n.outputs[0]


def build(name, obj, lid):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    t = mat.node_tree
    t.nodes.clear()
    g = G(t)
    M, rot = chest_frame(obj)
    tc = g.node("ShaderNodeTexCoord")
    mp = g.node("ShaderNodeMapping", vector_type="POINT")
    mp.inputs["Location"].default_value = tuple(M[:3, 3])
    mp.inputs["Rotation"].default_value = (0, 0, rot)
    g.link(tc.outputs["Object"], mp.inputs[0])
    mn = g.node("ShaderNodeMapping", vector_type="VECTOR")
    mn.inputs["Rotation"].default_value = (0, 0, rot)
    g.link(tc.outputs["Normal"], mn.inputs[0])
    sp = g.node("ShaderNodeSeparateXYZ"); g.link(mp.outputs[0], sp.inputs[0])
    sn = g.node("ShaderNodeSeparateXYZ"); g.link(mn.outputs[0], sn.inputs[0])
    x, y, z = sp.outputs
    ax, ay, az = (g.m("ABSOLUTE", s) for s in sn.outputs)
    mX = g.m("MULTIPLY", g.m("GREATER_THAN", ax, ay), g.m("GREATER_THAN", ax, az))
    notX = g.m("SUBTRACT", 1.0, mX)
    if lid:
        yc, zc, R = lid_arc(obj)
        arc = g.m("MULTIPLY", g.m("ARCTAN2", g.m("SUBTRACT", y, yc), g.m("SUBTRACT", z, zc)), R)
        u = g.m("ADD", g.m("MULTIPLY", mX, y), g.m("MULTIPLY", notX, x))
        v = g.m("ADD", g.m("MULTIPLY", mX, z), g.m("MULTIPLY", notX, arc))
    else:
        mY = g.m("MULTIPLY", g.m("GREATER_THAN", ay, ax), g.m("GREATER_THAN", ay, az))
        mZ = g.m("SUBTRACT", notX, mY)
        endZ = g.m("MULTIPLY", mZ, g.m("GREATER_THAN", g.m("ABSOLUTE", x), 2.32))
        useY = g.m("ADD", mX, endZ)
        u = g.m("ADD", g.m("MULTIPLY", useY, y), g.m("MULTIPLY", g.m("SUBTRACT", 1.0, useY), x))
        v = g.m("ADD", g.m("ADD", g.m("MULTIPLY", g.m("ADD", mX, mY), z),
                               g.m("MULTIPLY", g.m("SUBTRACT", mZ, endZ), y)), g.m("MULTIPLY", endZ, x))
    # boards
    b = g.m("DIVIDE", v, BOARD)
    i = g.m("FLOOR", b)
    tt = g.m("SUBTRACT", b, i)
    wn = g.node("ShaderNodeTexWhiteNoise", noise_dimensions="1D")
    g.link(g.m("ADD", i, 17.0 if lid else 3.0), wn.inputs["W"])
    rs = g.node("ShaderNodeSeparateColor"); g.link(wn.outputs["Color"], rs.inputs[0])
    r0 = wn.outputs["Value"]
    r1, r2, r3 = rs.outputs
    pick = g.m("FLOOR", g.m("MINIMUM", g.m("MULTIPLY", r0, 3.0), 2.999))
    flip = g.m("GREATER_THAN", r1, 0.5)
    uu = g.m("ADD", g.m("ADD", g.m("DIVIDE", u, LENGTH), 0.5), g.m("MULTIPLY", r2, 0.08))
    uu = g.m("ADD", g.m("MULTIPLY", flip, g.m("SUBTRACT", 1.0, g.m("MULTIPLY", uu, 2.0))), uu)  # flip: 1 - uu
    outs = {"albedo": [], "rough": [], "height16": []}
    for k, (stem, h) in enumerate(PLANKS):
        kh = 432.0 / h
        vv = g.m("ADD", g.m("MULTIPLY", tt, kh), g.m("MULTIPLY", r3, 1.0 - kh))
        cv = g.node("ShaderNodeCombineXYZ"); g.link(uu, cv.inputs[0]); g.link(vv, cv.inputs[1])
        for kind in outs:
            im = bpy.data.images[f"{stem}_{kind}.png"]
            tn = g.node("ShaderNodeTexImage", image=im, interpolation="Linear", extension="REPEAT")
            g.link(cv.outputs[0], tn.inputs[0])
            outs[kind].append(tn.outputs["Color"])
    is0 = g.m("LESS_THAN", pick, 0.5)
    is2 = g.m("GREATER_THAN", pick, 1.5)
    chosen = {k: g.mix(is2, g.mix(is0, o[1], o[0]), o[2]) for k, o in outs.items()}
    # seams and tone
    e = g.m("MULTIPLY", g.m("MINIMUM", tt, g.m("SUBTRACT", 1.0, tt)), BOARD)
    seam = g.smooth(e, *SEAM)
    edge = g.smooth(e, 0.0, ROUND)
    tone = g.m("ADD", TONE[0], g.m("MULTIPLY", g.m("FRACT", g.m("MULTIPLY", r0, 7.13)), TONE[1] - TONE[0]))
    ao = g.node("ShaderNodeAmbientOcclusion", samples=8)
    ao.inputs["Distance"].default_value = AO_DIST
    aof = g.m("ADD", AO_MIN, g.m("MULTIPLY", ao.outputs["AO"], 1.0 - AO_MIN))
    shade = g.m("MULTIPLY", g.m("MULTIPLY", tone, aof), g.m("ADD", 0.18, g.m("MULTIPLY", seam, 0.82)))
    col = g.node("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    col.inputs[0].default_value = 1.0
    g.link(chosen["albedo"], col.inputs[6]); g.link(shade, col.inputs[7])
    bsdf = g.node("ShaderNodeBsdfPrincipled")
    g.link(col.outputs[2], bsdf.inputs["Base Color"])
    rough_bw = g.node("ShaderNodeRGBToBW"); g.link(chosen["rough"], rough_bw.inputs[0])
    g.link(g.m("ADD", rough_bw.outputs[0], ROUGH_ADD, clamp=True), bsdf.inputs["Roughness"])
    h_bw = g.node("ShaderNodeRGBToBW"); g.link(chosen["height16"], h_bw.inputs[0])
    height = g.m("ADD", g.m("MULTIPLY", h_bw.outputs[0], 0.5), edge)
    bump = g.node("ShaderNodeBump")
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = BUMP_STRENGTH, BUMP_DIST
    g.link(height, bump.inputs["Height"]); g.link(bump.outputs[0], bsdf.inputs["Normal"])
    out = g.node("ShaderNodeOutputMaterial"); g.link(bsdf.outputs[0], out.inputs["Surface"])
    return mat


CORE_SEE_THROUGH = 0.04  # glow card brightness over the wood (it used to be an opaque card)


def core_see_through(scale):
    """The Magic Core glow card sat inside the chest as an opaque emitter and hid the floor and lower
    walls. Make it an additive glow over the wood (like the light beam), same driver, same noise."""
    m = bpy.data.materials["Reveal Magic Core"]
    nt = m.node_tree
    em, out, ramp = nt.nodes["Emission"], nt.nodes["Material Output"], nt.nodes["Color Ramp"]
    add = nt.nodes.get("Inside glow add") or nt.nodes.new("ShaderNodeAddShader")
    add.name = "Inside glow add"
    tr = nt.nodes.get("Inside glow clear") or nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.name = "Inside glow clear"
    mul = nt.nodes.get("Inside glow scale") or nt.nodes.new("ShaderNodeMix")
    mul.name, mul.data_type, mul.blend_type = "Inside glow scale", "RGBA", "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    mul.inputs[7].default_value = (scale, scale, scale, 1)
    nt.links.new(ramp.outputs["Color"], mul.inputs[6])
    nt.links.new(mul.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], add.inputs[0])
    nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    # Full glow while the lid is shut (it only shows through the seam then, as before), fading to
    # the faint value as seam_glow drops to zero while the lid opens (frames 116 to 128).
    sock = mul.inputs[7]
    for ch in range(3):
        sock.driver_remove("default_value", ch)
        d = sock.driver_add("default_value", ch).driver
        d.type = "SCRIPTED"
        var = d.variables.new()
        var.name, var.type = "seam_glow", "SINGLE_PROP"
        var.targets[0].id_type = "OBJECT"
        var.targets[0].id = bpy.data.objects["Reveal FX Controls"]
        var.targets[0].data_path = '["seam_glow"]'
        d.expression = f"{scale} + {1 - scale}*min(seam_glow, 1.0)"


core_see_through(CORE_SEE_THROUGH)
done = {}
for key, lid, mname in ((BODY, False, "Simple wood inside body"), (LID, True, "Simple wood inside lid")):
    obj = bpy.data.objects["R " + key]
    mat = build(mname, obj, lid)
    obj.data.materials[0] = mat
    done[obj.name] = mat.name
INSIDE = done
print("inside wood", done)


# The faces where the lid closes keep the look they had before the boards (owner, 2026-11-17): the
# rounded top of the body walls and the lid's bottom edge sit right next to the iron rim and the
# outside wood, which has no board streaks. They get the earlier inside material in a second slot.
EDGE_MAT = "Claude carved planks inside"


def closing_faces(obj, top):
    M = np.array(obj.matrix_parent_inverse)
    R3 = M[:3, :3]
    zs = [(M @ np.r_[np.array(v.co[:]), 1])[2] for v in obj.data.vertices]
    out = []
    for p in obj.data.polygons:
        vz = [zs[i] for i in p.vertices]
        nz = (R3 @ np.array(p.normal[:]))[2]
        if top and min(vz) > 2.74:                    # body: rounded wall tops at z 2.75 to 2.80
            out.append(p.index)
        if not top and max(vz) < 0.055 and nz < -0.3:  # lid: bottom edge at z 0.02 to 0.05
            out.append(p.index)
    return out


def restore_closing_edges():
    em = bpy.data.materials[EDGE_MAT]
    res = {}
    for key, top in ((BODY, True), (LID, False)):
        me = bpy.data.objects["R " + key].data
        names = [m.name if m else None for m in me.materials]
        if EDGE_MAT not in names:
            me.materials.append(em)
            names.append(EDGE_MAT)
        k = names.index(EDGE_MAT)
        faces = closing_faces(bpy.data.objects["R " + key], top)
        for i in faces:
            me.polygons[i].material_index = k
        me.update()
        res[key] = len(faces)
    return res


EDGES = restore_closing_edges()
print("closing edges restored", EDGES)
