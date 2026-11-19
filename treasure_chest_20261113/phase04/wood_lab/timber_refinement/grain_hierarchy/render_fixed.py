import bpy,time,json
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
candidate=bpy.data.filepath
bpy.ops.wm.open_mainfile(filepath=str(W/'baseline.blend'))
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'reused_canonical_setup','exec'))
canonical_camera=camera.copy();canonical_lights=lightstate.copy()
bpy.ops.wm.open_mainfile(filepath=candidate)
sc=bpy.data.scenes['Test plank master'];bpy.context.window.scene=sc;cam=sc.camera;camera=canonical_camera;lightstate=canonical_lights
lighting('cinema');frame('close');sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0;sc.render.resolution_x=1200;sc.render.resolution_y=888;sc.render.resolution_percentage=100;sc.cycles.device='GPU';sc.cycles.samples=64
folder=Path(candidate).parent;sc.render.filepath=str(folder/'cinema_close.png');start=time.time();bpy.ops.render.render(write_still=True);print('BATCH',folder.name,time.time()-start,flush=True)
