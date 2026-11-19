"""Version 7: pull the camera back so the chest is 10 percent smaller on screen (owner, 2026-11-18).

A real pull back, not a lens change: the camera moves back along its own view direction (its local +z,
under Reveal Camera Shake and Reveal Camera Dolly). On-screen size goes as one over the distance, so
the camera moves back by d / 9 (d / 0.9 - d), where d is its distance to the chest's centre on that
frame. The dolly's own move (rise and pull back while the lid opens) changes d, so the offset is keyed
on every other frame. Run inside Blender; safe to run again (replaces its own keys)."""
import bpy
from mathutils import Vector

scn = bpy.data.scenes["Chest Reveal"]
cam = bpy.data.objects["Reveal Camera"]
SMALLER = globals().get("PULL_SMALLER", 0.10)
F0, F1 = scn.frame_start, scn.frame_end
CENTRE = Vector((0.0, 0.0, -0.1))           # chest centre at rest (floor -2.455, rim top about 2.2)

if cam.animation_data:
    cam.animation_data_clear()
cam.location = (0.0, 0.0, 0.0)
_p = bpy.context.preferences.edit
_old = _p.keyframe_new_interpolation_type
_p.keyframe_new_interpolation_type = "LINEAR"
keys = []
for f in range(F0, F1 + 1, 2):
    scn.frame_set(f)
    cam.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    d = (cam.matrix_world.translation - CENTRE).length
    off = d * (1.0 / (1.0 - SMALLER) - 1.0)
    keys.append((f, off))
for f, off in keys:
    cam.location = (0.0, 0.0, off)
    cam.keyframe_insert("location", index=2, frame=f)
_p.keyframe_new_interpolation_type = _old
print("v7 camera pullback", keys[0], keys[len(keys) // 2], keys[-1])
