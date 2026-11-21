"""Version 12: the hall's shell (owner's third review, 2026-11-20). Run inside chest_reveal_v12_full.blend after
v12_dark.py (it makes the stone materials used here); safe to run again; nothing is deleted (objects are
reused by name and get new mesh data).

1. A real ceiling over the front hall. Owner, with a picture of the top of the screen at the start: "it doesn't
   look like an enclosed space. It should look like an enclosed place." The vault was a smooth dark shell that
   read as empty black. Now it is coursed stone with heavy ribs arching across it, it has thickness, and it is
   broken open in two ragged holes exactly where the two shafts of night light come down (a dim patch of night
   sky shows through). A faint cool light from below, as if bounced off the floor, lets the ribs and the
   courses be read.
2. The long hall behind the small arch. Owner, with a picture of the two arches in the gold light: the near
   arch's underside is a thin strip, the next one's is "way longer ... it doesn't look congruent". The small
   arch ran straight into a tunnel of the same radius, so its underside seemed to go on for 30 units. Now the
   tunnel is wider and higher than the arch (16.6 against 15.3), its vault is dark between the ribs, and each
   rib is a full arch that reaches the vault. Looking down the hall: an arch with a thin lit underside, a dark
   gap, the next arch, a dark gap, and so on, like the first arch against the dark wall behind it."""
import bpy, bmesh, math, random
from mathutils import Vector

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
story = bpy.data.objects["Temple Story"]
MATS = bpy.data.materials
LOW = FLOOR - 0.1
CAP_APSE = FLOOR + 0.88 * 28.95
WALL_Y, CORR_END = 89.0, 235.0
BAYS = (116.0, 145.0, 174.0, 203.0)
SHAFTS = (("L", -10.0, 36.0, 3.0), ("R", 11.5, 47.0, 2.7))        # name, x, y, the opening's size


def finish(V, F):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = [tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces]
    bm.free()
    return out


def join(parts):
    V, F = [], []
    for v, f in parts:
        o_ = len(V)
        V += v
        F += [tuple(i + o_ for i in ff) for ff in f]
    return V, F


def band(r0, r1, y0, y1, zc, n=96):
    """A bar of rectangular section bent into a half circle across the hall."""
    V, F = [], []
    for i in range(n + 1):
        th = math.pi * i / n
        c, s_ = math.cos(th), math.sin(th)
        for r, y in ((r0, y0), (r1, y0), (r1, y1), (r0, y1)):
            V.append((r * c, y, zc + r * s_))
    for i in range(n):
        for q in range(4):
            a, b = 4 * i + q, 4 * i + (q + 1) % 4
            F.append((a, b, b + 4, a + 4))
    F.append((0, 1, 2, 3))
    F.append((4 * n + 3, 4 * n + 2, 4 * n + 1, 4 * n))
    return finish(V, F)


def shell(r, zc, y0, y1, nv, ny):
    """The inside of a barrel vault, facing down into the hall."""
    V, F = [], []
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny
        for i in range(nv + 1):
            th = math.pi * i / nv
            V.append((r * math.cos(th), y, zc + r * math.sin(th)))
    for j in range(ny):
        for i in range(nv):
            a = j * (nv + 1) + i
            F.append((a, a + 1, a + nv + 2, a + nv + 1))
    return V, F


def only_in(o, colls):
    for c in list(o.users_collection):
        if c.name not in [k.name for k in colls]:
            c.objects.unlink(o)
    for c in colls:
        if o.name not in c.objects:
            c.objects.link(o)


def drv(idb, path, expr, **vs):
    try:
        idb.driver_remove(path)
    except Exception:
        pass
    d = idb.driver_add(path).driver
    d.type = "SCRIPTED"
    for nm, tpath in vs.items():
        v = d.variables.new()
        v.name = nm
        v.type = "SINGLE_PROP"
        v.targets[0].id = story
        v.targets[0].data_path = tpath
    d.expression = expr


# ------------------------------------------------------------------ 1. the ceiling of the front hall
VR, VZ = 15.0, 46.0
THICK = G("VAULT_THICK", 1.6)
rng = random.Random(G("HALL_SEED", 11))
MASKS = coll("Temple Shaft Masks", TC)
MASK_Z = VZ + VR + THICK + 1.4                     # just above the vault
cutters = []
for nm, sx, sy, r0 in SHAFTS:
    # Where stones have fallen out of the vault: an uneven broken outline, longer one way than the other, with
    # straight edges and corners. (Owner, 2026-11-20: "this is supposed to be a worn down temple ... it's not
    # going to be a perfect circle shining down. It's probably going to be not a well-defined shape".)
    nc = 13
    turn = math.radians(rng.uniform(-35, 35))       # the long way lies roughly across the hall, clear of the ribs
    corners = []
    for k in range(nc):
        a = 2 * math.pi * (k + rng.uniform(-0.28, 0.28)) / nc
        r = r0 * rng.uniform(0.62, 1.22)
        u, v = 1.25 * r * math.cos(a), 0.88 * r * math.sin(a)
        corners.append((sx + u * math.cos(turn) - v * math.sin(turn), sy + u * math.sin(turn) + v * math.cos(turn)))
    ring = []
    for k in range(nc):                           # four points along every straight edge
        (x0, y0), (x1, y1) = corners[k], corners[(k + 1) % nc]
        ring += [(x0 + (x1 - x0) * t / 4.0, y0 + (y1 - y0) * t / 4.0) for t in range(4)]
    n = len(ring)
    # the plug the boolean takes out of the vault
    V = [(x, y, 38.0) for x, y in ring] + [(x, y, 76.0) for x, y in ring]
    F = [tuple(reversed(range(n))), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    V, F = finish(V, F)
    co = put("Temple Vault Hole " + nm, mesh_from("Temple Vault Hole " + nm, V, F), TC, [], root)
    co.hide_render = True
    co.hide_viewport = False                      # the boolean reads it; shown as a wire only
    co.display_type = "WIRE"
    co.visible_shadow = False
    cutters.append(co)
    # The same outline as a plate above the vault that only the shaft's light sees: it gives the light the
    # opening's shape, in the air and on the floor. (The vault itself throws no shadows, so that the gold beam
    # and the other lights from above pass it as before.)
    RO = 8.5
    V = [(x, y, MASK_Z) for x, y in ring]
    for x, y in ring:
        d = math.hypot(x - sx, y - sy)
        V.append((sx + (x - sx) * RO / d, sy + (y - sy) * RO / d, MASK_Z))
    F = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    mo = put("Temple Shaft Mask " + nm, mesh_from("Temple Shaft Mask " + nm, V, F), MASKS, [], root)
    only_in(mo, [MASKS])
    mo.visible_camera = False
    mo.visible_shadow = True
    mo.hide_render = False
    mo.display_type = "WIRE"
    # the light itself: wider than the opening (the plate cuts it to shape), even across, a little soft at the edge
    so = bpy.data.objects["Temple Shaft " + nm]
    HI = so.location.z
    so.data.spot_size = 2.0 * math.atan(6.0 / (HI - MASK_Z))
    so.data.spot_blend = 0.8                      # still strongest in the middle, as a streak of light is
    so.data.shadow_soft_size = G("SHAFT_SOFT", 0.6)
    so.data.use_shadow = True
    so.light_linking.blocker_collection = MASKS
    # Its strength: `SHAFT_SHAPE` keeps the streak as strong as it was when the light was a soft round cone
    # (measured on the picture, each streak against the dark beside it: the left needs 1.15 times its old
    # energy to look the same, the right, whose opening came out larger, 0.87), and
    # `SHAFT_LEVEL` is the owner's "a teeny bit too bright. Maybe make them
    # 70% or 80%" for the dark part of the story. The gold ending keeps its level.
    e0 = 90000.0 * (1.0 if nm == "L" else 0.8) * 1.5 * ((HI - FLOOR) / 90.55) ** 2 * G("SHAFT_SHAPE", {"L": 1.15, "R": 0.87})[nm]
    lvl = G("SHAFT_LEVEL", 0.75)
    drv(so.data, "energy", "%.1f * (%.3f - %.3f * gold)" % (e0, 2.0 * lvl, 2.0 * lvl - 1.0), gold='["gold"]')
V, F = shell(VR, VZ, 10.0, WALL_Y + 0.5, 72, 132)
vault = put("Temple Vault", mesh_from("Temple Vault", V, F, smooth=True), TC, [MATS["Temple Vault Masonry"]], root)
vault.modifiers.clear()
sm = vault.modifiers.new("Thickness", "SOLIDIFY")
sm.thickness = THICK
sm.offset = -1.0                                  # grows away from the hall
sm.use_even_offset = True
for co in cutters:
    bm_ = vault.modifiers.new("Hole " + co.name[-1], "BOOLEAN")
    bm_.operation = "DIFFERENCE"
    bm_.solver = "EXACT"
    bm_.object = co
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
baked = bpy.data.meshes.new_from_object(vault.evaluated_get(dg))
vault.modifiers.clear()
baked.polygons.foreach_set("use_smooth", [True] * len(baked.polygons))
baked.set_sharp_from_angle(angle=math.radians(40))
baked.update()
vault = put("Temple Vault", baked, TC, [MATS["Temple Vault Masonry"]], root)
vault.visible_shadow = False                      # the beam and the shafts from above pass it, as before
for co in cutters:
    co.hide_viewport = True
RIB_Y = G("VAULT_RIBS", (18.0, 29.8, 41.6))        # clear of the two openings
parts = [band(VR - 1.4, VR + 0.3, y - 0.9, y + 0.9, VZ, n=72) for y in RIB_Y]
parts.append(band(VR - 1.4, VR + 0.3, 54.2, 56.1, VZ, n=72))      # the arch where the vault meets the wall over the big arch
V, F = join(parts)
ribs = put("Temple Vault Ribs", mesh_from("Temple Vault Ribs", V, F, smooth=True, sharp_deg=30), TC, [MATS["Temple Vault Rib Stone"]], root)
bevel(ribs, 0.07, 2, 30)
ribs.visible_shadow = False
VAULT_RECV = coll("Temple Vault Receivers", TC)
for o in (vault, ribs):
    if o.name not in VAULT_RECV.objects:
        VAULT_RECV.objects.link(o)
    back = bpy.data.collections["Temple Back Receivers"]
    if o.name in back.objects:
        back.objects.unlink(o)                    # the raking moonlight is for the wall and the arches, not the ceiling
    if o.name in RECV.objects:
        RECV.objects.unlink(o)                    # not lit by the shafts (they burned the openings' edges white) or the torches
    br = bpy.data.collections.get("Temple Burst Receivers")
    if br and o.name not in br.objects:
        br.objects.link(o)                        # the cold light from the chest shows the whole ceiling for a moment
# the night sky seen through the openings
sk = mat("Temple Night Sky")
n = NT(sk)
em = n.node("ShaderNodeEmission", ins={"Color": G("SKY_COLOR", (0.004, 0.0075, 0.017, 1)), "Strength": G("SKY_GLOW", 1.0)})
n.out(em.outputs[0])
zs = VZ + VR + THICK + 5.0
sky = put("Temple Night Sky", mesh_from("Temple Night Sky", [(-24, 14, zs), (24, 14, zs), (24, 84, zs), (-24, 84, zs)], [(0, 3, 2, 1)]), TC, [sk], root)
sky.visible_shadow = False
only_in(sky, [TC])
# a faint cool light from below, as if the moonlight bounced off the floor
bo = bpy.data.objects.get("Temple Vault Bounce")
if bo is None:
    bo = bpy.data.objects.new("Temple Vault Bounce", bpy.data.lights.new("Temple Vault Bounce", "SPOT"))
    TC.objects.link(bo)
bo.parent = root
bo.matrix_parent_inverse.identity()
bo.location = G("BOUNCE_AT", (-4.0, 30.0, 3.0))
bo.rotation_euler = (Vector(G("BOUNCE_AIM", (2.0, 52.0, 58.0))) - Vector(bo.location)).to_track_quat("-Z", "Y").to_euler()
bo.data.spot_size = math.radians(125)
bo.data.spot_blend = 1.0
bo.data.color = (0.60, 0.75, 1.0)
bo.data.shadow_soft_size = 3.0
bo.data.use_shadow = True
bo.data.volume_factor = 0.0
bo.light_linking.receiver_collection = VAULT_RECV
bo.light_linking.blocker_collection = VAULT_RECV   # only the ribs throw shadows on the vault
drv(bo.data, "energy", "%.1f * (1.0 - 0.6 * gold)" % G("BOUNCE_E", 14000.0), gold='["gold"]')

# ------------------------------------------------------------------ 2. the long hall
CW = G("CORRIDOR_HALF", 16.6)
Y0 = WALL_Y + 2.5
V, F = [], []
ny = 20
for sx in (-1, 1):
    base = len(V)
    for j in range(ny + 1):
        yy = Y0 + (CORR_END - Y0) * j / ny
        V += [(sx * CW, yy, LOW), (sx * CW, yy, CAP_APSE)]
    for j in range(ny):
        a = base + 2 * j
        q = (a, a + 1, a + 3, a + 2)
        F.append(q if sx > 0 else q[::-1])        # both face into the hall
put("Temple Apse Wall", mesh_from("Temple Apse Wall", V, F, smooth=False), TC, [MATS["Temple Wall Masonry"]], root)
V, F = shell(CW, CAP_APSE, Y0, CORR_END, 48, 20)
cv = put("Temple Corridor Vault", mesh_from("Temple Corridor Vault", V, F, smooth=True), TC, [MATS["Temple Corridor Vault Masonry"]], root)
for c in (RECV, bpy.data.collections.get("Temple Burst Receivers")):
    if c and cv.name not in c.objects:
        c.objects.link(cv)
V, F = join([band(13.7, CW + 0.1, yb - 1.3, yb + 1.3, CAP_APSE, n=64) for yb in BAYS])
cr = put("Temple Corridor Ribs", mesh_from("Temple Corridor Ribs", V, F, smooth=True, sharp_deg=30), TC, [MATS["Temple Arch Stone Ribs"]], root)
bevel(cr, 0.08, 2, 30)
ce = bpy.data.objects["Temple Corridor End"]
ce.scale.x = (CW + 1.0) / 16.3                    # the end wall closes the wider hall (its doorway widens by the same 8 percent)
result = {"hall": "ok", "vault_faces": len(baked.polygons), "vault_verts": len(baked.vertices)}
