"""Version 16: the hall's ceiling blended into the walls under it (owner, 2026-11-23).

Run inside Claude_Temple_Ceiling.blend (a copy of Codex_Temple_Fire.blend, which stays untouched); safe to run
again; no object is deleted (the ribs get new mesh data, the mesh they had is kept as "... (before v16)"; every
material node this adds is named "v16 ..." and taking those nodes out puts the material back as it was).

How it came about. The owner first had the ceiling made 50 percent wider with no arches on the pillars (version
15, Claude_Temple_Wide.blend), then said: "I actually do like the things above the pillars ... I want them to
remain", the ribs should "still ... shrink a bit to how you did before", and "I want a way to blend the top with
the bottom ... I see like a brick just kind of like floating in the air ... I want it to all blend seamlessly".
From the ideas shown (temple/tools/blend_options.py) they picked, in two steps: "I like C", then "Let's try C and
a darker cieling stone and no shine on the arch's edge". So this file has the ceiling at its original width, with
the arches, and:

1. The ribs stand half as far out of the ceiling (0.7, was 1.4), same width along the hall.
2. Each rib sinks into the ceiling as it comes down, over the lowest 24 degrees of the curve, so it has no foot.
   It used to stop dead at the top of the wall with a flat underside and nothing under it (the "floating brick").
3. The ceiling and the ribs have no shine at their foot; it comes back smoothly over the 12 units above. The pale
   patch at the foot of the ceiling (the "much lighter gray type of metal") was the stone's shine seen at a flat
   angle, mirroring the room's soft overall light. Darker stone alone left it.
4. The stone of the ceiling and the ribs is half as bright in colour (the owner's "darker cieling stone").
5. No shine on the faces of the arches that look across the hall, nor on the face of the wall standing on them.
   Seen from below and from the side, the arch's front face is a thin sliver right under the ceiling; with its
   shine it was brighter (47 of 255) than the arch's underside (25) and the ceiling beside it (41), which read as
   a line with small bright dots on it. Without it the sliver sits between the two (31).

Nothing else is changed: no light, no fog, no pillar, no camera, no timing, and the two openings in the ceiling
are not touched.

    V16 test, saves nothing:  blender -b <file> --python tools/v16_ceiling_blend.py --python tools/v12_render.py
V16_TONE (0.5), V16_SHINE_TOP (12), V16_TAPER (24), V16_ARCH_SHINE (0) set the amounts."""
import bpy, bmesh, math, os

E = os.environ.get
OB, MATS = bpy.data.objects, bpy.data.materials
ZC, VR = 46.0, 15.0                                  # the ceiling: axis height, inside radius
RIB_OUT = 0.7                                        # how far a rib stands out of the ceiling (was 1.4)
RIB_Y = ((17.1, 18.9), (28.9, 30.7), (40.7, 42.5), (54.2, 56.1))
TAPER = math.radians(float(E("V16_TAPER", "24")))    # how far up the curve the rib's foot fades out
TONE = float(E("V16_TONE", "0.5"))                   # the ceiling stone's colour, times this
SHINE_TOP = float(E("V16_SHINE_TOP", "12"))          # the shine is back in full this far above the foot
ARCH_SHINE = float(E("V16_ARCH_SHINE", "0"))         # the shine left on the arch's front face and the wall on it
TAG = "v16 "
VAULT_MATS = ("Temple Vault Masonry", "Temple Vault Rib Stone")


def principled(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def add(nt, kind, name):
    n = nt.nodes.new(kind)
    n.name = n.label = TAG + name
    return n


def clean(m):
    """Take out everything an earlier run of this script added to the material."""
    nt = m.node_tree
    sc = nt.nodes.get(TAG + "tone")
    if sc is not None and sc.inputs[0].is_linked:
        nt.links.new(sc.inputs[0].links[0].from_socket, principled(m).inputs["Base Color"])
    for n in [n for n in nt.nodes if n.name.startswith(TAG)]:
        nt.nodes.remove(n)


def ramp(nt, name, lo, hi, a, b):
    mr = add(nt, "ShaderNodeMapRange", name)
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = lo, hi
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = a, b
    return mr


def foot_shine(m):
    """No shine at the ceiling's foot, back in full SHINE_TOP above it."""
    nt = m.node_tree
    sock = principled(m).inputs["Specular IOR Level"]
    tc = add(nt, "ShaderNodeTexCoord", "place")
    sp = add(nt, "ShaderNodeSeparateXYZ", "height")
    nt.links.new(tc.outputs["Object"], sp.inputs[0])
    mr = ramp(nt, "shine by height", ZC, ZC + SHINE_TOP, 0.0, sock.default_value)
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], sock)


def darker(m, k):
    nt = m.node_tree
    pb = principled(m)
    src = pb.inputs["Base Color"].links[0].from_socket
    sc = add(nt, "ShaderNodeVectorMath", "tone")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = k
    nt.links.new(src, sc.inputs[0])
    nt.links.new(sc.outputs["Vector"], pb.inputs["Base Color"])


def front_shine(m, k, by):
    """The shine times k on the faces that look across the hall ("normal": whichever way a face points;
    "place": the wall's face toward the hall, 15 from the middle)."""
    nt = m.node_tree
    sock = principled(m).inputs["Specular IOR Level"]
    base = sock.default_value
    sp = add(nt, "ShaderNodeSeparateXYZ", "across")
    if by == "normal":
        geo = add(nt, "ShaderNodeNewGeometry", "face")
        vt = add(nt, "ShaderNodeVectorTransform", "face in the hall")
        vt.vector_type, vt.convert_from, vt.convert_to = "NORMAL", "WORLD", "OBJECT"
        nt.links.new(geo.outputs["True Normal"], vt.inputs[0])
        nt.links.new(vt.outputs[0], sp.inputs[0])
        lo, hi, a, b = 0.5, 0.8, base, base * k
    else:
        tc = add(nt, "ShaderNodeTexCoord", "place")
        nt.links.new(tc.outputs["Object"], sp.inputs[0])
        lo, hi, a, b = 15.05, 15.3, base * k, base
    ab = add(nt, "ShaderNodeMath", "either side")
    ab.operation = "ABSOLUTE"
    nt.links.new(sp.outputs["X"], ab.inputs[0])
    mr = ramp(nt, "shine by face", lo, hi, a, b)
    nt.links.new(ab.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], sock)


def thin_ribs():
    ribs = OB["Temple Vault Ribs"]
    keep = "Temple Vault Ribs (before v16)"
    old = bpy.data.meshes.get(keep)
    if old is None:                                  # first run: keep the mesh the ribs had
        old = ribs.data
        old.name = keep
        old.use_fake_user = True
    V, F, n = [], [], 72
    for y0, y1 in RIB_Y:
        o_ = len(V)
        for i in range(n + 1):
            th = math.pi * i / n
            c, s_ = math.cos(th), math.sin(th)
            t = min(max(min(th, math.pi - th) / TAPER, 0.0), 1.0) if TAPER > 0 else 1.0
            out = -0.03 + (RIB_OUT + 0.03) * t * t * (3 - 2 * t)      # sinks just inside the ceiling at the foot
            for r, y in ((VR - out, y0), (VR + 0.3, y0), (VR + 0.3, y1), (VR - out, y1)):
                V.append((r * c, y, ZC + r * s_))
        for i in range(n):
            for q in range(4):
                a, b = o_ + 4 * i + q, o_ + 4 * i + (q + 1) % 4
                F.append((a, b, b + 4, a + 4))
        F.append((o_, o_ + 1, o_ + 2, o_ + 3))
        F.append((o_ + 4 * n + 3, o_ + 4 * n + 2, o_ + 4 * n + 1, o_ + 4 * n))
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Temple Vault Ribs")
    bm.to_mesh(me)
    bm.free()
    for m in old.materials:
        me.materials.append(m)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(30))
    me.update()
    ribs.data = me
    return len(me.vertices)


nv = thin_ribs()
for nm in VAULT_MATS:
    clean(MATS[nm])
    foot_shine(MATS[nm])
    darker(MATS[nm], TONE)
done = []
for obname, by in (("Temple Arcade Arches", "normal"), ("Temple Aisle Walls", "place")):
    o = OB[obname]
    m = o.data.materials[0]
    if m.users > 1 and not m.name.endswith(" (hall face)"):          # only this object: its own copy of the stone
        m = m.copy()
        m.name = o.data.materials[0].name + " (hall face)"
        o.data.materials[0] = m
    clean(m)
    front_shine(m, ARCH_SHINE, by)
    done.append((obname, m.name, m.users))
bpy.context.view_layer.update()
print("V16 ceiling blend: ribs", nv, "points, tone", TONE, "shine back at", SHINE_TOP, "arch shine", ARCH_SHINE, done, flush=True)
