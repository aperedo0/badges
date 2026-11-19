import bpy,numpy as np,json,math,shutil
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;A=D/'N_charcoal_scale';C=D/'O_local_planishing';C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));o=bpy.data.scenes['Test plank master'].objects['Lab Chest Lower Rim'];o.data=o.data.copy();m=o.data;co=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',co.ravel());R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[co[:,0],co[:,2],-co[:,1]]@R;before=q.copy();x,y=q[:,0],q[:,1];front=q[:,2]>1.70
# Reference guided flattening strokes within existing formations, not new raised stamps.
polys=[
[[-1.98,-1.86],[-1.79,-1.80],[-1.57,-1.85],[-1.63,-1.96],[-1.84,-2.00],[-1.97,-1.95]],
[[-1.86,-2.08],[-1.70,-1.99],[-1.50,-2.04],[-1.42,-2.14],[-1.65,-2.16]],
[[-.97,-1.83],[-.79,-1.80],[-.54,-1.86],[-.47,-1.97],[-.70,-1.98],[-.87,-1.93]],
[[-.93,-2.11],[-.79,-2.04],[-.58,-2.08],[-.43,-2.14],[-.75,-2.17]],
[[.48,-1.86],[.65,-1.80],[.86,-1.86],[.91,-1.96],[.72,-1.99],[.51,-1.94]],
[[.55,-2.08],[.75,-2.02],[.95,-2.11],[.88,-2.16],[.65,-2.17]],
[[1.41,-2.02],[1.59,-1.96],[1.76,-2.04],[1.81,-2.15],[1.54,-2.16],[1.40,-2.10]],
[[1.72,-1.86],[1.88,-1.80],[2.06,-1.83],[2.12,-1.96],[1.97,-2.02],[1.78,-1.95]]]
for pts in polys:
 p=np.array(pts);inside=np.zeros(len(q),bool);distance=np.full(len(q),1e6)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  inside^=((a[1]>y)!=(b[1]>y))&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1]+1e-20)+a[0]);v=b-a;t=np.clip(((x-a[0])*v[0]+(y-a[1])*v[1])/(v@v),0,1);distance=np.minimum(distance,np.hypot(x-a[0]-t*v[0],y-a[1]-t*v[1]))
 mask=inside&front;ids=np.flatnonzero(mask);assert len(ids)>15
 design=np.c_[x[ids]-x[ids].mean(),y[ids]-y[ids].mean(),np.ones(len(ids))];fit=np.linalg.lstsq(design,q[ids,2],rcond=None)[0];fit[:2]=np.clip(fit[:2],-.06,.06);plane=design@fit;mix=np.clip(distance[ids]/.018,0,1);mix=mix*mix*(3-2*mix)*.82
 for xc in [-1.1277,1.1234]:
  r=np.hypot(x[ids]-xc,y[ids]+1.96575);t=np.clip((r-.105)/.065,0,1);mix*=t*t*(3-2*t)
 correction=np.clip(plane-q[ids,2],-.002,.002)*mix;q[ids,2]+=correction
rot=q@R.T;new=np.c_[rot[:,0],-rot[:,2],rot[:,1]];m.vertices.foreach_set('co',new.astype(np.float32).ravel());m.update();assert np.isfinite(new).all()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);shutil.copy2(A/'displacement.npz',C/'displacement.npz');np.savez_compressed(C/'local_planishing.npz',before=co,after=new,local_before=before,local_after=q);a=json.loads((A/'design.json').read_text());a.update(mesh=m.name,local_reference_guided_planishing=polys,maximum_local_change=float(abs(q-before).max()),source='N_charcoal_scale');(C/'design.json').write_text(json.dumps(a,indent=2));print('Saved local flattening trial')
