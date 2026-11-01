from pathlib import Path
import bpy,numpy as np,sys,importlib,json,re
from mathutils import Vector,Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/coin_standard_20261101');sys.path.insert(0,str(R));import geometry;importlib.reload(geometry)
cfg=json.loads((R/'draft_design.json').read_text());C=R/cfg['active_candidate']
with bpy.data.libraries.load(str(R/'original/source/emerald_sprout_original.blend'),link=False) as (source,loaded):loaded.scenes=source.scenes
scene=loaded.scenes[0];bpy.context.window.scene=scene;scene.name='Emerald Sprout rim '+str(round((1-cfg['radial_rim_width_factor'])*100))+' depth '+str(round((1-cfg['whole_coin_thickness_factor'])*100))+' reduction'
objects=[o for o in scene.objects if o.type=='MESH'];shell=next(o for o in objects if o.name.startswith('Casing___'));r=np.linalg.norm(np.array([v.co[:] for v in shell.data.vertices])[:,:2],axis=1);assert abs(r.max()-3.015)<1e-5
arrays={}
for ob in objects:
 me=ob.data;p=np.array([v.co[:] for v in me.vertices],float);n=np.array([v.vector[:] for v in me.corner_normals]);at=p[[l.vertex_index for l in me.loops]];new_n=geometry.normals_after(at,n);q=geometry.points_after(p)
 for vertex,point in zip(me.vertices,q):vertex.co=point
 me.update();me.normals_split_custom_set(new_n.tolist());me.update();name=re.sub(r'(?:\.\d{3})+$','',ob.name);arrays[name]=np.array([v.co[:] for v in me.vertices],np.float32)
scene['sprout_dimensions_changed']=True
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=9.7;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
np.savez_compressed(C/'inspected_points.npz',**arrays);bpy.data.libraries.write(str(C/'source/emerald_sprout.blend'),{scene},compress=True)
print('Emerald Sprout factors:',cfg['radial_rim_width_factor'],cfg['whole_coin_thickness_factor'],'from the original.')
