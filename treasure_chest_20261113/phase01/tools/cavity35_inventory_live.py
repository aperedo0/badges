# Read only actual triangle clipping against both planned empty volumes.
import bpy,numpy as np,json,math
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');P=R/'phase01';C=P/'candidate35';sc=bpy.context.scene;rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
def voids35():
 bodyN=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float);bodyD=np.array([2.33,2.33,.3475,2.0175,1.38,1.38])
 curve=[]
 for a in np.linspace(0,math.pi,97):
  n=np.array([math.sin(a)/1.9475,math.cos(a)/1.65]);n/=np.linalg.norm(n);curve.append([.38075+1.9475*math.sin(a)-.18*n[0],1.65*math.cos(a)-.18*n[1]])
 curve=np.array(curve);curve[[0,-1],0]=.38075;curve[0,1]=1.47;curve[-1,1]=-1.47;center=curve.mean(0);N=[[1,0,0],[-1,0,0]];D=[2.38,2.38]
 for a,b in zip(curve,np.roll(curve,-1,axis=0)):
  e=b-a;n=np.array([e[1],-e[0]]);n/=np.linalg.norm(n)
  if np.dot(n,center-a)>0:n=-n
  N.append([0,n[0],n[1]]);D.append(float(np.dot(n,a)))
 return {'body':(bodyN,bodyD),'lid':(np.array(N),np.array(D))}

def clips35(tris,N,D):
 # Shrink the empty volume very slightly so intended wood contacts do not count.
 D=D-1e-4;values=np.einsum('tvi,pi->tvp',tris,N)-D;possible=np.flatnonzero(~(values>0).all(1).any(1));hits=[]
 for idx in possible:
  poly=tris[idx].copy()
  for n,d in zip(N,D):
   if len(poly)==0:break
   out=[]
   for a,b in zip(poly,np.roll(poly,-1,axis=0)):
    sa,sb=np.dot(a,n)-d,np.dot(b,n)-d
    if sa<=0:out.append(a)
    if (sa<0 and sb>0) or (sa>0 and sb<0):out.append(a+(b-a)*(sa/(sa-sb)))
   poly=np.array(out)
  if len(poly)>=3:
   area=sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0])) for i in range(1,len(poly)-1))/2
   if area>1e-10:hits.append((int(idx),poly.mean(0).tolist(),float(area)))
 return hits

rows=[];spaces=voids35()
for ob in sc.objects:
 if ob.type!='MESH' or not ob.get('full_form') or ob.name in ('Chest Body Envelope','Chest Barrel Lid Envelope'):continue
 me=ob.data;me.calc_loop_triangles();a=np.array([v.co[:] for v in me.vertices]);q=np.c_[a[:,0],a[:,2],-a[:,1]]@rot;t=np.array([v.vertices[:] for v in me.loop_triangles]);tri=q[t]
 for space,(N,D) in spaces.items():
  hits=clips35(tri,N,D)
  if hits:rows.append(dict(name=ob.name,space=space,interior_triangle_count=len(hits),sample=hits[:2]))
output=globals().get('CAVITY35_INVENTORY_OUTPUT','intrusion_inventory_before.json');(C/output).write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows)[:7500])
