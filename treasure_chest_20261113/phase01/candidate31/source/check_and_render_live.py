import bpy,numpy as np,json,math
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';sc=bpy.context.scene;assert sc.name=='Chest Phase 1'
objects=[o for o in sc.objects if o.type=='MESH' and o.get('phase')==1];assert len(objects)==6
conv=lambda a:np.c_[a[:,0],a[:,2],-a[:,1]]
def closed(V,T):
 e=np.sort(np.vstack([T[:,[0,1]],T[:,[1,2]],T[:,[2,0]]]),axis=1);_,counts=np.unique(e,axis=0,return_counts=True);return bool((counts==2).all())
def bounds(V):return bool(V[:,0].max()<=3.35+1e-5 and V[:,0].min()>=-3.35-1e-5 and V[:,1].max()<=3.015+1e-5 and V[:,1].min()>=-2.895-1e-5)
data={};checks=[];allv=[];total=0
for i,ob in enumerate(objects):
 assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7
 me=ob.data;me.calc_loop_triangles();v=conv(np.array([p.co[:] for p in me.vertices]));t=np.array([p.vertices[:] for p in me.loop_triangles]);assert closed(v,t),ob.name;assert bounds(v),ob.name
 vol=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6);assert vol>0,ob.name
 checks.append(dict(name=ob.name,closed=True,identity_transform=True,triangles=len(t),volume=vol,bounds=[v.min(0).tolist(),v.max(0).tolist()]));data[f'part{i}_v']=v;data[f'part{i}_t']=t;allv.append(v);total+=len(t)
 if i==0:
  assert not closed(v,t[1:]);bad=v.copy();bad[0,1]=3.5;assert not bounds(bad)
V=np.vstack(allv);assert total<6500,total;assert abs(V[:,0].max()+V[:,0].min())<1e-5;assert abs(V[:,2].max()+V[:,2].min())<1e-5
np.savez_compressed(P/'geometry.npz',**data)
result=dict(phase=1,complete_badge=False,meshes=6,total_triangles=total,bounds=[V.min(0).tolist(),V.max(0).tolist()],maximum_rotational_width=float(2*np.linalg.norm(V[:,[0,2]],axis=1).max()),checks=checks,removed_cap_test_rejected=True,out_of_bounds_test_rejected=True,no_chest_app_build=True)
assert result['maximum_rotational_width']<=6.7
(P/'validation.json').write_text(json.dumps(result,indent=2));print('Validated',total,'triangles, all 6 closed, actual model bounds',result['bounds'])
OUT=P/'candidate02';OUT.mkdir(exist_ok=True)
D=json.loads((P/'design.json').read_text());a=math.radians(D['camera_elevation_degrees']);dist=D['camera_distance'];f=np.array([0,-math.sin(a),-math.cos(a)]);u=np.array([0,math.cos(a),-math.sin(a)])
def projected(param):
 y,lens=param;q=V-np.array([0,y+dist*math.tan(a),dist]);z=q@f;return 550-(q@u)/z*(1100*lens/36)
param=np.array([D['camera_target_height'],D['lens']],float)
for _ in range(7):
 y=projected(param);err=np.array([y.min()-154,y.max()-950]);J=[]
 for k,h in [(0,.0001),(1,.001)]:
  p=param.copy();p[k]+=h;yy=projected(p);J.append((np.array([yy.min(),yy.max()])-np.array([y.min(),y.max()]))/h)
 param-=np.linalg.solve(np.array(J).T,err)
cam=sc.camera;cam.location=(0,-dist,param[0]+dist*math.tan(a));from mathutils import Vector
cam.rotation_euler=(Vector((0,0,float(param[0])))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=float(param[1])
(P/'camera_refinement.json').write_text(json.dumps(dict(distance=dist,elevation_degrees=D['camera_elevation_degrees'],target_y=float(param[0]),lens=float(param[1]),common_projected_top=154,common_projected_bottom=950),indent=2))

original={o.name:o.matrix_world.copy() for o in objects}
try:
 for name,angle in [('reference',0),('straight_front',-32),('left_end',58),('right_end',-122),('back',180)]:
  for ob in objects:ob.matrix_world=Matrix.Rotation(math.radians(angle),4,'Z')@original[ob.name]
  sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
finally:
 for ob in objects:ob.matrix_world=original[ob.name]
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
import shutil
for name in ['geometry.npz','validation.json','design.json','camera_refinement.json']:shutil.copy2(P/name,OUT/name)
shutil.copy2(R/'treasure_chest.blend',OUT/'chest.blend')
print('Saved five actual Blender views and restored the reference pose.')
