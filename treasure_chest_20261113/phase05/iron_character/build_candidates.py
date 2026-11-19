import bpy,numpy as np,json,math,sys
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;F=D/'layers';keys=sys.argv[sys.argv.index('--')+1:];KNOBS=['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']
def build(key):
 bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];obj=sc.objects['Lab Chest Lower Rim'];obj.data=obj.data.copy();mat=obj.data.materials[0].copy();mat.name='Forged iron '+key;obj.data.materials[0]=mat
 for name in KNOBS:
  o=sc.objects[name];o.data=o.data.copy();o.data.materials[0]=mat
 nt=mat.node_tree;uv=next(n for n in nt.nodes if n.type=='UVMAP' and n.uv_map=='LowerIronAtlas');bs=[nt.nodes[n] for n in ['Blackened conductive iron','Exposed iron Filament diagnostic reflectance','Opaque dark oxide and forge scale']];bare_mix=nt.nodes['Localized exposed iron'];scale_mix=nt.nodes['Opaque scale coverage'];oldwear=bare_mix.inputs[0].links[0].from_socket;oldscale=scale_mix.inputs[0].links[0].from_socket;normal=bs[0].inputs['Normal'].links[0].from_socket
 def texture(name):
  im=bpy.data.images.load(str(F/name),check_existing=True);im.colorspace_settings.name='Non-Color';im.pack();t=nt.nodes.new('ShaderNodeTexImage');t.name='Character '+name;t.image=im;nt.links.new(uv.outputs['UV'],t.inputs['Vector']);return t.outputs['Color']
 def mathnode(op,a,b):
  n=nt.nodes.new('ShaderNodeMath');n.operation=op
  for i,value in enumerate([a,b]):
   if isinstance(value,(float,int)):n.inputs[i].default_value=value
   else:nt.links.new(value,n.inputs[i])
  return n.outputs[0]
 def ramp(value,lo,hi):
  n=nt.nodes.new('ShaderNodeMapRange');n.inputs['To Min'].default_value=lo;n.inputs['To Max'].default_value=hi;nt.links.new(value,n.inputs['Value']);return n.outputs['Result']
 def mix(value,a,b):
  n=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(value,n.inputs[0])
  for i,v in enumerate([a,b],1):
   if isinstance(v,(tuple,list)):n.inputs[i].default_value=(*v,1)
   else:nt.links.new(v,n.inputs[i])
  return n.outputs[0]
 def socket(s,value):
  for link in list(s.links):nt.links.remove(link)
  nt.links.new(value,s)
 weather='weathering' in key or 'combined' in key;edge='edge' in key or 'combined' in key
 if weather:
  protect=texture('protection.png');pig=texture('pigment.png');rough=texture('roughness.png');w=texture('weather.png');ex=texture('exposed.png');marks=texture('mark_height16.png')
  bump=nt.nodes.new('ShaderNodeBump');bump.name='Independent shallow fractured scale markings';bump.inputs['Distance'].default_value=.00028;nt.links.new(marks,bump.inputs['Height']);nt.links.new(normal,bump.inputs['Normal']);normal=bump.outputs['Normal']
  for b,lo,hi in [(bs[0],(.105,.105,.102),(.21,.175,.135)),(bs[2],(.006,.006,.005),(.023,.017,.011))]:
   old=tuple(b.inputs['Base Color'].default_value[:3]);socket(b.inputs['Base Color'],mix(protect,old,mix(pig,lo,hi)))
  for b,lo,hi in [(bs[0],.27,.56),(bs[1],.20,.38),(bs[2],.49,.76)]:
   old=b.inputs['Roughness'].links[0].from_socket;socket(b.inputs['Roughness'],mix(protect,old,ramp(rough,lo,hi)))
  change=mathnode('MULTIPLY',mathnode('SUBTRACT',w,.5),.28);coverage=mathnode('ADD',oldscale,mathnode('MULTIPLY',change,protect));coverage=mathnode('MINIMUM',.97,mathnode('MAXIMUM',.15,coverage));coverage=mathnode('MULTIPLY',coverage,ramp(ex,1,.18));socket(scale_mix.inputs[0],coverage);socket(bare_mix.inputs[0],mathnode('MAXIMUM',oldwear,mathnode('MULTIPLY',ex,.45)))
 if edge:
  wear=texture('edge_wear.png');current=bare_mix.inputs[0].links[0].from_socket;socket(bare_mix.inputs[0],mathnode('MAXIMUM',current,wear));current=scale_mix.inputs[0].links[0].from_socket;socket(scale_mix.inputs[0],mathnode('MULTIPLY',current,ramp(wear,1,.06)));old=bs[1].inputs['Roughness'].links[0].from_socket;socket(bs[1].inputs['Roughness'],mix(wear,old,(.20,.20,.20)))
  me=obj.data;co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[co[:,0],co[:,2],-co[:,1]]@R;rest=q.copy();x=q[:,0].copy();y=q[:,1].copy();front=np.clip((q[:,2]-1.70)/.05,0,1);guard=np.clip((2.58-abs(x))/.33,0,1)
  def ss(a,b,v):t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
  for xc in [-1.1255,1.1255]:guard*=ss(.105,.17,np.hypot(x-xc,y+1.96575))
  strength=np.zeros(len(q))
  for damage in json.loads((F/'design.json').read_text())['extra_edge_damage']:
   xx=(x-damage['x'])/damage['width'];shape=np.where(xx<.15,np.clip((xx+1)/1.15,0,1),np.clip((1-xx)/.85,0,1))**1.3;v=y+1.714 if damage['side']=='top' else y+2.2175;mask=shape*np.exp(-(v/.048)**2)*front*guard;amount=damage['extra_depth']*mask;q[:,1]+=amount*(-1 if damage['side']=='top' else 1);q[:,2]-=amount*.48;strength=np.maximum(strength,mask)
  rotated=q@R.T;after=np.c_[rotated[:,0],-rotated[:,2],rotated[:,1]];me.vertices.foreach_set('co',after.astype(np.float32).ravel());me.update();attr=me.attributes.new('Localized edge deterioration','FLOAT','POINT');attr.data.foreach_set('value',strength.astype(np.float32));assert np.isfinite(after).all()
 else:co=None;after=None
 for b in bs:socket(b.inputs['Normal'],normal)
 C=D/key;C.mkdir(exist_ok=True)
 if edge:np.savez_compressed(C/'edge_geometry.npz',before=co,after=after,local_before=rest,local_after=q)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);(C/'design.json').write_text(json.dumps(dict(target=obj.name,mesh=obj.data.name,material=mat.name,weathering=weather,edge=edge,hammer_fields_and_strength_unchanged=True,knob_geometry_unchanged=True,source='Packed live baseline',reference_RGB_not_copied=True,mark_height_distance=.00028 if weather else 0),indent=2));print('BUILT',key,flush=True)
for key in keys:build(key)
