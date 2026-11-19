"""Batch identical materials while preserving every rendered triangle corner."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,shutil,subprocess,tempfile,zipfile
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf

ROOT=Path(__file__).resolve().parent
C=ROOT/'candidate01'
SOURCE=ROOT/'baseline/astral_navigator_badge_mobile.usdz'
OUTPUT=C/'mobile/astral_navigator_badge_mobile.usdz'

def expanded(data,interpolation,indices,nfaces):
 a=np.asarray(data,dtype=np.float32)
 if interpolation=='vertex' or interpolation=='varying':return a[indices]
 if interpolation=='faceVarying':return a.reshape(nfaces,3,-1)
 if interpolation=='uniform':return np.repeat(a[:,None,:],3,axis=1)
 if interpolation=='constant':return np.broadcast_to(a.reshape(1,1,-1),(nfaces,3,a.shape[-1]))
 raise ValueError(interpolation)

def read(mesh):
 p=np.asarray(mesh.GetPointsAttr().Get(),np.float32)
 assert np.all(np.asarray(mesh.GetFaceVertexCountsAttr().Get())==3)
 t=np.asarray(mesh.GetFaceVertexIndicesAttr().Get(),np.int32).reshape(-1,3)
 normals=expanded(mesh.GetNormalsAttr().Get(),mesh.GetNormalsInterpolation(),t,len(t))
 uv=UsdGeom.PrimvarsAPI(mesh).GetPrimvar('BadgeUV')
 coords=expanded(uv.ComputeFlattened(),uv.GetInterpolation(),t,len(t)) if uv else np.zeros((len(t),3,2),np.float32)
 mat=UsdShade.MaterialBindingAPI(mesh).ComputeBoundMaterial()[0]
 assignment=np.full(len(t),str(mat.GetPath()),object)
 for sub in UsdGeom.Subset.GetGeomSubsets(mesh,'face','materialBind'):
  material=UsdShade.MaterialBindingAPI(sub).ComputeBoundMaterial()[0]
  assignment[np.asarray(sub.GetIndicesAttr().Get(),np.int32)]=str(material.GetPath())
 return p,t,normals,coords,assignment

def primitive_text(prim):
 layer=Sdf.Layer.CreateAnonymous();Sdf.CreatePrimInLayer(layer,prim.GetPath().GetParentPath());Sdf.CopySpec(prim.GetStage().GetRootLayer(),prim.GetPath(),layer,prim.GetPath())
 return layer.ExportToString()

def signatures(stage):
 grouped=defaultdict(list)
 for prim in stage.Traverse():
  if not prim.IsA(UsdGeom.Mesh):continue
  p,t,n,uv,assignment=read(UsdGeom.Mesh(prim))
  for material in dict.fromkeys(assignment):
   select=assignment==material
   # A plain side material has no UV input; its unused UVs have no appearance.
   used_uv=uv[select] if material.endswith(('_metal','_field')) else np.zeros_like(uv[select])
   grouped[material].append(np.concatenate([p[t[select]],n[select],used_uv],axis=2).astype(np.float32))
 result={}
 for material,arrays in grouped.items():
  data=np.concatenate(arrays);rows=data.reshape(len(data),-1).view(np.uint32)
  order=np.lexsort(rows[:,::-1].T[::-1])
  result[material]=dict(triangles=len(data),sha256=hashlib.sha256(np.ascontiguousarray(rows[order]).tobytes()).hexdigest())
 return result

original=Usd.Stage.Open(str(SOURCE));expected=signatures(original)
mesh_prims=[p for p in original.Traverse() if p.IsA(UsdGeom.Mesh)]
materials={str(p.GetPath()):primitive_text(p) for p in original.Traverse() if p.IsA(UsdShade.Material)}
gems={str(p.GetPath()):primitive_text(p) for p in mesh_prims if UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()[0].GetPrim().GetName().startswith('CrestGem_')}
assert len(gems)==18
before_draw_sections=sum(1+len(UsdGeom.Subset.GetGeomSubsets(UsdGeom.Mesh(p),'face','materialBind')) for p in mesh_prims)
groups=[];data={}

with tempfile.TemporaryDirectory(prefix='astral_batch_',dir='/tmp') as temp:
 pkg=Path(temp)
 with zipfile.ZipFile(SOURCE) as archive:
  for name in archive.namelist():
   if name.startswith('textures/'):
    destination=pkg/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(archive.read(name))
 original.GetRootLayer().Export(str(pkg/'badge.usdc'))
 stage=Usd.Stage.Open(str(pkg/'badge.usdc'));batches=defaultdict(list)
 for prim in [q for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)]:
  mesh=UsdGeom.Mesh(prim);p,t,n,uv,assignment=read(mesh)
  if str(prim.GetPath()) in gems:
   i=len(groups);groups.append(dict(name=prim.GetDisplayName() or prim.GetName(),material=str(UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0].GetPath()),gem=True))
   data[str(i)+'_points']=p;data[str(i)+'_triangles']=t;data[str(i)+'_normals']=n;data[str(i)+'_uv']=uv
   continue
  for material in dict.fromkeys(assignment):
   selected=assignment==material
   used_uv=uv[selected] if material.endswith(('_metal','_field')) else np.zeros_like(uv[selected])
   shading='flat' if mesh.GetNormalsInterpolation()=='uniform' else 'smooth'
   batches[(material,shading)].append(np.concatenate([p[t[selected]],n[selected],used_uv],axis=2))
  stage.RemovePrim(prim.GetPath())

 for (material,shading),chunks in sorted(batches.items()):
  corners=np.concatenate(chunks).reshape(-1,8).astype(np.float32)
  # Share a GPU vertex only when all of its render attributes are identical.
  key=corners[:,[0,1,2,6,7]].copy() if shading=='flat' else corners
  _,first,inverse=np.unique(key.view(np.uint32),axis=0,return_index=True,return_inverse=True)
  order=np.argsort(first);remap=np.empty(len(first),np.int32);remap[order]=np.arange(len(first))
  vertices=corners[first[order]];triangles=remap[inverse].reshape(-1,3).astype(np.int32)
  label=material.rsplit('_',1)[-1];mesh=UsdGeom.Mesh.Define(stage,'/Badge/Batch_'+label+'_'+shading)
  mesh.GetPrim().SetDisplayName('Astral Navigator '+label+' batch')
  mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(vertices[:,:3]));mesh.CreateFaceVertexCountsAttr([3]*len(triangles));mesh.CreateFaceVertexIndicesAttr(triangles.ravel().tolist())
  corner_normals=corners.reshape(-1,3,8)[:,:,3:6]
  if shading=='flat':mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(corner_normals[:,0]));mesh.SetNormalsInterpolation('uniform')
  else:mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(vertices[:,3:6]));mesh.SetNormalsInterpolation('vertex')
  mesh.CreateSubdivisionSchemeAttr('none')
  if label in ['metal','field']:
   UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('BadgeUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(Vt.Vec2fArray.FromNumpy(vertices[:,6:8]))
  mesh.CreateExtentAttr([Gf.Vec3f(*map(float,vertices[:,:3].min(0))),Gf.Vec3f(*map(float,vertices[:,:3].max(0)))])
  UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(UsdShade.Material(stage.GetPrimAtPath(material)))
  i=len(groups);groups.append(dict(name=mesh.GetPrim().GetDisplayName(),material=material,gem=False))
  data[str(i)+'_points']=vertices[:,:3];data[str(i)+'_triangles']=triangles;data[str(i)+'_normals']=corner_normals;data[str(i)+'_uv']=vertices[:,6:8][triangles]

 stage.GetRootLayer().Save()
 assert signatures(stage)==expected,'A triangle position, normal, UV or material changed'
 for path,serialized in gems.items():assert primitive_text(stage.GetPrimAtPath(path))==serialized,('Gem changed',path)
 for path,serialized in materials.items():assert primitive_text(stage.GetPrimAtPath(path))==serialized,('Material changed',path)
 # A fresh crate drops the deleted source mesh payload from incremental USD
 # saves. Reusing the edited crate would retain both old and batched arrays.
 stage.GetRootLayer().Export(str(pkg/'compacted.usdc'))
 (pkg/'compacted.usdc').replace(pkg/'badge.usdc')
 files=['badge.usdc']+[str(p.relative_to(pkg)) for p in sorted((pkg/'textures').glob('*')) if p.is_file()]
 OUTPUT.unlink(missing_ok=True)
 subprocess.run(['/usr/bin/usdzip',str(OUTPUT),*files],cwd=pkg,check=True,capture_output=True)

packed=Usd.Stage.Open(str(OUTPUT));assert signatures(packed)==expected
with zipfile.ZipFile(SOURCE) as a,zipfile.ZipFile(OUTPUT) as b:
 texture_names=[name for name in a.namelist() if name.startswith('textures/') and not name.endswith('/')]
 assert all(a.read(name)==b.read(name) for name in texture_names)
checker=subprocess.run(['/usr/bin/usdchecker','--arkit',str(OUTPUT)],capture_output=True,text=True)
(C/'usdchecker.txt').write_text(checker.stdout+checker.stderr);assert checker.returncode==0,checker.stdout+checker.stderr
np.savez_compressed(C/'optimized_geometry.npz',**data);(C/'optimized_groups.json').write_text(json.dumps(groups,indent=2)+'\n')
points=np.vstack([data[str(i)+'_points'] for i in range(len(groups))])
report=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),meshes_before=len(mesh_prims),meshes_after=len(groups),material_sections_before=before_draw_sections,material_sections_after=len(groups),gem_meshes=18,triangles=sum(v['triangles'] for v in expected.values()),bytes_before=SOURCE.stat().st_size,bytes_after=OUTPUT.stat().st_size,all_triangle_corner_attributes_and_materials_identical=True,all_gem_prims_unchanged=True,all_material_graphs_unchanged=True,all_textures_byte_identical=True,arkit_valid=True,bounds_min=points.min(0).tolist(),bounds_max=points.max(0).tolist(),material_triangle_signatures=expected)
(C/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='material_triangle_signatures'},indent=2))
