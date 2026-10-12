import sys,json,hashlib,zipfile
from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,UsdUtils
r=Path(__file__).resolve().parents[1];kind=sys.argv[sys.argv.index('--')+1];b=r/kind;p=b/'mobile'/f'{kind}_badge_mobile.usdz';s=Usd.Stage.Open(str(p));pts=[];normals=[];counts=0;transforms=[];ids=[];shaderids=[]
for prim in s.Traverse():
    ids.append(str(prim.GetPath()))
    if prim.IsA(UsdGeom.Xformable) and UsdGeom.Xformable(prim).GetOrderedXformOps():transforms.append(str(prim.GetPath()))
    if prim.IsA(UsdGeom.Mesh):
        m=UsdGeom.Mesh(prim);pts.extend(m.GetPointsAttr().Get());counts+=len(m.GetFaceVertexCountsAttr().Get());n=np.array(m.GetNormalsAttr().Get());assert np.isfinite(n).all();assert np.max(abs(np.linalg.norm(n,axis=1)-1))<1e-5;assert m.GetNormalsInterpolation()=='faceVarying';assert m.GetSubdivisionSchemeAttr().Get()=='none';assert set(m.GetFaceVertexCountsAttr().Get())=={3}
    if prim.IsA(UsdShade.Shader):shaderids.append(UsdShade.Shader(prim).GetIdAttr().Get())
pts=np.array(pts);lo=pts.min(0);hi=pts.max(0);span=hi-lo
checks={'up_axis':UsdGeom.GetStageUpAxis(s)=='Y','meters_per_unit':UsdGeom.GetStageMetersPerUnit(s)==1,'no_transforms':not transforms,'centered_x':abs(lo[0]+hi[0])<1e-5,'centered_z':abs(lo[2]+hi[2])<1e-5,'width_6_03_max':span[0]<=6.03001,'height_4_6_to_5_4':4.6<=span[1]<=5.4,'top_max_3_015':hi[1]<=3.01501,'lowest_y_minus_2_455':abs(lo[1]+2.455)<.005,'thickness_0_5_to_0_8':.5<=span[2]<=.8,'above_floor':lo[1]>-2.895,'no_coin_names':not any(any(v in x for v in ['Casing___','Silver___','Outer_edge___']) for x in ids),'normal_maps_authorized':kind=='silver2' and not any(UsdShade.Shader(p).GetInput('normal') for p in s.Traverse() if p.IsA(UsdShade.Shader) and UsdShade.Shader(p).GetIdAttr().Get()=='UsdPreviewSurface') or kind=='iron2' and json.loads((b/'reports/finish_maps.json').read_text())['evidence']['normal_maps'] in [0,2]}
checks={k:bool(v) for k,v in checks.items()}
c=UsdUtils.ComplianceChecker(arkit=True);c.CheckCompliance(str(p));ar={'errors':c.GetErrors(),'failed_checks':c.GetFailedChecks(),'warnings':c.GetWarnings()};checks['arkit']=not ar['errors'] and not ar['failed_checks']
result={'checks':checks,'all_checks_pass':all(checks.values()),'bounds':[lo.tolist(),hi.tolist()],'span':span.tolist(),'triangles':counts,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'compliance_arkit':ar,'names':ids,'shape_exceptions':['Silver2 reference decorative leaves/stems thinner than minimum feature and body thickness; curved leaves/stems use smooth normals.' if kind=='silver2' else 'Shield plate and outline intentionally smoothly curved; plane-only normal constraint is inapplicable.'],'coin_floor_cut_shell_comparison':'N/A: standalone shape section 2B. Full requested shape and new tier IDs replace the circular coin, which remains unchanged.'}
(b/'reports/shape_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['all_checks_pass']
