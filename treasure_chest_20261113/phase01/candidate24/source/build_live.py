import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';D=json.loads((P/'design.json').read_text())
assert 'APPROVED (review round 1)' in (R/'PLAN.md').read_text()
sc=bpy.data.scenes.get('Chest Phase 1') or bpy.data.scenes.new('Chest Phase 1');bpy.context.window.scene=sc
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=128;sc.cycles.use_denoising=True;sc.cycles.adaptive_threshold=.01
sc.render.resolution_x=sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.get('Chest Phase 1 studio') or bpy.data.worlds.new('Chest Phase 1 studio');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.14,.14,.14,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45;sc.world=world

def material(name,color,rough):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=0;return m
clay=material('Chest Phase 1 neutral clay',(.32,.32,.32),.45);guide=material('Chest Phase 1 foot guides',(.23,.23,.23),.45);floor=material('Chest development floor',(.023,.023,.023),.45)
yaw=Matrix.Rotation(math.radians(D['yaw_degrees']),3,'Y')

def finish(bm,name,mat,bevel_edges,bevel):
 if bevel_edges:
  new=bmesh.ops.bevel(bm,geom=bevel_edges,offset=bevel,segments=4,profile=.5,affect='EDGES',clamp_overlap=True)
  for f in new['faces']:f.smooth=True
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 for v in bm.verts:
  q=yaw@v.co;v.co=(q.x,-q.z,q.y)
 ob=sc.objects.get(name)
 if ob is None:
  me=bpy.data.meshes.new(name);ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob)
 else:me=ob.data;me.clear_geometry();me.materials.clear()
 bm.to_mesh(me);bm.free();me.update();me.materials.append(mat)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 wn=ob.modifiers.new('Stable broad face normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=50
 bpy.ops.object.modifier_apply(modifier=wn.name);ob.select_set(False)
 ob['phase']=1;ob['shape_only']=True;return ob

def box(name,lo,hi,mat):
 bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
 lo,hi=Vector(lo),Vector(hi)
 for v in bm.verts:v.co=Vector([lo[k]+(v.co[k]+.5)*(hi[k]-lo[k]) for k in range(3)])
 for f in bm.faces:f.smooth=False
 return finish(bm,name,mat,list(bm.edges),D['body_bevel'])
W,H=D['width'],D['depth']
box('Chest Body Envelope',[-W/2,D['body_bottom'],-H/2],[W/2,D['body_top'],H/2],clay)
bm=bmesh.new();N=D['lid_segments'];profile=[Vector((D['lid_bottom']+D['lid_rise']*math.sin(i*math.pi/N),H/2*math.cos(i*math.pi/N))) for i in range(N+1)];K=len(profile)
a=[bm.verts.new((-W/2,p.x,p.y)) for p in profile];b=[bm.verts.new((W/2,p.x,p.y)) for p in profile]
for j in range(K):
 f=bm.faces.new([a[j],a[(j+1)%K],b[(j+1)%K],b[j]]);f.smooth=j<K-1
bm.faces.new(a[::-1]).smooth=False;bm.faces.new(b).smooth=False;bm.normal_update()
# Round the actual end rims and long lower edges, preserving the smooth arch.
selected=[]
for e in bm.edges:
 v0,v1=e.verts
 same_end=abs(v0.co.x-v1.co.x)<1e-6
 bottom_ridge=abs(v0.co.y-D['lid_bottom'])<1e-6 and abs(v1.co.y-D['lid_bottom'])<1e-6
 if same_end or bottom_ridge:selected.append(e)
finish(bm,'Chest Barrel Lid Envelope',clay,selected,D['lid_bevel'])
for sx in (-1,1):
 for sz in (-1,1):
  cx=sx*D['foot_center_x'];cz=sz*D['foot_center_z'];r=D['foot_width']/2;s=D['foot_depth']/2;bottom=D['foot_bottom'];top=bottom+D['foot_height']
  box(f'Guide Foot {sx} {sz}',[cx-r,bottom,cz-s],[cx+r,top,cz+s],guide)
# All development objects remain outside the shape measurements and any future export.
if sc.objects.get('Development floor') is None:
 me=bpy.data.meshes.new('Development floor');me.from_pydata([(-40,-40,-2.895),(40,-40,-2.895),(40,40,-2.895),(-40,40,-2.895)],[],[[0,1,2,3]]);me.materials.append(floor);ob=bpy.data.objects.new('Development floor',me);sc.collection.objects.link(ob);ob['development_only']=True

def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
cam=sc.objects.get('Chest reference camera')
if cam is None:
 camdata=bpy.data.cameras.new('Chest reference camera');cam=bpy.data.objects.new('Chest reference camera',camdata);sc.collection.objects.link(cam)
camdata=cam.data;cam.location=(0,-D['camera_distance'],D['camera_target_height']+D['camera_distance']*math.tan(math.radians(D['camera_elevation_degrees'])));aim(cam,(0,0,D['camera_target_height']));camdata.lens=D['lens'];camdata.sensor_width=36;camdata.sensor_fit='HORIZONTAL';sc.camera=cam
for name,location,energy,size,color in [('Key',(-4,-6,7),1100,5,(1,.94,.87)),('Fill',(5,-3,2),500,4,(.88,.94,1)),('Rear',(-3,5,6),1000,4,(1,1,1))]:
 light=sc.objects.get('Chest Development '+name)
 if light is None:
  data=bpy.data.lights.new('Chest Development '+name,'AREA');light=bpy.data.objects.new(data.name,data);sc.collection.objects.link(light)
 data=light.data;data.energy=energy;data.shape='DISK';data.size=size;data.color=color;light.location=location;aim(light,(0,0,.2))
if sc.objects.get('First chest owner reference') is None:
 ref=bpy.data.objects.new('First chest owner reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(R/'reference.png'),check_existing=True);ref.data.pack();ref.location=(-8,0,.14);ref.rotation_euler=(math.pi/2,0,0);ref.empty_display_size=6.1;sc.collection.objects.link(ref)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  sp=area.spaces.active;sp.overlay.show_overlays=False;sp.shading.type='MATERIAL';v=sp.region_3d;v.view_location=(0,0,.14);v.view_distance=8.6;v.view_perspective='ORTHO';v.view_rotation=cam.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Built six closed shape masses in the open Blender. Saved phase 1 only.')
