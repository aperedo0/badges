import bpy,json,math,time,sys
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent;sc=bpy.data.scenes['Wood surface comparison'];bpy.context.window.scene=sc;cam=sc.camera;camera=cam.matrix_world.copy();lightstate={o.name:(o.matrix_world.copy(),o.data.energy,tuple(o.data.color),o.data.size) for o in sc.objects if o.type=='LIGHT'}
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 if any(d.type=='METAL' for d in prefs.devices):sc.cycles.device='GPU'
 print('RENDER DEVICES',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except Exception as e:print('CPU fallback',e,flush=True)
R=Matrix.Rotation(math.radians(32),3,'Y')
def world(q):
 a=R@Vector(q);return Vector((a.x,-a.z,a.y))
def lighting(mode):
 for n,(M,e,c,size) in lightstate.items():o=sc.objects[n];o.matrix_world=M;o.data.energy=e;o.data.color=c;o.data.size=size
 if mode=='warm':
  for suffix,c,e in [('Key',(1,.73,.48),1250),('Fill',(.74,.83,1),330),('Rear',(1,.53,.26),850)]:o=sc.objects['Lab Chest Development '+suffix];o.data.color=c;o.data.energy=e
 if mode=='cinema':
  for suffix,c,e in [('Key',(1,.84,.65),3300),('Fill',(.72,.83,1),440),('Rear',(1,.60,.30),1200)]:o=sc.objects['Lab Chest Development '+suffix];o.data.color=c;o.data.energy=e
  sc.objects['Lab Chest Development Key'].data.size=2.8
 if mode=='opposed':
  o=sc.objects['Lab Chest Development Key'];o.location.x=5;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 if mode=='graze':
  o=sc.objects['Lab Chest Development Key'];o.location=world((-3,-.1,2.3));o.rotation_euler=(world((-1,-1.4,1.6))-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=450;o.data.size=1.2;sc.objects['Lab Chest Development Fill'].data.energy=80

def select(k):
 for v in ['A','B','C','D','E','F','G','H']:
  if not sc.objects.get('Lab body '+('A baseline' if v=='A' else v)):continue
  sc.objects['Lab body '+('A baseline' if v=='A' else v)].hide_render=v!=k
  if v!='A':sc.objects['Lab relief '+v].hide_render=v!=k

def frame(mode):
 cam.matrix_world=camera;cam.data.type='ORTHO'
 if mode=='full':cam.data.ortho_scale=8.5;sc.render.resolution_x=sc.render.resolution_y=1000
 else:
  target=world((-.15,-1.45,1.6) if mode=='plank' else (-1.18,-1.52,1.6));forward=camera.to_quaternion()@Vector((0,0,-1));cam.location=target-forward*12;cam.rotation_euler=camera.to_euler();cam.data.ortho_scale=5.6 if mode=='plank' else 2.2;sc.render.resolution_x=1200 if mode=='plank' else 1000;sc.render.resolution_y=540 if mode=='plank' else 740
jobs=json.loads((P/'render_jobs.json').read_text()) if (P/'render_jobs.json').exists() else [(k,l,'plank') for k in 'ABC' for l in ['neutral','warm']]
if '--final' in sys.argv:jobs=[('B',l,f) for l,f in [('warm','close'),('neutral','close'),('graze','close'),('warm','full')]]
done=[]
for k,l,f in jobs:
 out=P/'renders'/f'{k}_{l}_{f}.png';out.parent.mkdir(exist_ok=True)
 if out.exists():continue
 select(k);lighting(l);frame(f);sc.cycles.samples=40;sc.render.resolution_percentage=100;sc.render.filepath=str(out);st=time.time();bpy.ops.render.render(write_still=True);done.append([out.name,round(time.time()-st,1)]);(P/'render_progress.json').write_text(json.dumps(done,indent=2));print('FINISHED',done[-1],flush=True)
