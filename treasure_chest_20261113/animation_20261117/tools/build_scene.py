"""Build the 'Chest Reveal' scene and rig in chest_reveal.blend (run inside Blender).

Safe to run again: it only creates what is missing and never deletes objects.
The chest parts are object copies of the 'Full chest material evaluation' chest
that share the original mesh data, so the review scenes stay exactly as they were.

Rig (all empties, collection 'Reveal Rig'):
  Reveal Chest Root    world placement of the chest (floor centre, chest yaw). Static.
  Reveal Chest Drop    fall and hop translation (child of Root).
  Reveal Chest Rock    roll (rotation y) and pitch (rotation x) about the boot edge that
                       touches the floor; drivers on its location keep that edge pinned.
  Reveal Chest Shake   small impact shocks (child of Rock). Parent of every body part.
  Reveal Lid Hinge     lid rotation about the real rear hinge barrels (rotation x, negative opens).
  Reveal Hasp Pivot    hasp rotation about its pin (child of the lid, rotation x, negative swings out).
  Reveal Lock Bolt     the key driven bolt inside the lock case (location x).
  Reveal Ring Pivot L/R  side rings about their rolled covers (rotation y, outward positive on R).
Chest frame: x = width (+x is the end away from the camera), y = depth (front is -y), z up,
origin on the floor under the chest centre.
"""
import bpy, math
from mathutils import Matrix, Vector

SRC = "Full chest material evaluation"
SCN = "Chest Reveal"
YAW = math.atan2(0.5299192070960999, 0.8480481505393982)   # 32 deg, chest's own yaw
FLOOR = -2.455

src = bpy.data.scenes[SRC]
scn = bpy.data.scenes.get(SCN) or bpy.data.scenes.new(SCN)
bpy.context.window.scene = scn   # rig matrices are only evaluated in the active scene
scn.render.fps = 30
scn.frame_start, scn.frame_end = 1, 215
scn.render.resolution_x, scn.render.resolution_y = 1080, 1920
scn.render.resolution_percentage = 50
scn.render.engine = "BLENDER_EEVEE"
scn.view_settings.view_transform = src.view_settings.view_transform
scn.view_settings.look = src.view_settings.look
scn.unit_settings.scale_length = src.unit_settings.scale_length


def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or scn.collection).children.link(c)
    return c


top = coll("Reveal")
C = {k: coll("Reveal " + k, top) for k in ("Rig", "Chest Body", "Chest Lid", "Lock And Hasp", "Rings",
                                         "Badge", "FX", "Stage")}

LID = {"Barrel Lid Envelope", "Upper Lid Rim", "Hasp Mount", "Front Hinge Pin",
       "Fixed Front Hinge Knuckle -1", "Fixed Front Hinge Knuckle 1",
       "Hasp Mount Fastener -1", "Hasp Mount Fastener 1", "Hasp Pivot Dome -1", "Hasp Pivot Dome 1",
       "Rear Hinge Upper -1", "Rear Hinge Upper 1", "Small Front Rail Rivet -1",
       "End Arch Crown Tab -1", "End Arch Crown Tab 1", "End Crown Fastener -1", "End Crown Fastener 1",
       "End Rail Rivet -1 0", "End Rail Rivet 1 0"}
LID_PREFIX = ("Crown Fastener Mass", "End Arch Rivet", "Hoop Rivet", "Rear Hinge Upper Rivet",
              "Upper Corner End Rivet", "Upper Corner Front Rivet")
LID_RAIL = {"Rail Rivet -1 0", "Rail Rivet -1 1", "Rail Rivet 1 0", "Rail Rivet 1 1", "Rail Rivet 1 2"}
CLAUDE_LID = {"Claude Lid Planks", "Claude Lid Cap Planks A", "Claude Lid Cap Planks B"}
HASP = {"Curved Hasp Tongue", "Front Hasp Barrel"}
BOLT = {"Key Driven Slider"}
RINGS = {"Solid Ring Handle -1": "L", "Solid Ring Handle 1": "R"}


def role(name):
    if name in CLAUDE_LID:
        return "lid"
    n = name[len("Lab Chest "):] if name.startswith("Lab Chest ") else name
    if n in HASP:
        return "hasp"
    if n in BOLT:
        return "bolt"
    if n in RINGS:
        return "ring" + RINGS[n]
    if n in LID or n in LID_RAIL or n.startswith(LID_PREFIX):
        return "lid"
    return "body"


# Chest frame: floor centre with the chest's yaw.
CH = Matrix.Translation((0, 0, FLOOR)) @ Matrix.Rotation(YAW, 4, "Z")


REST = {}   # rest world matrix of every rig empty (all rig channels are zero at rest)


def empty(name, parent, local_loc, shape="PLAIN_AXES", size=0.4, rot_mode="XYZ"):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, None)
        C["Rig"].objects.link(o)
    o.empty_display_type = shape
    o.empty_display_size = size
    o.rotation_mode = rot_mode
    o.parent = parent
    if parent is None:
        o.matrix_world = CH @ Matrix.Translation(local_loc)
        REST[name] = CH @ Matrix.Translation(local_loc)
    else:
        REST[name] = REST[parent.name] @ Matrix.Translation(local_loc)
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.location = local_loc
        o.rotation_euler = (0, 0, 0)
    return o


root = empty("Reveal Chest Root", None, (0, 0, 0), "ARROWS", 1.2)
drop = empty("Reveal Chest Drop", root, (0, 0, 0), "CUBE", 0.25)
# Rock is the animator's control (keyed roll/pitch); Tilt copies it through drivers and carries
# the chest. Separate objects, so the pivot drivers never read their own transform (no lag).
rock = empty("Reveal Chest Rock", drop, (0, 0, 0), "CIRCLE", 3.2)
tilt = empty("Reveal Chest Tilt", drop, (0, 0, 0), "PLAIN_AXES", 0.2)
shake = empty("Reveal Chest Shake", tilt, (0, 0, 0), "PLAIN_AXES", 0.6)
# Hinges in chest frame (measured from the real hardware, see README):
lid = empty("Reveal Lid Hinge", shake, (0, 1.930, 0.362 - FLOOR), "SINGLE_ARROW", 1.0)
hasp = empty("Reveal Hasp Pivot", lid, (0, -2.0 - 1.930, 0.485 - 0.362), "SINGLE_ARROW", 0.6)
bolt = empty("Reveal Lock Bolt", shake, (-0.125, -1.914, -0.43 - FLOOR), "CUBE", 0.12)
ringL = empty("Reveal Ring Pivot L", shake, (-2.93, 0.0, -0.36 - FLOOR), "SINGLE_ARROW", 0.6)
ringR = empty("Reveal Ring Pivot R", shake, (2.93, 0.0, -0.36 - FLOOR), "SINGLE_ARROW", 0.6)
fx = empty("Reveal FX Controls", root, (0, -3.2, 0.2), "SPHERE", 0.3)
for k, v in dict(keyhole_glow=0.0, seam_glow=0.0, interior_glow=0.0, beam=0.0, flash=0.0,
                 dust_1=0.0, dust_2=0.0, dust_3=0.0).items():
    if k not in fx:
        fx[k] = v
        fx.id_properties_ui(k).update(min=0.0, soft_max=2.0)

# Edge pinning drivers on the Rock: roll about y pivots on the boot edge at x = +-B,
# pitch about x pivots on the front or back boot edge at y = +-D.
B, D = 2.775, 1.865
rock.rotation_mode = tilt.rotation_mode = "XYZ"
for idx in range(3):
    rock.driver_remove("location", idx)
    tilt.driver_remove("location", idx)
    tilt.driver_remove("rotation_euler", idx)
# Exact corner pivot for rotation R = Ry(r) Rx(p) about the boot corner c = (sB, tD, 0) on the
# floor, s = sign(r), t = -sign(p): location = c - R c (simple expressions, no auto-run needed).
exprs = {("location", 0): "r/max(abs(r),1e-12)*B*(1-cos(r)) + D*abs(sin(p))*sin(r)",
         ("location", 1): "-p/max(abs(p),1e-12)*D*(1-cos(p))",
         ("location", 2): "B*abs(sin(r)) + D*abs(sin(p))*cos(r)",
         ("rotation_euler", 0): "p",
         ("rotation_euler", 1): "r"}
for (path, idx), ex in exprs.items():
    fc = tilt.driver_add(path, idx)
    d = fc.driver
    d.type = "SCRIPTED"
    for v in list(d.variables):
        d.variables.remove(v)
    for vn, i in (("r", 1), ("p", 0)):
        v = d.variables.new()
        v.name = vn
        v.type = "SINGLE_PROP"
        t = v.targets[0]
        t.id_type = "OBJECT"
        t.id = rock
        t.data_path = f"rotation_euler[{i}]"
    d.expression = ex.replace("B", str(B)).replace("D", str(D))
    d.use_self = False

parents = {"body": shake, "lid": lid, "hasp": hasp, "bolt": bolt, "ringL": ringL, "ringR": ringR}
dest = {"body": C["Chest Body"], "lid": C["Chest Lid"], "hasp": C["Lock And Hasp"],
        "bolt": C["Lock And Hasp"], "ringL": C["Rings"], "ringR": C["Rings"]}
skip_types = {"LIGHT", "CAMERA", "EMPTY"}
made = 0
for o in list(src.objects):
    if o.type in skip_types or "floor" in o.name.lower():
        continue
    name = "R " + o.name
    c = bpy.data.objects.get(name)
    r = role(o.name)
    if c is None:
        c = o.copy()
        c.name = name
        c.animation_data_clear()
        dest[r].objects.link(c)
        made += 1
    # attach relative to the rig's REST pose, so this works at any current frame
    c.parent = parents[r]
    c.matrix_parent_inverse = REST[parents[r].name].inverted()
    c.matrix_basis = o.matrix_basis.copy() if o.parent is None else o.matrix_world.copy()

print("copied", made)
