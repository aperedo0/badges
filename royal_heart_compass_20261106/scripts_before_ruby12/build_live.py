import os
"""Import a complete working badge into a new live Blender scene."""
from pathlib import Path
import json, bpy, numpy as np
from mathutils import Quaternion,Vector
ROOT=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
key=(ROOT/'active.txt').read_text().strip();R=ROOT/key;C=R/os.environ.get('BADGE_CANDIDATE','candidate21');cfg=json.loads((R/'design.json').read_text())
scene=bpy.data.scenes.new(cfg['name']+' complete working scene');bpy.context.window.scene=scene
D=np.load(C/'geometry.npz');groups=json.loads((C/'groups.json').read_text());specs=json.loads((C/'materials.json').read_text());mats={};out={}
for role,spec in specs.items():
 m=bpy.data.materials.new(role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*spec['color'],1);bs.inputs['Metallic'].default_value=spec['metallic'];bs.inputs['Roughness'].default_value=spec['roughness']
 bs.inputs['IOR'].default_value=1.1 if role.endswith('_velvet') else spec.get('ior',1.46)
 if 'sheen' in spec:bs.inputs['Sheen Weight'].default_value=spec['sheen'];bs.inputs['Sheen Roughness'].default_value=.4;bs.inputs['Specular IOR Level'].default_value=.06
 if role.startswith('CrestGem_'):bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=spec['ior']
 filename='gold_color.png' if role=='gold' and (C/'textures/gold_color.png').exists() else 'quilted_band_color.png' if role=='purple_velvet' and (C/'textures/quilted_band_color.png').exists() else 'chart_color.png' if role=='navy' else 'velvet_fold_color.png' if role.endswith('_fold_velvet') and (C/'textures/velvet_fold_color.png').exists() else 'velvet_color.png' if role.endswith('_velvet') else ''
 if filename and (C/'textures'/filename).exists():
  uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='BadgeUV';tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'textures'/filename),check_existing=False);tex.image.pack();m.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 if role=='gold' and (C/'textures/gold_roughness.png').exists():
  uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='BadgeUV';tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'textures/gold_roughness.png'),check_existing=False);tex.image.colorspace_settings.name='Non-Color';tex.image.pack();m.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
 mats[role]=m
for i,g in enumerate(groups):
 p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];me=bpy.data.meshes.new(g['name']);me.from_pydata(p.tolist(),[],t.tolist());me.update();ob=bpy.data.objects.new(g['name'],me);scene.collection.objects.link(ob);me.materials.append(mats[g['mat']]);ob['export_badge']=True
 for f in me.polygons:f.use_smooth=g['smooth']
 uv=me.uv_layers.new(name='BadgeUV')
 uvcoords=np.array([[(p[v,0]+3.25)/6.5,(p[v,1]+2.455)/6.5] for v in t.ravel()],np.float32).reshape(-1,3,2)
 if 'velvet cushion' in g['name']:
  gridN,gridM=g.get('cloth_grid',[144,40])
  uvcoords=np.stack([(t%gridN)/gridN,(t//gridN)/gridM],axis=-1).astype(np.float32)
  seam=np.ptp(uvcoords[:,:,0],axis=1)>.5
  uvcoords[seam,:,0]=np.where(uvcoords[seam,:,0]<.5,1.,uvcoords[seam,:,0])
 if 'band_grid' in g:
  bandN,bandM=g['band_grid'];limit=bandN*(bandM+1)
  uvcoords=np.stack([(t%bandN)/bandN,np.where(t<limit,(t//bandN)/bandM,np.where(t<limit+bandN,0.,1.))],axis=-1).astype(np.float32)
  seam=np.ptp(uvcoords[:,:,0],axis=1)>.5
  uvcoords[seam,:,0]=np.where(uvcoords[seam,:,0]<.5,1.,uvcoords[seam,:,0])
 for poly,coords in zip(me.polygons,uvcoords):
  for li,xy in zip(poly.loop_indices,coords):uv.data[li].uv=xy
 me.calc_loop_triangles();corner=np.empty(len(me.corner_normals)*3,np.float32);me.corner_normals.foreach_get('vector',corner);corner=corner.reshape(-1,3)
 tri=np.array([x.vertices[:] for x in me.loop_triangles],np.int32);loops=np.array([x.loops[:] for x in me.loop_triangles],np.int32)
 out[str(i)+'_points']=p;out[str(i)+'_triangles']=tri
 normals=corner[loops]
 if g['name']=='Custom gold ocean navigator frame':
  flat_face=np.all(np.isin(tri%8,[3,4]),axis=1)
  normals[flat_face]=np.array([0,0,1],np.float32)
 out[str(i)+'_normals']=normals
 out[str(i)+'_uv']=np.array([uv.data[li].uv[:] for li in loops.ravel()],np.float32).reshape(-1,3,2)
np.savez_compressed(C/'blender_geometry.npz',**out)
ref=bpy.data.objects.new(cfg['name']+' reference image',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'),check_existing=False);ref.data.pack();ref.empty_display_size=6;ref.location=(-7,0,0);scene.collection.objects.link(ref)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.world=bpy.data.worlds.new(key+' working studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.18,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,power,size in [('Upper left softbox',(-4,6,6),1100,5),('Right strip',(5,2,2),850,3),('Lower fill',(-2,-3,4),500,3),('Rear rim',(1,4,-5),950,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,0))-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new(key+' inspection camera');ob=bpy.data.objects.new('Working front inspection',cam);scene.collection.objects.link(ob);ob.location=(0,.30,14);ob.rotation_euler=(Vector((0,.18,0))-ob.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=7.2;scene.camera=ob
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(C/'review/blender_front.png')
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,.25,0));s.region_3d.view_distance=9;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(C/'source'/(key+'.blend')),{scene},compress=True)
print(key,len(groups),'editable pieces saved')
