"""Diagnostic only, never saved: are the pillars upright, how far does the resting camera look down, and what
does the last frame look like when the camera is held level and the lens is shifted instead (same position)?
Chain before tools/v8_render.py."""
import bpy, math
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
scn.frame_set(213)
bpy.context.view_layer.update()
cam = scn.camera
M = cam.matrix_world.copy()
fwd = (M.to_3x3() @ Vector((0, 0, -1))).normalized()
pitch = math.degrees(math.asin(fwd.z))
tilts = {}
for nm in ("Temple Pillar Front L", "Temple Pillar Front R", "Temple Pillar Apse L"):
    p = bpy.data.objects[nm]
    tilts[nm] = round(math.degrees((p.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized().angle(Vector((0, 0, 1)))), 4)
target = M.translation + fwd * 16.0
cd = cam.data.copy()
if cd.animation_data:
    cd.animation_data_clear()
c2 = bpy.data.objects.new("Straight Test Camera", cd)
scn.collection.objects.link(c2)
flat = Vector((fwd.x, fwd.y, 0)).normalized()
c2.matrix_world = Matrix.Translation(M.translation) @ flat.to_track_quat("-Z", "Y").to_matrix().to_4x4()
bpy.context.view_layer.update()
lo, hi = -0.8, 0.8
for _ in range(50):
    mid = (lo + hi) / 2
    cd.shift_y = mid
    if world_to_camera_view(scn, c2, target).y > 0.5:
        lo = mid
    else:
        hi = mid
for m in scn.timeline_markers:
    m.camera = None
scn.camera = c2
print("STRAIGHT TEST pitch_deg", round(pitch, 2), "pillar_tilt_deg", tilts, "shift_y", round(cd.shift_y, 4),
      "check_y", round(world_to_camera_view(scn, c2, target).y, 4))
