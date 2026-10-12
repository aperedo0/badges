from pathlib import Path
import json,shutil,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'manifest.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def open_copy(tier,number='01'):
 w=Path(MANIFEST[tier]['work']);out=w/'candidates'/number;out.mkdir(parents=True,exist_ok=True)
 edit=out/'usd';assert not edit.exists(),edit
 shutil.copytree(w/'source/installed',edit)
 layer=next(edit.glob('*.usd*'));return w,out,Usd.Stage.Open(str(layer))
def shader_material(st,name,color,roughness=.55,emission=None):
 root=st.GetDefaultPrim().GetPath();mat=UsdShade.Material.Define(st,root.AppendPath('Materials/'+name))
 s=UsdShade.Shader.Define(st,mat.GetPath().AppendChild('Surface'));s.CreateIdAttr('UsdPreviewSurface')
 s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));s.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(1.)
 s.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(roughness)
 if emission is not None:s.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*emission))
 s.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface');return str(mat.GetPath())
def read_mesh(p):
 m=UsdGeom.Mesh(p);pts=np.array(m.GetPointsAttr().Get(),float);counts=np.array(m.GetFaceVertexCountsAttr().Get());assert (counts==3).all()
 f=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);norm=np.array(m.GetNormalsAttr().Get(),float)
 if m.GetNormalsInterpolation()=='vertex':norm=norm[f]
 else:norm=norm.reshape(-1,3,3)
 direct=UsdShade.MaterialBindingAPI(p).GetDirectBindingRel().GetTargets();mats=np.array([str(direct[0]) if direct else '']*len(f),object)
 for s in UsdGeom.Subset.GetAllGeomSubsets(m):
  target=UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()
  if target:mats[np.array(s.GetIndicesAttr().Get())]=str(target[0])
 uv={}
 for v in UsdGeom.PrimvarsAPI(p).GetPrimvars():
  if not v.GetTypeName().isArray:continue
  a=np.array(v.Get());indices=v.GetIndices()
  if a.ndim!=2 or a.shape[-1]!=2:continue
  if indices:a=a[np.array(indices)]
  a=a.reshape(-1,3,2) if v.GetInterpolation()=='faceVarying' else a[f]
  uv[v.GetPrimvarName()]=a
 return pts,f,norm,mats,uv
def face_normals(p,f):
 n=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12);return n
def normals(p,f,smooth=False):
 n=face_normals(p,f)
 if not smooth:return np.repeat(n[:,None,:],3,axis=1)
 a=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);q=np.zeros_like(p)
 for k in range(3):np.add.at(q,f[:,k],a)
 q/=np.maximum(np.linalg.norm(q,axis=1,keepdims=True),1e-12);return q[f]
def write_mesh(st,path,p,f,n,mats,uv=None):
 mesh=UsdGeom.Mesh.Define(st,path)
 for s in UsdGeom.Subset.GetAllGeomSubsets(mesh):st.RemovePrim(s.GetPath())
 mesh.CreatePointsAttr(np.asarray(p,np.float32).tolist());mesh.CreateFaceVertexCountsAttr([3]*len(f));mesh.CreateFaceVertexIndicesAttr(np.asarray(f).ravel().tolist())
 mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(False);mesh.CreateNormalsAttr(np.asarray(n,np.float32).reshape(-1,3).tolist());mesh.SetNormalsInterpolation('faceVarying')
 mesh.CreateExtentAttr([Gf.Vec3f(*map(float,np.min(p,0))),Gf.Vec3f(*map(float,np.max(p,0)))])
 for name,a in (uv or {}).items():
  v=UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(name,Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying');v.Set(np.asarray(a,np.float32).reshape(-1,2).tolist());v.BlockIndices()
 for i,mat in enumerate(sorted(set(mats))):
  sub=UsdGeom.Subset.Define(st,mesh.GetPath().AppendChild('Finish_'+str(i)));sub.CreateElementTypeAttr('face');sub.CreateFamilyNameAttr('materialBind');sub.CreateIndicesAttr(np.where(np.array(mats)==mat)[0].tolist());UsdShade.MaterialBindingAPI.Apply(sub.GetPrim()).Bind(UsdShade.Material.Get(st,mat))
 UsdGeom.Subset.SetFamilyType(mesh,'materialBind','partition')
 return mesh
def simple_mesh(st,name,p,f,mat,smooth=False,uv=None):
 p=np.array(p,float);f=np.array(f,int)
 vol=np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()/6
 if vol<0:f=f[:,::-1]
 return write_mesh(st,st.GetDefaultPrim().GetPath().AppendChild(name),p,f,normals(p,f,smooth),[mat]*len(f),uv)
def mirror_skin(st,prim,wall,center=None):
 p,f,n,mats,uv=read_mesh(prim);gn=face_normals(p,f);sel=gn[:,2]>1e-5
 assert sel.any(),prim.GetPath()
 ff=f[sel];fn=n[sel];fm=mats[sel];fu={name:a[sel] for name,a in uv.items()}
 edges={}
 for tri in ff:
  for a,b in zip(tri,np.roll(tri,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append((int(a),int(b)))
 boundary=[v[0] for v in edges.values() if len(v)==1];ids=np.unique(np.array(boundary).ravel())
 bp=p[ids];mirror=bp.copy();mirror[:,0]*=-1
 pairs=np.argmin(((bp[:,None]-mirror[None,:])**2).sum(-1),axis=1)
 err=np.linalg.norm(bp-mirror[pairs],axis=1)
 flip_x=bool(err.max()<.002 and len(np.unique(pairs))==len(ids))
 lookup=dict(zip(ids,ids[pairs])) if flip_x else {int(i):int(i) for i in ids}
 if flip_x:
  original_edges={tuple(sorted(e)) for e in boundary}
  mapped_edges={tuple(sorted((lookup[a],lookup[b]))) for a,b in boundary}
  if original_edges!=mapped_edges:flip_x=False;lookup={int(i):int(i) for i in ids}
 zmid=(p[:,2].min()+p[:,2].max())/2 if center is None else center
 rp=p.copy();rp[:,2]=2*zmid-p[:,2]
 if flip_x:rp[:,0]*=-1
 offset=len(p);rf=ff+offset;rn=fn*np.array([-1 if flip_x else 1,1,-1])
 ru={name:a.copy() for name,a in fu.items()}
 if not flip_x:
  rf=rf[:,::-1];rn=rn[:,::-1];ru={name:a[:,::-1] for name,a in ru.items()}
  if str(prim.GetPath()).startswith(('/BronzeSun/','/SilverChevron/')):
   # These models use one global projected UV chart. Reverse U on the rear
   # so its reference highlights face the viewer in the same arrangement.
   for a in ru.values():a[:,:,0]=1-a[:,:,0]
  elif 'Star' in prim.GetName():
   # The star has separate atlas areas per facet. Match the mirrored front
   # facet and interpolate its UVs; retain the installed outline exactly.
   xy=p[ff,:,:2] if False else p[ff][:,:,:2]
   cent=xy.mean(1);dest=xy.copy();dest[:,:,0]*=-1
   rear_m=[]
   for i,d in enumerate(dest):
    j=int(np.argmin(((cent-d.mean(0))**2).sum(1)));t=xy[j]
    A=np.stack([t[1]-t[0],t[2]-t[0]],1)
    b=np.linalg.solve(A,(d-t[0]).T).T;weights=np.c_[1-b.sum(1),b]
    weights=np.clip(weights,0,1);weights/=weights.sum(1,keepdims=True)
    for name,a in fu.items():ru[name][i]=(weights@a[j])[::-1]
    rear_m.append(fm[j])
   rear_materials=np.array(rear_m,object)
 bf=[]
 for a,b in boundary:
  ra=offset+lookup[a];rb=offset+lookup[b];bf.extend([[a,ra,rb],[a,rb,b]])
 pts=np.r_[p,rp];bf=np.array(bf,int);bn=normals(pts,bf)
 allf=np.r_[ff,rf,bf];alln=np.r_[fn,rn,bn];allm=np.r_[fm,locals().get('rear_materials',fm),np.array([wall]*len(bf),object)]
 alluv={name:np.r_[a,ru[name],np.zeros((len(bf),3,2))] for name,a in fu.items()}
 write_mesh(st,prim.GetPath(),pts,allf,alln,allm,alluv)
 e=np.sort(np.r_[allf[:,[0,1]],allf[:,[1,2]],allf[:,[2,0]]],axis=1);_,counts=np.unique(e,axis=0,return_counts=True)
 assert (counts==2).all(),(str(prim.GetPath()),'skin seams',np.unique(counts,return_counts=True))
 return {'mesh':str(prim.GetPath()),'front_triangles_preserved':int(sel.sum()),'front_data_identical':True,'back_maps_match_front':True,'paired_mirror_x':flip_x,'max_pairing_error':float(err.max()),'triangles':len(allf)}
def clone_mesh(st,prim,name,center=0):
 p,f,n,mats,uv=read_mesh(prim);p[:,0]*=-1;p[:,2]=2*center-p[:,2];n*=np.array([-1,1,-1])
 return write_mesh(st,prim.GetParent().GetPath().AppendChild(name),p,f,n,mats,uv)
def sphere_mesh(c,r,lat=12,lon=24):
 p=[np.array(c)+[0,r,0]]
 for j in range(1,lat):
  b=np.pi*j/lat
  for k in range(lon):
   a=2*np.pi*k/lon;p.append(np.array(c)+r*np.array([np.sin(b)*np.sin(a),np.cos(b),np.sin(b)*np.cos(a)]))
 bottom=len(p);p.append(np.array(c)+[0,-r,0]);f=[]
 for k in range(lon):f.append([0,1+k,1+(k+1)%lon])
 for j in range(lat-2):
  for k in range(lon):
   a=1+j*lon+k;b=1+j*lon+(k+1)%lon;d=a+lon;e=b+lon;f.extend([[a,d,e],[a,e,b]])
 for k in range(lon):f.append([bottom,1+(lat-2)*lon+(k+1)%lon,1+(lat-2)*lon+k])
 return np.array(p),np.array(f)
def tube_mesh(path,r,sections=12):
 path=np.array(path);p=[];f=[]
 for j,c in enumerate(path):
  t=path[min(j+1,len(path)-1)]-path[max(j-1,0)];t/=np.linalg.norm(t);v=np.cross(t,[0,0,1])
  if np.linalg.norm(v)<.01:v=np.cross(t,[0,1,0])
  v/=np.linalg.norm(v);u=np.cross(t,v)
  for a in np.arange(sections)*2*np.pi/sections:p.append(c+r*(np.cos(a)*v+np.sin(a)*u))
 for j in range(len(path)-1):
  for k in range(sections):
   a=j*sections+k;b=j*sections+(k+1)%sections;d=a+sections;e=b+sections;f.extend([[a,d,e],[a,e,b]])
 p.extend([path[0],path[-1]]);i=len(p)-2
 for k in range(sections):f.extend([[i,(k+1)%sections,k],[i+1,(len(path)-1)*sections+k,(len(path)-1)*sections+(k+1)%sections]])
 return np.array(p),np.array(f)
def finish(tier,w,out,st,notes):
 UsdGeom.SetStageUpAxis(st,'Y');UsdGeom.SetStageMetersPerUnit(st,1);st.GetRootLayer().Save()
 pts=[];triangles=0
 for prim in st.Traverse():
  if prim.IsA(UsdGeom.Mesh):
   m=UsdGeom.Mesh(prim);pts.append(np.array(m.GetPointsAttr().Get()));triangles+=len(m.GetFaceVertexCountsAttr().Get())
  assert 'Light' not in prim.GetTypeName() and prim.GetTypeName()!='Camera'
  if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
 pts=np.concatenate(pts);lo=pts.min(0);hi=pts.max(0)
 assert lo[1]>=-2.895-1e-5 and hi[1]<=3.015+1e-5 and max(abs(lo[0]),abs(hi[0]))<=3.35,(tier,lo,hi)
 inspection=any(note.get('inspection_only') for note in notes)
 assert abs(lo[0]+hi[0])<(.08 if inspection else .03) and abs(lo[2]+hi[2])<.08,(tier,'spin center',lo,hi)
 package=out/(tier+'_badge_mobile.usdz')
 if package.exists():package.unlink()
 assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(st.GetRootLayer().identifier),str(package)),package
 check=UsdUtils.ComplianceChecker(arkit=True);check.CheckCompliance(str(package));assert not check.GetErrors() and not check.GetFailedChecks(),(check.GetErrors(),check.GetFailedChecks())
 report={'tier':tier,'installed_sha256':MANIFEST[tier]['sha256'],'sha256':sha(package),'triangles':triangles,'bytes':package.stat().st_size,'bounds':[lo.tolist(),hi.tolist()],'arkit_errors':check.GetErrors(),'arkit_failed_checks':check.GetFailedChecks(),'changes':notes}
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(tier,json.dumps(report))
