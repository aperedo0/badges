from pathlib import Path
import bpy,time,json
W=Path(__file__).resolve().parent;P=W.parent
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'reused_render_setup','exec'))
folder=Path(bpy.data.filepath).parent
lighting('cinema');frame('close');sc.render.resolution_x=1200;sc.render.resolution_y=888;sc.render.resolution_percentage=100;sc.cycles.samples=64
sc.render.filepath=str(folder/'cinema_close.png');start=time.time();bpy.ops.render.render(write_still=True);print('CANDIDATE',folder.name,time.time()-start,flush=True)
