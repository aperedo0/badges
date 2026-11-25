"""Check the actual delivered package, including hard normals after an index split."""
from pathlib import Path
from collections import Counter
from pxr import Usd,UsdGeom,UsdShade
import numpy as np, zipfile, json, sys
root=Path(__file__).resolve().parents[1]
folder=root/(sys.argv[1] if len(sys.argv)>1 else json.loads((root/'design.json').read_text())['candidate'])
file=folder/'model.usdz';st=Usd.Stage.Open(str(file))
assert UsdGeom.GetStageUpAxis(st)=='Y' and UsdGeom.GetStageMetersPerUnit(st)==1
archive=zipfile.ZipFile(file)
assert archive.testzip() is None and file.stat().st_size<5000000
report={};bounds=[]
for prim in st.Traverse():
    assert not prim.IsA(UsdGeom.Camera) and not prim.GetTypeName().endswith('Light')
    if prim.IsA(UsdGeom.Xformable):
        assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
    if prim.GetTypeName()=='Shader':
        sh=UsdShade.Shader(prim)
        if sh.GetIdAttr().Get()=='UsdUVTexture':
            asset=sh.GetInput('file').Get()
            assert asset.path in archive.namelist() and asset.resolvedPath
    if not prim.IsA(UsdGeom.Mesh):continue
    mesh=UsdGeom.Mesh(prim);pts=np.asarray(mesh.GetPointsAttr().Get());tri=np.asarray(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
    assert np.all(np.asarray(mesh.GetFaceVertexCountsAttr().Get())==3)
    u,weld=np.unique(pts,axis=0,return_inverse=True);wtri=weld[tri]
    edges=Counter((a[i],a[(i+1)%3]) for a in wtri for i in range(3))
    assert all(value==1 and edges[(b,a)]==1 for (a,b),value in edges.items())
    a,b,c=pts[tri].transpose(1,0,2);cross=np.cross(b-a,c-a);areas=np.linalg.norm(cross,axis=1)
    assert areas.min()>1e-12 and np.einsum('ij,ij->i',a,np.cross(b,c)).sum()>0
    mat=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0].GetPrim().GetName()
    if 'Ruby' in mat:
        n=np.asarray(mesh.GetNormalsAttr().Get());dot=(cross[:,None,:]/areas[:,None,None]*n[tri]).sum(axis=-1)
        assert mesh.GetNormalsInterpolation()=='vertex' and dot.min()>.99999,(prim.GetName(),dot.min())
    else:assert UsdGeom.PrimvarsAPI(mesh).GetPrimvar('st').HasValue()
    report[prim.GetName()]=dict(triangles=len(tri),closed=True,material=mat)
    bounds.append(np.vstack((pts.min(axis=0),pts.max(axis=0))))
bbox=[np.min(bounds,axis=0)[0],np.max(bounds,axis=0)[1]]
assert bbox[0][1]>=-2.45501 and bbox[1][1]<3.015
assert max(abs(bbox[0][0]),abs(bbox[1][0]))<3.35 and abs(bbox[0][2]+bbox[1][2])<1e-5
report=dict(file_bytes=file.stat().st_size,triangles=sum(d['triangles'] for d in report.values()),pieces=report,bounds=np.asarray(bbox).tolist())
(folder/'package_check.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['triangles'],report['file_bytes'])
