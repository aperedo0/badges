from mathutils import Quaternion
# Rigid controls preserve closed rest. The dynamic key is deliberately excluded.
def control31(name):
 ob=sc.objects.get(name)
 if ob is None:ob=bpy.data.objects.new(name,None);sc.collection.objects.link(ob)
 ob['chest_mechanism_controller']=True;ob.animation_data_clear();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.empty_display_size=.10;ob.hide_set(True);return ob
master=control31('Chest Rig Master')
for name,value in [('cycle',0.),('insert',0.),('hasp',0.),('show_key',0.)]:master[name]=value
master.id_properties_ui('cycle').update(min=0,max=4);master.id_properties_ui('insert').update(min=0,max=1);master.id_properties_ui('hasp').update(min=0,max=math.pi/3);master.id_properties_ui('show_key').update(min=0,max=1)
keyctrl=control31('Chest Rig KeyInsertTurn');boltctrl=control31('Chest Rig BoltShift');haspctrl=control31('Chest Rig HaspRelease');springctrl=control31('Chest Rig SpringLift')
def world31(q):
 p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
ax=world31((1,0,0));az=world31((0,0,1));kp=world31((0,-.536,0));hp=world31((0,.48525,2))
def driver31(owner,path,expr,variables,index=None):
 fc=owner.driver_add(path) if index is None else owner.driver_add(path,index);dr=fc.driver;dr.type='SCRIPTED';dr.expression=expr
 for name,target,prop in variables:
  var=dr.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=target;var.targets[0].data_path='["'+prop+'"]'
 return fc
for ctrl,pivot,axis in [(keyctrl,kp,az),(haspctrl,hp,ax)]:ctrl.location=pivot;ctrl.rotation_mode='AXIS_ANGLE';ctrl.rotation_axis_angle=(0,*axis)
angle='1.5707963267948966*min(p,2-p)'
boltctrl['phase']=0.;driver31(boltctrl,'["phase"]','c if c<2 else c-2',[('c',master,'cycle')])
shift='min(0,-0.14*sin('+angle+')+0.02) if p<=1 else max(-0.12,-0.14*sin('+angle+'))'
boltctrl['shift']=0.;driver31(boltctrl,'["shift"]',shift,[('p',boltctrl,'phase')])
for i in range(3):
 driver31(boltctrl,'location',repr(float(ax[i]))+'*d',[('d',boltctrl,'shift')],i)
 driver31(keyctrl,'location',repr(float(kp[i]))+'+'+repr(float(az[i]))+'*0.8*(1-i)',[('i',master,'insert')],i)
driver31(keyctrl,'rotation_axis_angle','-('+angle+')',[('p',boltctrl,'phase')],0)
driver31(haspctrl,'rotation_axis_angle','-h',[('h',master,'hasp')],0)
Rp=.010*math.cos(math.pi/192)-.000005;A=math.sqrt(Rp*Rp-.008**2);s0=A-math.sqrt(.008**2-.0065**2)
for name,value in [('detentA',A),('detentStart',s0),('detentTop',-.185),('detentRadius',.008),('detentFree',-.1785),('detentFlatLift',.0015)]:master[name]=value
lift='0 if abs(d)<=b else (t+sqrt(max(0,r*r-(a-abs(d))*(a-abs(d))))-f if abs(d)<a else h)+2e-6*min(1,max(0,(abs(d)-b)/.0001))*min(1,max(0,(abs(d)-b)/.0001))*(3-2*min(1,max(0,(abs(d)-b)/.0001)))'
assert len(lift)<256
springctrl['lift']=0.;driver31(springctrl,'["lift"]',lift,[('d',boltctrl,'shift'),('a',master,'detentA'),('b',master,'detentStart'),('t',master,'detentTop'),('r',master,'detentRadius'),('f',master,'detentFree'),('h',master,'detentFlatLift')]);driver31(deform,'value','l/0.002',[('l',springctrl,'lift')])

def bind31(ob,parent,pivot):
 ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.parent=parent;ob.matrix_parent_inverse=Matrix.Translation(-pivot);ob.matrix_basis=Matrix.Identity(4);ob['chest_mechanism_rig_part']=True
bind31(sc.objects['Chest Key Driven Slider'],boltctrl,Vector((0,0,0)))
for name in ['Chest Front Hasp Barrel','Chest Curved Hasp Tongue']:bind31(sc.objects[name],haspctrl,hp)
key=sc.objects['Chest Removable Crank Key'];key.hide_set(False);bind31(key,keyctrl,kp)
driver31(key,'hide_render','1-v',[('v',master,'show_key')]);driver31(key,'hide_viewport','1-v',[('v',master,'show_key')])
# Two forward progress cycles each encode clockwise release then return upright.
states=[(0,0,0,0,0),(10,0,0,0,1),(40,0,1,0,1),(50,0,1,0,1),(90,1,1,0,1),(100,1,1,0,1),(130,1,1,math.pi/3,1),(140,1,1,math.pi/3,1),(180,2,1,math.pi/3,1),(190,2,1,math.pi/3,1),(230,2,0,math.pi/3,1),(240,2,0,math.pi/3,0),(260,2,0,math.pi/3,1),(290,2,1,math.pi/3,1),(300,2,1,math.pi/3,1),(340,3,1,math.pi/3,1),(350,3,1,math.pi/3,1),(380,3,1,0,1),(390,3,1,0,1),(430,4,1,0,1),(440,4,1,0,1),(480,4,0,0,1),(490,4,0,0,0)]
for frame,c,i,h,v in states:
 for name,value in [('cycle',c),('insert',i),('hasp',h),('show_key',v)]:master[name]=float(value);master.keyframe_insert(data_path='["'+name+'"]',frame=frame)
master.id_properties_ui('hasp').update(min=0.,max=math.pi/3)
master.id_properties_ui('cycle').update(min=0.,max=4.)
if master.animation_data and master.animation_data.action:master.animation_data.action.name='Chest Key Catch Unlock Release And Relock'
if master.animation_data and master.animation_data.action:
 action=master.animation_data.action
 curves=list(action.fcurves) if hasattr(action,'fcurves') else [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
 for fc in curves:
  fc.update_autoflags(master)
  for point in fc.keyframe_points:
   if fc.data_path=='["show_key"]':point.interpolation='CONSTANT'
   else:point.interpolation='LINEAR';point.handle_left_type='AUTO_CLAMPED';point.handle_right_type='AUTO_CLAMPED'

sc.frame_start=0;sc.frame_end=490;sc.render.fps=30
for marker in list(sc.timeline_markers):
 if marker.name.startswith('Catch '):sc.timeline_markers.remove(marker)
for frame,label in [(0,'Locked'),(40,'Key inserted'),(90,'Pin retracted'),(130,'Hasp released'),(180,'Key upright'),(230,'Key withdrawn'),(340,'Closing pin retracted'),(380,'Hasp closed'),(430,'Catch extended'),(490,'Relocked')]:sc.timeline_markers.new('Catch '+label,frame=frame)
checks=[]
for frame,want in [(0,0.),(90,-.12),(180,0.),(340,-.12),(430,0.),(490,0.)]:
 sc.frame_set(frame);bpy.context.view_layer.update();actual=float(boltctrl['shift']);assert abs(actual-want)<.00001,(frame,actual,want)
 spring_actual=float(springctrl['lift']);spring_expected=.001502 if want<-.1 else 0.
 assert abs(spring_actual-spring_expected)<.000001,(frame,'actual spring driver',spring_actual,spring_expected)
 assert all(fc.driver.is_valid for fc in springctrl.animation_data.drivers), 'Spring driver invalid'
 checks.append(dict(frame=frame,actual_shift=actual,spring_lift=spring_actual,expected_spring_lift=spring_expected))
sc.frame_set(0);bpy.context.view_layer.update()
for ob in sc.objects:
 if ob.type=='MESH' and ob.get('full_form'):assert np.max(abs(np.array(ob.matrix_world)-np.eye(4)))<.00001,(ob.name,'closed rest transform')
(C/'rig_stage.json').write_text(json.dumps(dict(action='Chest Key Catch Unlock Release And Relock',master=master.name,controls={'cycle':'0..4, two clockwise release and upright return cycles','insert':'0..1','hasp':'0..pi/3','show_key':'0 or1'},driver_endpoint_checks=checks,rest_frame=0,complete_lock_proof=False,full_chest_opening=False),indent=2))
print('Built actual key, slider, hasp and spring controls; driver endpoints verified and closed rest restored.')
