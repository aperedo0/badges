import bpy,sys,time,json,os,fcntl
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;key,view,light=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+4];F=D if key=='baseline' else W/key;file=D/'baseline.blend' if key=='baseline' else F/'master.blend'
render_lock=(D/'render.lock').open('w');fcntl.flock(render_lock,fcntl.LOCK_EX)
cached=F/(view+'_'+light+('_final' if os.environ.get('WOOD_FINAL')=='1' else '')+'.png')
if os.environ.get('WOOD_SKIP_CACHED')=='1' and cached.exists():
 print('CACHED',cached,flush=True);sys.exit(0)
bpy.ops.wm.open_mainfile(filepath=str(file));code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']");exec(compile(code,'existing_render_setup','exec'));sc.frame_set(0)
if light in ['balanced','contrast','neutral','softwarm']:
 fill=sc.objects['Lab Chest Development Fill'];fill.location=(4,-5.5,4.5);fill.rotation_euler=(world((.4,-1.3,1.6))-fill.location).to_track_quat('-Z','Y').to_euler();fill.data.energy=350 if light=='contrast' else 800;fill.data.color=(1,.80,.62);fill.data.size=3.5
if view=='core':view='close'
if light=='softwarm':
 colors={'Key':(1,.82,.58),'Fill':(1,.9,.78),'Rear':(1,.70,.45)}
 weights=(.2126,.7152,.0722)
 for suffix,color in colors.items():
  obj=sc.objects['Lab Chest Development '+suffix];old=sum(c*w for c,w in zip(obj.data.color,weights));new=sum(c*w for c,w in zip(color,weights));obj.data.energy*=old/new;obj.data.color=color
if light=='neutral':
 for obj in sc.objects:
  if obj.type=='LIGHT':obj.data.color=(1,1,1)
(F/('lighting_'+light+'.json')).write_text(json.dumps({o.name:dict(matrix=[list(r) for r in o.matrix_world],energy=o.data.energy,color=list(o.data.color),size=o.data.size) for o in sc.objects if o.type=='LIGHT'},indent=2))
frame('plank' if view=='plank' else 'full' if view in ['full','context','context_contact'] else 'close')
if view=='right':
 target=world((1.4,-1.45,1.6));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12
if view.startswith('context'):
 def proxy(name,color,metal,rough):
  m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
 iron=proxy('Temporary dark iron',(.055,.043,.035),1,.42);brass=proxy('Temporary brass',(.48,.24,.06),1,.32);wood=proxy('Temporary quiet wood',(.11,.036,.011),0,.68)
 for obj in sc.objects:
  if obj.type!='MESH' or 'Development floor' in obj.name:continue
  obj.data=obj.data.copy()
  if obj.name=='Master Chest Body Envelope':
   for i,m in enumerate(obj.data.materials):
    if not m or not m.name.startswith('Wood Lab '):obj.data.materials[i]=wood
  else:
   m=wood if 'Envelope' in obj.name else brass if any(q in obj.name for q in ['Rivet','Fastener','Dome','Diamond','Lock Plate','Lock Border','Hasp','Ring Handle','Rolled Handle']) and 'Seat' not in obj.name else iron
   obj.data.materials.clear();obj.data.materials.append(m)
   for f in obj.data.polygons:f.material_index=0
if view=='context_contact':
 sc.world=sc.world.copy();sc.world.use_nodes=True;nt=sc.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD' and n.is_active_output);existing=out.inputs['Surface'].links[0].from_socket
 bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.006,.0045,.006,1);bg.inputs['Strength'].default_value=1
 path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(existing,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);sc.render.film_transparent=False
 stage=[o for o in sc.objects if o.type=='MESH' and 'Development floor' in o.name]
 bottoms=[(o.matrix_world@Vector(q)).z for o in sc.objects if o.type=='MESH' and not o.hide_render and 'Development floor' not in o.name for q in o.bound_box]
 for floor in stage:
  top=max((floor.matrix_world@Vector(q)).z for q in floor.bound_box);floor.location.z+=min(bottoms)-top+.0005
sc.render.resolution_x=1600 if view=='plank' else 1100 if view in ['full','context','context_contact'] else 1200;sc.render.resolution_y=740 if view=='plank' else 1100 if view in ['full','context','context_contact'] else 888;sc.render.resolution_percentage=100;sc.cycles.samples=32;sc.cycles.seed=17;sc.render.image_settings.color_depth='8'
if os.environ.get('WOOD_FINAL')=='1':
 sc.render.resolution_x=int(sc.render.resolution_x*1.5 if view not in ['full','context','context_contact'] else 1400);sc.render.resolution_y=int(sc.render.resolution_y*1.5 if view not in ['full','context','context_contact'] else 1400);sc.cycles.samples=96 if view=='close' else 64
if view in ['full','context','context_contact']:
 from bpy_extras.object_utils import world_to_camera_view
 points=[world_to_camera_view(sc,cam,obj.matrix_world@Vector(q)) for obj in sc.objects if obj.type=='MESH' and not obj.hide_render and 'Development floor' not in obj.name for q in obj.bound_box]
 bounds=[min(q.x for q in points)*sc.render.resolution_x,(1-max(q.y for q in points))*sc.render.resolution_y,max(q.x for q in points)*sc.render.resolution_x,(1-min(q.y for q in points))*sc.render.resolution_y]
 kp=world_to_camera_view(sc,cam,world((-1.31,-1.35,1.59)))
 (F/(view+'_'+light+'_frame.json')).write_text(json.dumps(dict(projected_knot_center=[kp.x*sc.render.resolution_x,(1-kp.y)*sc.render.resolution_y],projected_chest_bounds=bounds,render_size=[sc.render.resolution_x,sc.render.resolution_y],scope='Chest geometry bounds only, stage excluded'),indent=2))
if view in ['clay','mask']:
 body=sc.objects['Master Chest Body Envelope'];body.data=body.data.copy();i=next(i for i,m in enumerate(body.data.materials) if m and m.name.startswith('Wood Lab '));m=body.data.materials[i].copy();body.data.materials[i]=m;bs=m.node_tree.nodes['Principled BSDF']
 for socket in ['Base Color','Normal','Roughness']:
  for l in list(bs.inputs[socket].links):m.node_tree.links.remove(l)
 bs.inputs['Base Color'].default_value=(.22,.22,.22,1);bs.inputs['Roughness'].default_value=.72
 if view=='mask':
  image=bpy.data.images.load(str(D/'coverage.png'),check_existing=False);image.colorspace_settings.name='Non-Color';tex=m.node_tree.nodes['Single plank albedo'];tex.image=image;em=m.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);output=m.node_tree.nodes['Material Output']
  for link in list(output.inputs['Surface'].links):m.node_tree.links.remove(link)
  m.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
sc.render.filepath=str(F/(view+'_'+light+('_final' if os.environ.get('WOOD_FINAL')=='1' else '')+'.png'));st=time.time();bpy.ops.render.render(write_still=True);print('COMPLETE',key,view,light,time.time()-st,flush=True)
