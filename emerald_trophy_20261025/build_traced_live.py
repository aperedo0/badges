"""Build reference traced sculpture in the complete live Blender badge."""
from pathlib import Path
import bpy,math,json
import numpy as np
from mathutils import Vector,Quaternion
R=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025');OUT=R/'candidate05';TEMP=Path('/tmp/emerald_trophy_20261025')
data=np.load(TEMP/'reference_relief.npz');source=R/'candidate04/emerald_trophy.blend'
for old in list(bpy.data.scenes):
 if old.name=='emerald_trophy_traced':bpy.data.scenes.remove(old)
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
scene=loaded.scenes[0];scene.name='emerald_trophy_traced';bpy.context.window.scene=scene
context=bpy.data.collections.new('Previous complete trophy preserved');scene.collection.children.link(context)
for ob in list(scene.objects):
 if ob.type=='MESH' and ob.name.startswith('Casing___'):continue
 for c in list(ob.users_collection):c.objects.unlink(ob)
 context.objects.link(ob)
context.hide_render=True;context.hide_viewport=True
palette={'relief':((.5,.5,.5),.45,.45),'wall':((.24,.09,.012),.8,.53),'field':((.0006,.014,.0020),.72,.32)}
mats={}
for role,(color,metal,rough) in palette.items():
 m=bpy.data.materials.new('Reference_traced_'+role);m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
 bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;mats[role]=m
 if role=='wall':continue
 nt=m.node_tree;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='CoinReliefUV'
 for suffix,socket,space in ([('color','Base Color','sRGB'),('roughness','Roughness','Non-Color')] if role=='field' else [('color','Base Color','sRGB'),('emission','Emission Color','sRGB')]):
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'textures'/(role+'_'+suffix+'.png')),check_existing=False)
  tex.image.colorspace_settings.name=space;tex.image.pack();nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
 if role=='relief':bs.inputs['Emission Strength'].default_value=8
objects=[]
def make(name,p,t,role,smooth):
 me=bpy.data.meshes.new(name);me.from_pydata(p.tolist(),[],t.tolist());me.update()
 ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(mats[role]);ob['role']=role
 for face in me.polygons:face.use_smooth=smooth
 uv=me.uv_layers.new(name='CoinReliefUV')
 for li,l in enumerate(me.loops):
  v=me.vertices[l.vertex_index].co;uv.data[li].uv=((v.x+3.015)/6.03,(v.y+3.015)/6.03)
 objects.append(ob);return ob
make('Reference traced curved trophy and botanical relief',data['relief_points'],data['relief_triangles'],'relief',True)
make('Continuous relief side walls',data['wall_points'],data['wall_triangles'],'wall',True)
for i in range(2):make(('Upper' if i==0 else 'Pedestal')+' reference emerald flat facets',data['gem'+str(i)+'_points'],data['gem'+str(i)+'_triangles'],'relief',False)
n=96;v=[[0,0,.056]]
for radius in [.80,1.60,2.445]:
 for a in np.arange(n)*math.tau/n:v.append([radius*math.cos(a),radius*math.sin(a),.044+.012*(1-(radius/2.445)**2)])
f=[(0,1+i,1+(i+1)%n) for i in range(n)]
for k in range(2):
 a=1+k*n;b=a+n
 for i in range(n):f += [(a+i,b+i,b+(i+1)%n),(a+i,b+(i+1)%n,a+(i+1)%n)]
make('Exact Archer brushed emerald field',np.array(v),np.array(f),'field',True)
arrays={};groups=[]
for i,ob in enumerate(objects):
 me=ob.data;me.calc_loop_triangles();p=np.array([v.co[:] for v in me.vertices],float)
 tt=[t for t in me.loop_triangles if np.linalg.norm(np.cross(p[t.vertices[1]]-p[t.vertices[0]],p[t.vertices[2]]-p[t.vertices[0]]))>1e-10]
 arrays[str(i)+'_points']=p;arrays[str(i)+'_triangles']=np.array([t.vertices[:] for t in tt],np.int32)
 arrays[str(i)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in t.loops] for t in tt],float)
 groups.append({'name':ob.name,'role':ob['role']})
 back=ob.copy();back.data=ob.data.copy();back.name='Back '+ob.name
 for v in back.data.vertices:v.co=(-v.co.x,v.co.y,-v.co.z-.33)
 scene.collection.objects.link(back)
np.savez_compressed(TEMP/'candidate05_geometry.npz',**arrays)
(OUT/'design.json').write_text(json.dumps({'groups':groups,'palette':palette,'emission':{},'source_shell':'sprout','reference_center':[627,590],'reference_inner_radius':490},indent=2))
ref=bpy.data.objects.new('Exact trophy owner reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'),check_existing=True);ref.data.pack();ref.empty_display_size=6.2;ref.location=(-7,0,0);scene.collection.objects.link(ref)
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=8.8;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(OUT/'emerald_trophy.blend'),{scene},compress=True)
print('Reference sculpture:',sum(len(a) for k,a in arrays.items() if k.endswith('_triangles')),'front triangles')
