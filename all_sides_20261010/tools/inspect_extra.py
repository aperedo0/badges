from pathlib import Path
import json,numpy as np
from pxr import Usd,UsdGeom,UsdShade
R=Path(__file__).resolve().parents[1]
for t,r in json.loads((R/'manifest.json').read_text()).items():
 if t not in ['iron','silver','steel','bronze']:continue
 st=Usd.Stage.Open(json.loads((Path(r['work'])/'source/inspection.json').read_text())['layer']);print('TIER',t)
 for p in st.Traverse():
  if not p.IsA(UsdGeom.Mesh):continue
  m=UsdGeom.Mesh(p);a=np.array(m.GetPointsAttr().Get());f=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);n=np.cross(a[f[:,1]]-a[f[:,0]],a[f[:,2]]-a[f[:,0]]);n/=np.linalg.norm(n,axis=1,keepdims=True);print(p.GetName(),'positive-Z faces',sum(n[:,2]>1e-5),'negative-Z',sum(n[:,2]<-1e-5),'plane',sum(abs(n[:,2])<=1e-5))
  if t=='iron':
   for s in UsdGeom.Subset.GetAllGeomSubsets(m):
    i=np.array(s.GetIndicesAttr().Get());q=a[f[i]].reshape(-1,3);print(s.GetPath(),q.min(0),q.max(0),'normal z',np.quantile(n[i,2],[0,.5,1]))
