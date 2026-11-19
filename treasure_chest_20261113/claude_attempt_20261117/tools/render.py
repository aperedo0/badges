# usage: blender -b file.blend --python tools/render.py -- out.png [camera=NAME] [samples=N] [res=N] [border=x0,x1,y0,y1] [scene=NAME]
import bpy, sys
args = sys.argv[sys.argv.index("--")+1:]
out = args[0]; kw = dict(a.split("=",1) for a in args[1:])
sc = bpy.data.scenes[kw.get("scene","Full chest material evaluation")]
bpy.context.window.scene = sc
if "camera" in kw: sc.camera = bpy.data.objects[kw["camera"]]
if "view" in kw:
    # view=azimuth,elevation,ortho_scale[,center_z]: azimuth 0 looks at the front, 180 at the back
    import math, mathutils
    v = [float(t) for t in kw["view"].split(",")]
    az, el, scale = math.radians(v[0]), math.radians(v[1]), v[2]
    cz = v[3] if len(v) > 3 else 0.0
    Nf = mathutils.Vector((0.529919175863294, -0.8480481513760686, 0.0)); Uf = mathutils.Vector((0.8480481513760686, 0.529919175863294, 0.0))
    d = math.cos(el) * (math.cos(az) * Nf + math.sin(az) * Uf) + math.sin(el) * mathutils.Vector((0, 0, 1))
    cam = bpy.data.objects.new("Claude view camera", bpy.data.cameras.new("Claude view camera"))
    sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = scale; cam.data.clip_end = 500
    cam.location = mathutils.Vector((0, 0, cz)) + d * 45
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
if kw.get("rear") == "1":
    for o in sc.objects:
        if o.type == "LIGHT" and "Rear" in o.name: o.hide_render = False
sc.cycles.samples = int(kw.get("samples", 64))
r = int(kw.get("res", 1400)); sc.render.resolution_x = r; sc.render.resolution_y = int(kw.get("resy", r)); sc.render.resolution_percentage = 100
if "border" in kw:
    x0,x1,y0,y1 = map(float, kw["border"].split(","))
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = x0,x1,y0,y1
else:
    sc.render.use_border = False
if kw.get("neutral") == "1":
    # neutral white studio light for this render only (the saved file keeps its warm lights)
    for o in sc.objects:
        if o.type == "LIGHT": o.data.color = (1.0, 0.97, 0.93)
    for n in sc.world.node_tree.nodes:
        if n.bl_idname == "ShaderNodeMixRGB": n.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"; prefs.get_devices()
for d in prefs.devices: d.use = True
sc.cycles.device = "GPU"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = out
bpy.ops.render.render(write_still=True, scene=sc.name)
