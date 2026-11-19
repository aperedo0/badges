"""Check the exact compact packages against the app contract and source gems."""
from pathlib import Path
import json,hashlib,zipfile
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parent;report={}
for row in json.loads((ROOT/'manifest.json').read_text()):
 C=ROOT/row['slug']/'candidate14';path=C/'model.usdz';stage=Usd.Stage.Open(str(path));base=Usd.Stage.Open(row['source'])
 assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
 allp=[];gems={};triangles=0
 for prim in stage.Traverse():
  assert 'light' not in prim.GetTypeName().lower() and prim.GetTypeName()!='Camera'
  if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
  if not prim.IsA(UsdGeom.Mesh):continue
  assert prim.GetName()!='Casing___smooth_rounded_outer_edge_mobile_geometry'
  mesh=UsdGeom.Mesh(prim);p=np.asarray(mesh.GetPointsAttr().Get());allp.append(p);triangles+=len(mesh.GetFaceVertexIndicesAttr().Get())//3
  material=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0];assert material
  surface=material.ComputeSurfaceSource()[0];assert surface.GetIdAttr().Get()=='UsdPreviewSurface'
  for child in Usd.PrimRange(material.GetPrim()):
   if child.GetTypeName()=='Shader' and UsdShade.Shader(child).GetIdAttr().Get()=='UsdPrimvarReader_float2':
    name=UsdShade.Shader(child).GetInput('varname').Get();assert UsdGeom.PrimvarsAPI(mesh).GetPrimvar(name).HasValue()
  if material.GetPrim().GetName().startswith('CrestGem_'):
   gems[str(prim.GetPath())]=material.GetPrim().GetName()
   assert str(prim.GetPath()) in row['protected_mesh_paths']
   source=UsdGeom.Mesh(base.GetPrimAtPath(prim.GetPath()));assert np.array_equal(p,np.asarray(source.GetPointsAttr().Get()))
   assert list(mesh.GetFaceVertexIndicesAttr().Get())==list(source.GetFaceVertexIndicesAttr().Get())
 assert set(gems)==set(row['protected_mesh_paths'])
 p=np.vstack(allp);low=p.min(0);high=p.max(0)
 assert low[1]>=-2.45501 and high[1]<=3.01501 and abs(p[:,0]).max()<=3.35
 assert abs(low[0]+high[0])<1e-5 and abs(low[2]+high[2])<1e-5
 if row['slug']=='ruby_crown':assert set(gems.values())=={'CrestGem_Ruby','CrestGem_Ice'}
 report[row['slug']]=dict(meshes=len(allp),optical_meshes=len(gems),triangles=triangles,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounds=[low.tolist(),high.tolist()],all_runtime_gem_meshes_preserved=True,app_contract_passed=True)
(ROOT/'asset_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
