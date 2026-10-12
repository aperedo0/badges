import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work'])
st=Usd.Stage.Open(str(w/'candidates/03/usd/compacted.usdc'))
for prim in st.Traverse():
 if not prim.IsA(UsdGeom.Mesh):continue
 p,f,n,m,uv=read_mesh(prim);gn=face_normals(p,f)
 assert len(p)==768*28
 for k in range(28):
  ids=np.arange(k*2,len(f),56);ids=np.r_[ids,ids+1]
  print(k, 'nz',np.round(np.percentile(gn[ids,2],[0,50,100]),3),'mat',[(Path(v).name,int((m[ids]==v).sum())) for v in set(m[ids])])
