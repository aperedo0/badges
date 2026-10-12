import bpy,sys,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];kind=sys.argv[sys.argv.index('--')+1];b=r/kind;(b/'stills').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0;scene=bpy.context.scene;scene.frame_set(360);rig=bpy.data.objects['Turntable | one slow 360 degree spin'];rig.animation_data_clear();rig.rotation_euler=(0,0,0)
for obj in scene.objects:
    if obj.type=='MESH' and obj not in rig.children_recursive:obj.hide_render=True
camera=bpy.data.objects.new('Still camera',bpy.data.cameras.new('Still camera'));scene.collection.objects.link(camera);camera.location=(0,0,23);camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=6.7;scene.camera=camera
scene.render.use_border=False;scene.render.film_transparent=True;scene.render.use_compositing=False;scene.render.resolution_x=scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.dither_intensity=0;scene.render.filepath=str(b/'stills'/f'{kind}_1080.png');scene.cycles.samples=128
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type=='METAL'
scene.cycles.device='GPU';bpy.ops.render.render(write_still=True)
