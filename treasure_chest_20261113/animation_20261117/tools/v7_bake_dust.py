"""Bake the landing dust in background Blender:
blender -b chest_reveal_v7_dust.blend --python tools/v7_bake_dust.py
Old particle bakes freed, air first (the dust clumps run live inside it; the grit follows the air), then the particles; saves so the file knows about both caches."""
import bpy, time
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
dom = bpy.data.objects["Reveal Dust Domain"]
for o in scn.objects:
    o.select_set(False)
dom.select_set(True)
bpy.context.view_layer.objects.active = dom
# only the solved sources may feed the air (plan 4.4): every enabled flow and particle system, checked
ALLOWED = ("Reveal Dust Opening ", "Reveal Dust Grit Boot ", "Reveal Ending Mote")   # specks in the ending beam (no air)
live = []
for o in scn.objects:
    for m in o.modifiers:
        if m.show_render and ((m.type == "FLUID" and m.fluid_type == "FLOW") or m.type == "PARTICLE_SYSTEM"):
            live.append((o.name, m.type))
print("ENABLED SOURCES", len(live), sorted({n.rsplit(" ", 1)[0] for n, _ in live}))
bad = [x for x in live if not x[0].startswith(ALLOWED)]
assert not bad, f"stale sources still enabled: {bad}"
# old particle bakes first: a baked cache ignores changed settings, and the air bake reads the dust
# clumps from it (a stale cache emitted almost nothing in one test)
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.free_bake_all()
t = time.time()
with bpy.context.temp_override(object=dom, active_object=dom, scene=scn):
    bpy.ops.fluid.free_all()
    r = bpy.ops.fluid.bake_all()
print("DUST AIR BAKE", r, round(time.time() - t, 1), "s")
t = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.free_bake_all()
    r = bpy.ops.ptcache.bake_all(bake=True)
print("DUST GRIT BAKE", r, round(time.time() - t, 1), "s")
bpy.ops.wm.save_mainfile()
print("saved", bpy.data.filepath)
