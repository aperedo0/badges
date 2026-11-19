import bpy,sys,json,time,fcntl,os
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;key,view=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3];C=D/key;lock=(D/'render.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX);final=os.environ.get('IRON_FINAL')=='1';out=C/(view+('_final' if final else '')+'.png')
if out.exists():print('CACHED',out,flush=True);sys.exit(0)
bpy.ops.wm.open_mainfile(filepath=str(C/'master.blend'));P=D.parents[1]/'phase04/wood_lab';code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']");exec(compile(code,'reused_owner_render_rig','exec'));sc.frame_set(0)
if view in ['context','full','context_reflection']:frame('full')
else:
 target=world((1.3,-1.94,1.78) if view in ['right','reflection_right'] else (-1.2,-1.94,1.78));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12;cam.rotation_euler=camera.to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.65
if view in ['reflection','reflection_right','context_reflection']:
 target=world((0,-1.965,1.78));N=(world((0,0,1))-world((0,0,0))).normalized();V=camera.to_quaternion()@Vector((0,0,1));L=(2*N.dot(V)*N-V).normalized();position=target+L*2.2
 feet=min((o.matrix_world@Vector(q)).z for o in sc.objects if o.type=='MESH' and not o.hide_render and 'Development floor' not in o.name for q in o.bound_box);position.z=max(position.z,feet+.22)
 data=bpy.data.lights.new('Temporary lower iron reflection strip','AREA');data.energy=180;data.color=(1,.72,.40);data.shape='RECTANGLE';data.size=4.8;data.size_y=.30;light=bpy.data.objects.new(data.name,data);sc.collection.objects.link(light);light.location=position;light.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler()
 (C/(view+'_reflection_light.json')).write_text(json.dumps(dict(position=list(position),target=list(target),color=list(data.color),power=data.energy,source='Temporary diagnostic floor reflection strip, existing lights unchanged'),indent=2))
if view=='warmkey':
 weights=(.2126,.7152,.0722)
 for suffix,color in [('Key',(1,.58,.24)),('Fill',(1,.85,.65)),('Rear',(1,.54,.19))]:
  obj=sc.objects['Lab Chest Development '+suffix];old=sum(c*w for c,w in zip(obj.data.color,weights));new=sum(c*w for c,w in zip(color,weights));obj.data.energy*=old/new;obj.data.color=color
if view=='neutral':
 for obj in sc.objects:
  if obj.type=='LIGHT':obj.data.color=(1,1,1)
if view in ['context','context_reflection','iron','right','neutral','warmkey','reflection','reflection_right']:
 def proxy(name,color,metal,rough):
  m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
 iron=proxy('Temporary iron context',(.055,.043,.035),1,.42);brass=proxy('Temporary brass context',(.48,.24,.06),1,.32);wood=proxy('Temporary wood context',(.11,.036,.011),0,.68)
 for obj in sc.objects:
  if obj.type!='MESH' or 'Development floor' in obj.name or obj.name=='Lab Chest Lower Rim':continue
  obj.data=obj.data.copy()
  if obj.name=='Master Chest Body Envelope':
   for i,m in enumerate(obj.data.materials):
    if not m or not m.name.startswith('Wood Lab '):obj.data.materials[i]=wood
  else:
   m=wood if 'Envelope' in obj.name else brass if any(t in obj.name for t in ['Rivet','Fastener','Dome','Diamond','Lock Plate','Lock Border','Hasp','Ring Handle','Rolled Handle']) and 'Seat' not in obj.name else iron;obj.data.materials.clear();obj.data.materials.append(m)
   for p in obj.data.polygons:p.material_index=0
if view in ['context','context_reflection']:
 sc.world=sc.world.copy();sc.world.use_nodes=True;nt=sc.world.node_tree;output=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD' and n.is_active_output);existing=output.inputs['Surface'].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.006,.0045,.006,1);bg.inputs['Strength'].default_value=1;path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(existing,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface']);sc.render.film_transparent=False
 stage=[o for o in sc.objects if o.type=='MESH' and 'Development floor' in o.name];bottoms=[(o.matrix_world@Vector(q)).z for o in sc.objects if o.type=='MESH' and not o.hide_render and 'Development floor' not in o.name for q in o.bound_box]
 for floor in stage:floor.location.z+=min(bottoms)-max((floor.matrix_world@Vector(q)).z for q in floor.bound_box)+.0005
sc.render.resolution_x=1400 if view in ['context','full','context_reflection'] else 1600;sc.render.resolution_y=1400 if view in ['context','full','context_reflection'] else 800
if not final:sc.render.resolution_x=int(sc.render.resolution_x*.75);sc.render.resolution_y=int(sc.render.resolution_y*.75)
if view in ['context','full','context_reflection']:
 from bpy_extras.object_utils import world_to_camera_view
 import numpy as np
 origin=world_to_camera_view(sc,cam,Vector((0,0,0)));basis=np.array([[*(world_to_camera_view(sc,cam,Vector(q))-origin)][:2] for q in [(1,0,0),(0,1,0),(0,0,1)]],np.float64);minimum=np.array([1e10,1e10]);maximum=-minimum
 for obj in sc.objects:
  if obj.type!='MESH' or obj.hide_render or 'Development floor' in obj.name:continue
  co=np.empty((len(obj.data.vertices),3),np.float32);obj.data.vertices.foreach_get('co',co.ravel());M=np.array(obj.matrix_world);uv=(co@M[:3,:3].T+M[:3,3])@basis+np.array([origin.x,origin.y]);minimum=np.minimum(minimum,uv.min(0));maximum=np.maximum(maximum,uv.max(0))
 bounds=[minimum[0]*sc.render.resolution_x,(1-maximum[1])*sc.render.resolution_y,maximum[0]*sc.render.resolution_x,(1-minimum[1])*sc.render.resolution_y];(C/(view+'_frame.json')).write_text(json.dumps(dict(projected_chest_bounds=bounds,actual_mesh_projection=True,render_size=[sc.render.resolution_x,sc.render.resolution_y]),indent=2))
sc.render.resolution_percentage=100;sc.cycles.samples=64 if final else 24;sc.cycles.seed=17;sc.cycles.use_denoising=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.filepath=str(out);t=time.time();bpy.ops.render.render(write_still=True);print('COMPLETE',key,view,time.time()-t,flush=True)
