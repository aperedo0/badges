from pathlib import Path
import json,zipfile
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parents[1]
for tier,rec in json.loads((ROOT/'manifest.json').read_text()).items():
 w=Path(rec['work']);src=w/'source/installed';src.mkdir(exist_ok=True)
 with zipfile.ZipFile(w/'source/installed.usdz') as z:z.extractall(src)
 layer=next(src.glob('*.usd*'));st=Usd.Stage.Open(str(layer));meshes=[];mats=[]
 for p in st.Traverse():
  if p.IsA(UsdGeom.Mesh):
   m=UsdGeom.Mesh(p);pts=np.array(m.GetPointsAttr().Get());cnt=np.array(m.GetFaceVertexCountsAttr().Get());idx=np.array(m.GetFaceVertexIndicesAttr().Get());f=idx.reshape(-1,3) if np.all(cnt==3) else None
   normals=np.array(m.GetNormalsAttr().Get());subsets=[{'path':str(s.GetPath()),'faces':len(s.GetIndicesAttr().Get()),'material':[str(t) for t in UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()]} for s in UsdGeom.Subset.GetAllGeomSubsets(m)]
   mesh={'path':str(p.GetPath()),'vertices':len(pts),'faces':len(cnt),'triangles':int(cnt.sum()-2*len(cnt)),'counts':np.unique(cnt).tolist(),'bounds':[pts.min(0).tolist(),pts.max(0).tolist()],'normals':m.GetNormalsInterpolation(),'material':[str(t) for t in UsdShade.MaterialBindingAPI(p).GetDirectBindingRel().GetTargets()], 'subsets':subsets,'uv':[{ 'name':v.GetPrimvarName(),'interpolation':v.GetInterpolation(),'len':len(v.Get()) if hasattr(v.Get(),'__len__') else 0} for v in UsdGeom.PrimvarsAPI(p).GetPrimvars() if v.GetTypeName().isArray]}
   meshes.append(mesh)
   if f is not None:
    np.savez_compressed(w/'source'/('mesh_'+str(len(meshes))+'.npz'),points=pts,faces=f,normals=normals)
  if p.IsA(UsdShade.Shader) and UsdShade.Shader(p).GetIdAttr().Get()=='UsdPreviewSurface':
   sh=UsdShade.Shader(p);inputs={}
   for i in sh.GetInputs():
    inputs[i.GetBaseName()]={'value':str(i.Get()),'sources':[str(c.source.GetPrim().GetPath()) for c in i.GetConnectedSources()[0]]}
   mats.append({'path':str(p.GetPath()),'inputs':inputs})
 report={'layer':str(layer),'meshes':meshes,'materials':mats}
 (w/'source/inspection.json').write_text(json.dumps(report,indent=2)+'\n')
 print(tier,json.dumps({'meshes':[(x['path'],x['triangles'],x['bounds'],x['subsets']) for x in meshes],'materials':mats}))
