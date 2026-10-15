"""Flatter, wider coin shell prototype, authorized by the owner on 2026-10-14."""
from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
R=Path('/Users/antonioperedo/Desktop/badges/water_match_20261014')
scene=bpy.data.scenes['water_match'];bpy.context.window.scene=scene
profile=np.array([[2.420,.190],[2.485,.300],[2.945,.300],[3.015,.230],[3.015,-.560],[2.945,-.630],[2.485,-.630],[2.420,-.520]])
roles=['inner','face','bevel','side','bevel','face','inner','inner'];segments=256
points=[];triangles=[];normals=[];face_roles=[]
def clipped(poly):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>=-2.895;ib=b[1]>=-2.895
  if ia:result.append(a)
  if ia!=ib:result.append(a+(b-a)*((-2.895-a[1])/(b[1]-a[1])))
 return result
for j,(p1,p2) in enumerate(zip(profile,np.roll(profile,-1,axis=0))):
 dr,dz=p2-p1
 for k in range(segments):
  a=k*2*math.pi/segments;b=(k+1)*2*math.pi/segments
  quad=[np.array([p1[0]*math.cos(a),p1[0]*math.sin(a),p1[1]]),np.array([p2[0]*math.cos(a),p2[0]*math.sin(a),p2[1]]),np.array([p2[0]*math.cos(b),p2[0]*math.sin(b),p2[1]]),np.array([p1[0]*math.cos(b),p1[0]*math.sin(b),p1[1]])]
  poly=clipped(quad)
  for q in range(1,len(poly)-1):
   tri=np.array([poly[0],poly[q],poly[q+1]])
   if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))<1e-10:continue
   start=len(points);points.extend(tri.tolist());triangles.append([start,start+1,start+2]);face_roles.append(roles[j])
   angle=np.arctan2(tri[:,1],tri[:,0]);n=np.c_[-dz*np.cos(angle),-dz*np.sin(angle),np.full(3,dr)];n/=np.linalg.norm(n,axis=1,keepdims=True);normals.append(n)
p=np.asarray(points);t=np.asarray(triangles);n=np.asarray(normals);assert p[:,1].min()>=-2.895001
np.savez_compressed(R/'shell_geometry.npz',points=p,triangles=t,normals=n,roles=np.array(face_roles))
(R/'shell_design.json').write_text(json.dumps({'outer_radius':3.015,'inner_radius':2.420,'flat_face_inner_radius':2.485,'flat_face_outer_radius':2.945,'band_width':.595,'depth':.930,'center_z':-.165,'floor_cut':-2.895,'profile':profile.tolist()},indent=2))
for obj in list(scene.objects):
 if obj.type=='MESH' and (obj.name.startswith(('Casing___','Inner_channel___','Inner_edge___','Rim_inner_lip___','Rear_Inner_edge___'))):bpy.data.objects.remove(obj,do_unlink=True)
mesh=bpy.data.meshes.new('Flat_wide_rim_geometry');mesh.from_pydata(p.tolist(),[],t.tolist());mesh.update();mesh.normals_split_custom_set(n.reshape(-1,3).tolist())
obj=bpy.data.objects.new('Casing___smooth_rounded_outer_edge_mobile_geometry',mesh);scene.collection.objects.link(obj)
for role,color,rough in [('face',(.24,.25,.27,1),.34),('bevel',(.19,.20,.22,1),.32),('side',(.085,.095,.11,1),.48),('inner',(.055,.060,.070,1),.48)]:
 mat=bpy.data.materials.new('Silver___circumferential_brushed_steel' if role=='face' else 'Shell_'+role);mat.use_nodes=True;mat.diffuse_color=color;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Metallic'].default_value=1;bsdf.inputs['Roughness'].default_value=rough;mesh.materials.append(mat)
for polygon,role in zip(mesh.polygons,face_roles):polygon.material_index=['face','bevel','side','inner'].index(role);polygon.use_smooth=True
uv=mesh.uv_layers.new(name='USDZ_UV')
for loop in mesh.loops:
 q=mesh.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((q.x+3.015)/6.03,(q.y+3.015)/6.03)
bpy.data.libraries.write(str(R/'water.blend'),{scene},compress=True)
print('New flat, wider rim built: width .595, depth .930, original outer diameter retained.')
