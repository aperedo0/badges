"""Version 15: a wider hall (owner, 2026-11-23, pointing at a frame of the Codex Temple Fire video).

Run inside Claude_Temple_Wide.blend (a copy of Codex_Temple_Fire.blend, which stays untouched); safe to run
again; no object is deleted (objects are reused by name and get new mesh data, the meshes they had are kept
under their old name plus " (before v15)").

What the owner asked for, in their words:
1. "the top, the oval shape ... I want you to extend it. So it should be about overall 50% wider. So the building
   is 50% wider." The ceiling over the front hall was half a circle, 15 across from the middle. It is now half an
   ellipse, 22.5 across from the middle and as high as before.
2. "It should have 1 or 2 holes where light comes through. Don't change that at all." The two broken openings are
   cut again with the same two plugs (Temple Vault Hole L and R), so they have the same outline at the same place
   on the floor plan, and the shafts of light, their plates and the night sky above are not touched.
3. "these like things on the inside that look like they support the ceiling ... When you extend the ceiling,
   you're going to extend those as well ... the ends of those aren't going to be in view." The four ribs follow the
   wider ceiling, so their feet stand outside the picture.
4. "I want them to be half their height. Not width ... closer to the ceiling." The ribs stood 1.4 out of the
   ceiling; now 0.7. Their width along the hall (1.8, and 1.9 for the last one) is the same.
5. "on top of the pillar there are these arches. You're gonna remove the arches." The arches from pillar to pillar
   along each side (Temple Arcade Arches) are switched off, and the wall slab that stood on them and carried the
   old ceiling (two loose blocks inside Temple Aisle Walls) is taken out of that mesh: it would stand in the
   middle of the wider ceiling otherwise. For the same reason the flat ceiling over each side aisle, which ran
   in to that slab's outer face (19.4 from the middle), now starts where the wider ceiling comes down (22.5).

The stone pattern of the ceiling and the ribs was laid out by the angle around the old circle. On an ellipse that
would squeeze and stretch the stones, so both meshes carry a number at every point, "arc" (how far round the
ceiling the point is, in units along the curve), and the two materials read it in place of the angle. The stones
keep their old size: courses 2.3 high on the ceiling, rib stones about 1.66 long (35 where there were 27).

Nothing else is changed: no light, no fog, no pillar, no wall, no camera, no timing. One unseen object is added,
Temple Wide Light Blockers, so that the light on the floor stays as it was (see the last part of the script).

    blender -b Claude_Temple_Wide.blend --python tools/v15_wide_vault.py --python tools/v12_render.py   (test, saves nothing)
V15_KEEP_ARCHES=1 leaves the arches and their wall as they are (to look at the ceiling change alone)."""
import bpy, bmesh, math, os
import numpy as np

E = os.environ.get
OB, MATS = bpy.data.objects, bpy.data.materials
ZC, R_OLD, THICK = 46.0, 15.0, 1.6                  # the old ceiling: axis height, inside radius, thickness
WIDE = float(E("V15_WIDE", "1.5"))
A, B = R_OLD * WIDE, R_OLD                           # half width and height of the new ceiling's inside
Y0, Y1 = 10.0, 89.5
RIB_Y = ((17.1, 18.9), (28.9, 30.7), (40.7, 42.5), (54.2, 56.1))
RIB_OUT, RIB_IN = 1.4 * float(E("V15_RIB", "0.5")), 0.3   # how far a rib stands out of the ceiling, and sits in it
ROW_H, RIB_STONE = 2.3, math.pi * 14.3 / 27.0        # the old stone sizes
KEPT = " (before v15)"

# ------------------------------------------------------------------ the curve, measured along its length
N_T = 8001
TT = np.linspace(0.0, math.pi, N_T)
EX, EZ = A * np.cos(TT), B * np.sin(TT)
SS = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(EX), np.diff(EZ)))])
S = float(SS[-1])                                    # from one foot of the ceiling to the other


def even(n):
    """n + 1 places on the curve, evenly spaced along it."""
    return np.interp(np.linspace(0.0, S, n + 1), SS, TT)


def arc_of(x, z):
    """How far round the curve the nearest point of the curve is, for points given as arrays (z above the axis)."""
    out = np.empty(len(x))
    for a in range(0, len(x), 400):
        px, pz = x[a:a + 400, None], z[a:a + 400, None]
        k = np.argmin((px - EX[None, :]) ** 2 + (pz - EZ[None, :]) ** 2, axis=1)
        best_d, best_s = np.full(len(k), 1e30), np.zeros(len(k))
        for k0 in (np.clip(k - 1, 0, N_T - 2), np.clip(k, 0, N_T - 2)):       # the two pieces of curve next to it
            ax, az, bx, bz = EX[k0], EZ[k0], EX[k0 + 1], EZ[k0 + 1]
            ux, uz = bx - ax, bz - az
            w = np.clip(((px[:, 0] - ax) * ux + (pz[:, 0] - az) * uz) / (ux * ux + uz * uz), 0.0, 1.0)
            d = (px[:, 0] - ax - w * ux) ** 2 + (pz[:, 0] - az - w * uz) ** 2
            s = SS[k0] + w * (SS[k0 + 1] - SS[k0])
            best_s = np.where(d < best_d, s, best_s)
            best_d = np.minimum(d, best_d)
        out[a:a + 400] = best_s
    return out


def set_arc(me):
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3).astype(np.float64)
    at = me.attributes.get("arc") or me.attributes.new("arc", "FLOAT", "POINT")
    at.data.foreach_set("value", arc_of(co[:, 0], co[:, 2] - ZC).astype(np.float32))
    me.update()


def keep(me):
    """Keep the mesh an object had, once, under its old name plus KEPT."""
    if me.name.endswith(KEPT) or me.get("v15"):
        return
    me.name = me.name + KEPT
    me.use_fake_user = True


def smooth(me, deg):
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(deg))
    me.update()


def recalc(V, F):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = [tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return out


# ------------------------------------------------------------------ 1 and 2. the ceiling, with the same two openings
vault = OB["Temple Vault"]
vmat = MATS["Temple Vault Masonry"]
cutters = [OB["Temple Vault Hole L"], OB["Temple Vault Hole R"]]
was_hidden = [c.hide_viewport for c in cutters]
for c in cutters:
    c.hide_viewport = False                          # the boolean reads them
bpy.context.view_layer.update()
for c in cutters:
    M = vault.matrix_world.inverted() @ c.matrix_world
    assert all(abs(M[i][j] - (1.0 if i == j else 0.0)) < 1e-4 for i in range(4) for j in range(4)), "the plug %s does not sit in the ceiling's own space" % c.name

NV = int(round(72 * S / (math.pi * R_OLD)))          # the same size of face as before
NY = 132
ts = even(NV)
V, F = [], []
for j in range(NY + 1):
    y = Y0 + (Y1 - Y0) * j / NY
    for i in range(NV + 1):
        V.append((A * math.cos(ts[i]), y, ZC + B * math.sin(ts[i])))
for j in range(NY):
    for i in range(NV):
        a = j * (NV + 1) + i
        F.append((a, a + 1, a + NV + 2, a + NV + 1))  # facing down into the hall
shell = bpy.data.meshes.new("Temple Vault shell")
shell.from_pydata(V, [], F)
shell.materials.append(vmat)
shell.update()
old = vault.data
vault.data = shell
keep(old)
vault.modifiers.clear()
sm = vault.modifiers.new("Thickness", "SOLIDIFY")
sm.thickness = THICK
sm.offset = -1.0                                     # grows away from the hall
sm.use_even_offset = True
for c in cutters:
    bo = vault.modifiers.new("Hole " + c.name[-1], "BOOLEAN")
    bo.operation = "DIFFERENCE"
    bo.solver = "EXACT"
    bo.object = c
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
baked = bpy.data.meshes.new_from_object(vault.evaluated_get(dg))
vault.modifiers.clear()
baked.name = "Temple Vault wide"
baked["v15"] = 1
smooth(baked, 40)
set_arc(baked)
vault.data = baked
# the plugs have no material: the boolean gives the openings' inside faces an empty second slot. One stone for all.
baked.polygons.foreach_set("material_index", [0] * len(baked.polygons))
while len(baked.materials) > 1:
    baked.materials.pop(index=len(baked.materials) - 1)
if len(baked.materials) == 0:
    baked.materials.append(vmat)
baked.update()
bpy.data.meshes.remove(shell)
for c, h in zip(cutters, was_hidden):
    c.hide_viewport = h

# ------------------------------------------------------------------ 3 and 4. the ribs: on the wider curve, half as deep
ribs = OB["Temple Vault Ribs"]
rmat = MATS["Temple Vault Rib Stone"]
tr = even(NV)
V, F = [], []
for y0, y1 in RIB_Y:
    o_ = len(V)
    for i in range(NV + 1):
        c, s_ = math.cos(tr[i]), math.sin(tr[i])
        nx, nz = B * c, A * s_                       # straight out of the curve
        L = math.hypot(nx, nz)
        nx, nz = nx / L, nz / L
        for d, y in ((-RIB_OUT, y0), (RIB_IN, y0), (RIB_IN, y1), (-RIB_OUT, y1)):
            V.append((A * c + d * nx, y, ZC + B * s_ + d * nz))
    for i in range(NV):
        for q in range(4):
            a, b = o_ + 4 * i + q, o_ + 4 * i + (q + 1) % 4
            F.append((a, b, b + 4, a + 4))
    F.append((o_, o_ + 1, o_ + 2, o_ + 3))
    F.append((o_ + 4 * NV + 3, o_ + 4 * NV + 2, o_ + 4 * NV + 1, o_ + 4 * NV))
V, F = recalc(V, F)
rm = bpy.data.meshes.new("Temple Vault Ribs wide")
rm.from_pydata(V, [], F)
rm.materials.append(rmat)
rm["v15"] = 1
smooth(rm, 30)
set_arc(rm)
old = ribs.data
ribs.data = rm
keep(old)

# ------------------------------------------------------------------ the stone patterns follow the curve's length
def arc_node(nt):
    n = nt.nodes.get("v15 arc")
    if n is None:
        n = nt.nodes.new("ShaderNodeAttribute")
        n.name = n.label = "v15 arc"
        n.attribute_type = "GEOMETRY"
        n.attribute_name = "arc"
    return n


def angle_user(nt):
    """The node the old angle (or, on a second run, the arc) goes into."""
    for n in nt.nodes:
        if n.type == "MATH" and n.operation == "ARCTAN2" and n.outputs[0].links:
            return n.outputs[0].links[0].to_node, n
    a = nt.nodes["v15 arc"]
    return a.outputs["Fac"].links[0].to_node, None


# the ceiling: courses were (angle x 15) high up the curve; now the length along the curve itself
nt = vmat.node_tree
mul, atan = angle_user(nt)
an = arc_node(nt)
if atan is not None:
    an.location = (atan.location.x, atan.location.y - 180)
nt.links.new(an.outputs["Fac"], mul.inputs[0])
mul.inputs[1].default_value = 1.0
# the ribs: 27 stones round the half circle; now as many of the same length as fit the longer curve (odd, for a keystone)
S_MID = S - math.pi * RIB_OUT / 2.0                  # along the middle of the rib's visible side
n_st = int(round(S_MID / RIB_STONE))
n_st += 1 - n_st % 2
nt = rmat.node_tree
mul, atan = angle_user(nt)
an = arc_node(nt)
if atan is not None:
    an.location = (atan.location.x, atan.location.y - 180)
nt.links.new(an.outputs["Fac"], mul.inputs[0])
mul.inputs[1].default_value = n_st / S               # stones counted along the curve
wid = nt.nodes.get("v15 stone length")
if wid is None:
    sq = next(n for n in nt.nodes if n.type == "MATH" and n.operation == "SQRT")
    wid = sq.outputs[0].links[0].to_node             # was: distance from the axis x (pi / 27) = one stone's length
    wid.name = wid.label = "v15 stone length"
    nt.links.remove(wid.inputs[0].links[0])
wid.inputs[0].default_value = S_MID / n_st
wid.inputs[1].default_value = 1.0

# ------------------------------------------------------------------ 5. the arches on the pillars
done = {"wide": WIDE, "half_width": A, "curve_length": round(S, 2), "faces_round": NV, "ceiling_polys": len(baked.polygons),
        "rib_stones": n_st, "rib_out": RIB_OUT}
if E("V15_KEEP_ARCHES") != "1":
    arc = OB["Temple Arcade Arches"]
    arc.hide_render = True
    arc.hide_viewport = True
    aisle = OB["Temple Aisle Walls"]
    M = vault.matrix_world.inverted() @ aisle.matrix_world
    assert all(abs(M[i][j] - (1.0 if i == j else 0.0)) < 1e-4 for i in range(4) for j in range(4)), "the side walls do not sit in the ceiling's own space"
    if not aisle.data.get("v15"):
        old = aisle.data
        new = old.copy()
        new.name = "Temple Aisle Walls wide"
        new["v15"] = 1
        bm = bmesh.new()
        bm.from_mesh(new)
        seen, gone, blocks = set(), [], 0
        for v0 in bm.verts:
            if v0 in seen:
                continue
            part, todo = [], [v0]
            seen.add(v0)
            while todo:
                v = todo.pop()
                part.append(v)
                for e in v.link_edges:
                    w = e.other_vert(v)
                    if w not in seen:
                        seen.add(w)
                        todo.append(w)
            ax = [abs(v.co.x) for v in part]
            # the slab on top of the arches: 15 to 19.4 from the middle, from the pillar tops (28.4) up to 62
            if min(ax) > 14.9 and max(ax) < 19.5 and min(v.co.z for v in part) > 28.3:
                gone += part
                blocks += 1
        assert blocks == 2, "expected the two slabs over the arches, found %d" % blocks
        bmesh.ops.delete(bm, geom=gone, context="VERTS")
        # The flat ceiling over each side aisle ran in to 19.4, where the slab's outer face was. Left there, its
        # edge is a ledge inside the wider ceiling (a dark wedge in both top corners of the picture). It now
        # starts where the wider ceiling comes down.
        moved = 0
        for v in bm.verts:
            if 19.3 < abs(v.co.x) < 19.5 and 45.9 < v.co.z < 47.6:
                v.co.x = math.copysign(A, v.co.x)
                moved += 1
        assert moved == 8, "expected the 8 corners of the two aisle ceilings' inner edges, found %d" % moved
        bm.to_mesh(new)
        bm.free()
        new.update()
        aisle.data = new
        keep(old)
        done["slab_blocks_removed"] = blocks
    # ---------------------------------------------------------------- the light stays as it was
    # The ceiling throws no shadows (so the beam and the shafts pass it), which made the slab over the arches and
    # the aisle ceilings the hall's real roof against the room's ambient light (the world, which casts shadows).
    # Taking them away let that light in: the floor in front came out 5 to 7 of 255 brighter in the test. So what
    # was taken away still keeps the light out, from outside the new ceiling where it is never seen and never
    # stands between a light in the hall and the ceiling: a skin on the ceiling's back from its foot up to where
    # the old slab stood (15 from the middle), and the slab's top part above that, up to its old top (62).
    if E("V15_BLOCK", "roof") == "roof":
        d = THICK + 0.05
        prof = []
        for t in even(NV):
            c, s_ = math.cos(t), math.sin(t)
            nx, nz = B * c, A * s_
            L = math.hypot(nx, nz)
            prof.append((A * c + d * nx / L, ZC + B * s_ + d * nz / L))
        V, F = [], []

        def height(x):                                # the skin's height at x (right hand side)
            pts = sorted(p for p in prof if p[0] >= 0)
            return float(np.interp(x, [p[0] for p in pts], [p[1] for p in pts]))

        for sign in (1.0, -1.0):
            side = [(x, z) for x, z in prof if x * sign >= 15.0]
            side.append((sign * 15.0, height(15.0)))
            side.sort(key=lambda p: p[1])
            o_ = len(V)
            for x, z in side:
                V += [(x, Y0, z), (x, Y1, z)]
            for i in range(len(side) - 1):
                a = o_ + 2 * i
                F.append((a, a + 1, a + 3, a + 2))
            o_ = len(V)
            sec = [(sign * 15.0, height(15.0)), (sign * 19.4, height(19.4)), (sign * 19.4, 62.0), (sign * 15.0, 62.0)]
            for y in (12.0, 91.0):
                V += [(x, y, z) for x, z in sec]
            F += [(o_, o_ + 1, o_ + 2, o_ + 3), (o_ + 7, o_ + 6, o_ + 5, o_ + 4)]
            F += [(o_ + q, o_ + (q + 1) % 4, o_ + 4 + (q + 1) % 4, o_ + 4 + q) for q in range(4)]
        name = "Temple Wide Light Blockers"
        pm = bpy.data.meshes.new(name)
        pm.from_pydata(V, [], F)
        pm.update()
        ph = OB.get(name)
        if ph is None:
            ph = bpy.data.objects.new(name, pm)
            bpy.data.collections["Reveal Temple"].objects.link(ph)
        else:
            was = ph.data
            ph.data = pm
            bpy.data.meshes.remove(was)
        ph.parent = aisle.parent
        ph.matrix_parent_inverse = aisle.matrix_parent_inverse.copy()
        ph.visible_camera = False
        ph.visible_shadow = True
        ph.hide_render = False
        ph.display_type = "WIRE"
        ph.hide_viewport = True                       # renders still use it
        done["blockers"] = len(F)
bpy.context.view_layer.update()
print("V15 DONE", done, flush=True)
result = done
