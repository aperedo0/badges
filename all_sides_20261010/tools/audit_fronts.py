import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
sel=json.loads((ROOT/'selection.json').read_text());reports={}
for tier,num in sel.items():
 if tier in ['gold','diamond']:
  reports[tier]=[{'new_full_volume_geometry':True,'front_geometry_preservation_required':False,'reference_front_appearance_review_required':True}];continue
 w=Path(MANIFEST[tier]['work']);out=w/'candidates'/num
 original=Usd.Stage.Open(str(next((w/'source/installed').glob('*.usd*'))));new=Usd.Stage.Open(str(out/(tier+'_badge_mobile.usdz')))
 records=[]
 for prim in original.Traverse():
  if not prim.IsA(UsdGeom.Mesh):continue
  replacement=new.GetPrimAtPath(prim.GetPath())
  if not replacement:continue
  p,f,n,m,uv=read_mesh(prim);q,g,nn,mm,vv=read_mesh(replacement)
  mask=face_normals(p,f)[:,2]>1e-5;old_ids=np.flatnonzero(mask)
  # Compare vertices/UV/normals/material by the original triangle IDs. Candidate front
  # triangles are first for mirrored skins; Iron/Platinum preserve the source ordering.
  if tier in ['bronze','steel','silver'] and 'Lip' not in prim.GetName():new_ids=np.arange(mask.sum())
  elif tier=='iron' and 'Border' in prim.GetName():new_ids=np.flatnonzero(face_normals(q,g)[:,2]>1e-5)[:len(old_ids)]
  else:new_ids=old_ids
  same={'mesh':str(prim.GetPath()),'front_triangles':len(old_ids),'positions_equal':bool(np.array_equal(p[f[old_ids]],q[g[new_ids]])),'normals_equal':bool(np.array_equal(n[old_ids],nn[new_ids])),'uv_equal':all(np.array_equal(a[old_ids],vv[k][new_ids]) for k,a in uv.items()),'material_paths_equal':bool(np.array_equal(m[old_ids],mm[new_ids]))}
  records.append(same)
 reports[tier]=records
(ROOT/'front_data_audit.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports,indent=2))
