import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/03';out.mkdir(exist_ok=True);
if not (out/'usd').exists():shutil.copytree(w/'candidates/02/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));root=st.GetDefaultPrim().GetPath();wall=str(root.AppendPath('Materials/PlatinumKnot_TexturedWalls'))
notes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);gn=face_normals(p,f);edge=np.abs(gn[:,2])<.4;m[edge]=wall
 for key,a in uv.items():
  world=p[f].reshape(-1,3);values=a.reshape(-1,2);primary=gn[:,2]>.9;wx=p[f[primary]].reshape(-1,3);av=a[primary].reshape(-1,2);coef=np.linalg.lstsq(np.c_[wx[:,:2],np.ones(len(wx))],av,rcond=None)[0];res=np.max(np.abs(np.c_[wx[:,:2],np.ones(len(wx))]@coef-av));print('front UV affine residual',res,coef);assert res<.03,res
  inward=n[edge,:,:2].copy();inward/=np.maximum(np.linalg.norm(inward,axis=-1,keepdims=True),1e-9)
  a[edge]-=.12*inward@coef[:2,:]
 write_mesh(st,prim.GetPath(),p,f,n,m,uv);notes.append({'wall_faces':int(edge.sum()),'method':'Side-wall UVs sample 0.12 units inside the ribbon rather than the front silhouette, preventing background and outline-band stripes. Main front surfaces and textures remain unchanged; grazing wall shading is moderate and textured.'})
finish('platinum',w,out,st,notes)
for old in (out/'usd').glob('*.usd*'):
 if old.name!='compacted.usdc':old.unlink()
