"""True circular crown; project the existing reference finish onto its curved wall."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/13'
if (out/'usd/badge.usdc').exists():st=Usd.Stage.Open(str(out/'usd/badge.usdc'))
else:w,out,st=open_copy('gold','13')
source=Usd.Stage.Open(str(w/'source/installed/badge.usdc'))
fit=json.loads((ROOT/'gold_circle_fit.json').read_text())
R=fit['radius'];H=fit['height'];tilt=np.radians(fit['tilt_degrees'])
axis=np.array([0,np.cos(tilt),np.sin(tilt)]);depth=np.array([0,-np.sin(tilt),np.cos(tilt)])
C=np.array([0,fit['bottom_y'],.65]);CAM=np.array([0,1.8,23.]);SLOPE=.25
front='/GoldCrown/Materials/GoldCrown_Front'
edge=shader_material(st,'RoundCrown_RolledGold',[.18,.085,.008],.65)
inside=shader_material(st,'RoundCrown_InnerGold',[.32,.16,.016],.55)
def project(p):
 return np.c_[p[:,0]*23/(23-p[:,2]),1.8+(p[:,1]-1.8)*23/(23-p[:,2])]
def surface(projected,radius_delta=0):
 plane=np.c_[projected,np.zeros(len(projected))];d=plane-CAM
 o=CAM-C;x=o[0];z=o@depth;y=o@axis
 dx=d[:,0];dz=d@depth;dy=d@axis
 base=R-SLOPE*H+radius_delta
 aa=dx*dx+dz*dz-(SLOPE*dy)**2
 bb=2*(x*dx+z*dz-(base+SLOPE*y)*SLOPE*dy)
 cc=x*x+z*z-(base+SLOPE*y)**2
 disc=bb*bb-4*aa*cc
 # At flared outer tips, the camera ray may be tangent just outside the
 # nominal cone. Keep that silhouette point on its ray, at the tangent
 # depth; only the circular band has a fixed radius.
 if disc.min()<0:print('Flared tip tangent adjustment',float(disc.min()))
 t=(-bb-np.sqrt(np.maximum(disc,0)))/(2*aa)
 return CAM+t[:,None]*d
# The local half turn preserves the physical tilt; the normal app Y turn
# then exposes the same finished crown all around.
ROT=2*np.outer(axis,axis)-np.eye(3)
def back(p):return (p-C)@ROT.T+C
records=[]
for prim in [p for p in source.Traverse() if p.IsA(UsdGeom.Mesh)]:
 name=prim.GetName();p,f,n,m,uv=read_mesh(prim)
 if 'Band' in name:
  st.RemovePrim(prim.GetPath());continue
 if 'Finial' in name or 'Collar' in name:
  center=(p.min(0)+p.max(0))/2
  if 'Collar' in name:
   num=name[-1];ball=source.GetPrimAtPath('/GoldCrown/GoldCrown_Finial'+num);bp=read_mesh(ball)[0];center=(bp.min(0)+bp.max(0))/2
  dst=surface(project(center[None]))[0]
  scale=(23-dst[2])/(23-center[2])
  pp=dst+(p-center)*scale
 else:
  pp=surface(project(p))
  if 'ScallopedShell' in name:
   half=len(p)//2
   # The inner face is the same circular wall, with real radial thickness.
   local=pp[:half]-C;rad=local[:,0,None]*np.array([1,0,0])+ (local@depth)[:,None]*depth
   pp[half:]=pp[:half]-.10*rad/np.linalg.norm(rad,axis=1,keepdims=True)
  elif 'ValleyFlange' in name:
   # Keep the actual flange relief, rather than flattening both faces onto
   # the same cylinder and causing depth fights.
   displacement=p[:,2]-np.median(p[:,2]);pp+=displacement[:,None]*.10*depth
  elif 'Lip' in name:
   # Tube thickness follows its original local offset from the source wall.
   displacement=p[:,2]-np.median(p[:,2]);pp+=displacement[:,None]*.04*depth
 m=np.array([front if 'Back' in a else a for a in m],object)
 write_mesh(st,prim.GetPath(),pp,f,n,m,uv)
 write_mesh(st,prim.GetParent().GetPath().AppendChild(name+'_RoundRear'),back(pp),f,n@ROT.T,m,uv)
 records.append({'mesh':name,'source_uv_and_front_finish_preserved':True,'wrapped_to_circular_wall':True})
# An annulus whose top and bottom circles share a single tilted axis.
N=192;J=8;angles=np.arange(N)*2*np.pi/N;pts=[];f=[];m=[];uv=[]
band=source.GetPrimAtPath('/GoldCrown/GoldCrown_HollowBand');bp,bf,bn,bm,bu=read_mesh(band)
# The source atlas is sampled by the same angular and vertical coordinates.
source_uv=np.zeros((len(bp),2));count=np.zeros(len(bp))
for k,a in bu.items():
 for c in range(3):np.add.at(source_uv,bf[:,c],a[:,c]);np.add.at(count,bf[:,c],1)
 source_uv/=np.maximum(count[:,None],1);break
for inner in [False,True]:
 for j in range(J+1):
  h=H*(1-j/J);r=R-(.19 if inner else 0)
  for a in angles:pts.append(C+h*axis+r*np.sin(a)*np.array([1,0,0])+r*np.cos(a)*depth)
size=(J+1)*N
vuv=[]
for inner in [False,True]:
 for j in range(J+1):
  t=j/J*6;low=int(np.floor(t));high=min(6,low+1);mix=t-low
  for a in angles:
   # Rear facing facets use the matching half of the reference band.
   aa=a if np.cos(a)>=0 else np.pi-a
   k=aa%(2*np.pi)*128/(2*np.pi);k0=int(k)%128;k1=(k0+1)%128;frac=k-np.floor(k)
   offset=896 if inner else 0
   value=(1-mix)*((1-frac)*source_uv[offset+low*128+k0]+frac*source_uv[offset+low*128+k1])+mix*((1-frac)*source_uv[offset+high*128+k0]+frac*source_uv[offset+high*128+k1])
   vuv.append(value)
for inner in [0,1]:
 for j in range(J):
  for k in range(N):
   q=(k+1)%N;o=inner*size;a=o+j*N+k;b=o+j*N+q;c=o+(j+1)*N+q;d=o+(j+1)*N+k
   f.extend([[a,b,c],[a,c,d]]);m.extend([front if not inner else inside]*2)
for k in range(N):
 q=(k+1)%N
 for a,b,c,d in [(k,size+k,size+q,q),(J*N+k,J*N+q,size+J*N+q,size+J*N+k)]:f.extend([[a,b,c],[a,c,d]]);m.extend([inside]*2)
p=np.array(pts);f=np.array(f);vuv=np.array(vuv)
# Outward winding across all four connected surfaces.
f[:J*N*2]=f[:J*N*2,::-1]
f[2*J*N*2:]=f[2*J*N*2:,::-1]
write_mesh(st,'/GoldCrown/GoldCrown_TrueCircularBand',p,f,normals(p,f,True),np.array(m),{'BadgeUV':vuv[f]})
# Thin circular rolled lips are bounded gold so grazing pixels stay clean.
for name,h in [('Upper',H),('Lower',0)]:
 path=np.array([C+h*axis+R*np.sin(a)*np.array([1,0,0])+R*np.cos(a)*depth for a in np.linspace(0,2*np.pi,N+1)])
 pp,ff=tube_mesh(path,.020,8);simple_mesh(st,'GoldCrown_Circular'+name+'Lip',pp,ff,edge,True)
# Align the entire object's thickness to the fixed app spin axis.
allp=np.concatenate([read_mesh(p)[0] for p in st.Traverse() if p.IsA(UsdGeom.Mesh)])
shift=np.array([-(allp[:,0].min()+allp[:,0].max())/2,0,-(allp[:,2].min()+allp[:,2].max())/2])
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);write_mesh(st,prim.GetPath(),p+shift,f,n,m,uv)
records.append({'true_circular_band':True,'radius':R,'height':H,'tilt_degrees':fit['tilt_degrees'],'axis':axis.tolist(),'circle_radius_error':float(np.max(abs(np.linalg.norm((np.array(pts[:N])-C-H*axis),axis=1)-R))),'center_shift':shift.tolist(),'floating_height_guidance_exception':'A real tilted circular band reaches lower at the far side than the flattened source. Retain reference projection and satisfy the hard floor.'})
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/compacted.usdc';layer.Export(str(dest));finish('gold',w,out,Usd.Stage.Open(str(dest)),records)
(ROOT/'gold13_selection.json').write_text(json.dumps({'gold':'13'})+'\n')
