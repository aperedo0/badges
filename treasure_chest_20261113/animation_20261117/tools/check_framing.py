"""Framing check (run inside Blender): projects the chest's outer parts and the badge into the
camera every frame and reports frames where anything comes within MARGIN of the frame edge
(after the chest has fully entered the picture). Result in FRAMING."""
import bpy
from bpy_extras.object_utils import world_to_camera_view

scn = bpy.data.scenes["Chest Reveal"]
cam = scn.camera
MARGIN = 0.02
names = ["R Lab Chest " + n for n in ("Angular Boot -1 -1", "Angular Boot -1 1", "Angular Boot 1 -1", "Angular Boot 1 1",
                                      "Upper Lid Rim", "Solid Ring Handle -1", "Solid Ring Handle 1", "Lower Rim")]
badge = [o.name for o in bpy.data.collections["Reveal Badge"].all_objects if o.type == "MESH"]


def pts(name, step):
    o = bpy.data.objects[name]
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    mw = oe.matrix_world
    vs = oe.data.vertices
    return [mw @ vs[i].co for i in range(0, len(vs), step)]


FRAMING = {"tight": [], "extent": {}}
for f in range(1, scn.frame_end + 1):
    scn.frame_set(f)
    P = []
    for n in names:
        P += pts(n, 40)
    if bpy.data.objects["Reveal Badge Root"].scale.x > 0.05:
        for n in badge:
            P += pts(n, 60)
    uv = [world_to_camera_view(scn, cam, p) for p in P]
    xs = [v.x for v in uv]
    ys = [v.y for v in uv]
    ext = (round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3))
    FRAMING["extent"][f] = ext
    entered = f > 9
    if entered and (ext[0] < MARGIN or ext[1] > 1 - MARGIN or ext[2] < MARGIN or ext[3] > 1 - MARGIN):
        FRAMING["tight"].append((f, ext))
print("framing: tight frames", [t[0] for t in FRAMING["tight"]][:40])
