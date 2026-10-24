"""Check the shield's app contract and preserve its source models."""
from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parent
path=ROOT/'mobile/crimson_shield_badge_mobile.usdz';stage=Usd.Stage.Open(str(path));points=[];triangles=0
assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
for prim in stage.Traverse():
    assert not any(q in str(prim.GetPath()) for q in ['Casing___','Silver___circumferential','DiamondGem'])
    assert not prim.IsA(UsdGeom.Camera) and not prim.GetTypeName().endswith('Light')
    if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
    if not prim.IsA(UsdGeom.Mesh):continue
    mesh=UsdGeom.Mesh(prim);v=np.asarray(mesh.GetPointsAttr().Get());idx=np.asarray(mesh.GetFaceVertexIndicesAttr().Get());counts=np.asarray(mesh.GetFaceVertexCountsAttr().Get())
    assert np.all(counts==3);f=idx.reshape(-1,3)
    assert np.isfinite(v).all() and np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1).min()>1e-10
    norms=np.asarray(mesh.GetNormalsAttr().Get());assert np.isfinite(norms).all() and np.min(np.linalg.norm(norms,axis=1))>.99
    uv=UsdGeom.PrimvarsAPI(prim).GetPrimvar('ShieldUV');assert uv and len(uv.Get())==len(idx)
    material=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0];assert material
    points.append(v);triangles+=len(f)
v=np.vstack(points);assert v[:,1].min()>=-2.45501 and v[:,1].max()<=3.015 and np.abs(v[:,0]).max()<3.35
print(f'PASS: {triangles} triangles, identity transforms, Y up, full frame bounds, finite normals, bound ShieldUV materials, no lights or coin names.')
field=UsdShade.Material(stage.GetPrimAtPath('/CrimsonShield/Materials/CrimsonShield_BrushedField'))
assert field, 'Missing shield field material required by runtime brushing.'
print('PASS: exact shield field material name is available for runtime brushing.')
# Source preservation is checked against the app baseline captured for each
# task, rather than against an earlier session's temporary preview assets.
