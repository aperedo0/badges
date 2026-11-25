"""Version 20: the left shaft of night light gets an opening of its own, in the picture (owner, 2026-11-25).

Run inside Claude_Temple_Ceiling.blend; safe to run again (every run starts over from what was there before the
first run); no object is deleted. The meshes that change are kept as "<object> (before v20)", and V20_UNDO=1 puts
everything back as it was.

The owner, with a phone picture of the waiting screen: "the light on the right ... interesting shape in the sense
that it's not a circle, it's not a square. I want something similar on the left, and also the left light is too
big. And make sure that when the sand comes down, it only shows in the area where the light shines ... for some
reason it became like thicker or something". Shown the left light made smaller where it was, and moved back so its
opening shows like the right one, they answered: "I want it to be on the left and a little before or after in z
space, but I want a different but similar shape for the light, so similar but different shape in the roof opening".

Why the left light was big and had no shape. Its opening in the ceiling was wider than the right one (8.9 against
6.6 across the hall), nearer the camera (hall y 36 against 47), and so high in the view that the opening itself
was above the top of the picture for the whole video; its light ran off the picture's left edge. Only a wide band
of light showed. (Version 17 then made that band even from side to side for the whole video, which read thicker.)

What this does, all on the left side:
1. A new outline for the opening, drawn the same way as the two first ones (tools/v12_hall.py: thirteen corners
   round a centre, uneven, longer across the hall than along it, straight edges) but from its own roll of the dice
   (V20_SEED), at the right opening's size (V20_SIZE 2.7; the left was 3.0).
2. It sits at hall (V20_X, V20_Y): on the left, in the same stretch of ceiling as the right opening (between the
   rib at 40.7 to 42.5 and the arch at 54.2 to 56.1) and a little farther from the camera than it (the right one
   is at y 47), so the two do not line up.
3. The plate that gives the light its shape (Temple Shaft Mask L) takes that outline, and the light (Temple Shaft
   L) moves over it, standing 1 in front of the centre as before. Strength, colour, cone, softness and the steady
   shadow level of version 17 are not touched.
4. The ceiling (Temple Vault) gets that opening cut through it, with the same stone and the same edge treatment as
   the right opening, so the night sky shows through. The plug that cuts it (Temple Vault Hole L) takes the new
   outline too. The old left opening stays in the ceiling: it is above the top of the picture for the whole
   video, and the ceiling throws no shadows, so no light comes through it any more.
5. The falling sand on the left (Temple Dust Cloud L) moves with the light and narrows by the same amount as the
   opening (0.9). The sand is only ever lit by its own shaft; its look and timing are not touched.

Nothing on the right side changes, and no material, camera, fog or timing.

    V20 test, saves nothing:  blender -b <file> --python tools/v20_left_shaft.py --python tools/v12_render.py
V20_X (-11.0), V20_Y (50.5) place it, V20_SIZE (2.7) sizes it, V20_SEED (126) picks the outline, V20_UNDO=1 undoes."""
import bpy, bmesh, math, os, random

E = os.environ.get
OB, ME = bpy.data.objects, bpy.data.meshes
X, Y = float(E("V20_X", "-11.0")), float(E("V20_Y", "50.5"))
SIZE = float(E("V20_SIZE", "2.7"))
SEED = int(E("V20_SEED", "126"))
UNDO = E("V20_UNDO") == "1"
OLD_SIZE = 3.0                                       # the left opening's size in tools/v12_hall.py
BAY = (42.5, 54.2)                                   # the stretch of ceiling between the rib and the arch (v16)
RIM = 8.5                                            # the plate's outer edge, round the opening's centre
KEEP, TAG = " (before v20)", "v20 before"
root = OB["Temple Root"]
light, mask, cutter, vault, sand = (OB[n] for n in ("Temple Shaft L", "Temple Shaft Mask L", "Temple Vault Hole L",
                                                    "Temple Vault", "Temple Dust Cloud L"))
for o in (light, mask, cutter, vault, sand):
    assert o.parent == root, o.name + " does not hang on Temple Root"
assert not vault.modifiers, "the ceiling has modifiers; its openings are expected to be part of its mesh"


def P(*a):
    print("V20", *a, flush=True)


def kept(o):
    return ME.get(o.name + KEEP)


def put_back():
    """everything as it was before the first run; True if there was anything to put back"""
    did = False
    for o in (mask, cutter, vault):
        old = kept(o)
        if old is not None and o.data != old:
            new, o.data = o.data, old
            if new.users == 0:
                ME.remove(new)
            did = True
    if TAG in light:
        light.location.x, light.location.y = light[TAG]
        did = True
    if TAG in sand:
        sand.location.x, sand.location.y, sand.scale.x, sand.scale.y = sand[TAG]
        did = True
    return did


def forget():
    """after an undo: the kept meshes get their names back and the notes go"""
    for o in (mask, cutter, vault):
        old = kept(o)
        if old is not None:
            old.name = old["v20 name"]
            del old["v20 name"]
            old.use_fake_user = False
    for o in (light, sand):
        if TAG in o:
            del o[TAG]


def keep(o):
    """the mesh the object has now, kept under '<object> (before v20)'; returns it and the name a new one takes"""
    old = kept(o)
    if old is None:
        old = o.data
        old["v20 name"] = old.name
        old.name = o.name + KEEP
        old.use_fake_user = True
    return old, old["v20 name"]


def outline(seed, cx, cy, r0):
    """a broken outline where stones fell out of the ceiling: the recipe of tools/v12_hall.py, its own dice"""
    rng = random.Random(seed)
    nc = 13
    turn = math.radians(rng.uniform(-35, 35))
    corners = []
    for k in range(nc):
        a = 2 * math.pi * (k + rng.uniform(-0.28, 0.28)) / nc
        r = r0 * rng.uniform(0.62, 1.22)
        u, v = 1.25 * r * math.cos(a), 0.88 * r * math.sin(a)
        corners.append((cx + u * math.cos(turn) - v * math.sin(turn), cy + u * math.sin(turn) + v * math.cos(turn)))
    ring = []
    for k in range(nc):                              # four points along every straight edge
        (x0, y0), (x1, y1) = corners[k], corners[(k + 1) % nc]
        ring += [(x0 + (x1 - x0) * t / 4.0, y0 + (y1 - y0) * t / 4.0) for t in range(4)]
    return ring


def on_ring(x, y, ring, tol=2e-3):
    for i in range(len(ring)):
        (x0, y0), (x1, y1) = ring[i], ring[(i + 1) % len(ring)]
        ex, ey = x1 - x0, y1 - y0
        t = min(max(((x - x0) * ex + (y - y0) * ey) / (ex * ex + ey * ey), 0.0), 1.0)
        if math.hypot(x - x0 - t * ex, y - y0 - t * ey) < tol:
            return True
    return False


def new_mask(ring):
    old, name = keep(mask)
    n = len(ring)
    assert len(old.vertices) == 2 * n and len(old.polygons) == n, "the plate is not built the way v12_hall.py builds it"
    z = old.vertices[0].co.z
    me = old.copy()
    me.name = name
    me.use_fake_user = False
    for k in ("v20 name",):
        if k in me:
            del me[k]
    for i, (x, y) in enumerate(ring):
        me.vertices[i].co = (x, y, z)
        d = math.hypot(x - X, y - Y)
        me.vertices[n + i].co = (X + (x - X) * RIM / d, Y + (y - Y) * RIM / d, z)
    me.update()
    mask.data = me


def new_cutter(ring):
    old, name = keep(cutter)
    zs = [v.co.z for v in old.vertices]
    z0, z1 = min(zs), max(zs)
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in ring]
    hi = [bm.verts.new((x, y, z1)) for x, y in ring]
    n = len(ring)
    bm.faces.new(lo)
    bm.faces.new(hi)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = ME.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in old.materials:
        me.materials.append(m)
    cutter.data = me


def cut_ceiling(ring):
    old, name = keep(vault)
    vault.data = old
    hidden = cutter.hide_viewport
    cutter.hide_viewport = False                     # the cut reads it
    md = vault.modifiers.new("v20 hole", "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.solver = "EXACT"
    md.object = cutter
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = ME.new_from_object(vault.evaluated_get(dg))
    vault.modifiers.remove(md)
    cutter.hide_viewport = hidden
    assert len(me.vertices) != len(old.vertices), "the cut took nothing out of the ceiling"
    # The cut's own faces are the ceiling's stone, smooth, with a hard edge only where two faces meet at more than
    # 40 degrees: what v12_hall.py gave the first two openings. Every other edge of the ceiling keeps what it had.
    bm = bmesh.new()
    bm.from_mesh(me)
    sharp0 = sum(1 for e in bm.edges if not e.smooth)
    mine = hard = 0
    for f in bm.faces:
        f.smooth = True
        f.material_index = 0
    for e in bm.edges:
        if len(e.link_faces) == 2 and all(on_ring(v.co.x, v.co.y, ring) for v in e.verts):
            mine += 1
            e.smooth = e.calc_face_angle() <= math.radians(40)
            hard += not e.smooth
    bm.to_mesh(me)
    bm.free()
    while len(me.materials) > len(old.materials):
        me.materials.pop(index=len(me.materials) - 1)
    me.update()
    me.name = name
    vault.data = me
    sharp_old = sum(1 for e in old.edges if e.use_edge_sharp)
    return (len(old.vertices), len(old.polygons), sharp_old), (len(me.vertices), len(me.polygons), sharp0, mine, hard)


had = put_back()
if UNDO:
    forget()
    bpy.context.view_layer.update()
    P("undone:" if had else "nothing to undo:", "left opening, its light and its sand are as before version 20")
else:
    ring = outline(SEED, X, Y, SIZE)
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    assert BAY[0] + 0.3 <= min(ys) and max(ys) <= BAY[1] - 0.3, "the opening would run into a rib: y %.2f to %.2f" % (min(ys), max(ys))
    assert max(math.hypot(x - X, y - Y) for x, y in ring) < RIM - 1.0
    if TAG not in light:
        light[TAG] = [light.location.x, light.location.y]
    if TAG not in sand:
        sand[TAG] = [sand.location.x, sand.location.y, sand.scale.x, sand.scale.y]
    was = (round(light.location.x, 2), round(light.location.y + 1.0, 2))
    new_mask(ring)
    new_cutter(ring)
    before, after = cut_ceiling(ring)
    light.location.x, light.location.y = X, Y - 1.0  # it stands 1 in front of the opening's centre, as before
    k = SIZE / OLD_SIZE
    sand.location.x, sand.location.y = X, Y
    sand.scale.x, sand.scale.y = sand[TAG][2] * k, sand[TAG][3] * k
    bpy.context.view_layer.update()
    P("left opening: centre", was, "->", (X, Y), "outline", SEED, "size", SIZE,
      "| across %.2f (x %.2f to %.2f), along %.2f (y %.2f to %.2f)" % (max(xs) - min(xs), min(xs), max(xs), max(ys) - min(ys), min(ys), max(ys)))
    P("ceiling points, faces, hard edges before", before, "| after: points, faces, hard edges kept, edges of the new opening, hard among them", after)
    P("light at", [round(v, 2) for v in light.location], "| sand at", [round(v, 2) for v in sand.location], "scale", [round(v, 3) for v in sand.scale])
