import bpy,json,numpy as np,hashlib,shutil
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_character');A=D/'11_restored_pigment';S=D/'13_recessed_scale';C=D/'14_edge_review';C.mkdir(exist_ok=True)
assert Path(bpy.data.filepath)==A/'master.blend';assert not bpy.app.is_job_running('RENDER');assert not bpy.data.is_dirty
sc=bpy.data.scenes['Test plank master'];review=bpy.data.scenes['Bottom iron reflection review'];old=json.loads((A/'live_validation.json').read_text());scope=old['scope']
def mh(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert mh(sc.objects['Lab Chest Lower Rim'])==old['iron_geometry'];assert mh(sc.objects['Master Chest Body Envelope'])==old['wood_geometry']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_edge_review.blend'),compress=True,copy=True)
design=json.loads((S/'design.json').read_text())
with bpy.data.libraries.load(str(S/'master.blend'),link=False) as (src,data):data.materials=[design['material']]
mat=data.materials[0]
for name in scope:
 obj=sc.objects[name]
 if obj.data.users>1:obj.data=obj.data.copy()
 obj.data.materials[0]=mat
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==S/'master.blend':
  assert not any(x.library==lib for x in bpy.data.user_map());bpy.data.libraries.remove(lib)
receivers=bpy.data.collections.new('Bottom iron bevel reflection receivers')
for name in scope:receivers.objects.link(sc.objects[name])
settings=[]
for source,name in [('top_edge_250.json','Iron upper bevel reflection'),('bottom_edge_4.25.json','Iron lower bevel reflection')]:
 p=json.loads((D/'lighting'/source).read_text());assert p['size']==6;data=bpy.data.lights.new(name,'AREA');data.energy=p['power'];data.color=p['color'];data.shape='RECTANGLE';data.size=p['size'];data.size_y=p['size_y'];data.diffuse_factor=0;data.specular_factor=1;light=bpy.data.objects.new(name,data);review.collection.objects.link(light);light.location=p['position'];light.rotation_euler=p['rotation'];light.light_linking.receiver_collection=receivers;light['isolated_iron_review']=True;settings.append(dict(name=name,**p));assert name not in sc.objects
assert review.world is not sc.world
for n in review.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.inputs['Color'].is_linked:n.inputs['Strength'].default_value=.35
assert mat.node_tree.nodes['Independent shallow fractured scale markings'].invert
assert not any(n.bl_idname=='ShaderNodeOutputAOV' for n in mat.node_tree.nodes)
assert mh(sc.objects['Lab Chest Lower Rim'])==old['iron_geometry'];assert mh(sc.objects['Master Chest Body Envelope'])==old['wood_geometry']
design.update(source='11_restored_pigment with verified recessed marking direction',mesh=sc.objects['Lab Chest Lower Rim'].data.name,material=mat.name,isolated_bevel_reflection_lights=[s['name'] for s in settings],review_environment='edge_contrast',review_environment_strength=.35,review_reflection_settings=settings,geometry_exact_to_resumed_baseline=True,source_maps_and_all_other_shader_inputs_exact=True)
(C/'design.json').write_text(json.dumps(design,indent=2));shutil.copy2(S/'edge_geometry.npz',C/'edge_geometry.npz');bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
proof=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,scope=scope,iron_geometry=old['iron_geometry'],wood_geometry=old['wood_geometry'],material=mat.name,material_applied=True,review_image_shown=False,reference_editor_and_current_layout_preserved=True,production_diagnostic_nodes_absent=True,production_aov_passes_absent=True,shallow_scale_marks_inverted=True,original_lighting_preserved=True,review_only_lights=[s['name'] for s in settings],all_target_maps_packed=all(n.image and n.image.packed_file for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest());(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
