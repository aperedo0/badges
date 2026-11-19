import bpy,json,numpy as np,hashlib
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_character');choice=json.loads((D/'selection.json').read_text());C=D/choice['candidate'];checkpoint=json.loads((D/'checkpoint.json').read_text());a=json.loads((C/'design.json').read_text());sc=bpy.data.scenes['Test plank master'];target=sc.objects['Lab Chest Lower Rim'];wood=sc.objects['Master Chest Body Envelope'];assert not bpy.app.is_job_running('RENDER');assert Path(bpy.data.filepath)==Path(checkpoint['file'])
def mh(o):
 v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v);return hashlib.sha256(v.tobytes()).hexdigest()
assert mh(target)==checkpoint['iron_geometry'] and mh(wood)==checkpoint['wood_geometry'];png=C/('iron_'+choice['environment']+'_final.png');png=png if png.exists() else C/('iron_'+choice['environment']+'.png');assert png.exists();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'live_before_promotion.blend'),compress=True,copy=True)
with bpy.data.libraries.load(str(C/'master.blend'),link=False) as (src,data):
 assert a['mesh'] in src.meshes;data.meshes=[a['mesh']]
target.data=data.meshes[0];material=target.data.materials[0]
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:
 knob=sc.objects[name];knob.data=knob.data.copy();knob.data.materials[0]=material
users=bpy.data.user_map()
for lib in list(bpy.data.libraries):
 if Path(bpy.path.abspath(lib.filepath))==C/'master.blend':
  assert not users.get(lib) and not any(x.library==lib for x in users);bpy.data.libraries.remove(lib)
# The existing review lights are already calibrated. Update its world only, avoiding compounded light changes.
review=bpy.data.scenes['Bottom iron reflection review'];review.world=review.world.copy();nt=review.world.node_tree;bg=next(n for n in nt.nodes if n.type=='BACKGROUND' and n.inputs['Color'].is_linked);bg.inputs['Strength'].default_value=.65;source=bg.inputs['Color'].links[0].from_socket;t=nt.nodes.new('ShaderNodeMixRGB');t.name='Restrained warm studio reflection tint';t.blend_type='MULTIPLY';t.inputs[0].default_value=1;t.inputs[2].default_value=(1,.88,.72,1);nt.links.new(source,t.inputs[1]);nt.links.new(t.outputs[0],bg.inputs['Color']);review.cycles.samples=128
shown=False
for window in list(bpy.context.window_manager.windows)[1:]:
 for area in window.screen.areas:
  if area.type=='IMAGE_EDITOR':
   im=bpy.data.images.load(str(png),check_existing=True);im.name='Weathered bottom iron review';im.use_view_as_render=False;im.pack();area.spaces.active.image=im;region=next(r for r in area.regions if r.type=='WINDOW')
   with bpy.context.temp_override(window=window,area=area,region=region):bpy.ops.image.view_all(fit_view=True)
   shown=True
assert shown;assert mh(wood)==checkpoint['wood_geometry'];a.update(mesh=target.data.name,material=material.name,review_environment=choice['environment']);(C/'design.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);proof=dict(file=bpy.data.filepath,dirty=bpy.data.is_dirty,wood_geometry=mh(wood),iron_geometry=mh(target),scope=['Lab Chest Lower Rim','Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4'],review_image_shown=shown,original_reference_and_main_framing_preserved=True,review_world_only_updated=True,material=material.name,all_target_maps_packed=all(n.image and n.image.packed_file for n in material.node_tree.nodes if n.type=='TEX_IMAGE'),file_sha256=hashlib.sha256((C/'master.blend').read_bytes()).hexdigest());(C/'live_validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
