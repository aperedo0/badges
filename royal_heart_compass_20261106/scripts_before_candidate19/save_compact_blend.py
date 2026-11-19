"""Create a matching editable file in a separate, empty Blender process."""
from pathlib import Path
import bpy,json,sys,zipfile,tempfile,hashlib,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;key=sys.argv[sys.argv.index('--')+1];R=ROOT/key;C=R/'candidate18';cfg=json.loads((R/'design.json').read_text());specs=json.loads((C/'materials.json').read_text());model=C/'model.usdz'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.name=cfg['name']+' compact editable checkpoint'
with tempfile.TemporaryDirectory(prefix=key+'_usd_import_',dir='/tmp') as tmp:
 base=Path(tmp)
 with zipfile.ZipFile(model) as z:
  z.extractall(base);expected={Path(n).name:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.png')}
 usd=next(p for p in base.iterdir() if p.suffix in ['.usd','.usdc','.usda'])
 bpy.ops.wm.usd_import(filepath=str(usd),import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK',tex_name_collision_mode='OVERWRITE')
 for filename in expected:
  if not any(Path(image.filepath).name==filename for image in bpy.data.images):
   image=bpy.data.images.load(str(base/'textures'/filename),check_existing=False);image.pack()
   if filename=='velvet_occlusion.png':
    image.colorspace_settings.name='Non-Color'
    for mat in bpy.data.materials:
     if mat.name.endswith('_fold_velvet'):
      node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='Native geometric ambient occlusion';node.image=image
 meshes=[ob for ob in scene.objects if ob.type=='MESH'];triangles=0
 for ob in meshes:
  ob['export_badge']=True;ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles)
  for material in ob.data.materials:
   role=material.name
   if role.startswith('CrestGem_'):
    bs=material.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=specs[role]['ior']
    material['native_optics_profile']=role
   elif role.endswith('_velvet'):
    bs=material.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Sheen Weight'].default_value=.65;bs.inputs['Specular IOR Level'].default_value=.06
 source=json.loads((C/'validation.json').read_text());assert len(meshes)==source['after']['meshes'];assert triangles==source['after']['triangles']
 packed={}
 for image in bpy.data.images:
  if image.source!='FILE':continue
  if not image.packed_file:image.pack()
  if image.packed_file:
   name=Path(image.filepath).name;packed[name]=hashlib.sha256(image.packed_file.data).hexdigest()
 assert all(packed.get(name)==sha for name,sha in expected.items()),(expected,packed)
 ref=bpy.data.objects.new(cfg['name']+' owner reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'),check_existing=False);ref.data.pack();ref.empty_display_size=6;ref.location=(-7,0,0);scene.collection.objects.link(ref)
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
 scene.world=bpy.data.worlds.new('Working studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.12,.15,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 for name,loc,power,size in [('Working key',(-4,6,6),1100,5),('Working fill',(5,2,3),700,3),('Working back',(0,4,-5),900,4)]:
  data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
 camera=bpy.data.cameras.new('Working camera');ob=bpy.data.objects.new('Working camera',camera);scene.collection.objects.link(ob);ob.location=(0,.26,14);ob.rotation_euler=(Vector((0,.26,0))-ob.location).to_track_quat('-Z','Y').to_euler();camera.type='ORTHO';camera.ortho_scale=7.2;scene.camera=ob
 scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 path=C/'source'/(key+'_compact.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 report=dict(meshes=len(meshes),triangles=triangles,all_asset_textures_packed_byte_identically=True,packed_textures=expected,complete_editable_checkpoint=str(path),native_gem_profiles_preserved=True)
 (C/'checkpoint_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
