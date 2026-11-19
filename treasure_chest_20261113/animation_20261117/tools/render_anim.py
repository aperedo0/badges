"""Background render of the Chest Reveal animation.
blender -b chest_reveal.blend --python tools/render_anim.py -- OUTDIR [pct=50] [samples=24] [blur=1] [start=1] [end=215]"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
kw = dict(x.split("=") for x in a[1:])
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
scn.render.resolution_percentage = int(kw.get("pct", 50))
scn.eevee.taa_render_samples = int(kw.get("samples", 24))
scn.render.use_motion_blur = kw.get("blur", "1") == "1"
scn.frame_start = int(kw.get("start", 1))
scn.frame_end = int(kw.get("end", scn.frame_end))
scn.render.image_settings.file_format = "PNG"
scn.render.filepath = out.rstrip("/") + "/"
bpy.ops.render.render(animation=True, scene=scn.name)
