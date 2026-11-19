"""Build the complete crest in the connected Blender application."""
from pathlib import Path
import json,bpy,numpy as np
from mathutils import Quaternion,Vector
R=Path('/Users/antonioperedo/Desktop/badges/aurora_mountain_20261101');C=R/(R/'candidate.txt').read_text().strip()
scene=bpy.data.scenes.new('Aurora Mountain complete crest');bpy.context.window.scene=scene
# Keep a complete approved shell as a hidden construction guide.
bpy.ops.wm.usd_import(filepath=str(R.parent/'coin_standard_20261101/family/template/shell_template.usdz'),import_cameras=False,import_lights=False)
for ob in list(scene.objects):
 ob.hide_viewport=True;ob.hide_render=True;ob['construction_guide']=True
spec={
 'silver':((.58,.55,.51),1.,.32),
 'gold':((.92,.67,.25),1.,.30),
 'gold_trim':((.25,.12,.025),1.,.44),
 'gold_side':((.30,.14,.035),1.,.50),
 'star':((.78,.49,.10),1.,.26),
 'star_minor':((.78,.49,.10),1.,.32),
 'star_core':((1.,.68,.15),.0,.30),
 'rock_edge':((.015,.022,.06),.2,.52),
 'sky':((.002,.003,.01),1.,.80),
 'rock':((.02,.03,.07),1.,.66),
 'CrestGem_Amethyst':((.25,.015,.45),0.,.055)}
materials={}
for role,(color,metal,rough) in spec.items():
 m=bpy.data.materials.new(role if role.startswith('CrestGem_') else 'AuroraMountain_'+role);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if role in ['sky','rock']:
  nt=m.node_tree;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='AuroraUV'
  for suffix,socket in [('color','Base Color'),('emission','Emission Color')]:
   tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'textures'/(role+'_'+suffix+'.png')),check_existing=False);tex.image.pack()
   nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
  bs.inputs['Emission Strength'].default_value=8
 if role=='star':bs.inputs['Emission Color'].default_value=(.12,.045,.002,1);bs.inputs['Emission Strength'].default_value=1
 if role=='star_minor':bs.inputs['Emission Color'].default_value=(.8,.35,.025,1);bs.inputs['Emission Strength'].default_value=1
 if role=='star_core':bs.inputs['Emission Color'].default_value=(4,2,.5,1);bs.inputs['Emission Strength'].default_value=1
 if role=='CrestGem_Amethyst':bs.inputs['IOR'].default_value=1.55
 materials[role]=m
D=np.load(C/'geometry.npz');groups=json.loads((C/'groups.json').read_text());output={}
for i,g in enumerate(groups):
 p=D[str(i)+'_points'];t=D[str(i)+'_triangles'].copy();uv=D[str(i)+'_uv']
 # Closed solids must have outward winding before their facet normals are computed.
 edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,cnt=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
 if (cnt==2).all():
  volume=np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()/6
  if volume<0:t=t[:,::-1]
 me=bpy.data.meshes.new(g['name']);me.from_pydata(p.tolist(),[],t.tolist());me.update()
 ob=bpy.data.objects.new(g['name'],me);scene.collection.objects.link(ob);me.materials.append(materials[g['role']])
 for face in me.polygons:face.use_smooth=g['smooth']
 if str(i)+'_normal_hints' in D.files:
  hints=D[str(i)+'_normal_hints'];loop_normals=np.array([hints[l.vertex_index] for l in me.loops],float)
  for face in me.polygons:
   indices=np.array(face.loop_indices);actual=np.array(face.normal[:]);dots=loop_normals[indices]@actual
   loop_normals[indices]+=np.maximum(0,.12-dots)[:,None]*actual
  loop_normals/=np.maximum(np.linalg.norm(loop_normals,axis=1)[:,None],1e-12)
  me.normals_split_custom_set(loop_normals.tolist());me.update()
 layer=me.uv_layers.new(name='AuroraUV')
 for loop in me.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 me.calc_loop_triangles();outt=np.array([tri.vertices[:] for tri in me.loop_triangles],np.int32)
 output[str(i)+'_points']=np.array([v.co[:] for v in me.vertices],np.float32)
 output[str(i)+'_triangles']=outt
 output[str(i)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in tri.loops] for tri in me.loop_triangles],np.float32)
 output[str(i)+'_uv']=np.array([[layer.data[l].uv[:] for l in tri.loops] for tri in me.loop_triangles],np.float32)
np.savez_compressed(C/'blender_geometry.npz',**output)
(C/'material_specs.json').write_text(json.dumps(spec,indent=2)+'\n')
reference=bpy.data.objects.new('Owner reference',None);reference.empty_display_type='IMAGE';reference.data=bpy.data.images.load(str(R/'reference.png'));reference.data.pack();reference.empty_display_size=6;reference.location=(-6.4,.28,0);scene.collection.objects.link(reference)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,.28,0));s.region_3d.view_distance=9.4;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(C/'source/aurora_mountain.blend'),{scene},compress=True)
print('Aurora Mountain saved:',len(groups),'parts')
