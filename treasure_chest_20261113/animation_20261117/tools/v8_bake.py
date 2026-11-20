"""Bake the version 8 mist in background Blender (the landing dust is left as it is):
    MIST_RES=96 MIST_NOISE=2 blender -b chest_reveal_v8_mist.blend --python tools/v8_bake.py
MIST_RES and MIST_NOISE are optional (default: what the file has). Other MIST_* numbers (ALPHA, BETA,
VORT, DISSOLVE) can be given the same way for a test. Saves, so the file knows about the cache."""
import bpy, os, time
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
dom = bpy.data.objects["Reveal Opening Domain"]
ds = dom.modifiers["Fluid"].domain_settings
assert ds.cache_directory.rstrip("/").endswith("cache_smoke_mist"), ds.cache_directory   # never the version 7 fog cache
E = os.environ.get
if E("MIST_RES"):
    ds.resolution_max = int(E("MIST_RES"))
if E("MIST_NOISE") is not None:
    n = int(E("MIST_NOISE"))
    ds.use_noise = n > 0
    if n:
        ds.noise_scale = n
for key, attr in (("MIST_ALPHA", "alpha"), ("MIST_BETA", "beta"), ("MIST_VORT", "vorticity")):
    if E(key):
        setattr(ds, attr, float(E(key)))
if E("MIST_DISSOLVE"):
    ds.dissolve_speed = int(E("MIST_DISSOLVE"))
print("MIST BAKE res", ds.resolution_max, "noise", ds.use_noise and ds.noise_scale, "alpha beta", ds.alpha, ds.beta,
      "vort", ds.vorticity, "dissolve", ds.dissolve_speed,
      "sources", [o.name for o in ds.fluid_group.objects], "colliders", [o.name for o in ds.effector_group.objects])
for o in scn.objects:
    o.select_set(False)
dom.select_set(True)
bpy.context.view_layer.objects.active = dom
t = time.time()
with bpy.context.temp_override(object=dom, active_object=dom, scene=scn):
    bpy.ops.fluid.free_all()
    r = bpy.ops.fluid.bake_all()
print("MIST BAKE", r, round(time.time() - t, 1), "s")
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)
