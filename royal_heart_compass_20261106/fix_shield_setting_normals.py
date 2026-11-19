from pathlib import Path
import bpy,bmesh,numpy as np,json
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');C=R/'amethyst_crown/candidate06';G=json.loads((C/'groups.json').read_text());A=dict(np.load(C/'geometry.npz'));D=dict(np.load(C/'blender_geometry.npz'));scene=bpy.context.scene;fixed=[]
for i,g in enumerate(G):
 if 'sculpted shield gold setting' not in g['name']:continue
 expected=A[str(i)+'_points'];matches=[]
 for ob in scene.objects:
  if ob.type!='MESH' or not ob.name.startswith(g['name']) or len(ob.data.vertices)!=len(expected):continue
  p=np.array([v.co[:] for v in ob.data.vertices],np.float32)
  if np.array_equal(p,expected):matches.append(ob)
 assert len(matches)==1,(i,len(matches));ob=matches[0];me=ob.data
 bm=bmesh.new();bm.from_mesh(me)
 for face in bm.faces:face.normal_flip()
 bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles()
 p=np.array([v.co[:] for v in me.vertices],np.float32);t=np.array([x.vertices[:] for x in me.loop_triangles],np.int32);loops=np.array([x.loops[:] for x in me.loop_triangles],np.int32)
 assert np.array_equal(p,expected)
 q=p[t];volume=float(np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6);assert volume>0
 n=np.empty(len(me.corner_normals)*3,np.float32);me.corner_normals.foreach_get('vector',n);n=n.reshape(-1,3)[loops]
 uv=me.uv_layers['BadgeUV'];coords=np.array([uv.data[li].uv[:] for li in loops.ravel()],np.float32).reshape(-1,3,2)
 A[str(i)+'_triangles']=t;D[str(i)+'_triangles']=t;D[str(i)+'_normals']=n;D[str(i)+'_uv']=coords;fixed.append(dict(part=i,volume=volume))
np.savez_compressed(C/'geometry.npz',**A);np.savez_compressed(C/'blender_geometry.npz',**D)
bpy.data.libraries.write(str(C/'source/amethyst_crown.blend'),{scene},compress=True)
(C/'shield_setting_normals.json').write_text(json.dumps(dict(outward_winding_verified=True,parts=fixed),indent=2)+'\n');print(fixed)
