"""Inside framing of the chest: the structure a real chest has behind its boards.
Run inside Blender: exec(open(PATH).read()). Safe to run again (objects are reused by name, their
mesh replaced; nothing is deleted).

Body (moves with Reveal Chest Shake): square posts in the four inside corners and a bottom and a
top rail around the walls.
Lid (moves with Reveal Lid Hinge): a rail around the lid's lower edge and two thick ribs at both
ends of the lid, against the end caps, each made of five straight pieces (owner: shaped the way a
person would actually cut wood, not a smooth curve).
Owner, 2026-11-17: ribs thicker and at the ends; no inside hinge plates, bolts or wall battens
(REMOVED below takes earlier versions of those out of the scene).

Positions are measured from the inside surfaces by ray casts, so every part sits on the wood.
Inspired by real chest construction, not copied from any game.
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

LENGTH = 5.1        # plank picture length in world units (as outside)
BOARD = 0.54        # plank picture height in world units
POST = 0.20         # corner post size
RAIL_D, RAIL_H = 0.075, 0.16   # rail depth from the wall and height
RIB_W, RIB_D = 0.28, 0.13     # lid end ribs: width along the chest, depth off the boards at the joints
RIB_PIECES = 5      # straight rib pieces, all with the same visible length (owner, 2026-11-17)
# Each rib is five equal straight pieces, the way a woodworker cuts them from straight boards: back
# trimmed to the lid's curve, front face flat, joints placed so every front face is the same length.


def equal_joints(path, inward, pieces, depth, n=600):
    """Resample the rib path evenly and place joints so the straight front faces are equal."""
    P = np.array(path, float); N = np.array(inward, float)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    t = np.linspace(0, s[-1], n)
    P2 = np.stack([np.interp(t, s, P[:, k]) for k in range(3)], 1)
    N2 = np.stack([np.interp(t, s, N[:, k]) for k in range(3)], 1)
    N2 /= np.linalg.norm(N2, axis=1)[:, None]
    F = P2 + depth * N2
    seg = np.full(pieces, s[-1] / pieces)
    for _ in range(60):
        idx = np.r_[0, np.round(np.cumsum(seg)[:-1] / s[-1] * (n - 1)).astype(int), n - 1]
        chords = np.linalg.norm(F[idx[1:]] - F[idx[:-1]], axis=1)
        seg *= chords.mean() / chords
        seg *= s[-1] / seg.sum()
    return [tuple(q) for q in P2], [tuple(q) for q in N2], sorted(set(idx.tolist())), chords
REMOVED = ("Inside Body Hinge Plates", "Inside Body Hinge Bolts", "Inside Lid Hinge Plates",
           "Inside Lid Hinge Bolts")
BOLT_R = 0.042
BEVEL = 0.012
FRAME_TONE = 0.70   # framing slightly darker than the boards

SCENE = bpy.data.scenes["Chest Reveal"]
BODY_ENV = bpy.data.objects["R Master Chest Body Envelope"]
LID_ENV = bpy.data.objects["R Lab Chest Barrel Lid Envelope"]
SHAKE = bpy.data.objects["Reveal Chest Shake"]
HINGE = bpy.data.objects["Reveal Lid Hinge"]
IRON = bpy.data.materials["Simple smoky iron pieces"]
BOLT = bpy.data.materials["Simple steel rivet"]
rng = random.Random(7)


def local_bvh(env):
    """BVH of an envelope in its parent's space (the space the new parts are built in)."""
    M = env.matrix_parent_inverse @ env.matrix_basis
    me = env.data
    return BVHTree.FromPolygons([M @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])


def hit(bvh, origin, direction):
    loc, nor, _, _ = bvh.ray_cast(Vector(origin), Vector(direction).normalized())
    if loc is None:
        raise RuntimeError(f"no surface from {origin} toward {direction}")
    return loc, nor


# ---------------- frame material ----------------
def frame_material():
    name = "Simple wood inside frame"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links
    uv = N.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    tex = {}
    for k, cs in (("albedo", "sRGB"), ("rough", "Non-Color"), ("height16", "Non-Color")):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images[f"Simple plank02_{k}.png"]
        L.new(uv.outputs[0], t.inputs[0]); tex[k] = t
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.5
    aom = N.new("ShaderNodeMath"); aom.operation = "MULTIPLY_ADD"
    L.new(ao.outputs["AO"], aom.inputs[0]); aom.inputs[1].default_value = 0.5; aom.inputs[2].default_value = 0.5
    tone = N.new("ShaderNodeMath"); tone.operation = "MULTIPLY"; tone.inputs[1].default_value = FRAME_TONE
    L.new(aom.outputs[0], tone.inputs[0])
    mul = N.new("ShaderNodeMix"); mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    L.new(tex["albedo"].outputs[0], mul.inputs[6]); L.new(tone.outputs[0], mul.inputs[7])
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    L.new(mul.outputs[2], bsdf.inputs["Base Color"])
    rb = N.new("ShaderNodeRGBToBW"); L.new(tex["rough"].outputs[0], rb.inputs[0])
    ra = N.new("ShaderNodeMath"); ra.operation = "ADD"; ra.use_clamp = True; ra.inputs[1].default_value = 0.06
    L.new(rb.outputs[0], ra.inputs[0]); L.new(ra.outputs[0], bsdf.inputs["Roughness"])
    hb = N.new("ShaderNodeRGBToBW"); L.new(tex["height16"].outputs[0], hb.inputs[0])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.02
    L.new(hb.outputs[0], bump.inputs["Height"]); L.new(bump.outputs[0], bsdf.inputs["Normal"])
    out = N.new("ShaderNodeOutputMaterial"); L.new(bsdf.outputs[0], out.inputs["Surface"])
    return mat


# ---------------- mesh builders ----------------
class Parts:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def quad(self, pts, uvs):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        for loop, t in zip(f.loops, uvs):
            loop[self.uv].uv = t
        return f

    def box(self, lo, hi):
        """Axis aligned board; grain along its longest side, random strip of the plank picture."""
        lo, hi = np.array(lo, float), np.array(hi, float)
        size = hi - lo
        long_ax = int(np.argmax(size))
        uo, vo = rng.uniform(0, 0.6), rng.uniform(0.15, 0.55)

        def uvmap(p, a, b):
            if long_ax in (a, b):
                other = b if long_ax == a else a
                return (p[long_ax] / LENGTH + uo, p[other] / BOARD + vo)
            return (p[a] / BOARD + uo, p[b] / BOARD + vo)

        c = [np.array([(lo, hi)[i >> k & 1][k] for k in range(3)]) for i in range(8)]
        faces = [((0, 2, 6, 4), 1, 2), ((1, 5, 7, 3), 1, 2), ((0, 4, 5, 1), 0, 2), ((2, 3, 7, 6), 0, 2),
                 ((0, 1, 3, 2), 0, 1), ((4, 6, 7, 5), 0, 1)]
        for idx, a, b in faces:
            self.quad([tuple(c[i]) for i in idx], [uvmap(c[i], a, b) for i in idx])

    def sweep(self, path, inward, x0, x1, depth, joints=None):
        """Rib along a path in the y z plane at x0..x1, standing `depth` off the surface. With joints
        (path indices), the front face is straight between joints (flat pieces), the back follows the
        surface."""
        P = [np.array(p, float) for p in path]
        n = [np.array(v, float) / np.linalg.norm(v) for v in inward]
        s = np.r_[0, np.cumsum([np.linalg.norm(P[i + 1] - P[i]) for i in range(len(P) - 1)])]
        uo, vo = rng.uniform(0, 0.6), rng.uniform(0.15, 0.55)
        out = [(p - 0.004 * m) for p, m in zip(P, n)]          # sunk slightly into the boards
        inn = [(p + depth * m) for p, m in zip(P, n)]
        if joints:
            for a, b in zip(joints[:-1], joints[1:]):
                A, B = inn[a], inn[b]
                for i in range(a + 1, b):
                    # where the line from P[i] along n[i] crosses the chord A B (in y z)
                    M2 = np.array([[n[i][1], -(B - A)[1]], [n[i][2], -(B - A)[2]]])
                    t, _ = np.linalg.solve(M2, (A - P[i])[1:])
                    inn[i] = P[i] + t * n[i]
        V = lambda x, q: (x, q[1], q[2])
        for i in range(len(P) - 1):
            u0, u1 = s[i] / LENGTH + uo, s[i + 1] / LENGTH + uo
            w = (x1 - x0) / BOARD
            self.quad([V(x0, inn[i]), V(x1, inn[i]), V(x1, inn[i + 1]), V(x0, inn[i + 1])],
                      [(u0, vo), (u0, vo + w), (u1, vo + w), (u1, vo)])
            d = depth / BOARD
            self.quad([V(x0, out[i]), V(x0, inn[i]), V(x0, inn[i + 1]), V(x0, out[i + 1])],
                      [(u0, vo), (u0, vo + d), (u1, vo + d), (u1, vo)])
            self.quad([V(x1, inn[i]), V(x1, out[i]), V(x1, out[i + 1]), V(x1, inn[i + 1])],
                      [(u0, vo + d), (u0, vo), (u1, vo), (u1, vo + d)])
        for i, flip in ((0, False), (len(P) - 1, True)):
            pts = [V(x0, out[i]), V(x1, out[i]), V(x1, inn[i]), V(x0, inn[i])]
            self.quad(pts[::-1] if flip else pts, [(0, 0), (0.03, 0), (0.03, 0.03), (0, 0.03)])

    def finish(self, name, parent, coll, mat, bevel=True):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-6)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        me.materials.append(mat)
        o = bpy.data.objects.get(name)
        if o is None:
            o = bpy.data.objects.new(name, me)
            coll.objects.link(o)
        else:
            old = o.data
            o.data = me
            if old.users == 0:
                bpy.data.meshes.remove(old)
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = Matrix.Identity(4)
        for m in list(o.modifiers):
            o.modifiers.remove(m)
        if bevel:
            b = o.modifiers.new("Rounded edges", "BEVEL")
            b.width, b.segments, b.limit_method = BEVEL, 2, "ANGLE"
            b.harden_normals = False
        for p in me.polygons:
            p.use_smooth = False
        return o


def bolts(name, centers, axis_dir, parent, coll):
    """Low dome bolt heads standing on a plate, domes pointing along axis_dir."""
    bm = bmesh.new()
    d = Vector(axis_dir).normalized()
    rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    for c in centers:
        geom = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=BOLT_R)
        vs = geom["verts"]
        keep = []
        for v in vs:
            v.co.z = max(v.co.z, 0.0) * 0.55
        bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ rot, verts=vs)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(BOLT)
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me); coll.objects.link(o)
    else:
        old = o.data; o.data = me
        if old.users == 0:
            bpy.data.meshes.remove(old)
    o.parent, o.matrix_parent_inverse, o.matrix_basis = parent, Matrix.Identity(4), Matrix.Identity(4)
    return o


# ---------------- measure ----------------
SCENE.frame_set(1)
bb = local_bvh(BODY_ENV)
mid_z = 1.5
X = hit(bb, (0, 0, mid_z), (1, 0, 0))[0].x            # inner end wall
Y = hit(bb, (0, 0, mid_z), (0, 1, 0))[0].y            # inner back wall (+y)
Yf = -hit(bb, (0, 0, mid_z), (0, -1, 0))[0].y         # inner front wall
FLOOR = hit(bb, (0, 0, mid_z), (0, 0, -1))[0].z
TOP = max(v.z for v in [BODY_ENV.matrix_parent_inverse @ v.co for v in BODY_ENV.data.vertices])
TOPI = TOP - 0.06                                      # framing stops below the wall top

lb = local_bvh(LID_ENV)
lid_pts = [LID_ENV.matrix_parent_inverse @ v.co for v in LID_ENV.data.vertices]
LZ0 = min(v.z for v in lid_pts)
LYC = 0.5 * (min(v.y for v in lid_pts) + max(v.y for v in lid_pts))
LX = hit(lb, (0, LYC, LZ0 + 0.1), (1, 0, 0))[0].x
LYB = hit(lb, (0, LYC, LZ0 + 0.1), (0, 1, 0))[0].y    # back side (hinge side, +y)
LYF = hit(lb, (0, LYC, LZ0 + 0.1), (0, -1, 0))[0].y

body_coll = BODY_ENV.users_collection[0]
lid_coll = LID_ENV.users_collection[0]
FRAME = frame_material()
made = []

# ---------------- body framing ----------------
p = Parts()
for sx in (-1, 1):
    for sy in (-1, 1):
        wy = Y if sy > 0 else Yf
        xa, xb = sorted((sx * X, sx * (X - POST)))
        ya, yb = sorted((sy * wy, sy * (wy - POST)))
        p.box((xa, ya, FLOOR), (xb, yb, TOPI))
xin = X - POST
for z0 in (FLOOR, TOPI - RAIL_H):                      # bottom and top rails between the posts
    z1 = z0 + RAIL_H
    p.box((-xin, Y - RAIL_D, z0), (xin, Y, z1))
    p.box((-xin, -Yf, z0), (xin, -Yf + RAIL_D, z1))
    p.box((X - RAIL_D, -Y + POST, z0), (X, Y - POST, z1))
    p.box((-X, -Yf + POST, z0), (-X + RAIL_D, Y - POST, z1))
made.append(p.finish("Inside Body Frame", SHAKE, body_coll, FRAME).name)

# ---------------- lid framing ----------------
p = Parts()
z0, z1 = LZ0 + 0.004, LZ0 + 0.004 + RAIL_H
p.box((-LX, LYB - RAIL_D, z0), (LX, LYB, z1))
p.box((-LX, LYF, z0), (LX, LYF + RAIL_D, z1))
p.box((LX - RAIL_D, LYF + RAIL_D, z0), (LX, LYB - RAIL_D, z1))
p.box((-LX, LYF + RAIL_D, z0), (-LX + RAIL_D, LYB - RAIL_D, z1))
# arch ribs: ray cast the inner surface from the arch centre, from rail top to rail top
c_y = LYC
c_z = z1 + 0.05
for sx in (-1, 1):
    x_mid = sx * (LX - RIB_W / 2 - 0.001)              # against the end cap
    path, inward = [], []
    for k in range(73):
        th = math.radians(-100 + 200 * k / 72)
        d = (0, math.sin(th), math.cos(th))
        loc, nor, _, _ = lb.ray_cast(Vector((x_mid, c_y, c_z)), Vector(d))
        if loc is None or loc.z < z1:
            continue
        if nor.dot(Vector((x_mid, c_y, c_z)) - loc) < 0:
            nor = -nor
        nor = Vector((0, nor.y, nor.z)).normalized()
        path.append((x_mid, loc.y, loc.z)); inward.append(tuple(nor))
    # extend both ends straight down the side walls to the rail top
    for end in (0, -1):
        q = path[end]; m = inward[end]
        if q[2] > z1 + 0.01:
            pt = (x_mid, q[1], z1)
            if end == 0:
                path.insert(0, pt); inward.insert(0, m)
            else:
                path.append(pt); inward.append(m)
    path, inward, joints, chords = equal_joints(path, inward, RIB_PIECES, RIB_D)
    RIB_CHORDS = [round(float(c), 3) for c in chords]
    p.sweep(path, inward, x_mid - RIB_W / 2, x_mid + RIB_W / 2, RIB_D, joints)
made.append(p.finish("Inside Lid Frame", HINGE, lid_coll, FRAME).name)

for name in REMOVED:                                   # unlink only, nothing is deleted
    o = bpy.data.objects.get(name)
    if o is not None:
        for c in list(o.users_collection):
            c.objects.unlink(o)

INSIDE_FRAME = dict(made=made, body=dict(X=X, Y=Y, Yf=Yf, FLOOR=FLOOR, TOP=TOP),
                    lid=dict(LX=LX, LYB=LYB, LYF=LYF, LZ0=LZ0, LYC=LYC), rib_faces=RIB_CHORDS)
print("inside frame", INSIDE_FRAME)
