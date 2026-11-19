from pathlib import Path
import bpy,json,time
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');W=P/'timber_refinement'
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'reused_render_setup','exec'))
lighting('cinema');frame('close');sc.render.resolution_x=1200;sc.render.resolution_y=888;sc.render.resolution_percentage=100;sc.cycles.samples=64;sc.render.filepath=str(W/'baseline_cinema.png');st=time.time();bpy.ops.render.render(write_still=True);print('BASELINE',time.time()-st,flush=True)
