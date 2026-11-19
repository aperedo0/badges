"""Real rigid body landing for the chest (Blender's Bullet physics), run in a background Blender:
    blender -b --factory-startup --python physics_landing.py -- OUT.json [key=value ...]

A box with the chest's boot footprint (5.55 x 3.73), height 5.0 and centre of mass 2.15 above the
boot bottoms falls onto a floor. Chest frame: x = width, y = depth (front is -y), z up.
Scale: the chest is about 0.7 m wide, so 1 unit = 0.126 m and real gravity is 77.9 units/s^2.
The simulation runs at 120 steps per second (4 per animation frame). Output: COM position and
rotation per step, plus the impacts found from the contact speeds."""
import bpy, sys, json, math
from mathutils import Vector, Euler, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
P = dict(g=77.9, drop=13.0, roll=-13.0, pitch=4.0, yaw=0.0, e=0.38, mu=0.7, com=2.15,
         steps=4, seconds=3.0, sub=30, iters=80, adamp=0.02, ldamp=0.0, margin=0.01)
for kv in a[1:]:
    k, v = kv.split("=")
    P[k] = float(v)

scn = bpy.context.scene
for o in list(scn.objects):
    bpy.data.objects.remove(o)
scn.render.fps = 30
n = int(P["seconds"] * 30 * P["steps"])
scn.frame_start, scn.frame_end = 1, n + 1
scn.gravity = (0, 0, -P["g"])
bpy.ops.rigidbody.world_add()
rbw = scn.rigidbody_world
rbw.time_scale = 1.0 / P["steps"]
rbw.substeps_per_frame = int(P["sub"])
rbw.solver_iterations = int(P["iters"])
rbw.point_cache.frame_start, rbw.point_cache.frame_end = 1, n + 1


def box(name, x0, x1, y0, y1, z0, z1):
    me = bpy.data.meshes.new(name)
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me.from_pydata(v, [], f)
    o = bpy.data.objects.new(name, me)
    scn.collection.objects.link(o)
    return o


floor = box("floor", -40, 40, -40, 40, -0.5, 0.5)   # Bullet box shapes are centred on the origin
floor.location = (0, 0, -0.5)
B, D, H, C = 2.775, 1.865, 5.0, P["com"]
chest = box("chest", -B, B, -D, D, -C, H - C)        # origin = centre of mass
for o, kind in ((floor, "PASSIVE"), (chest, "ACTIVE")):
    scn.view_layers[0].objects.active = o
    o.select_set(True)
    bpy.ops.rigidbody.object_add(type=kind)
    rb = o.rigid_body
    rb.collision_shape = "CONVEX_HULL" if o is chest else "BOX"
    rb.friction = P["mu"] if o is chest else 1.0       # Bullet multiplies the two bodies' values
    rb.restitution = P["e"] if o is chest else 1.0
    rb.use_margin = True
    rb.collision_margin = P["margin"]
    rb.use_deactivation = False
    o.select_set(False)
chest.rigid_body.mass = 1.0
chest.rigid_body.linear_damping = P["ldamp"]
chest.rigid_body.angular_damping = P["adamp"]
rot = Euler((math.radians(P["pitch"]), math.radians(P["roll"]), math.radians(P["yaw"])), "XYZ")
chest.rotation_euler = rot
R = rot.to_matrix()
low = min((R @ Vector((sx * B, sy * D, -C))).z for sx in (-1, 1) for sy in (-1, 1))
chest.location = (0.0, 0.0, P["drop"] - low)

frames = []
for f in range(1, n + 2):
    scn.frame_set(f)
    m = chest.matrix_world
    frames.append({"t": (f - 1) / (30.0 * P["steps"]), "loc": list(m.translation), "quat": list(m.to_quaternion())})

# impacts: steps where the lowest corner is on the floor and its downward speed collapses
corners = [Vector((sx * B, sy * D, -C)) for sx in (-1, 1) for sy in (-1, 1)]
dt = 1.0 / (30.0 * P["steps"])
from mathutils import Quaternion
def cpos(i):
    fr = frames[i]
    M = Matrix.Translation(fr["loc"]) @ Quaternion(fr["quat"]).to_matrix().to_4x4()
    return [M @ c for c in corners]
vel_prev = None
impacts = []
cz = [cpos(i) for i in range(len(frames))]
for i in range(1, len(frames) - 1):
    for k in range(4):
        v_in = (cz[i][k].z - cz[i - 1][k].z) / dt
        v_out = (cz[i + 1][k].z - cz[i][k].z) / dt
        if cz[i][k].z < 0.06 and v_in < -1.0 and v_out > v_in + 1.0:
            if not impacts or i - impacts[-1]["step"] > 3:
                impacts.append({"step": i, "t": frames[i]["t"], "corner": k, "speed": -v_in,
                                "pos": [cz[i][k].x, cz[i][k].y]})
            elif -v_in > impacts[-1]["speed"]:
                impacts[-1].update(step=i, corner=k, speed=-v_in, pos=[cz[i][k].x, cz[i][k].y])
json.dump({"params": P, "frames": frames, "impacts": impacts}, open(out, "w"))
print("IMPACTS", [(round(im["t"], 3), im["corner"], round(im["speed"], 1)) for im in impacts])
last = frames[-1]
print("FINAL", [round(v, 3) for v in last["loc"]], [round(v, 4) for v in last["quat"]])
