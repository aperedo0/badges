import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['diamond']['work']);out=w/'candidates/04';out.mkdir(exist_ok=True);assert not (out/'usd').exists();shutil.copytree(w/'candidates/03/usd',out/'usd');st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);theta=np.arctan2(p[:,0],p[:,2]);tex=[];lo=p[:,1].min();hi=p[:,1].max()
 for tri in f:
  a=theta[tri].copy();rad=np.linalg.norm(p[tri][:,[0,2]],axis=1);valid=rad>1e-5
  if a[valid].max()-a[valid].min()>np.pi:a[a<0]+=2*np.pi
  a[~valid]=a[valid].mean();tex.append(np.stack([(a+np.pi)/(2*np.pi),(p[tri,1]-lo)/(hi-lo)],-1))
 write_mesh(st,prim.GetPath(),p,f,n,m,{key:np.array(tex) for key in uv})
finish('diamond',w,out,st,[{'design':'Closed round brilliant, unchanged from candidate 03.','mapping':'One continuous angular/height chart around the whole gem. Installed optics retained on forward/rear facets; side-facing facets use broad blue crystal reflections instead of a collapsed front projection.'}])
for old in (out/'usd').glob('*.usd*'):
 if old.name!='compacted.usdc':old.unlink()
