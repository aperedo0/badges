"""Give the editable master the same baked surfaces and UV correspondence as mobile."""
import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'scenes/iron_medallion_master.blend'))
bpy.context.preferences.filepaths.save_version=0
objects={o.name.split(' | ')[0]:o for o in bpy.data.objects['Turntable | one slow 360 degree spin'].children_recursive if o.type=='MESH'}
g=json.loads((r/'work/uv_geometry.json').read_text())
for short in ['Casing','Inset','Emblem']:
 o=objects[short];m=o.data;uv=m.uv_layers.get('USDZ_UV') or m.uv_layers.new(name='USDZ_UV')
 if short=='Emblem':
  coords=[((m.vertices[l.vertex_index].co.x+1.4)/2.8,(m.vertices[l.vertex_index].co.y+2.15)/4.3) for l in m.loops]
 else:
  data=next(v for k,v in g.items() if k.startswith(short+'___'));points=[Vector(v) for v in data['points']];faces=data['indices'];uvs=data['uv'];bvh=BVHTree.FromPolygons(points,faces,all_triangles=True)
  coords=[None]*len(m.loops)
  for poly in m.polygons:
   for li in poly.loop_indices:
    v=m.vertices[m.loops[li].vertex_index].co;query=v.lerp(poly.center,.00001);hit=bvh.find_nearest(query);fi=hit[2];tri=faces[fi]
    q=barycentric_transform(v,*(points[i] for i in tri),*(Vector((u[0],u[1],0)) for u in uvs[fi]));coords[li]=(q.x,q.y)
 uv.data.foreach_set('uv',np.asarray(coords,dtype=np.float32).ravel());uv.active_render=True
 for mat in m.materials:
  if mat.name.startswith('Silver | polished'):continue
  bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  if short=='Casing':stem='USDZ_Casing_outer' if mat.name.startswith('Outer') else 'USDZ_Casing_back' if mat.name.startswith('Back') else 'USDZ_Casing'
  elif short=='Inset':stem='USDZ_Inset'
  else:stem='USDZ_Emblem_shaded' if mat.name.startswith('Emblem | shaded') else 'USDZ_Emblem'
  for channel,socket in [('base_color','Base Color'),('roughness','Roughness'),('normal','Normal')]:
   if channel=='normal' and mat.name.startswith('Back and edge'):continue
   name=stem+'_'+channel
   if short=='Emblem' and channel=='roughness':name='USDZ_Emblem_roughness'
   if channel=='normal':name='USDZ_'+short+'_normal'
   image=bpy.data.images.load(str(r/'source/bakes'/(name+'.png')),check_existing=True);image.colorspace_settings.name='sRGB' if channel=='base_color' else 'Non-Color';image.pack()
   tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
   mapping=mat.node_tree.nodes.new('ShaderNodeUVMap');mapping.uv_map='USDZ_UV'
   mat.node_tree.links.new(mapping.outputs['UV'],tex.inputs['Vector'])
   output=tex.outputs['Color']
   if channel=='normal':
    decode=mat.node_tree.nodes.new('ShaderNodeNormalMap');decode.uv_map='USDZ_UV';decode.inputs['Strength'].default_value=1.;mat.node_tree.links.new(output,decode.inputs['Color']);output=decode.outputs['Normal']
   mat.node_tree.links.new(output,bs.inputs[socket])
 print('MASTER TEXTURES',short,'loops',len(m.loops),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'scenes/iron_medallion_master.blend'),check_existing=False)
print('Master updated with the same baked reference surfaces; mesh positions unchanged.')
