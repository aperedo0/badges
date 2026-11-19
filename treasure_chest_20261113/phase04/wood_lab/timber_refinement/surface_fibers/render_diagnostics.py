import bpy,time,json
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent
import sys
key=sys.argv[sys.argv.index('--')+1]
candidate=str(W/key/'master.blend')
bpy.ops.wm.open_mainfile(filepath=str(W/'baseline.blend'))
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'reused_canonical_setup','exec'))
canonical_camera=camera.copy();canonical_lights=lightstate.copy()
bpy.ops.wm.open_mainfile(filepath=candidate)
sc=bpy.data.scenes['Test plank master'];bpy.context.window.scene=sc;cam=sc.camera;camera=canonical_camera;lightstate=canonical_lights
lighting('cinema');frame('close');sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0;sc.render.resolution_x=1200;sc.render.resolution_y=888;sc.render.resolution_percentage=100;sc.cycles.device='GPU';sc.cycles.samples=64
mode=sys.argv[sys.argv.index('--')+2]
folder=Path(candidate).parent
if mode=='neutral_close':lighting('neutral');frame('close')
elif mode=='cinema_full':lighting('cinema');frame('full');sc.render.resolution_x=sc.render.resolution_y=1200
elif mode=='clay_graze':
 lighting('graze');frame('close')
 mesh=sc.objects['Master Chest Body Envelope'].data
 slot=next(i for i,m in enumerate(mesh.materials) if m and m.name.startswith('Wood Lab '))
 clay=mesh.materials[slot].copy();bs=clay.node_tree.nodes['Principled BSDF']
 for socket in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[socket].links):clay.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=(.28,.28,.28,1);bs.inputs['Roughness'].default_value=.76
 mesh.materials[slot]=clay
sc.render.resolution_x=1200;sc.render.resolution_y=1200 if mode=='cinema_full' else 888
sc.render.filepath=str(folder/(mode+'.png'));start=time.time();bpy.ops.render.render(write_still=True);print('FINAL',mode,time.time()-start,flush=True)
