import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Matrix
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/final_polish');selection=json.loads((D/'selection.json').read_text());C=D.parent/selection['selected'];asset=json.loads((C/'asset.json').read_text());checkpoint={'source': '/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/AE_controlled_fibers/master.blend', 'source_file_sha256': 'b6d750678979478829e1c816985d0934764b70e6ed3d2f7e3425fd0183438ea8', 'geometry_sha256': 'e937f8fa06cbc244a96933b97e07e16aa36180da66654c48125758edb94146e5', 'material': ['Chest Phase 1 neutral clay', 'Wood Lab AE_controlled_fibers'], 'reference_camera': 'Owner reference comparison camera', 'live_dirty': False};win=bpy.context.window_manager.windows[0];sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];coords=np.empty(len(body.data.vertices)*3,np.float32);body.data.vertices.foreach_get('co',coords)
assert hashlib.sha256(coords.tobytes()).hexdigest()==selection.get('input_geometry_sha256',checkpoint['geometry_sha256']),'Live geometry changed since checkpoint'
source=bpy.data.scenes['Chest Complete Form Phase 1'];ref=sc.objects['First chest owner reference'];assert ref is source.objects[ref.name]
oldpref=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:
 bpy.ops.wm.save_as_mainfile(filepath=str(D/selection.get('snapshot','live_before_selection.blend')),compress=True,copy=True)
 win.scene=sc
 oldmesh=body.data
 with bpy.data.libraries.load(str(C/'master.blend'),link=False) as (available,target):
  assert asset['mesh'] in available.meshes;target.meshes=[asset['mesh']]
 newmesh=target.meshes[0];assert len(newmesh.vertices)==len(oldmesh.vertices)
 for i,m in enumerate(newmesh.materials):
  if not m or not m.name.startswith('Wood Lab '):newmesh.materials[i]=oldmesh.materials[i]
 body.data=newmesh;body['timber_refinement']=selection['selected']
 lights=json.loads((C/('lighting_'+selection['light']+'.json')).read_text())
 for name,data in lights.items():
  light=sc.objects[name]
  assert all(light.data is not o.data for o in source.objects if o.type=='LIGHT'),'Source light data must remain independent'
  light.matrix_world=Matrix(data['matrix']);light.data.energy=data['energy'];light.data.color=data['color'];light.data.size=data['size']
 for area in win.screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='RENDERED'
 sc.cycles.samples=96;sc.cycles.preview_samples=48;sc.cycles.use_denoising=True
 users=bpy.data.user_map()
 for lib in list(bpy.data.libraries):
  if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
   assert not users.get(lib) and not any(x.library==lib for x in users)
   bpy.data.libraries.remove(lib)
 bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
 asset['mesh']=newmesh.name;asset['material']=next(m.name for m in body.data.materials if m and m.name.startswith('Wood Lab '));(C/'asset.json').write_text(json.dumps(asset,indent=2))
 proof=dict(file=bpy.data.filepath,selected=selection['selected'],only_target_mesh_swapped=True,owner_layout_and_reference_retained=True,reference_shared_without_reimport=ref is source.objects[ref.name],maps_packed=all(n.image and n.image.packed_file for n in next(m for m in body.data.materials if m and m.name.startswith('Wood Lab ')).node_tree.nodes if n.type=='TEX_IMAGE'))
 (C/'live_save.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
finally:bpy.context.preferences.filepaths.save_version=oldpref
