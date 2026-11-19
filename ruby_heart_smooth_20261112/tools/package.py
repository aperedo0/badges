from pathlib import Path
from pxr import Usd,UsdGeom,UsdUtils,Gf,Vt,Sdf
import zipfile,numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];C=R/'candidate01';source=R.parent/'ruby_heart_claude_20261107/candidate06/model.usdz'
package=C/'package';package.mkdir(exist_ok=True)
with zipfile.ZipFile(source) as z:z.extractall(package);root=z.namelist()[0]
d=np.load(C/'geometry.npz');old=np.load(source.parent/'geometry.npz')
s=Usd.Stage.Open(str(package/root));m=UsdGeom.Mesh(s.GetPrimAtPath('/Badge/Frame'))
assert np.array_equal(np.array(m.GetPointsAttr().Get()),old['frame_v'].astype(np.float32))
assert np.array_equal(d['frame_uv'],old['frame_uv']) and np.array_equal(d['frame_t'],old['frame_t'])
m.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(d['frame_v'].astype(np.float32)))
m.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(d['frame_n'].astype(np.float32)))
s.GetRootLayer().Save();UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(package/root)),str(C/'model.usdz'))
a=Usd.Stage.Open(str(source));b=Usd.Stage.Open(str(C/'model.usdz'))
changes=[]
for p in a.Traverse():
 q=b.GetPrimAtPath(p.GetPath());assert q
 for attr in p.GetAttributes():
  av,bv=attr.Get(),q.GetAttribute(attr.GetName()).Get()
  if str(av)!=str(bv):changes.append(str(p.GetPath())+'.'+attr.GetName())
assert set(changes)=={'/Badge/Frame.points','/Badge/Frame.normals'},changes
with zipfile.ZipFile(source) as z1,zipfile.ZipFile(C/'model.usdz') as z2:
 assert z1.read('0/gold_brush_roughness.png')==z2.read('0/gold_brush_roughness.png')
V=d['frame_v'];T=d['frame_t'];unique,idx=np.unique(np.round(V,7),axis=0,return_inverse=True);tris=idx[T];tris=tris[(tris[:,0]!=tris[:,1])&(tris[:,1]!=tris[:,2])&(tris[:,2]!=tris[:,0])]
edges=np.sort(np.vstack([tris[:,[0,1]],tris[:,[1,2]],tris[:,[2,0]]]),axis=1);_,count=np.unique(edges,axis=0,return_counts=True)
result=dict(changed_attributes=changes,gem_exact=True,gold_graph_and_texture_exact=True,uv_topology_exact=True,frame_closed=bool((count==2).all()),edge_counts=dict(zip(*[x.tolist() for x in np.unique(count,return_counts=True)])),bounds=[V.min(0).tolist(),V.max(0).tolist()],max_displacement=float(np.linalg.norm(V-old['frame_v'],axis=1).max()),triangles=int(len(T)+len(d['gem_t'])),meshes=2,bytes=(C/'model.usdz').stat().st_size,sha256=hashlib.sha256((C/'model.usdz').read_bytes()).hexdigest())
(C/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
