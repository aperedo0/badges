"""Diagnostic only, never saved: look at one spot up close through a temporary camera.
CLOSE="px,py,pz;tx,ty,tz;lens;resx;resy" in the chest's frame (camera position; point it looks at).
Chain before tools/v8_render.py. Soft focus is switched off for the close look."""
import bpy, os
from mathutils import Vector, Matrix
spec = os.environ.get("CLOSE")
if spec:
    scn = bpy.data.scenes["Chest Reveal"]
    bpy.context.window.scene = scn
    pos, tgt, lens, rx, ry = spec.split(";")
    root = bpy.data.objects["Reveal Chest Root"].matrix_world
    p = root @ Vector([float(v) for v in pos.split(",")])
    t = root @ Vector([float(v) for v in tgt.split(",")])
    cd = bpy.data.cameras.new("Close Look")
    cd.lens = float(lens)
    cd.clip_start, cd.clip_end = 0.1, 600.0
    cam = bpy.data.objects.new("Close Look", cd)
    scn.collection.objects.link(cam)
    cam.matrix_world = Matrix.Translation(p) @ (t - p).to_track_quat("-Z", "Y").to_matrix().to_4x4()
    for m in scn.timeline_markers:
        m.camera = None
    scn.camera = cam
    scn.render.resolution_x, scn.render.resolution_y = int(rx), int(ry)
    print("CLOSE LOOK", spec)
