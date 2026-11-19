import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate34';sc=bpy.context.scene
Y=Matrix.Rotation(math.radians(32),3,'Y');IN=np.array(Y.inverted());A=np.array(Y)
def world(q):
 p=A@np.array(q);return Vector((p[0],-p[2],p[1]))
def mesh(ob):
 dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();v=np.array([p.co[:] for p in me.vertices]);t=np.array([p.vertices[:] for p in me.loop_triangles]);M=np.array(eo.matrix_world);eo.to_mesh_clear();v=v@M[:3,:3].T+M[:3,3];local=np.c_[v[:,0],v[:,2],-v[:,1]]@IN.T
 return local,t,BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=1e-8)
names=['Chest Shield Lock Plate With Bore','Chest Lock Border With Bore','Chest Lock Backing With Bore','Chest Case Back With Key Bore']
sc.frame_set(0);bpy.context.view_layer.update();fixed={n:mesh(sc.objects[n]) for n in names};apertures=[]
for n,(v,t,tree) in fixed.items():
 hits=[]
 for z in np.linspace(max(v[:,2].min()+.00001,1.78001),min(v[:,2].max()-.00001,2.11699),20):
  for u in np.linspace(0,2*math.pi,192,endpoint=False):
   dr=(math.cos(u),math.sin(u),0);loc,normal,index,distance=tree.ray_cast(world((0,-.536,z)),world(dr),.3)
   if loc is not None and distance<.25:hits.append({'radius':distance,'z':float(z),'angle':float(u),'triangle':index})
 apertures.append({'name':n,'z_extent':[float(v[:,2].min()),float(v[:,2].max())],'minimum_radial_opening':min(hits,key=lambda d:d['radius']) if hits else None})
pairs=[]
for frame in [40,60,90,180,340]:
 sc.frame_set(frame);bpy.context.view_layer.update();key=mesh(sc.objects['Chest Removable Crank Key'])
 for n,f in fixed.items():
  hit=key[2].overlap(f[2]);samples=[]
  for ia,ib in hit[:12]:samples.append({'key_triangle':int(ia),'face_triangle':int(ib),'key_xyz':key[0][key[1][ia]].tolist(),'face_xyz':f[0][f[1][ib]].tolist()})
  if hit:pairs.append({'frame':frame,'fixed':n,'count':len(hit),'samples':samples})
sc.frame_set(0);bpy.context.view_layer.update()
(C/'actual_key_aperture_diagnosis.json').write_text(json.dumps({'apertures':apertures,'pairs':pairs},indent=2))
print(json.dumps({'apertures':apertures,'pairs':[{'frame':p['frame'],'fixed':p['fixed'],'count':p['count'],'first_key_bounds':[np.min(p['samples'][0]['key_xyz'],axis=0).tolist(),np.max(p['samples'][0]['key_xyz'],axis=0).tolist()],'first_plate_bounds':[np.min(p['samples'][0]['face_xyz'],axis=0).tolist(),np.max(p['samples'][0]['face_xyz'],axis=0).tolist()]} for p in pairs]}))
