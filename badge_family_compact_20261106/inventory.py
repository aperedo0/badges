"""Inventory the current installed badge family without editing its sources."""
from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json,re,shutil
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'asset_inventory.json').read_text());byhash=defaultdict(list)
for row in rows:byhash[row['sha256']].append(row)
swift=(ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift').read_text()
items=json.loads(re.search(r'static let items: \[String: String\] = (\[.*?\])',swift).group(1).replace('[','{').replace(']','}'))
out=[]
for digest,aliases in byhash.items():
 preview=next(a for a in aliases if a['origin']=='preview');dataset=preview['dataset']
 if 'Preview' in dataset:
  name=dataset.removeprefix('Badge3DPreview');key=name[0].lower()+name[1:];title=items[key]
 else:key=dataset.removeprefix('Badge3DModel').lower();title=key.title()
 if key=='iron':title='Original Iron'
 slug=re.sub(r'(?<!^)(?=[A-Z])','_',key).lower()
 base=ROOT/'badges'/slug/'baseline';base.mkdir(parents=True,exist_ok=True);copy=base/'model.usdz'
 if not copy.exists():shutil.copyfile(preview['path'],copy)
 assert hashlib.sha256(copy.read_bytes()).hexdigest()==digest
 s=Usd.Stage.Open(str(copy));meshes=[UsdGeom.Mesh(p) for p in s.Traverse() if p.IsA(UsdGeom.Mesh)]
 mats=Counter();normals=Counter();uvs=Counter();extra=Counter();nontri=0;transformed=[];protected=[];verts=0;tris=0;sections=0
 for m in meshes:
  mat=UsdShade.MaterialBindingAPI(m).ComputeBoundMaterial()[0];matname=mat.GetPrim().GetName() if mat else '<subsets>';mats[matname]+=1;normals[str(m.GetNormalsInterpolation())]+=1
  sizes=np.asarray(m.GetFaceVertexCountsAttr().Get());nontri+=int((sizes!=3).sum());tris+=int(np.maximum(sizes-2,0).sum());verts+=len(m.GetPointsAttr().Get());sections+=1+len(UsdGeom.Subset.GetGeomSubsets(m,'face','materialBind'))
  prim=m.GetPrim();names=[prim.GetName(),prim.GetDisplayName()]
  if matname=='DiamondGem' or matname.startswith('CrestGem_') or any('Casing___' in n or 'Inset___' in n for n in names):protected.append(str(prim.GetPath()))
  if UsdGeom.Xformable(prim).GetOrderedXformOps():transformed.append(str(prim.GetPath()))
  for pv in UsdGeom.PrimvarsAPI(m).GetPrimvars():uvs[pv.GetPrimvarName()+':'+str(pv.GetTypeName())+':'+str(pv.GetInterpolation())]+=1
  for a in prim.GetAttributes():
   if a.HasAuthoredValueOpinion() and a.GetName() not in ['points','normals','faceVertexCounts','faceVertexIndices','extent','subdivisionScheme'] and not a.GetName().startswith('primvars:'):extra[a.GetName()]+=1
 item=dict(key=key,slug=slug,title=title,dataset=dataset,source_sha256=digest,aliases=aliases,source=str(copy),meshes=len(meshes),material_sections=sections,materials=len(mats),material_names=dict(mats),normal_interpolations=dict(normals),primvars=dict(uvs),other_authored_attributes=dict(extra),non_triangular_faces=nontri,transformed_meshes=transformed,protected_mesh_paths=protected,triangles=tris,vertices=verts,bytes=copy.stat().st_size,status='already_optimized' if key=='astralNavigator' else 'pending')
 out.append(item)
(ROOT/'manifest.json').write_text(json.dumps(out,indent=2)+'\n')
for r in sorted(out,key=lambda a:a['meshes'],reverse=True):print(f"{r['title']:21} meshes={r['meshes']:4} materials={r['materials']:3} protected={len(r['protected_mesh_paths']):3} tris={r['triangles']:7} nontri={r['non_triangular_faces']:4} xform={len(r['transformed_meshes']):2} attrs={list(r['other_authored_attributes'])}")
print('PRIMVARS',dict(sum((Counter(r['primvars']) for r in out),Counter())))
