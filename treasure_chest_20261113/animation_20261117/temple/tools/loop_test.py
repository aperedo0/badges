"""First look at the ending that keeps moving: renders the frames after the reveal for a seamless loop.
Not saved. LOOP frames repeat; FADE more frames are rendered and blended into the start by loop_join.py.
The chest's mist simulation ends at frame 213, so it is held on that frame (its cache offset follows the frame).
    OUT=folder PCT=40 SAMPLES=24 LOOP=90 FADE=24 blender -b chest_reveal_v10_temple_polish.blend --python temple/tools/loop_test.py"""
import bpy, os, time
E = os.environ.get
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
out = E("OUT")
os.makedirs(out, exist_ok=True)
LOOP, FADE = int(E("LOOP", "90")), int(E("FADE", "24"))
r = scn.render
r.resolution_percentage = int(E("PCT", "40"))
r.image_settings.file_format = "PNG"
scn.eevee.taa_render_samples = int(E("SAMPLES", "24"))
cam = scn.camera.data
px = 0.5 * (cam.sensor_width / cam.lens) / (max(r.resolution_x, r.resolution_y) * r.resolution_percentage / 100.0)
ng = bpy.data.node_groups.get("Reveal Beam Specks")
if ng and "pixel radius" in ng.nodes:
    ng.nodes["pixel radius"].inputs[1].default_value = px
dom = bpy.data.objects["Reveal Opening Domain"]
ds = next(m for m in dom.modifiers if m.type == "FLUID").domain_settings
dust = bpy.data.objects.get("Reveal Dust Domain")
END = 213
scn.frame_end = END + LOOP + FADE + 2
SIGN = int(E("OFFSET_SIGN", "-1"))
t0 = time.time()
first = int(E("FIRST", "0"))
for i in range(first, LOOP + FADE):
    f = END + i
    path = os.path.join(out, f"{i:04d}.png")
    if E("SKIP_DONE") and os.path.exists(path):
        continue
    ds.cache_frame_offset = SIGN * (f - END)        # the mist stays on its last baked frame
    if dust:
        dust.hide_render = f > END
    scn.frame_set(f)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("LOOP FRAME", i, round(time.time() - t0, 1), "s", flush=True)
print("LOOP DONE", LOOP + FADE, "frames", round(time.time() - t0, 1), "s")
