"""Version 12: bake the chest's mist again so it runs past the old end of the reveal (frames 80 to the story's end plus 6) and can
play all the way out. Same simulation settings as version 8 (the file already carries them and the new end
frame, set by tools/v12_slow.py), so the first 134 frames come out as before. Does not save the file.
    blender -b chest_reveal_v12_full.blend --python tools/v12_bake_mist.py
The old cache is copied to cache_smoke_mist_before_v12 first by the shell (not by this script)."""
import bpy, time
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
dom = bpy.data.objects["Reveal Opening Domain"]
ds = dom.modifiers["Fluid"].domain_settings
assert ds.cache_directory.rstrip("/").endswith("cache_smoke_mist"), ds.cache_directory
assert ds.cache_frame_end >= 290, ds.cache_frame_end
print("V12 MIST BAKE res", ds.resolution_max, "noise", ds.use_noise, "frames", ds.cache_frame_start, ds.cache_frame_end,
      "dissolve", ds.dissolve_speed, "alpha beta", ds.alpha, ds.beta, flush=True)
for o in scn.objects:
    o.select_set(False)
dom.select_set(True)
bpy.context.view_layer.objects.active = dom
t = time.time()
with bpy.context.temp_override(object=dom, active_object=dom, scene=scn):
    bpy.ops.fluid.free_all()
    r = bpy.ops.fluid.bake_all()
print("V12 MIST BAKE", r, round(time.time() - t, 1), "s", flush=True)
