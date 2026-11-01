from pathlib import Path
import json,re,hashlib
import numpy as np
from pxr import Usd,UsdGeom
R=Path(__file__).resolve().parent;APP=R.parent/'emerald_trophy_20261025/preview';A=APP/'ScreenTime/SupportingFiles/Assets.xcassets';result=[]
for source in sorted(A.glob('Badge3DPreview*.dataset/coin.usdz')):
 stage=Usd.Stage.Open(str(source));meshes=[p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and 'Casing___smooth_rounded_outer_edge_mobile_geometry' in p.GetName()]
 if not meshes:continue
 prim=meshes[0];mesh=UsdGeom.Mesh(prim);points=np.asarray(mesh.GetPointsAttr().Get(),float);r=np.linalg.norm(points[:,:2],axis=1)
 profile=np.unique(np.round(np.c_[r,points[:,2]],5),axis=0)
 allp=np.vstack([np.asarray(UsdGeom.Mesh(p).GetPointsAttr().Get(),float) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)])
 result.append(dict(dataset=source.parent.name[:-8],source=str(source),shell_path=str(prim.GetPath()),points=len(points),profile=profile.tolist(),radial_min=float(r.min()),radial_max=float(r.max()),z_min=float(points[:,2].min()),z_max=float(points[:,2].max()),model_bounds=[allp.min(0).tolist(),allp.max(0).tolist()],sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
(R/'family_audit.json').write_text(json.dumps(result,indent=2)+'\n')
for item in result:print(item['dataset'],'points',item['points'],'radial',round(item['radial_min'],5),round(item['radial_max'],5),'depth',round(item['z_max']-item['z_min'],5),'profile',len(item['profile']))
print('TOTAL',len(result))
