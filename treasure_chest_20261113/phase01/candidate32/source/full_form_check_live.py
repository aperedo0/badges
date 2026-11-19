import bpy,numpy as np,json,math,shutil
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';OUT=P/'candidate32';OUT.mkdir(exist_ok=True);sc=bpy.context.scene
exec(compile((P/'tools/check_arch20_contact_live.py').read_text(),'check_arch20_contact_live.py','exec'))
objects=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')]
assert len(objects)>40
conv=lambda a:np.c_[a[:,0],a[:,2],-a[:,1]]
def closed(T):
 e=np.sort(np.vstack([T[:,[0,1]],T[:,[1,2]],T[:,[2,0]]]),axis=1);_,counts=np.unique(e,axis=0,return_counts=True);return bool((counts==2).all())
def bounds(V):return bool(V[:,0].max()<=3.35+1e-5 and V[:,0].min()>=-3.35-1e-5 and V[:,1].max()<=3.015+1e-5 and V[:,1].min()>=-2.895-1e-5)
data={};checks=[];allv=[];total=0
for i,ob in enumerate(objects):
 assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<1e-7,ob.name
 me=ob.data;me.calc_loop_triangles();v=conv(np.array([p.co[:] for p in me.vertices]));t=np.array([p.vertices[:] for p in me.loop_triangles]);assert closed(t),ob.name+' open';assert bounds(v),ob.name+' bounds'
 vol=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6);assert vol>0,(ob.name,vol)
 assert not ob.name.startswith('Casing')
 checks.append(dict(name=ob.name,closed=True,identity_transform=True,triangles=len(t),volume=vol,bounds=[v.min(0).tolist(),v.max(0).tolist()]));data[f'part{i}_v']=v;data[f'part{i}_t']=t;allv.append(v);total+=len(t)
 if i==0:
  assert not closed(t[1:]);bad=v.copy();bad[0,1]=3.5;assert not bounds(bad)
V=np.vstack(allv);assert total<180000,total
result=dict(phase=1,complete_badge=False,complete_major_forms=True,meshes=len(objects),total_triangles=total,bounds=[V.min(0).tolist(),V.max(0).tolist()],maximum_rotational_width=float(2*np.linalg.norm(V[:,[0,2]],axis=1).max()),checks=checks,removed_cap_test_rejected=True,out_of_bounds_test_rejected=True,no_chest_app_build=True)
assert result['maximum_rotational_width']<=6.7
holes={}
for i,m in enumerate(checks):
 if 'With Bore' in m['name'] or 'Solid Ring Handle' in m['name']:
  t=data[f'part{i}_t'];v=data[f'part{i}_v'];e=np.unique(np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0);chi=len(v)-len(e)+len(t);assert chi==0,(m['name'],chi);holes[m['name']]=dict(closed=True,euler_characteristic=int(chi),one_true_through_hole=True)
result['through_hole_checks']=holes
np.savez_compressed(OUT/'geometry.npz',**data);(OUT/'validation.json').write_text(json.dumps(result,indent=2));print('Validated',len(objects),'closed solids,',total,'triangles',result['bounds'],'turn width',result['maximum_rotational_width'])
D=json.loads((P/'design.json').read_text());a=math.radians(D['camera_elevation_degrees']);dist=D['camera_distance'];f=np.array([0,-math.sin(a),-math.cos(a)]);u=np.array([0,math.cos(a),-math.sin(a)])
def projected(param):
 y,lens=param;q=V-np.array([0,y+dist*math.tan(a),dist]);z=q@f;return 550-(q@u)/z*(1100*lens/36)
param=np.array([D['camera_target_height'],D['lens']],float)
for _ in range(7):
 y=projected(param);err=np.array([y.min()-154,y.max()-950]);J=[]
 for k,h in [(0,.0001),(1,.001)]:
  p=param.copy();p[k]+=h;yy=projected(p);J.append((np.array([yy.min(),yy.max()])-np.array([y.min(),y.max()]))/h)
 param-=np.linalg.solve(np.array(J).T,err)
cam=sc.camera;cam.location=(0,-dist,param[0]+dist*math.tan(a));cam.rotation_euler=(Vector((0,0,float(param[0])))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=float(param[1])
(OUT/'camera.json').write_text(json.dumps(dict(distance=dist,elevation_degrees=D['camera_elevation_degrees'],target_y=float(param[0]),lens=float(param[1]),common_projected_top=154,common_projected_bottom=950),indent=2))
sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.cycles.samples=64;sc.cycles.use_denoising=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
shutil.copy2(P/'design.json',OUT/'design.json');shutil.copy2(R/'treasure_chest.blend',OUT/'chest.blend')

meta=json.loads((OUT/'design.json').read_text());meta.update(body_width=5.100,body_depth=3.200,lid_width=5.200,lid_depth=3.300,body_metal_thickness_revision=24);(OUT/'design.json').write_text(json.dumps(meta,indent=2))
