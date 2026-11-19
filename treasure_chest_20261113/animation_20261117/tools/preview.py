"""Quick EEVEE preview frames of the Chest Reveal scene (run inside Blender via exec).
Set PREVIEW = dict(frames=range(...), pct=25, samples=8, out=folder) before exec, or edit below."""
import bpy, os, time
P = globals().get("PREVIEW", {})
scn = bpy.data.scenes["Chest Reveal"]
frames = list(P.get("frames", range(1, 61)))
out = P.get("out", "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/previews/frames")
os.makedirs(out, exist_ok=True)
old = (scn.render.resolution_percentage, scn.eevee.taa_render_samples, scn.render.filepath, scn.render.use_motion_blur)
scn.render.resolution_percentage = P.get("pct", 25)
scn.eevee.taa_render_samples = P.get("samples", 8)
scn.render.use_motion_blur = P.get("blur", False)
t = time.time()
for f in frames:
    scn.frame_set(f)
    scn.render.filepath = os.path.join(out, f"{f:04d}.png")
    bpy.ops.render.render(write_still=True, scene=scn.name)
(scn.render.resolution_percentage, scn.eevee.taa_render_samples, scn.render.filepath, scn.render.use_motion_blur) = old
print("rendered", len(frames), "in", round(time.time() - t, 1), "s")
