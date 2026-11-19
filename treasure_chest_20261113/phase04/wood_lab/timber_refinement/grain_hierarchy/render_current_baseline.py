import bpy,json,time,math
from pathlib import Path
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
bpy.ops.wm.open_mainfile(filepath=str(W/'baseline.blend'))
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'canonical_render_setup','exec'))
canonical_camera=camera.copy();canonical_lights=lightstate.copy()
meta=json.loads((D/'comparison_geometry.json').read_text())
bpy.ops.wm.open_mainfile(filepath=meta['checkpoint'])
sc=bpy.data.scenes['Test plank master'];bpy.context.window.scene=sc;cam=sc.camera;camera=canonical_camera;lightstate=canonical_lights
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0
lighting('cinema');frame('close');sc.cycles.device='GPU';sc.cycles.samples=64;sc.render.resolution_x=1200;sc.render.resolution_y=888;sc.render.resolution_percentage=100;sc.render.filepath=str(D/'current_baseline.png')
right=cam.matrix_world.col[0].xyz.normalized();up=cam.matrix_world.col[1].xyz.normalized();center=cam.matrix_world.translation;corners=[]
for x,y in [(-2.15,-.90),(-2.15,-2.10),(-.35,-2.10),(-.35,-.90)]:
 delta=world((x,y,1.6))-center;corners.append([600+delta.dot(right)*1200/2.2,444-delta.dot(up)*1200/2.2])
meta['model_quad']=corners;meta['canonical_camera_and_lights']='Preserved H baseline';(D/'comparison_geometry.json').write_text(json.dumps(meta,indent=2))
bpy.ops.render.render(write_still=True)
