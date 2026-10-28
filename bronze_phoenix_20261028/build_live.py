"""Build the entire custom shape in the connected Blender application."""
from pathlib import Path
import bpy,json,math
import numpy as np
from mathutils import Vector,Quaternion
ROOT=Path('/Users/antonioperedo/Desktop/badges/bronze_phoenix_20261028')
key=(ROOT/'active_badge.txt').read_text().strip();R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
cfg=json.loads((R/'design.json').read_text());D=np.load(C/'geometry.npz')
finish=json.loads((C/'metal_finish.json').read_text()) if (C/'metal_finish.json').exists() else {}
scene=bpy.data.scenes.new(cfg['name']+' complete sculpture');bpy.context.window.scene=scene
materials={}
for role,col in [('surface',(.004,.004,.004)),('star',(.004,.004,.004)),('silver_edge',(.16,.20,.27)),('gold_edge',(.32,.14,.025)),('blue_edge',(.018,.045,.09))]:
 col=finish.get('edge_colors',{}).get(role,col)
 m=bpy.data.materials.new(cfg['name']+' '+role);m.use_nodes=True;m.diffuse_color=(*col,1)
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1)
 bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.53 if role=='surface' else .55
 if role in finish.get('edge_roughness',{}):bs.inputs['Roughness'].default_value=finish['edge_roughness'][role]
 if role in ['surface','star'] and (role=='surface' or (C/'textures/star_color.png').exists()):
  uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='CrestUV'
  for suffix,socket in [('color','Base Color'),('emission','Emission Color')]:
   tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(C/'textures'/(role+'_'+suffix+'.png')),check_existing=False);tex.image.pack()
   nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
  bs.inputs['Emission Strength'].default_value=8
  rough_path=C/'textures'/(role+'_roughness.png')
  if rough_path.exists():
   tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(rough_path),check_existing=False);tex.image.colorspace_settings.name='Non-Color';tex.image.pack()
   nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
 materials[role]=m
objects=[]
def make(name,v,t,uv=None,role='surface',smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(v.tolist(),[],t.tolist());me.update()
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(materials[role]);ob['role']=role
 for f in me.polygons:f.use_smooth=smooth
 if uv is not None:
  layer=me.uv_layers.new(name='CrestUV')
  for i,l in enumerate(me.loops):layer.data[i].uv=uv[l.vertex_index]
 objects.append(ob);return ob
ob=make(cfg['name']+' sculpted front and matching rear',D['points'],D['triangles'],D['uv'])
w,h=json.loads((C/'trace.json').read_text())['reference_size'];surface_uv=D['uv']
for face in ob.data.polygons:
 # Determine feature membership using the original atlas dimensions.
 uv=surface_uv[list(face.vertices)].mean(0);px,py=uv[0]*w,(1-uv[1])*h
 for feature in ([] if key=='phoenix' else cfg.get('facets',[])):
  polygon=feature['outline'];inside=False
  for a,b in zip(polygon,polygon[1:]+polygon[:1]):
   if (a[1]>py)!=(b[1]>py) and px<(b[0]-a[0])*(py-a[1])/(b[1]-a[1])+a[0]:inside=not inside
  if inside:face.use_smooth=False;break
if (C/'polished_normals.npz').exists():
 polished=np.load(C/'polished_normals.npz');hints=polished['normals'];metal=polished['metal'];me=ob.data
 corner_normals=np.array([n.vector[:] for n in me.corner_normals],float)
 for face in me.polygons:
  if not face.use_smooth:continue
  actual=np.array(face.normal[:])
  for index in face.loop_indices:
   vertex=me.loops[index].vertex_index
   if metal[vertex]:
    normal=hints[vertex].astype(float);normal+=actual*max(0,.15-float(normal@actual));normal/=max(np.linalg.norm(normal),1e-8);corner_normals[index]=normal
 me.normals_split_custom_set(corner_normals.tolist());me.update()
for role,index in [('silver_edge',0),('gold_edge',1),('blue_edge',2)]:
 tt=D['wall_triangles'][D['wall_roles']==index]
 if len(tt):
  wall_points,first_wall_indices,wall_indices=np.unique(D['wall_points'],axis=0,return_index=True,return_inverse=True)
  edge=make(cfg['name']+' continuous '+role,wall_points,wall_indices[tt],role=role,smooth=True)
  if 'wall_normal_hints' in D.files:
   hints=D['wall_normal_hints'][first_wall_indices];me=edge.data
   corner_normals=np.array([hints[loop.vertex_index] for loop in me.loops],float)
   for face in me.polygons:
    actual=np.array(face.normal[:]);indices=np.array(face.loop_indices);dots=corner_normals[indices]@actual
    # Keep the smoothed reflection normals on the visible side of every face.
    correction=np.maximum(0,.15-dots)
    corner_normals[indices]+=correction[:,None]*actual
   corner_normals/=np.maximum(np.linalg.norm(corner_normals,axis=1)[:,None],1e-8)
   me.normals_split_custom_set(corner_normals.tolist());me.update()
if 'explicit_star_points' in D.files:
 make('Three amber gems with exact planar front and rear',D['explicit_star_points'],D['explicit_star_triangles'],D['explicit_star_uv'],role='star',smooth=False)
 make('Amber gem straight bronze walls',D['explicit_star_points'],D['explicit_star_wall_triangles'],role='gold_edge',smooth=False)
if 'explicit_bezel_points' in D.files:
 make('Three bronze bezels with continuous straight bevels',D['explicit_bezel_points'],D['explicit_bezel_triangles'],D['explicit_bezel_uv'],role='surface',smooth=False)
 make('Straight bronze bezel walls',D['explicit_bezel_points'],D['explicit_bezel_wall_triangles'],role='gold_edge',smooth=False)
arrays={};groups=[]
for i,ob in enumerate(objects):
 me=ob.data;me.calc_loop_triangles();p=np.array([v.co[:] for v in me.vertices],np.float32);t=np.array([t.vertices[:] for t in me.loop_triangles],np.int32)
 # Skinny triangles near sharp tips keep their own face normals.
 cross=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);unit=cross/np.maximum(np.linalg.norm(cross,axis=1)[:,None],1e-20)
 for check in range(3):
  normals=np.array([[me.corner_normals[l].vector[:] for l in tri.loops] for tri in me.loop_triangles],np.float32)
  bad=np.flatnonzero(np.einsum('ijk,ik->ij',normals,unit).mean(1)<.02)
  if not len(bad):break
  for index in bad:me.polygons[me.loop_triangles[int(index)].polygon_index].use_smooth=False
  me.update()
 # Custom reflection normals must remain in the actual face hemisphere,
 # including the narrow triangles beside hard ornament cuts.
 positions=p.astype(float);geometric=np.cross(positions[t[:,1]]-positions[t[:,0]],positions[t[:,2]]-positions[t[:,0]])
 geometric/=np.maximum(np.linalg.norm(geometric,axis=1)[:,None],1e-20)
 loop_normals=np.array([n.vector[:] for n in me.corner_normals],float);changed=False
 for j,triangle in enumerate(me.loop_triangles):
  indices=np.array(triangle.loops);values=loop_normals[indices];dots=values@geometric[j];bad=dots<.08
  if bad.any():
   values[bad]+=geometric[j]*(.12-dots[bad,None]);values/=np.maximum(np.linalg.norm(values,axis=1)[:,None],1e-10);loop_normals[indices]=values;changed=True
 if changed:me.normals_split_custom_set(loop_normals.tolist());me.update()
 arrays[str(i)+'_points']=p;arrays[str(i)+'_triangles']=t
 arrays[str(i)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in t.loops] for t in me.loop_triangles],np.float32)
 if me.uv_layers.active:arrays[str(i)+'_uv']=np.array([[me.uv_layers.active.data[l].uv[:] for l in t.loops] for t in me.loop_triangles],np.float32)
 else:arrays[str(i)+'_uv']=np.zeros((len(t),3,2),np.float32)
 groups.append({'name':ob.name,'role':ob['role']})
np.savez_compressed(C/'blender_geometry.npz',**arrays);(C/'groups.json').write_text(json.dumps(groups,indent=2))
ref=bpy.data.objects.new(cfg['name']+' owner reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'));ref.data.pack();ref.empty_display_size=6;ref.location=(-6.5,.28,0);scene.collection.objects.link(ref)
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,.28,0));s.region_3d.view_distance=8.8;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(C/(key+'.blend')),{scene},compress=True)
print(cfg['name'],'saved with',sum(len(arrays[k]) for k in arrays if k.endswith('_triangles')),'triangles')
