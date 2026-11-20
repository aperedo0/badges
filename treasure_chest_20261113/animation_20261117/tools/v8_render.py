"""Render frames of the version 8 opening from the front camera in background Blender:
    FRAMES=100,112,150 OUT=/some/folder PCT=50 blender -b chest_reveal_v8_mist.blend --python tools/v8_render.py
FRAMES is a list (100,112) or a range (86-213). Optional look tests that are not saved:
MIST_GAIN, MOTE_GAIN, LIGHT_SCALE (the mist light), GLOW_SCALE (the soft light on the wood), SAMPLES, VOL_SAMPLES."""
import bpy, os, time
E = os.environ.get
scn = bpy.data.scenes["Chest Reveal"]
bpy.context.window.scene = scn
spec = E("FRAMES", "86-213")
if "-" in spec:
    a, b = spec.split("-")
    frames = list(range(int(a), int(b) + 1))
else:
    frames = [int(x) for x in spec.split(",")]
out = E("OUT")
os.makedirs(out, exist_ok=True)
r = scn.render
r.resolution_percentage = int(E("PCT", "50"))
r.image_settings.file_format = "PNG"
if E("SAMPLES"):
    scn.eevee.taa_render_samples = int(E("SAMPLES"))
if E("VOL_SAMPLES"):
    scn.eevee.volumetric_samples = int(E("VOL_SAMPLES"))
if E("MIST_GAIN"):
    bpy.data.materials["Reveal Opening Mist"].node_tree.nodes["mist density"].inputs[1].default_value = float(E("MIST_GAIN"))
if E("MOTE_GAIN"):
    bpy.data.materials["Reveal Beam Speck"].node_tree.nodes["speck brightness"].inputs[1].default_value = float(E("MOTE_GAIN"))
# the specks are drawn one pixel wide: tell them how big a pixel is at this render size
cam = scn.camera.data
px = 0.5 * (cam.sensor_width / cam.lens) / (max(r.resolution_x, r.resolution_y) * r.resolution_percentage / 100.0)
ng = bpy.data.node_groups.get("Reveal Beam Specks")
if ng and "pixel radius" in ng.nodes:
    ng.nodes["pixel radius"].inputs[1].default_value = px * float(E("MOTE_PIXELS", "1.0"))
for key, name in (("LIGHT_SCALE", "Reveal Opening Light"), ("GLOW_SCALE", "Reveal Opening Glow")):
    if E(key):
        k = float(E(key))
        for layer in bpy.data.objects[name].data.animation_data.action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for kp in fc.keyframe_points:
                            kp.co.y *= k; kp.handle_left.y *= k; kp.handle_right.y *= k
t0 = time.time()
for f in frames:
    path = os.path.join(out, f"{f:04d}.png")
    if E("SKIP_DONE") and os.path.exists(path):
        continue
    scn.frame_set(f)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    print("V8 FRAME", f, round(time.time() - t0, 1), "s", flush=True)
print("V8 RENDER DONE", len(frames), "frames", round(time.time() - t0, 1), "s")
