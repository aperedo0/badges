import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase06/material_rollout');assert Path(bpy.data.filepath)==D/'master.blend';assert not bpy.app.is_job_running('RENDER');sc=bpy.data.scenes['Full chest material evaluation'];sc.render.engine='CYCLES';sc.render.resolution_x=sc.render.resolution_y=1800;sc.render.resolution_percentage=100;sc.cycles.samples=128;sc.cycles.seed=17;sc.cycles.use_denoising=True
for view,name in [('full','Full chest wood and iron review'),('close','Full chest wood and iron closeup')]:
 image=bpy.data.images.load(str(D/'final_'/(view+'.png')),check_existing=True);image.name=name;image.use_fake_user=True;image.use_view_as_render=False;image.pack()
origin=world_to_camera_view(sc,sc.camera,Vector((0,0,0)));basis=np.array([[*(world_to_camera_view(sc,sc.camera,Vector(q))-origin)][:2] for q in [(1,0,0),(0,1,0),(0,0,1)]],np.float64);lo=np.array([1e10,1e10]);hi=-lo
for o in sc.objects:
 if o.type!='MESH' or o.hide_render or 'floor' in o.name.lower():continue
 a=np.empty((len(o.data.vertices),3),np.float32);o.data.vertices.foreach_get('co',a.ravel());M=np.array(o.matrix_world);uv=(a@M[:3,:3].T+M[:3,3])@basis+np.array([origin.x,origin.y]);lo=np.minimum(lo,uv.min(0));hi=np.maximum(hi,uv.max(0))
bounds=[lo[0]*1800,(1-hi[1])*1800,hi[0]*1800,(1-lo[1])*1800];(D/'final_/frame.json').write_text(json.dumps(dict(projected_chest_bounds=bounds,actual_mesh_projection=True,render_size=[1800,1800]),indent=2));bpy.ops.wm.save_mainfile();proof=json.loads((D/'live_validation.json').read_text());proof.update(final_images_packed=True,final_cycles_samples=128,file_sha256=hashlib.sha256((D/'master.blend').read_bytes()).hexdigest(),dirty=bpy.data.is_dirty);(D/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
