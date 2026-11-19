"""Version 7: side ring hinges that can really swing (owner, 2026-11-18: the right ring did not look like
real physics; both rings must be real physics).

Cause: each ring's top bar sat in a rolled cover whose outer sleeves droop to follow the ring's
round top, so any swing past about 15 degrees ran the ring into the cover. The simulated ring spent
most of the landing pressed against that stop, which on the right side read as a ring glued on at
an angle.

Fix, on copies of the meshes (the source chest's meshes are untouched):
- Cover: the straight middle part with its beaded collars is kept (|y| <= CUT); the two drooping
  outer sleeves are trimmed off and the cut barrel ends closed. A short straight hinge barrel.
- Ring: its top is eased up (at most 0.05 units, about 6 mm) so the part inside the barrel is centred on the
  barrel's axis, blending back into the original round ring by BLEND.
- Pivot: moved up AX onto the barrel's axis; the ring keeps its place (parent inverse compensated).
Then a ring turning about the pivot never touches its barrel (checked 0 to 170 degrees; at 180 it
meets the rivets above). Run inside Blender; safe to run again. Then rebake the swing with
anim_rings.py and RING_OUTER_DEG = 170, RING_START_STILL = True, RING_PIVOT_UP = 0.026,
RING_F_END = 150 (the toss spun the chest, not the loose rings).

Coordinates: each ring's pivot frame at the old pivot (chest axes: x out of the end wall for R,
y along the chest's depth, z up)."""
import bpy, bmesh, math
from mathutils import Matrix, Vector

AX = 0.026               # barrel axis above the old pivot
CUT = 0.172              # keep the barrel for |y| <= CUT (beaded collars at 0.115 to 0.165)
ZC, RM = -0.481, 0.5017  # ring centre height and centreline radius in the pivot frame (tube radius 0.111)
BORE = 0.119             # barrel bore radius after the fix (ring tube 0.111 to 0.115)
FLAT, BLEND = 0.18, 0.37 # ring centreline on the axis within FLAT, eased back to the round ring by BLEND


def smooth_down(a):
    if a <= FLAT:
        return 1.0
    if a >= BLEND:
        return 0.0
    t = (a - FLAT) / (BLEND - FLAT)
    return 1.0 - t * t * (3 - 2 * t)


def fix_side(side, num):
    piv = bpy.data.objects["Reveal Ring Pivot " + side]
    ring = bpy.data.objects[f"R Lab Chest Solid Ring Handle {num}"]
    cover = bpy.data.objects[f"R Lab Chest Measured Rolled Handle Cover {num}"]
    moved = piv.get("v7_axis", 0.0)
    old_loc = piv.location - Vector((0, 0, moved))

    # ---- ring
    src = bpy.data.meshes[ring.get("v7_src", ring.data.name)]
    ring["v7_src"] = src.name
    Mr = Matrix.Translation((0, 0, moved)) @ ring.matrix_parent_inverse @ ring.matrix_basis
    Mri = Mr.inverted()
    me = bpy.data.meshes.get(src.name + " v7 hinge") or src.copy()
    me.name = src.name + " v7 hinge"
    shift_max = 0.0
    for v, v0 in zip(me.vertices, src.vertices):
        q = Mr @ v0.co
        if q.z > ZC:
            yc = RM * math.sin(math.atan2(q.y, q.z - ZC))
            d = AX - (ZC + math.sqrt(max(RM * RM - yc * yc, 0.0)))
            dz = d * smooth_down(abs(yc))
            q.z += dz
            shift_max = max(shift_max, dz)
        v.co = Mri @ q
    me.update()
    ring.data = me

    # ---- cover
    csrc = bpy.data.meshes[cover.get("v7_src", cover.data.name)]
    cover["v7_src"] = csrc.name
    Mc = Matrix.Translation(-old_loc) @ cover.matrix_parent_inverse @ cover.matrix_basis
    bm = bmesh.new()
    bm.from_mesh(csrc)
    bm.transform(Mc)
    for sgn in (1, -1):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, sgn * CUT, 0), plane_no=(0, sgn, 0), clear_outer=True)
    # close the cut ends: boundary loops at each end (outer and inner wall of the barrel)
    caps = 0
    for sgn in (1, -1):
        edges = [e for e in bm.edges if e.is_boundary and all(abs(v.co.y - sgn * CUT) < 1e-4 for v in e.verts)]
        if not edges:
            continue
        # flat fill that keeps the bore open (handles a C shaped wall or an outer plus inner loop)
        out = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=(0, sgn, 0))
        caps += len(out["geom"])
    open_edges = sum(1 for e in bm.edges if e.is_boundary)
    # the collar lips inside the barrel hugged the old drooping ring: open the bore to BORE everywhere
    # (inside faces only, not visible); relative to the new axis
    for v in bm.verts:
        x, z = v.co.x, v.co.z - AX
        r = math.hypot(x, z)
        if 1e-6 < r < BORE:
            v.co.x, v.co.z = x * BORE / r, AX + z * BORE / r
    bm.transform(Mc.inverted())
    cme = bpy.data.meshes.get(csrc.name + " v7 hinge") or bpy.data.meshes.new(csrc.name + " v7 hinge")
    bm.to_mesh(cme)
    bm.free()
    # the stored custom normals no longer match the trimmed and opened cover (it shaded pale): let
    # Blender shade it from its shape, smooth across the round barrel, sharp at the collars' edges
    if "custom_normal" in cme.attributes:
        cme.attributes.remove(cme.attributes["custom_normal"])
    cme.set_sharp_from_angle(angle=math.radians(40))
    cme.materials.clear()
    for m in csrc.materials:
        cme.materials.append(m)
    cover.data = cme
    # the chest's look is set per object (simple style): swapping the mesh reset the slot to the
    # mesh's plain default, so put the object materials back
    for o, mname in ((cover, "Simple smoky iron pieces"), (ring, "Simple brass ring")):
        slot = o.material_slots[0]
        slot.link = "OBJECT"
        slot.material = bpy.data.materials[mname]

    # ---- pivot onto the barrel axis, ring stays put
    if not moved:
        piv.location.z += AX
        ring.matrix_parent_inverse = Matrix.Translation((0, 0, -AX)) @ ring.matrix_parent_inverse
        piv["v7_axis"] = AX
    return dict(ring_shift_max=round(shift_max, 4), caps=caps, open_edges=open_edges)


V7_RINGS = {side: fix_side(side, num) for side, num in (("L", "-1"), ("R", "1"))}
print("v7 rings", V7_RINGS)
