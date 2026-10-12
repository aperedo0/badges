"""Render actual mesh plane IDs with flat emission, without saving scene changes."""
import bpy,sys,json,numpy as np
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];r=Path(args[0]).resolve()
scene=bpy.context.scene;scene.frame_set(360)
rig=bpy.data.objects['Turntable | one slow 360 degree spin'];rig.animation_data_clear();rig.location=(0,0,0);rig.rotation_euler=(0,0,0);rig.scale=(1,1,1)
for o in list(scene.objects):
 if o.type=='MESH':o.hide_render=True
before=set(bpy.data.objects);bpy.ops.wm.usd_import(filepath=str(r/'mobile/iron_badge_mobile.usdz'),import_materials=True,import_usd_preview=True,import_cameras=False,import_lights=False,create_world_material=False,import_textures_mode='IMPORT_PACK')
new=[o for o in bpy.data.objects if o not in before]
for o in new:
 if o.parent is None:o.matrix_world.identity()
 if o.type=='MESH':o.hide_render=not o.name.startswith('Emblem')
obj=next(o for o in new if o.type=='MESH' and o.name.startswith('Emblem'));obj.data.materials.clear()
d=json.loads((r/'reports/crystal_triangle_planes.json').read_text());normals=np.array(d['canonical_normals'],dtype=np.float32);ns=np.array([n.vector for n in obj.data.corner_normals]).reshape(-1,3,3)
# Imported packed custom normals can differ slightly; each triangle's common
# direction still maps unambiguously to the verified canonical plane.
for i in range(len(normals)):
 mat=bpy.data.materials.new('proof_only_plane_'+str(i));mat.use_nodes=True;mat.node_tree.nodes.clear();out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');em=mat.node_tree.nodes.new('ShaderNodeEmission')
 em.inputs['Color'].default_value=(float(i+1),0,0,1);em.inputs['Strength'].default_value=1;mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);obj.data.materials.append(mat)
for poly,normal in zip(obj.data.polygons,ns[:,0]):poly.material_index=int(np.argmax(normals@normal));poly.use_smooth=True
scene.render.engine='BLENDER_EEVEE';scene.eevee.use_raytracing=False
scene.world=bpy.data.worlds.new('ID world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1)
scene.render.resolution_x=1080;scene.render.resolution_y=1440;scene.render.resolution_percentage=100
scene.render.use_border=True;scene.render.use_crop_to_border=False;scene.render.border_min_x=.19;scene.render.border_max_x=.81;scene.render.border_min_y=.30;scene.render.border_max_y=.77
scene.render.use_compositing=False;scene.render.use_sequencer=False;scene.render.film_transparent=True
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.filepath=str(r/'proof/plane_ids.exr');bpy.ops.render.render(write_still=True)
# EXR preserves scene-linear IDs, independent of tone mapping. Record a label
# only for full-coverage interiors with exact emission, never blended borders.
img=bpy.data.images.load(str(r/'proof/plane_ids.exr'),check_existing=False);a=np.asarray(img.pixels[:],dtype=np.float32).reshape(1440,1080,4)[::-1];values=a[:,:,0];ids=np.rint(values).astype(np.int16)
ids[(np.abs(values-ids)>.001)|(a[:,:,3]<.999)]=0
np.save(r/'proof/plane_ids.npy',ids)
print('ID MASK labels/pixels',[(i,int((ids==i).sum())) for i in np.unique(ids)])
