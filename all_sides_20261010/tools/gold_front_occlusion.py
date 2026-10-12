"""Hide the far-side finial caps behind the reference front silhouette."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/19';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/18/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));camera=np.array([0,1.8,23.]);forward=np.array([0,-.55,0])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
axis=np.array([0,.9553869282796957,-.2953571012728279])
def screen(p):
 d=p-camera;depth=d@forward
 return np.stack([540+2250*(d@right)/depth,720-2250*(d@up)/depth],-1)*47/60+[180,70]
top=np.full(1206,np.inf)
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh) and '_RoundRear' not in q.GetName()]:
 p,f,*_=read_mesh(prim);xy=screen(p)
 edges=np.unique(np.sort(np.r_[f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]],axis=1),axis=0)
 for a,b in xy[edges]:
  if abs(b[0]-a[0])<1e-9:continue
  lo=max(0,int(np.ceil(min(a[0],b[0])-.5)));hi=min(1205,int(np.floor(max(a[0],b[0])-.5)))
  if hi<lo:continue
  x=np.arange(lo,hi+1);y=a[1]+(x+.5-a[0])/(b[0]-a[0])*(b[1]-a[1]);top[x]=np.minimum(top[x],y)
notes=[]
for num in ['2','4']:
 prim=st.GetPrimAtPath('/GoldCrown/GoldCrown_Finial'+num+'_RoundRear');p,f,n,m,uv=read_mesh(prim);xy=screen(p);x=np.clip(np.rint(xy[:,0]-.5).astype(int),0,1205)
 delta=np.maximum(top[x]+.8-xy[:,1],0);delta[~np.isfinite(delta)]=0
 deriv=(screen(p-axis*.001)[:,1]-xy[:,1])/.001;amount=float(np.max(delta/deriv))
 if amount<=0:continue
 assert amount<.22,(num,amount)
 for detail in ['Finial','Collar']:
  prim=st.GetPrimAtPath('/GoldCrown/GoldCrown_'+detail+num+'_RoundRear');q,g,nn,mm,vv=read_mesh(prim);write_mesh(st,prim.GetPath(),q-axis*amount,g,nn,mm,vv)
 notes.append({'rear_finial':num,'shortened_along_crown_axis':amount,'reason':'The far finial cap peeked above a front valley. Keep the sphere round and hide it behind the reference five-point silhouette.'})
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh) and '_RoundRear' in q.GetName() and any(k in q.GetName() for k in ['Lip','Flange'])]:
 p,f,n,m,uv=read_mesh(prim);total=np.zeros(len(p))
 for _ in range(2):
  xy=screen(p);x=np.clip(np.rint(xy[:,0]-.5).astype(int),0,1205);delta=np.maximum(top[x]+.8-xy[:,1],0);delta[~np.isfinite(delta)]=0
  deriv=(screen(p-axis*.001)[:,1]-xy[:,1])/.001;amount=delta/deriv;p-=axis*amount[:,None];total+=amount
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
 notes.append({'rear_detail':prim.GetName(),'maximum_occlusion_adjustment':float(total.max())})
old=json.loads((w/'candidates/18/build.json').read_text())['changes']
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/final.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc');finish('gold',w,out,Usd.Stage.Open(str(dest)),old+notes)
(ROOT/'gold19_selection.json').write_text(json.dumps({'gold':'19'})+'\n')
