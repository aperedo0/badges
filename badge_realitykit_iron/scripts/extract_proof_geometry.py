import bpy,json,numpy as np
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
for name,path in [('iron',r/'work/iron_baked.usdz'),('silver',r/'source/silver_uncut.usdz')]:
 stage=Usd.Stage.Open(str(path));prim=next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and 'Emblem' in str(p.GetPath()));m=UsdGeom.Mesh(prim)
 subsets={UsdShade.MaterialBindingAPI(s.GetPrim()).ComputeBoundMaterial()[0].GetPath().name:list(s.GetIndicesAttr().Get()) for s in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim))}
 (r/f'proof/emblem_{name}.json').write_text(json.dumps({'points':np.asarray(m.GetPointsAttr().Get()).tolist(),'indices':np.asarray(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3).tolist(),'subsets':subsets}))
print('proof geometry extracted; iron bevel strips excluded from broad facet masks')
