import bpy,numpy as np,json,hashlib,shutil
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';S=R/'phase03/wood_sample44';C=S/'candidate01';D=json.loads((S/'design.json').read_text());sc=bpy.context.scene
assert 'Status: APPROVED' in (S/'PLAN.md').read_text();assert bpy.data.filepath==str(R/'treasure_chest.blend') and not bpy.data.is_dirty and sc.frame_current==0
policy=json.loads((R/'work_mode.json').read_text());assert policy['manual_work_authorized'] and policy['wood_grain_authorized'] and not policy['material_finish_authorized']
exec(compile((P/'tools/frame36_geometry.py').read_text(),'g36','exec'));exec(compile((P/'tools/hinge38_geometry.py').read_text(),'g38','exec'))
B=P/'candidate43';assert hashlib.sha256((R/'treasure_chest.blend').read_bytes()).digest()==hashlib.sha256((B/'chest.blend').read_bytes()).digest();frozen={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in B.rglob('*') if f.is_file()};(C/'baseline43_hashes.json').write_text(json.dumps(frozen,indent=2));model=[o for o in sc.objects if o.type=='MESH' and o.get('full_form')];assert len(model)==155;before={o.name:capture36(o) for o in model};parents={o.name:dict(parent=o.parent.name if o.parent else None,inverse=np.array(o.matrix_parent_inverse).tolist(),basis=np.array(o.matrix_basis).tolist()) for o in model};keybefore=capture36(sc.objects['Chest Removable Crank Key']);ob=sc.objects[D['part']];me=ob.data;local=local38(before[ob.name]['v']);prior_indices=[f.material_index for f in me.polygons];gray=list(me.materials)
def graph(m):
 return dict(name=m.name,nodes=[dict(name=n.name,type=n.bl_idname,inputs={s.name:(list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value) for s in n.inputs if hasattr(s,'default_value')}) for n in m.node_tree.nodes],links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
oldmaterials={m.name:graph(m) for m in gray};selected=[]
for f in me.polygons:
 q=local[list(f.vertices)];n=np.cross(q[1]-q[0],q[2]-q[0]);n/=np.linalg.norm(n)
 if q[:,1].max()<=-.84+2e-6 and q[:,2].min()>1.53 and n[2]>.55:selected.append(f.index)
expected=json.loads((S/'selection_preflight.json').read_text());assert selected==expected['faces'] and len(selected)==28
# Same predicate must reject a real opposite lower back face.
back=[f.index for f in me.polygons if local[list(f.vertices),1].max()<-.84 and local[list(f.vertices),2].max()<-1.53];assert back and not set(back).intersection(selected)
assert me.uv_layers.get(D['uv']) is None;uv=me.uv_layers.new(name=D['uv']);b=D['bounds'];pad=D['padding'];W=D['texture_width'];H=D['texture_height'];coords=[]
for f in me.polygons:
 for li in f.loop_indices:
  q=local[me.loops[li].vertex_index];u=pad/W+(q[0]-b['xmin'])/(b['xmax']-b['xmin'])*(W-2*pad)/W;v=pad/H+(q[1]-b['ymin'])/(b['ymax']-b['ymin'])*(H-2*pad)/H;uv.data[li].uv=(float(u),float(v))
  if f.index in selected:coords.append((u,v))
coords=np.array(coords);assert (coords[:,0]>=pad/W-1e-6).all() and (coords[:,0]<=1-pad/W+1e-6).all() and (coords[:,1]>=pad/H-1e-6).all() and (coords[:,1]<=1-pad/H+1e-6).all()
mat=bpy.data.materials.new(D['material']);mat.use_nodes=True;mat.diffuse_color=(.48,.21,.07,1);nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['IOR'].default_value=D['ior'];bsdf.inputs['Specular IOR Level'].default_value=D['specular_level'];bsdf.inputs['Coat Weight'].default_value=0;bsdf.inputs['Emission Strength'].default_value=0
uvnode=nodes.new('ShaderNodeUVMap');uvnode.name='Single plank explicit UV';uvnode.uv_map=D['uv'];uvnode.location=(-650,100);images={}
for role,file,space,y in [('albedo','wood_albedo.png','sRGB',260),('roughness','wood_roughness.png','Non-Color',0),('normal','wood_normal.png','Non-Color',-260)]:
 img=bpy.data.images.load(str(C/'textures'/file),check_existing=False);img.colorspace_settings.name=space;img.pack();images[role]=img.name;n=nodes.new('ShaderNodeTexImage');n.name='Single plank '+role;n.image=img;n.interpolation='Linear';n.extension='EXTEND';n.location=(-430,y);links.new(uvnode.outputs['UV'],n.inputs['Vector'])
 if role=='albedo':links.new(n.outputs['Color'],bsdf.inputs['Base Color'])
 elif role=='roughness':links.new(n.outputs['Color'],bsdf.inputs['Roughness'])
 else:
  normal=nodes.new('ShaderNodeNormalMap');normal.name='Single plank physical tangent normal';normal.space='TANGENT';normal.uv_map=D['uv'];normal.inputs['Strength'].default_value=1;normal.location=(-120,-240);links.new(n.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
me.materials.append(mat);slot=len(me.materials)-1
for f in me.polygons:
 if f.index in selected:f.material_index=slot
for f,old in zip(me.polygons,prior_indices):assert f.material_index==(slot if f.index in selected else old)
assert sum(f.material_index==slot for f in me.polygons)==28 and all(graph(m)==oldmaterials[m.name] for m in gray)
for o in model:
 a=capture36(o);old=before[o.name]
 for key in ('vertex_hash','triangle_hash','normal_hash'):assert a[key]==old[key],(o.name,'geometry changed',key)
 if o is not ob:assert a['materials']==old['materials'],(o.name,'other part material changed')
 now=dict(parent=o.parent.name if o.parent else None,inverse=np.array(o.matrix_parent_inverse).tolist(),basis=np.array(o.matrix_basis).tolist());assert now==parents[o.name]
for k in ('vertex_hash','triangle_hash','normal_hash','materials'):assert capture36(sc.objects['Chest Removable Crank Key'])[k]==keybefore[k]
for rel,sha in frozen.items():assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha,rel
report=dict(single_plank_only=True,part=ob.name,faces=selected,polygon_count=len(selected),all155_mesh_geometry_and_normals_unchanged=True,other154_parts_materials_unchanged=True,original_shared_gray_material_unchanged=True,opposite_back_faces_rejected=len(back),parents_unchanged=True,material=mat.name,uv=D['uv'],uv_min=coords.min(0).tolist(),uv_max=coords.max(0).tolist(),images=images,all_images_packed=all(i.packed_file is not None for i in [bpy.data.images[n] for n in images.values()]),metallic=0,emission=0,other_planks_finished=False)
(C/'isolation_proof.json').write_text(json.dumps(report,indent=2));(C/'before_geometry_manifest.json').write_text(json.dumps({n:{k:v[k] for k in ('vertex_hash','triangle_hash','normal_hash','materials')} for n,v in before.items()},indent=2));(C/'source').mkdir(exist_ok=True)
for f in ('apply_live.py','generate_wood.py'):shutil.copy2(S/f,C/'source'/f)
old=bpy.context.preferences.filepaths.save_version
try:bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'chest.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:v for k,v in report.items() if k!='faces'}))
