from pathlib import Path
from collections import Counter
import hashlib,json,numpy as np,subprocess,sys
from pxr import Usd,UsdGeom,UsdShade
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from pack import shell_signature
name=sys.argv[1];p=R/name/'mobile'/(name+'_badge_mobile.usdz');s=Usd.Stage.Open(str(p));template=Usd.Stage.Open(str(R/'shell_template.usdz'))
assert shell_signature(s)==shell_signature(template)
assert UsdGeom.GetStageUpAxis(s)=='Y' and UsdGeom.GetStageMetersPerUnit(s)==1
points=[]
for prim in s.Traverse():
 assert prim.GetTypeName() not in ['Camera','DomeLight','SphereLight','RectLight','DistantLight']
 if prim.IsA(UsdGeom.Xformable):assert np.allclose(np.asarray(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default())),np.eye(4))
 if prim.IsA(UsdGeom.Mesh):
  m=UsdGeom.Mesh(prim);q=np.asarray(m.GetPointsAttr().Get());assert np.isfinite(q).all();points.append(q);assert np.isfinite(np.asarray(m.GetNormalsAttr().Get())).all()
 if prim.IsA(UsdShade.Shader):
  sh=UsdShade.Shader(prim)
  if sh.GetInput('file'):assert sh.GetInput('file').Get().resolvedPath
allp=np.concatenate(points);assert allp[:,1].min()>=-2.895001 and allp[:,1].max()<=3.015001;assert max(abs(allp[:,0]))<=3.015001
# A welded shell may be open only on the intentional floor cut.
a=np.load(R/'shell_geometry.npz');q=a['points'];t=a['triangles'];key=np.round(q/1e-5).astype(np.int64);_,ids=np.unique(key,axis=0,return_inverse=True);faces=ids[t]
counts=Counter(tuple(sorted(e)) for f in faces for e in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]);open_edges=[e for e,c in counts.items() if c==1];assert all(c<=2 for c in counts.values())
welded=np.zeros((ids.max()+1,3));welded[ids]=q
assert all(np.allclose(welded[list(e),1],-2.895,atol=1e-5) for e in open_edges)
source=R.parent/'badge_realitykit_silver/mobile/silver_badge_mobile.usdz';assert hashlib.sha256(source.read_bytes()).hexdigest()=='5d64e709da342ad73d747c5873589e73a8d0e09daf2797f0d0f523693a7219ce'
subprocess.run(['/usr/bin/usdchecker','--arkit',str(p)],check=True)
result=json.loads((R/name/'model.json').read_text());result.update({'matches_authorized_shell_template':True,'original_silver_unchanged':True,'shell_open_only_at_floor':True,'identity_transforms':True,'textures_resolve':True,'bounds_min':allp.min(0).tolist(),'bounds_max':allp.max(0).tolist()});(R/name/'validation.json').write_text(json.dumps(result,indent=2))
print(name+' contract passed; new shell has no gaps except the intentional floor cut.')
