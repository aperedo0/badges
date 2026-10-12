import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/12';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/11/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));source=Usd.Stage.Open(str(w/'source/installed/badge.usdc'))
notes=[]
for prim in [p for p in source.Traverse() if p.IsA(UsdGeom.Mesh) and any(k in p.GetName() for k in ['Lip','Collar','Flange'])]:
 p,f,n,m,uv=read_mesh(prim);sel=face_normals(p,f)[:,2]>1e-5
 write_mesh(st,prim.GetPath(),p,f[sel],n[sel],m[sel],{k:a[sel] for k,a in uv.items()})
 rp=p.copy();rp[:,0]*=-1;rp[:,2]*=-1;rn=n[sel]*[-1,1,-1]
 write_mesh(st,prim.GetParent().GetPath().AppendChild(prim.GetName()+'_MatchingRear'),rp,f[sel],rn,m[sel],{k:a[sel] for k,a in uv.items()})
 notes.append({'detail':prim.GetName(),'front_faces_unchanged':int(sel.sum()),'rear_camera_facing_skin_copied':True,'reason':'Remove the hidden halves of duplicated rolled details which otherwise protrude as extra ellipses across the band.'})
finish('gold',w,out,st,notes)
(ROOT/'gold12_selection.json').write_text(json.dumps({'gold':'12'})+'\n')
