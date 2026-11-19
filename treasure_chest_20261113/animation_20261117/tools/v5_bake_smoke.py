"""Bake the smoke in background Blender:
blender -b chest_reveal_v5.blend --python tools/v5_bake_smoke.py
Frees the old cache first, bakes data (and noise when enabled), prints timing, then saves the file
so it remembers the bake (Blender only reads a baked cache that the file knows about)."""
import bpy, time
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
dom = bpy.data.objects["Reveal Smoke Domain"]
for o in scn.objects:
    o.select_set(False)
dom.select_set(True)
bpy.context.view_layer.objects.active = dom
t = time.time()
with bpy.context.temp_override(object=dom, active_object=dom, scene=scn):
    bpy.ops.fluid.free_all()
    r = bpy.ops.fluid.bake_all()
print("SMOKE BAKE", r, round(time.time() - t, 1), "s")
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)
