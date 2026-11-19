import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/lookdev_evidence');W=D.parent;C=W/'V_lookdev_refinement';sc=bpy.data.scenes['Test plank master'];source=bpy.data.scenes['Chest Complete Form Phase 1'];body=sc.objects['Master Chest Body Envelope'];slot=next(i for i,m in enumerate(body.data.materials) if m and m.name.startswith('Wood Lab '));prior=body.data.materials[slot]
a=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',a);assert hashlib.sha256(a.tobytes()).hexdigest()==json.loads((D/'baseline_inventory.json').read_text())['geometry_sha256'];assert prior.name=='Wood Lab U_scan_fibers';assert sc is bpy.context.scene
for suffix in ['Key','Fill','Rear']:assert sc.objects['Lab Chest Development '+suffix].data is not source.objects['Chest Development '+suffix].data
mat=prior.copy();mat.name='Wood Lab V_lookdev_refinement';prior.use_fake_user=True
for role in ['albedo','roughness','normal']:
 im=bpy.data.images.load(str(C/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();mat.node_tree.nodes['Single plank '+role].image=im
body.data.materials[slot]=mat;body['timber_refinement']='V_lookdev_refinement'
key=sc.objects['Lab Chest Development Key'];R=Matrix.Rotation(math.radians(32),3,'Y');p=R@Vector((-1.1,-1.35,1.6));target=Vector((p.x,-p.z,p.y));key.location=(-2,-7,4.6);key.rotation_euler=(target-key.location).to_track_quat('-Z','Y').to_euler();key.data.size=1;key.data.energy=2200;key.data.color=(1,.62,.28)
sc.frame_set(0);sc.cycles.samples=128;sc.cycles.seed=17;sc.cycles.use_denoising=True;sc.view_settings.exposure=0
for suffix in ['Key','Fill','Rear']:sc.objects['Lab Chest Development '+suffix].hide_set(False)
# Keep the existing reference image editor, rendered viewport and camera framing.
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
proof=dict(geometry_sha256=hashlib.sha256(a.tobytes()).hexdigest(),geometry_and_topology_not_edited=True,original_reference_object_retained=sc.objects['First chest owner reference'] is source.objects['First chest owner reference'],original_scene_light_data_independent=True,material=mat.name,all_final_images_packed=True,previous_material_retained_in_file=prior.use_fake_user,layout_preserved=[a.type for a in bpy.context.screen.areas])
(C/'live_save.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
