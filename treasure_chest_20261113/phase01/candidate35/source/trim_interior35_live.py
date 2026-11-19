# Remove only concealed armor inside the new wooden cavity.
import bpy,bmesh,numpy as np,json
from mathutils import Vector
trim_names35=[f'Chest Angular Boot {sx} {sz}' for sx in (-1,1) for sz in (-1,1)]+[f'Chest Body Corner Collar {sx} {sz}' for sx in (-1,1) for sz in (-1,1)]
cut_lo35=np.array([-2.34,-2.0275,-1.39]);cut_hi35=np.array([2.34,.46,1.39]);targets35={};oldtrim35={};trim_stage35={}
for name in trim_names35:assert name in before35
# One real closed clearance cutter, kept hidden as a development tool.
cut=sc.objects.get('Chest Interior Clearance Tool 35')
if cut is None:
 me=bpy.data.meshes.new('Chest Interior Clearance Tool 35');cut=bpy.data.objects.new(me.name,me);sc.collection.objects.link(cut)
else:me=cut.data
bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
for v in bm.verts:v.co=Vector(vector35(cut_lo35+(np.array(v.co)+.5)*(cut_hi35-cut_lo35)))
bm.to_mesh(me);bm.free();me.update();cut['full_form']=False;cut['development_only']=True;cut.hide_render=True;cut.hide_set(False)
selected35=[o.name for o in bpy.context.selected_objects];active35=bpy.context.view_layer.objects.active
try:
 for o in sc.objects:o.select_set(False)
 for name in trim_names35:
  ob=sc.objects[name];old=before35[name];v0=old['v'];t0=old['t'];tn0=old['tn'];tri0=v0[t0];E=tri0[:,1]-tri0[:,0];F=tri0[:,2]-tri0[:,0];G=np.cross(E,F);G/=np.linalg.norm(G,axis=1)[:,None];aa=np.einsum('ij,ij->i',E,E);bb=np.einsum('ij,ij->i',E,F);cc=np.einsum('ij,ij->i',F,F);den=aa*cc-bb*bb
  # Preserve the exact triangles the accepted surface already rendered.
  me=ob.data;me.clear_geometry();me.from_pydata(v0.tolist(),[],t0.tolist());me.update()
  for f,a in zip(me.polygons,old['tattrs']):f.use_smooth=a['smooth'];f.material_index=a['material']
  me.normals_split_custom_set(tn0.reshape(-1,3).tolist());ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.context.view_layer.update()
  mod=ob.modifiers.new('Hidden interior clearance 35','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
  if hasattr(mod,'use_hole_tolerant'):mod.use_hole_tolerant=True
  bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False);me=ob.data;me.update();normals=[];matched=[]
  for face in me.polygons:
   target_face=np.array(face.normal);eligible=np.einsum('ij,j->i',G,target_face)>.999;face_matches=0
   for li in face.loop_indices:
    p=np.array(me.vertices[me.loops[li].vertex_index].co);D=p-tri0[:,0];plane=np.einsum('ij,ij->i',D,G);de=np.einsum('ij,ij->i',D,E);df=np.einsum('ij,ij->i',D,F);u=(cc*de-bb*df)/den;w=(aa*df-bb*de)/den;bary=np.c_[1-u-w,u,w];possible=np.flatnonzero(eligible & (abs(plane)<1e-5) & (bary.min(1)>-2e-4) & (bary.max(1)<1.0002))
    if len(possible):
     k=int(possible[np.argmin(abs(plane[possible]))]);weights=np.clip(bary[k],0,1);weights/=weights.sum();n=(tn0[k]*weights[:,None]).sum(0);n/=np.linalg.norm(n);normals.append(n.tolist());matched.append(True);face_matches+=1
    else:normals.append(target_face.tolist());matched.append(False)
   if face_matches==0:face.use_smooth=False
  assert {a['material'] for a in old['attrs']}=={0},name
  for face in me.polygons:face.material_index=0
  while len(me.materials)>1:me.materials.pop(index=len(me.materials)-1)
  assert me.materials[0] is not None
  me.normals_split_custom_set(normals);targets35[name]=np.array(normals);targets35[name+' matched']=np.array(matched,bool);oldtrim35[name+' v']=v0;oldtrim35[name+' t']=t0;oldtrim35[name+' tn']=tn0
  trim_stage35[name]=dict(old_vertices=len(v0),new_vertices=len(me.vertices),old_triangles=len(t0),new_polygons=len(me.polygons),original_surface_loops=int(sum(matched)),new_cut_loops=int(len(matched)-sum(matched)))
finally:
 cut.hide_set(True)
 for o in sc.objects:o.select_set(o.name in selected35)
 bpy.context.view_layer.objects.active=active35
(C/'trim_stage.json').write_text(json.dumps(trim_stage35,indent=2)+'\n');np.savez_compressed(C/'trim_old.npz',**oldtrim35);np.savez_compressed(C/'trim_normal_targets.npz',**targets35);print('Trimmed eight concealed corner masses to0.010 behind the new wooden cavity surfaces; no exterior armor redesign.')
