"""Check shell preservation, closed geometry and mobile USD constraints."""
from pathlib import Path
import sys,json,zipfile,hashlib
from collections import Counter
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pack import SOURCES,SHELL,ROOT
results={}
for name,source in SOURCES.items():
 path=ROOT/name/'mobile'/(name+'_badge_mobile.usdz')
 a,b=Usd.Stage.Open(str(source)),Usd.Stage.Open(str(path))
 assert UsdGeom.GetStageUpAxis(b)=='Y'
 assert UsdGeom.GetStageMetersPerUnit(b)==1
 def attrs(prim):
  return {str(p.GetPath()):{x.GetName():((x.Get().path if isinstance(x.Get(),Sdf.AssetPath) else repr(x.Get())),[str(c) for c in x.GetConnections()]) for x in p.GetAttributes()} for p in Usd.PrimRange(prim)}
 assert attrs(a.GetPrimAtPath(SHELL))==attrs(b.GetPrimAtPath(SHELL))
 for material in ['Silver___circumferential_brushed_steel_Mobile_Casing','Shell_inner','Shell_bevel']:
  p='/Badge/_materials/'+material
  assert attrs(a.GetPrimAtPath(p))==attrs(b.GetPrimAtPath(p)),p
 with zipfile.ZipFile(source) as za,zipfile.ZipFile(path) as zb:
  for prim in b.Traverse():
   if prim.IsA(UsdShade.Shader) and 'New_' not in str(prim.GetPath()):
    f=UsdShade.Shader(prim).GetInput('file')
    if f:
     asset=f.Get().path
     assert za.read(asset)==zb.read(asset),asset
 points=[];degenerate=0;zeros=0
 for prim in b.Traverse():
  assert prim.GetTypeName() not in ['Camera','DistantLight','SphereLight','RectLight','DomeLight']
  if prim.HasAttribute('xformOpOrder'):assert not prim.GetAttribute('xformOpOrder').Get()
  if not prim.IsA(UsdGeom.Mesh):continue
  mesh=UsdGeom.Mesh(prim);p=np.asarray(mesh.GetPointsAttr().Get());points.append(p)
  assert np.isfinite(p).all()
  counts=np.asarray(mesh.GetFaceVertexCountsAttr().Get());indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get())
  assert (counts==3).all()
  t=indices.reshape(-1,3);tri=p[t]
  area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
  degenerate+=int((area<1e-12).sum())
  normals=np.asarray(mesh.GetNormalsAttr().Get());assert np.isfinite(normals).all()
  zeros+=int((np.linalg.norm(normals,axis=-1)<.01).sum())
  if str(prim.GetPath())==SHELL:
   _,w=np.unique(np.round(p/1e-5).astype(np.int64),axis=0,return_inverse=True)
   edges=Counter(tuple(sorted(e)) for f in w[t] for e in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])])
   assert all(v==2 for v in edges.values())
 p=np.concatenate(points);assert np.max(np.abs(p[:,0]))<=3.01501
 assert abs(p[:,1].min()+3.015)<1e-5 and abs(p[:,1].max()-3.015)<1e-5
 results[name]={'rim_geometry_materials_and_maps':'unchanged','closed_round_shell':True,'identity_transforms':True,'Y_up_meters':True,'no_lights_or_cameras':True,'degenerate_triangles':degenerate,'zero_normals':zeros,'bounds':[p.min(0).tolist(),p.max(0).tolist()]}
print(json.dumps(results,indent=2))
(ROOT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
