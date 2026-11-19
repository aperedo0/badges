from pathlib import Path
from pxr import Usd,UsdGeom,UsdUtils,Sdf,Vt,Gf
import numpy as np,zipfile,json,hashlib
R=Path(__file__).resolve().parents[1];C=R/'candidate03';source=R/'baseline/model.usdz';P=C/'package';P.mkdir(exist_ok=True)
with zipfile.ZipFile(source) as z:z.extractall(P);root=z.namelist()[0]
s=Usd.Stage.Open(str(P/root));m=UsdGeom.Mesh(s.GetPrimAtPath('/Badge/Gem'));d=np.load(C/'geometry.npz');V,N,T=d['gem_v'],d['gem_n'],d['gem_t']
m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(V.astype(np.float32)));m.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(N.astype(np.float32)));m.GetFaceVertexCountsAttr().Set(Vt.IntArray([3]*len(T)));m.GetFaceVertexIndicesAttr().Set(Vt.IntArray(T.astype(np.int32).ravel().tolist()));m.GetExtentAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*V.min(0).tolist()),Gf.Vec3f(*V.max(0).tolist())]));s.GetRootLayer().Save();UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(P/root)),str(C/'model.usdz'))
a=Usd.Stage.Open(str(source));b=Usd.Stage.Open(str(C/'model.usdz'));changes=[]
for p in a.Traverse():
 q=b.GetPrimAtPath(p.GetPath());assert q
 for attr in p.GetAttributes():
  if str(attr.Get())!=str(q.GetAttribute(attr.GetName()).Get()):changes.append(str(p.GetPath())+'.'+attr.GetName())
assert all(x.startswith('/Badge/Gem.') for x in changes),changes
with zipfile.ZipFile(source) as aa,zipfile.ZipFile(C/'model.usdz') as bb:assert aa.read('0/gold_brush_roughness.png')==bb.read('0/gold_brush_roughness.png')
_,idx=np.unique(V.astype(np.float32),axis=0,return_inverse=True);tri=idx[T];edges=np.sort(np.vstack([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);assert (counts==2).all(),np.unique(counts,return_counts=True)
vol=np.einsum('ij,ij->i',V[T[:,0]],np.cross(V[T[:,1]],V[T[:,2]])).sum()/6;assert vol>0
normalgeo=np.cross(V[T[:,1]]-V[T[:,0]],V[T[:,2]]-V[T[:,0]]);normalgeo/=np.linalg.norm(normalgeo,axis=1)[:,None];assert np.max(np.linalg.norm(normalgeo-N[T[:,0]],axis=1))<1e-5
result=dict(changed_attributes=changes,gold_geometry_and_finish_exact=True,app_optics_unchanged=True,gem_closed=True,outward_volume=float(vol),bounds=[V.min(0).tolist(),V.max(0).tolist()],meshes=2,material_sections=2,gem_triangles=int(len(T)),total_triangles=int(len(T)+len(d['frame_t'])),bytes=(C/'model.usdz').stat().st_size,sha256=hashlib.sha256((C/'model.usdz').read_bytes()).hexdigest())
(C/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
