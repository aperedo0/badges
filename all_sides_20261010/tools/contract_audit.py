import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
selection=json.loads((ROOT/'selection.json').read_text());report={}
for tier,num in selection.items():
 p=Path(MANIFEST[tier]['work'])/'candidates'/num/(tier+'_badge_mobile.usdz');st=Usd.Stage.Open(str(p));allpoints=[];used=set();uvchecks=[]
 assert UsdGeom.GetStageUpAxis(st)=='Y';assert UsdGeom.GetStageMetersPerUnit(st)==1
 for prim in st.Traverse():
  assert prim.GetTypeName() not in ['Camera','DistantLight','SphereLight','DomeLight','RectLight','DiskLight','CylinderLight']
  assert not prim.GetAttribute('xformOpOrder').Get()
  assert prim.GetName() not in ['Casing___smooth_rounded_outer_edge_mobile_geometry','Silver___circumferential_brushed_steel']
  if not prim.IsA(UsdGeom.Mesh):continue
  pts,f,n,m,uv=read_mesh(prim);allpoints.append(pts)
  for mat in set(m):
   assert mat;mp=st.GetPrimAtPath(mat);assert mp
   for child in Usd.PrimRange(mp):
    if child.IsA(UsdShade.Shader):
     sh=UsdShade.Shader(child);ident=sh.GetIdAttr().Get()
     if ident=='UsdPreviewSurface':used.add(str(child.GetPath()))
     if ident=='UsdPrimvarReader_float2':
      name=sh.GetInput('varname').Get();assert name in uv,(tier,prim.GetPath(),mat,name,list(uv));uvchecks.append(str(prim.GetPath())+':'+name)
 allpoints=np.concatenate(allpoints);radius=float(np.linalg.norm(allpoints[:,[0,2]],axis=1).max());lo=allpoints.min(0);hi=allpoints.max(0)
 assert radius<=3.35+1e-5,(tier,radius)
 assert lo[1]>=-2.895-1e-5 and hi[1]<=3.015+1e-5
 if tier!='gold':assert abs(lo[1]+2.455)<1e-5
 assert abs(lo[0]+hi[0])<.03 and abs(lo[2]+hi[2])<.08
 report[tier]={'max_width_any_turn':2*radius,'bounds':[lo.tolist(),hi.tolist()],'floating_height_guideline_met':bool(abs(lo[1]+2.455)<1e-5),'materials_preview_surface':len(used),'reader_uv_matches':sorted(set(uvchecks)),'no_transforms_or_stage_objects':True}
(ROOT/'contract_audit.json').write_text(json.dumps(report,indent=2)+'\n');print({t:r['max_width_any_turn'] for t,r in report.items()})
