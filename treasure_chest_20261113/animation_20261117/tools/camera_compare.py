"""Render the same key moments from several frontal camera candidates with a temporary camera
(the animated camera rig is untouched). Set CANDS and FRAMES before exec. Output: OUT/<name>_<frame>.png"""
import bpy, math, os
from mathutils import Vector

scn = bpy.data.scenes["Chest Reveal"]
NF = Vector((0.529919175863294, -0.8480481513760686, 0.0))
UF = Vector((0.8480481513760686, 0.529919175863294, 0.0))
CANDS = globals().get("CANDS", {})
FRAMES = globals().get("FRAMES", [20, 128, 190])
OUT = globals().get("OUT", "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/previews/camcmp")
os.makedirs(OUT, exist_ok=True)
cd = bpy.data.cameras.get("Reveal Camera Test") or bpy.data.cameras.new("Reveal Camera Test")
co = bpy.data.objects.get("Reveal Camera Test") or bpy.data.objects.new("Reveal Camera Test", cd)
if co.name not in scn.collection.objects:
    scn.collection.objects.link(co)
cd.sensor_fit = "AUTO"; cd.sensor_width = 36; cd.clip_start, cd.clip_end = 0.5, 300
old_cam = scn.camera
old = (scn.render.resolution_percentage, scn.eevee.taa_render_samples, scn.render.use_motion_blur)
scn.render.resolution_percentage, scn.eevee.taa_render_samples, scn.render.use_motion_blur = 30, 12, False
for name, c in CANDS.items():
    d = (math.cos(math.radians(c["el"])) * (math.cos(math.radians(c["az"])) * NF + math.sin(math.radians(c["az"])) * UF)
         + math.sin(math.radians(c["el"])) * Vector((0, 0, 1)))
    aim = Vector((0, 0, c["aim_z"])) + UF * c.get("off", 0.0)
    co.location = aim + d * c["dist"]
    co.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cd.lens = c.get("lens", 50)
    scn.camera = co
    for f in FRAMES:
        scn.frame_set(f)
        scn.render.filepath = os.path.join(OUT, f"{name}_{f:04d}.png")
        bpy.ops.render.render(write_still=True, scene=scn.name)
scn.camera = old_cam
scn.render.resolution_percentage, scn.eevee.taa_render_samples, scn.render.use_motion_blur = old
print("camera candidates rendered", list(CANDS))
