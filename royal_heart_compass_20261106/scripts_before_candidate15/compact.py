"""Lossless material batching of the installed badge family on working copies."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,subprocess,tempfile,zipfile,shutil
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf
ROOT=Path(__file__).resolve().parent

def primitive_text(prim):
 layer=Sdf.Layer.CreateAnonymous();Sdf.CreatePrimInLayer(layer,prim.GetPath().GetParentPath());Sdf.CopySpec(prim.GetStage().GetRootLayer(),prim.GetPath(),layer,prim.GetPath());return layer.ExportToString()

def expanded(a,interp,t):
 a=np.asarray(a);a=a.reshape(len(a),-1)
 if interp in ['vertex','varying']:return a[t]
 if interp=='faceVarying':return a.reshape(len(t),3,-1)
 if interp=='uniform':return np.repeat(a[:,None,:],3,axis=1)
 if interp=='constant':return np.broadcast_to(a.reshape(1,1,-1),(len(t),3,a.shape[-1]))
 raise ValueError(interp)

def read(m):
 p=np.asarray(m.GetPointsAttr().Get(),np.float32);t=np.asarray(m.GetFaceVertexIndicesAttr().Get(),np.int32).reshape(-1,3)
 assert np.all(np.asarray(m.GetFaceVertexCountsAttr().Get())==3)
 n=expanded(m.GetNormalsAttr().Get(),str(m.GetNormalsInterpolation()),t).astype(np.float32)
 arrays=[p[t],n];schema=[]
 for pv in sorted(UsdGeom.PrimvarsAPI(m).GetPrimvars(),key=lambda x:x.GetPrimvarName()):
  if not pv.HasValue():continue
  a=expanded(pv.ComputeFlattened(),str(pv.GetInterpolation()),t)
  assert a.dtype.kind=='f',(m.GetPath(),pv.GetName(),a.dtype)
  arrays.append(a.astype(np.float32));schema.append((pv.GetPrimvarName(),str(pv.GetTypeName()),a.shape[-1]))
 mat=UsdShade.MaterialBindingAPI(m).ComputeBoundMaterial()[0];assignment=np.full(len(t),str(mat.GetPath()) if mat else '',object)
 for sub in UsdGeom.Subset.GetGeomSubsets(m,'face','materialBind'):
  material=UsdShade.MaterialBindingAPI(sub).ComputeBoundMaterial()[0];assignment[np.asarray(sub.GetIndicesAttr().Get(),np.int32)]=str(material.GetPath())
 assert all(assignment)
 return np.concatenate(arrays,axis=2).astype(np.float32),tuple(schema),assignment

def props(m):
 return (str(m.GetOrientationAttr().Get()),bool(m.GetDoubleSidedAttr().Get()),str(m.GetVisibilityAttr().Get()),str(m.GetPurposeAttr().Get()),str(m.GetSubdivisionSchemeAttr().Get()))

def signatures(stage):
 chunks=defaultdict(list)
 for prim in stage.Traverse():
  if not prim.IsA(UsdGeom.Mesh):continue
  m=UsdGeom.Mesh(prim);a,s,assignment=read(m)
  for mat in dict.fromkeys(assignment):chunks[(mat,s,props(m))].append(a[assignment==mat])
 out={}
 for key,arrays in chunks.items():
  a=np.concatenate(arrays);rows=a.reshape(len(a),-1).view(np.uint32);order=np.lexsort(rows.T[::-1]);out[repr(key)]=dict(triangles=len(a),sha256=hashlib.sha256(np.ascontiguousarray(rows[order]).tobytes()).hexdigest())
 return out

def counts(stage):
 ms=[UsdGeom.Mesh(p) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
 return dict(meshes=len(ms),sections=sum(len(set(read(m)[2])) for m in ms),triangles=sum(len(m.GetFaceVertexIndicesAttr().Get())//3 for m in ms),vertices=sum(len(m.GetPointsAttr().Get()) for m in ms))

def compact(row):
 base=ROOT/row['slug'];c=base/'candidate14';c.mkdir(exist_ok=True)
 source=Path(row['source']);stage=Usd.Stage.Open(str(source));before=counts(stage)
 if row['status']=='already_optimized':return dict(status='already_optimized',before=before,after=before)
 exclusions=json.loads((ROOT/'review_exclusions.json').read_text())
 if row['key'] in exclusions and row['source_sha256']==exclusions[row['key']]['source_sha256']:
  return dict(status='retained_rendering_baseline',before=before,after=before,reason=exclusions[row['key']]['reason'])
 expected=signatures(stage)
 mats={str(p.GetPath()):primitive_text(p) for p in stage.Traverse() if p.IsA(UsdShade.Material)}
 protected=set(row['protected_mesh_paths']);batches=defaultdict(list);preserved={}
 actual_gems=set()
 for prim in stage.Traverse():
  if not prim.IsA(UsdGeom.Mesh):continue
  material=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
  if material and material.GetPrim().GetName().startswith('CrestGem_'):actual_gems.add(str(prim.GetPath()))
 assert actual_gems <= protected, 'Protection manifest is stale: an exported optical stone would be merged'
 protected |= actual_gems
 for prim in [p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]:
  m=UsdGeom.Mesh(prim)
  # Runtime geometry lookups and independent convex optical stones stay intact.
  if str(prim.GetPath()) in protected or UsdGeom.Xformable(prim).GetOrderedXformOps():
   preserved[str(prim.GetPath())]=primitive_text(prim);continue
  assert not prim.GetChildren() or all(x.IsA(UsdGeom.Subset) for x in prim.GetChildren())
  a,s,assignment=read(m)
  # Same parent keeps any inherited transforms and attributes unchanged.
  for mat in dict.fromkeys(assignment):batches[(str(prim.GetParent().GetPath()),mat,s,props(m))].append(a[assignment==mat])
 # Splitting to one material per mesh can increase object count. Only package a
 # candidate when either object count or actual material section count improves.
 predicted=len(preserved)+len(batches)
 if predicted>=before['meshes'] and predicted>=before['sections']:
  return dict(status='already_minimal',before=before,after=before)
 with tempfile.TemporaryDirectory(prefix='badge_batch_',dir='/tmp') as temp:
  pkg=Path(temp)
  with zipfile.ZipFile(source) as z:
   extra=[n for n in z.namelist() if not n.endswith('/') and not n.endswith(('.usdc','.usda','.usd'))]
   for name in extra:
    dest=pkg/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
  stage.GetRootLayer().Export(str(pkg/'badge.usdc'));out=Usd.Stage.Open(str(pkg/'badge.usdc'))
  for prim in [p for p in out.Traverse() if p.IsA(UsdGeom.Mesh)]:
   if str(prim.GetPath()) not in preserved:out.RemovePrim(prim.GetPath())
  for i,((parent,mat,s,pr),chunks) in enumerate(sorted(batches.items())):
   a=np.concatenate(chunks);corners=a.reshape(-1,a.shape[-1]);flat=np.array_equal(a[:,:,3:6],np.repeat(a[:,:1,3:6],3,axis=1))
   columns=[0,1,2]+list(range(6,corners.shape[-1])) if flat else list(range(corners.shape[-1]))
   key=np.ascontiguousarray(corners[:,columns]).view(np.uint32)
   _,first,inverse=np.unique(key,axis=0,return_index=True,return_inverse=True);order=np.argsort(first);remap=np.empty(len(first),np.int32);remap[order]=np.arange(len(first));v=corners[first[order]];t=remap[inverse].reshape(-1,3)
   mesh=UsdGeom.Mesh.Define(out,parent+'/CompactBatch_'+str(i));mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(v[:,:3]));mesh.CreateFaceVertexCountsAttr([3]*len(t));mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist())
   mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(a[:,0,3:6] if flat else v[:,3:6]));mesh.SetNormalsInterpolation('uniform' if flat else 'vertex')
   offset=6
   for name,typ,width in s:
    pv=UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(name,Sdf.ValueTypeNames.Find(typ),'vertex');data=v[:,offset:offset+width];offset+=width
    ctor={1:Vt.FloatArray,2:Vt.Vec2fArray,3:Vt.Vec3fArray,4:Vt.Vec4fArray}[width];pv.Set(ctor.FromNumpy(data.ravel() if width==1 else data))
   mesh.CreateOrientationAttr(pr[0]);mesh.CreateDoubleSidedAttr(pr[1]);mesh.CreateVisibilityAttr(pr[2]);mesh.CreatePurposeAttr(pr[3]);mesh.CreateSubdivisionSchemeAttr(pr[4]);mesh.CreateExtentAttr([Gf.Vec3f(*map(float,v[:,:3].min(0))),Gf.Vec3f(*map(float,v[:,:3].max(0)))])
   UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(UsdShade.Material(out.GetPrimAtPath(mat)))
  assert signatures(out)==expected,'Render attributes changed'
  for p,value in {**mats,**preserved}.items():assert primitive_text(out.GetPrimAtPath(p))==value,('Protected spec changed',p)
  out.GetRootLayer().Export(str(pkg/'fresh.usdc'));(pkg/'fresh.usdc').replace(pkg/'badge.usdc')
  output=c/'model.usdz';output.unlink(missing_ok=True);subprocess.run(['/usr/bin/usdzip',str(output),'badge.usdc',*extra],cwd=pkg,capture_output=True,check=True)
 packed=Usd.Stage.Open(str(output));assert signatures(packed)==expected
 with zipfile.ZipFile(source) as a,zipfile.ZipFile(output) as b:assert all(a.read(n)==b.read(n) for n in extra)
 check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(output)],capture_output=True,text=True);(c/'usdchecker.txt').write_text(check.stdout+check.stderr);assert check.returncode==0,check.stdout+check.stderr
 report=dict(status='validated_candidate',before=before,after=counts(packed),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes_before=source.stat().st_size,bytes_after=output.stat().st_size,all_triangle_corner_attributes_and_materials_identical=True,all_material_graphs_unchanged=True,protected_meshes_unchanged=list(preserved),all_textures_byte_identical=True,arkit_valid=True)
 (c/'validation.json').write_text(json.dumps(report,indent=2)+'\n');return report

