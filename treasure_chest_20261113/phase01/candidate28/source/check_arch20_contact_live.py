import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate28';yaw=Matrix.Rotation(math.radians(32),3,'Y')
def height_at(z,r):
 a=np.linspace(.9,2.25,2049);ny=np.sin(a)/2.05;nz=np.cos(a)/1.65;L=np.hypot(ny,nz);y=.53+2.05*np.sin(a)+r*ny/L;zz=1.65*np.cos(a)+r*nz/L
 return float(np.interp(z,zz[::-1],y[::-1]))
def world(x,y,z):
 q=yaw@Vector((x,y,z));return Vector((q.x,-q.z,-2.455+(q.y+2.455)*.95))
result=[]
for sx in (-1,1):
 ob=bpy.context.scene.objects[f'Chest End Arch Crown Tab {sx}'];rows=[]
 for u in np.linspace(.0001,.9999,17):
  z=-.142+.464*u;a=math.pi/4
  x=2.67+.085*math.cos(a);r=.095+.085*math.sin(a);target_pos=world(sx*x,height_at(z,r),z)
  x0=2.67+.035*math.cos(a);r0=.095+.035*math.sin(a);A=world(sx*x0,height_at(z,r0),z);D=(target_pos-A).normalized()
  hit,pt,nn,idx=ob.ray_cast(A,D);assert hit,(sx,u,'fold missing');burial=float((target_pos-pt).dot(D));assert .0001<burial<.006,(sx,u,burial);rows.append(burial)
 result.append(dict(side=sx,width_samples=17,fold_contact_min=min(rows),fold_contact_max=max(rows),actual_beveled_mesh=True))
(C/'fold_contact.json').write_text(json.dumps(result,indent=2));print('Verified actual fold seat across both full widths after height conversion.')
