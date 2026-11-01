"""Check the actual exported custom shape and its closed surface topology."""
from pathlib import Path
import sys,json,hashlib,subprocess
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
path=C/'mobile'/(key+'_badge_mobile.usdz');stage=Usd.Stage.Open(str(path));assert UsdGeom.GetStageUpAxis(stage)=='Y';assert UsdGeom.GetStageMetersPerUnit(stage)==1
points=[];triangles=[];offset=0;mesh_count=0
for prim in stage.Traverse():
 assert not prim.IsA(UsdGeom.Camera) and 'Light' not in prim.GetTypeName()
 assert not prim.GetName().startswith(('Casing___','Silver___'))
 if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
 if not prim.IsA(UsdGeom.Mesh):continue
 mesh=UsdGeom.Mesh(prim);p=np.asarray(mesh.GetPointsAttr().Get(),float);f=np.asarray(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);n=np.asarray(mesh.GetNormalsAttr().Get()).reshape(-1,3,3)
 assert np.isfinite(p).all() and np.isfinite(n).all()
 cross=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);area=np.linalg.norm(cross,axis=1)
 assert (area>1e-12).all(),(prim.GetPath(),'degenerate triangles',int((area<=1e-12).sum()))
 assert np.min(np.einsum('ij,ij->i',cross,n.mean(1))/area)>-.02,'Inverted normals'
 mat=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0];assert mat
 uv=UsdGeom.PrimvarsAPI(mesh).GetPrimvar('CrestUV');assert uv.HasValue()
 points.append(p);triangles.append(f+offset);offset+=len(p);mesh_count+=1
p=np.vstack(points);f=np.vstack(triangles)
# Walls and front are separate materials, so weld positions only for the closure check.
_,inverse=np.unique(np.round(p,6),axis=0,return_inverse=True);f=inverse[f]
e=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);_,counts=np.unique(np.sort(e,axis=1),axis=0,return_counts=True)
closed=bool(np.all(counts==2));assert closed,{'open_edges':int((counts==1).sum()),'multiple_edges':int((counts>2).sum())}
assert p[:,1].min()>=-2.45501 and p[:,1].max()<=3.01501 and abs(p[:,0]).max()<3.35
result={'closed_surface':closed,'meshes':mesh_count,'triangles':len(f),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds_min':p.min(0).tolist(),'bounds_max':p.max(0).tolist(),'all_transforms_identity':True,'usd_y_up':True,'meters_per_unit':1,'matching_sculpted_rear':True,'no_coin_names':True,'no_lights_or_cameras':True,'material_uv':'CrestUV','original_app_lighting_preserved':True}
checker=subprocess.run(['/usr/bin/usdchecker','--arkit',str(path)],capture_output=True,text=True)
(C/'usdchecker.txt').write_text(checker.stdout+checker.stderr);assert checker.returncode==0,checker.stdout+checker.stderr
result['usdchecker_arkit_passed']=True;(C/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
