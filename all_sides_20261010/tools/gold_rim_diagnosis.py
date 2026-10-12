import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);st=Usd.Stage.Open(str(w/'candidates/20/usd/compacted.usdc'))
camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
def screen(p):
 d=p-camera;z=d@forward
 return np.stack([540+2250*(d@right)/z,720-2250*(d@up)/z],-1)*47/60+[180,70],z
meshes=[]
for prim in st.Traverse():
 if prim.IsA(UsdGeom.Mesh):
  p,f,n,m,uv=read_mesh(prim);xy,z=screen(p);meshes.append((prim.GetName(),p,f,xy,z,m))
for x,y in [(600,664),(570,664),(660,665),(450,676),(600,660),(600,670)]:
 hits=[]
 for name,p,f,xy,z,m in meshes:
  t=xy[f];a=t[:,1]-t[:,0];b=t[:,2]-t[:,0];d=np.array([x+.5,y+.5])-t[:,0]
  det=a[:,0]*b[:,1]-a[:,1]*b[:,0];valid=abs(det)>1e-10;det=np.where(valid,det,1)
  u=(d[:,0]*b[:,1]-d[:,1]*b[:,0])/det;v=(a[:,0]*d[:,1]-a[:,1]*d[:,0])/det
  ids=np.where(valid&(u>=0)&(v>=0)&(u+v<=1))[0]
  for i in ids:
   weights=np.array([1-u[i]-v[i],u[i],v[i]]);dep=1/(weights/z[f[i]]).sum();world=(weights[:,None]*p[f[i]]/z[f[i],None]).sum(0)*dep
   hits.append((float(dep),name,int(i),Path(m[i]).name,world.tolist()))
 print((x,y),sorted(hits)[:5])
axis=np.array([0,.95538692828,-.29535710127]);band=read_mesh(st.GetPrimAtPath('/GoldCrown/GoldCrown_TrueCircularBand'))[0];top=band[:192].mean(0)
for prim in st.Traverse():
 if prim.IsA(UsdGeom.Mesh) and 'Shell' in prim.GetName():
  p,*_=read_mesh(prim);h=(p-top)@axis;print(prim.GetName(),'minimum distance above band',h.min(),'bottom rows',[(j,float(h[j*281:(j+1)*281].min()),float(h[j*281:(j+1)*281].max())) for j in range(6)])
