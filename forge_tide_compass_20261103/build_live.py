"""Build the complete active overnight badge in the live Blender application."""
from pathlib import Path
import json,bpy,numpy as np
from mathutils import Quaternion,Vector
ROOT=Path('/Users/antonioperedo/Desktop/badges/forge_tide_compass_20261103')
key=(ROOT/'active_badge.txt').read_text().strip();R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text())
scene=bpy.data.scenes.new(cfg['name']+' complete working badge');bpy.context.window.scene=scene
# A complete current shell is a hidden size guide, never an exported duplicate.
bpy.ops.wm.usd_import(filepath=str(ROOT.parent/'coin_standard_20261101/family/template/shell_template.usdz'),import_cameras=False,import_lights=False)
for ob in list(scene.objects):ob.hide_viewport=True;ob.hide_render=True;ob['construction_guide']=True
materials={};spec={}
for role in cfg['textured_roles']:
 m=bpy.data.materials.new(key+'_'+role);m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=cfg['roughness'][role]
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='BadgeUV'
 for suffix,socket in [('color','Base Color'),('emission','Emission Color'),('roughness','Roughness')]:
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'textures'/(role+'_'+suffix+'.png')),check_existing=False)
  if suffix=='roughness':tex.image.colorspace_settings.name='Non-Color'
  tex.image.pack();nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
 bs.inputs['Emission Strength'].default_value=8;materials[role]=m
 spec[role]=dict(textured=True,metallic=1,roughness=cfg['roughness'][role])
for role,color,metal,rough in [('side',cfg['side_color'],1,cfg['side_roughness']),('ember_side',[.10,.016,.002],1,.6),('CrestGem_Sapphire',[.015,.04,.24],0,.06),('CrestGem_SapphireAstral',[.003,.012,.075],0,.06)]:
 m=bpy.data.materials.new(role if role.startswith('CrestGem_') else key+'_'+role);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if role.startswith('CrestGem_'):bs.inputs['IOR'].default_value=1.77
 materials[role]=m;spec[role]=dict(textured=False,color=color,metallic=metal,roughness=rough)
D=np.load(C/'geometry.npz');groups=json.loads((C/'groups.json').read_text());out={}
for i,g in enumerate(groups):
 p=D[str(i)+'_points'];t=D[str(i)+'_triangles'].copy();uv=D[str(i)+'_uv']
 edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,cnt=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
 if (cnt==2).all():
  volume=np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()/6
  if volume<0:t=t[:,::-1]
 me=bpy.data.meshes.new(g['name']);me.from_pydata(p.tolist(),[],t.tolist());me.update();ob=bpy.data.objects.new(g['name'],me);scene.collection.objects.link(ob);me.materials.append(materials[g['role']])
 for face in me.polygons:face.use_smooth=g['smooth']
 if g.get('plain_vertical_walls'):
  me.materials.append(materials['side'])
  for face in me.polygons:
   if abs(face.normal.z)<.05:face.material_index=1
 if str(i)+'_normal_hints' in D.files:
  hints=D[str(i)+'_normal_hints'];nn=np.array([hints[l.vertex_index] for l in me.loops],float)
  for face in me.polygons:
   inds=np.array(face.loop_indices);actual=np.array(face.normal[:]);dots=nn[inds]@actual;nn[inds]+=np.maximum(0,.12-dots)[:,None]*actual
  nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-12);me.normals_split_custom_set(nn.tolist());me.update()
 layer=me.uv_layers.new(name='BadgeUV')
 for loop in me.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 me.calc_loop_triangles();out[str(i)+'_points']=np.array([v.co[:] for v in me.vertices],np.float32);out[str(i)+'_triangles']=np.array([t.vertices[:] for t in me.loop_triangles],np.int32)
 out[str(i)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in t.loops] for t in me.loop_triangles],np.float32);out[str(i)+'_uv']=np.array([[layer.data[l].uv[:] for l in t.loops] for t in me.loop_triangles],np.float32)
 out[str(i)+'_side_mask']=np.array([me.polygons[t.polygon_index].material_index==1 for t in me.loop_triangles])
np.savez_compressed(C/'blender_geometry.npz',**out);(C/'material_specs.json').write_text(json.dumps(spec,indent=2)+'\n')
ref=bpy.data.objects.new(cfg['name']+' reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'));ref.data.pack();ref.empty_display_size=6;ref.location=(-6.4,.28,0);scene.collection.objects.link(ref)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,.28,0));s.region_3d.view_distance=9.1;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(C/'source'/(key+'.blend')),{scene},compress=True)
print(cfg['name'],'complete working checkpoint saved')
