"""Ideas for blending the hall's ceiling into the walls below it (owner, 2026-11-23). Pictures only: run before
tools/v12_render.py in the same background Blender; nothing is saved.

    OPT=A PIECE=reveal ONLY=75 OUT=... blender -b <file> --python temple/tools/blend_options.py --python tools/v12_render.py

The owner, on the top left of two frames of the Codex Temple Fire video: the arches on the pillars stay ("I actually
do like the things above the pillars"); the ribs still shrink ("to how you did before"); "the thing above the
pillars, they're like dark, and then you see this like much lighter gray ... Perhaps what we do is we actually make
that ... darker, more like the wall. And maybe another way to blend it in"; "I see like a brick just kind of like
floating in the air ... I want it to all blend seamlessly ... give me some ideas for how to blend it."

What the corner shows (found with a colour coded render): the pale patch is the foot of the ceiling, lit by lights
the wall under it never gets, so there is a hard line where the two meet; and each rib ends at that line with a
flat underside, standing 1.4 out of the wall with nothing under it.

Every idea has the ribs half as deep (0.7 out of the ceiling). Then:
  A  darker stone: the ceiling and the ribs toned down evenly (the owner's own idea)
  B  fade: the ceiling and the ribs keep their tone at the top and sink into the dark toward the foot
  C  stone band: a carved band along the line where the ceiling meets the wall; every rib stands on it
  D  C and B together
  E  no shine at the foot (it comes back toward the top), and each rib sinks into the ceiling as it comes down
  F  no shine at the foot, and the stone band for the ribs to stand on
TONE (A), FOOT, FADE_TOP (B) and BAND_OUT set the amounts."""
import bpy, bmesh, math, os

E = os.environ.get
OPT = E("OPT", "A")
OB, MATS = bpy.data.objects, bpy.data.materials
ZC, VR = 46.0, 15.0
RIB_OUT = 1.4 * float(E("RIB", "0.5"))
RIB_Y = ((17.1, 18.9), (28.9, 30.7), (40.7, 42.5), (54.2, 56.1))
TAPER = math.radians(float(E("TAPER", "24"))) if OPT == "E" else 0.0     # how far up the curve the foot fades out


def recalc(V, F):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = [tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return out


def smooth(me, deg):
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(deg))
    me.update()


def thin_ribs():
    ribs = OB["Temple Vault Ribs"]
    V, F, n = [], [], 72
    for y0, y1 in RIB_Y:
        o_ = len(V)
        for i in range(n + 1):
            th = math.pi * i / n
            c, s_ = math.cos(th), math.sin(th)
            out = RIB_OUT
            if TAPER > 0:                             # the rib sinks into the ceiling as it comes down: no foot at all
                t = min(max(min(th, math.pi - th) / TAPER, 0.0), 1.0)
                out = -0.03 + (RIB_OUT + 0.03) * t * t * (3 - 2 * t)
            for r, y in ((VR - out, y0), (VR + 0.3, y0), (VR + 0.3, y1), (VR - out, y1)):
                V.append((r * c, y, ZC + r * s_))
        for i in range(n):
            for q in range(4):
                a, b = o_ + 4 * i + q, o_ + 4 * i + (q + 1) % 4
                F.append((a, b, b + 4, a + 4))
        F.append((o_, o_ + 1, o_ + 2, o_ + 3))
        F.append((o_ + 4 * n + 3, o_ + 4 * n + 2, o_ + 4 * n + 1, o_ + 4 * n))
    V, F = recalc(V, F)
    me = bpy.data.meshes.new("Temple Vault Ribs thin")
    me.from_pydata(V, [], F)
    for m in ribs.data.materials:
        me.materials.append(m)
    smooth(me, 30)
    ribs.data = me


def tone(name, foot, top, z0, z1):
    """Multiply the stone's colour by `foot` at height z0, rising smoothly to `top` at z1 (foot == top: even)."""
    nt = MATS[name].node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    src = pb.inputs["Base Color"].links[0].from_socket
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sp.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = z0, z1
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = foot, top
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    nt.links.new(src, sc.inputs[0])
    nt.links.new(mr.outputs["Result"], sc.inputs["Scale"])
    nt.links.new(sc.outputs["Vector"], pb.inputs["Base Color"])


def shine(name, foot, z0, z1, top=1.0):
    """The stone's shine (its mirror like reflection of the room) times `foot` at height z0, rising to full at z1.
    Found with lights off one by one: the pale patch at the ceiling's foot is the stone's shine at a flat angle,
    reflecting the room's ambient light. Darker stone does not touch it (tested: idea A leaves the patch)."""
    nt = MATS[name].node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    sock = pb.inputs["Specular IOR Level"]
    base = sock.default_value
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sp.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = z0, z1
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = base * foot, base * top
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], sock)


def band():
    """A carved band on top of the wall, under the ceiling's foot, on both sides: the ribs stand on it."""
    out = float(E("BAND_OUT", "1.1"))                # how far it stands out past the ceiling's face (the ribs: 0.7)
    x1 = VR - out
    prof = [(VR + 0.2, ZC), (x1, ZC), (x1, ZC - 0.5), (x1 + 0.4, ZC - 1.1), (VR - 0.3, ZC - 1.4), (VR + 0.2, ZC - 1.4)]
    y0, y1 = 10.0, 68.3
    V, F, k = [], [], len(prof)
    for sign in (1.0, -1.0):
        o_ = len(V)
        for y in (y0, y1):
            V += [(sign * x, y, z) for x, z in prof]
        F += [(o_ + q, o_ + (q + 1) % k, o_ + k + (q + 1) % k, o_ + k + q) for q in range(k)]
        F += [tuple(o_ + q for q in range(k)), tuple(o_ + k + q for q in reversed(range(k)))]
    V, F = recalc(V, F)
    me = bpy.data.meshes.new("Temple Vault Band")
    me.from_pydata(V, [], F)
    arc = OB["Temple Arcade Arches"]                 # it belongs to the wall: same stone, same lights, same shadows
    for m in arc.data.materials:
        me.materials.append(m)
    smooth(me, 30)
    o = bpy.data.objects.new("Temple Vault Band", me)
    for c in arc.users_collection:
        c.objects.link(o)
    o.parent = arc.parent
    o.matrix_parent_inverse = arc.matrix_parent_inverse.copy()
    bv = o.modifiers.new("Temple Bevel", "BEVEL")
    bv.width, bv.segments, bv.limit_method, bv.angle_limit = 0.07, 2, "ANGLE", math.radians(30)


thin_ribs()
if OPT == "A":
    k = float(E("TONE", "0.3"))
    for nm in ("Temple Vault Masonry", "Temple Vault Rib Stone"):
        tone(nm, k, k, ZC, ZC + 1.0)
if OPT in ("B", "D"):
    foot, top = float(E("FOOT", "0.1")), ZC + float(E("FADE_TOP", "10.0"))
    for nm in ("Temple Vault Masonry", "Temple Vault Rib Stone"):
        tone(nm, foot, 1.0, ZC, top)
if OPT in ("C", "D", "F"):
    band()
if OPT in ("E", "F"):
    for nm in ("Temple Vault Masonry", "Temple Vault Rib Stone"):
        shine(nm, float(E("SHINE_FOOT", "0.0")), ZC, ZC + float(E("SHINE_TOP", "12.0")), float(E("SHINE_ALL", "1.0")))

# Second round (owner, on idea E: "there is still this line caused from it going from light to dark ... maybe we can
# make the line not as visible by darkening the stone on top? like not just the brick strips but the entire
# cieling?"). A colour coded render showed the line is the front face of the arch on the pillars: a thin sliver seen
# from the side, brighter than the arch's dark underside on one side and than the ceiling's foot on the other. It is
# the same shine at a flat angle as the pale patch was: with the sliver's shine off it drops from 47 to 31 of 255,
# between the underside (25) and the ceiling (40). Darker ceiling stone (TONE_ALL=0.5) moves the ceiling by 1 of 255
# in the dark frame: up there the picture is haze and shine, not the stone's colour.
#   TONE_ALL    the whole ceiling and its ribs evenly darker in colour, on top of any idea (1 = unchanged)
#   SHINE_ALL   with E or F: the shine left at the top of the ceiling (1 = unchanged, 0 = no shine anywhere on it)
#   ARCH_SHINE  the shine left on the faces of the arches that look across the hall (1 = unchanged, 0 = none)
#   WALL_SHINE  the same for the face of the wall standing on the arches
def front_shine(mat, k, by):
    nt = mat.node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    sock = pb.inputs["Specular IOR Level"]
    base = sock.default_value
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    if by == "normal":                               # faces that look across the hall, whatever their place
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vt = nt.nodes.new("ShaderNodeVectorTransform")
        vt.vector_type, vt.convert_from, vt.convert_to = "NORMAL", "WORLD", "OBJECT"
        nt.links.new(geo.outputs["True Normal"], vt.inputs[0])
        nt.links.new(vt.outputs[0], sp.inputs[0])
        lo, hi, a, b = 0.5, 0.8, base, base * k
    else:                                            # the wall's face toward the hall, 15 from the middle
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], sp.inputs[0])
        lo, hi, a, b = 15.05, 15.3, base * k, base
    ab = nt.nodes.new("ShaderNodeMath")
    ab.operation = "ABSOLUTE"
    nt.links.new(sp.outputs["X"], ab.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = lo, hi
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = a, b
    nt.links.new(ab.outputs[0], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], sock)


if E("TONE_ALL"):
    k = float(E("TONE_ALL"))
    for nm in ("Temple Vault Masonry", "Temple Vault Rib Stone"):
        tone(nm, k, k, ZC, ZC + 1.0)
for env, obname, by in (("ARCH_SHINE", "Temple Arcade Arches", "normal"), ("WALL_SHINE", "Temple Aisle Walls", "place")):
    if E(env):
        o = OB[obname]
        m = o.data.materials[0]
        print(env, obname, m.name, "users", m.users, "local matrix is identity:",
              all(abs(o.matrix_local[i][j] - (1.0 if i == j else 0.0)) < 1e-5 for i in range(4) for j in range(4)), flush=True)
        if m.users > 1:                              # only this object: its own copy of the stone
            m = m.copy()
            o.data.materials[0] = m
        front_shine(m, float(E(env)), by)
bpy.context.view_layer.update()
print("BLEND OPTION", OPT, flush=True)
