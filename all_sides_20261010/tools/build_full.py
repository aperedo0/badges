import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
tier,number=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3]
w,out,st=open_copy(tier,number);root=st.GetDefaultPrim().GetPath()
oldmeshes=[p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]
olddata=[read_mesh(p) for p in oldmeshes]
for p in oldmeshes:st.RemovePrim(p.GetPath())
front=str(root.AppendPath('Materials/'+('GoldCrown_Front' if tier=='gold' else 'DiamondCrystal_Front')))
uvname=next(iter(olddata[0][4]))
notes=[]
if tier=='gold':
 if int(number)>=7:st.RemovePrim(root.AppendChild('Materials'))
 if int(number)>=3:
  bright=int(number)>=5 and number!='09'
  front=shader_material(st,'GoldCrown_ContinuousPolishedGold',[1.,.66,.11] if bright else [.83,.52,.095],.30,emission=[.035,.015,.001] if bright else None)
 mapping=json.loads((Path('/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/gold/source/mapping.json')).read_text())
 def golden_uv(p,f):
  if int(number)>=7:return {}
  x=p[:,0];y=p[:,1]
  uv=np.stack([(x/mapping['scale']+mapping['center_x'])/1254,1-(mapping['reference_bottom']-(y+2.455)/mapping['scale'])/1254],-1)
  return {uvname:uv[f]}
 inner=shader_material(st,'GoldCrown_InsidePolishedGold',[.38,.21,.025],.39)
 trim=shader_material(st,'GoldCrown_RoundedGoldTrim',[.29,.13,.018],.5)
 jewel=shader_material(st,'GoldCrown_AmberCabochons',[.18,.069,.004],.24,emission=[.045,.012,.001])
 N=260 if int(number)>=7 else 256;theta=np.arange(N)*2*np.pi/N
 peak_coeff=np.polyfit([1.,np.cos(np.pi/5)**2,np.cos(2*np.pi/5)**2],[1.3173617,.7735519,.247],2)
 def point_peak(a):return np.polyval(peak_coeff,np.cos(a)**2) if int(number)>=7 else .45+1.22*np.cos(a)**2
 def crown_top(a):
  step=2*np.pi/10;k=np.floor(a/step+.5);peak=point_peak(k*step)
  d=np.abs((a/step-k)*2)
  return -.35+(peak+.35)*(1-d)**2
 # A closed continuous hollow crown wall, with true curved scallops around all 360 degrees.
 top=crown_top(theta);p=[];rows=20
 for inside in [False,True]:
  for j in range(rows+1):
   t=j/rows;rr=2.71+.29*t-(.13 if inside else 0)
   yy=-1.82+(top+1.82)*t
   p.extend(np.stack([rr*np.sin(theta),yy,rr*np.cos(theta)],-1))
 p=np.array(p);f=[];m=[];stride=(rows+1)*N
 for side in [0,1]:
  for j in range(rows):
   for k in range(N):
    a=side*stride+j*N+k;b=side*stride+j*N+(k+1)%N;c=a+N;d=b+N
    faces=[[a,b,d],[a,d,c]]
    if side:faces=[v[::-1] for v in faces]
    f.extend(faces);m.extend([inner if side else front]*2)
 for j in [0,rows]:
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=a+stride;d=b+stride
   faces=[[a,c,d],[a,d,b]]
   if j==0:faces=[v[::-1] for v in faces]
   f.extend(faces);m.extend([trim]*2)
 f=np.array(f);nn=normals(p,f,True)
 # Correct outward winding by testing outer radial faces.
 if np.sum(face_normals(p,f[:2])[:,[0,2]]*p[f[:2]].mean(1)[:,[0,2]])<0:f=f[:,::-1];nn=normals(p,f,True)
 write_mesh(st,root.AppendChild('GoldCrown_FullScallopedWall'),p,f,nn,m,golden_uv(p,f))
 # Round hollow band, mildly domed outer face, and a darker inner surface.
 p=[];profile=[(2.72,-2.455),(2.77,-2.39),(2.79,-2.12),(2.76,-1.84),(2.71,-1.78),(2.56,-1.78),(2.56,-2.455)]
 for r,y in profile:p.extend(np.stack([r*np.sin(theta),np.full(N,y),r*np.cos(theta)],-1))
 p=np.array(p);f=[];m=[]
 for j in range(len(profile)):
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=((j+1)%len(profile))*N+k;d=((j+1)%len(profile))*N+(k+1)%N
   f.extend([[a,b,d],[a,d,c]]);m.extend([front if j<4 else inner]*2)
 f=np.array(f)
 if np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()<0:f=f[:,::-1]
 write_mesh(st,root.AppendChild('GoldCrown_FullRoundBand'),p,f,normals(p,f,True),m,golden_uv(p,f))
 for i in range(10):
  a=i*2*np.pi/10;h=point_peak(a);r=(.22 if int(number)>=7 else .16)+.12*np.cos(a)**2
  c=[3.0*np.sin(a),h+r*.80,3.0*np.cos(a)]
  pp,ff=sphere_mesh(c,r,16 if int(number)>=7 else 12,32 if int(number)>=7 else 24);simple_mesh(st,'GoldCrown_Finial'+str(i+1),pp,ff,front,True,golden_uv(pp,ff))
  # Cabochons and their small circular settings are repeated on the complete band.
  if int(number)<7:
   pp,ff=sphere_mesh([2.82*np.sin(a),-2.115,2.82*np.cos(a)],.12,8,16)
   simple_mesh(st,'GoldCrown_BandJewel'+str(i+1),pp,ff,jewel,True)
 if number in ['02','04','06','08']:
  degrees=10 if number=='08' else 6
  angle=np.deg2rad(degrees);rot=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
  records=[]
  for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh)]:
   p,f,n,m,uv=read_mesh(prim);records.append((prim,p@rot.T,f,n@rot.T,m,uv))
  joined=np.concatenate([r[1] for r in records]);dy=-2.455-joined[:,1].min();dz=-(joined[:,2].min()+joined[:,2].max())/2
  for prim,p,f,n,m,uv in records:p+=np.array([0,dy,dz]);write_mesh(st,prim.GetPath(),p,f,n,m,uv)
  notes.append({'test_only':True,'baked_tilt_degrees':degrees,'tilt_reverses_toward_back':True})
 notes.append({'design':'Continuous circular hollow gold band and ten scalloped points with polished globe finials around the full circumference. Point heights and globe sizes follow the installed crown; all ten tips land on exact mesh samples so every globe intersects its point.','front_style':'Polished warm physical gold on continuous surfaces; darker physical metal inside and at narrow trim. Plain lower band matches the reference and keeps the reflection quiet.'})
elif tier=='diamond':
 # Round brilliant profile; each sector is real planar crown/pavilion geometry.
 N=24;theta=np.arange(N)*2*np.pi/N
 rings=[(1.38,2.34860635),(2.13,1.60),(3.12,.88),(3.12,.78),(.70,-1.72)]
 p=[]
 for r,y in rings:p.extend(np.stack([r*np.sin(theta),np.full(N,y),r*np.cos(theta)],-1))
 p.extend([[0,2.34860635,0],[0,-2.455,0]]);p=np.array(p);f=[]
 for k in range(N):f.append([len(p)-2,(k+1)%N,k])
 for j in range(len(rings)-1):
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=a+N;d=b+N
   f.extend([[a,b,d],[a,d,c]])
 for k in range(N):f.append([len(p)-1,(len(rings)-1)*N+k,(len(rings)-1)*N+(k+1)%N])
 f=np.array(f)
 if np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()<0:f=f[:,::-1]
 oldp,oldf,oldn,oldmat,olduv=olddata[0];sel=np.array([x.endswith('_Front') for x in oldmat])&(face_normals(oldp,oldf)[:,2]>.01)
 source=oldf[sel];su=olduv[uvname][sel];cent=oldp[source].mean(1);uv=[]
 np.savez_compressed(out/'optical_geometry.npz',points=p,faces=f,source_points=oldp,source_faces=source,source_uv=su)
 for tri in f:
  c=p[tri].mean(0);theta_c=np.arctan2(c[0],c[2]);x=3.12*np.sin(theta_c);y=c[1]
  # Reuse optical facet paintings of the installed gem at the corresponding height and angular position.
  score=(cent[:,0]-x)**2+(cent[:,1]-y)**2
  pick=int(np.argmin(score));faceuv=su[pick];mid=faceuv.mean(0);uv.append(mid+(faceuv-mid)*.86)
 if int(number)>=2:
  uv=[]
  for i in range(len(f)):
   col=i%16;row=i//16;xy=np.array([[col*64+4,row*64+4],[col*64+60,row*64+4],[col*64+4,row*64+60]])
   uv.append(np.stack([xy[:,0]/1024,1-xy[:,1]/1024],-1))
  uv=np.array(uv);np.savez_compressed(out/'new_uv.npz',uv=uv)
 if int(number)>=3:
  used=oldp[source].reshape(-1,3);lo=used.min(0);hi=used.max(0)
  vertex_uv=np.stack([(p[:,0]-lo[0])/(hi[0]-lo[0]),(p[:,1]-lo[1])/(hi[1]-lo[1])],-1)
  uv=vertex_uv[f]
  np.savez_compressed(out/'new_uv.npz',uv=uv)
 simple_mesh(st,'DiamondCrystal_FullBrilliant',p,f,front,False,{uvname:np.array(uv)})
 notes.append({'design':'Closed round brilliant with a real table, faceted crown, girdle, pavilion and culet, all the way around.','look':'Installed blue optical facet maps and supplemental emission retained; no added lights or normal maps.'})
else:raise ValueError(tier)
finish(tier,w,out,st,notes)
