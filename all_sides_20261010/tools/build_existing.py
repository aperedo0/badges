import sys,json
from pathlib import Path
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
tier=sys.argv[sys.argv.index('--')+1];number=sys.argv[sys.argv.index('--')+2] if len(sys.argv)>sys.argv.index('--')+2 else '01'
w,out,st=open_copy(tier,number);root=st.GetDefaultPrim().GetPath()
changes=[]
if tier in ['bronze','steel','silver']:
 color={'bronze':[.19,.085,.021],'steel':[.20,.21,.23],'silver':[.20,.195,.182]}[tier]
 wall=shader_material(st,tier.title()+'_FinishedTurnWalls',color,.58)
 meshes=[p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]
 for prim in meshes:
  if tier=='bronze' and ('OuterLip' in prim.GetName() or 'InnerLip' in prim.GetName()):
   clone_mesh(st,prim,prim.GetName()+'_RearMatchingLip',0)
   changes.append({'mesh':str(prim.GetPath()),'original_preserved':True,'rear_lip_added':True})
  else:changes.append(mirror_skin(st,prim,wall))
elif tier=='platinum':
 front=str(root.AppendPath('Materials/PlatinumKnot_Front'));dst=root.AppendPath('Materials/PlatinumKnot_TexturedWalls')
 Sdf.CopySpec(st.GetRootLayer(),Sdf.Path(front),st.GetRootLayer(),dst)
 # CopySpec preserves internal connections; repoint them into the copied material.
 for prim in Usd.PrimRange(st.GetPrimAtPath(dst)):
  for a in prim.GetAttributes():
   connections=a.GetConnections()
   if connections:a.SetConnections([p.ReplacePrefix(Sdf.Path(front),dst) for p in connections])
 wallshader=UsdShade.Shader.Get(st,dst.AppendChild('Surface'));wallshader.GetInput('roughness').Set(.55)
 for prim in Usd.PrimRange(st.GetPrimAtPath(dst)):
  if prim.IsA(UsdShade.Shader):
   sh=UsdShade.Shader(prim)
   if sh.GetIdAttr().Get()=='UsdUVTexture':
    factor=.7 if prim.GetName()=='diffuseColor' else .45
    scale=sh.GetInput('scale');old=scale.Get() if scale else None;values=np.array(old if old is not None else [1,1,1,1],float);values[:3]*=factor
    sh.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(*map(float,values)))
 for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
  p,f,n,mats,uv=read_mesh(prim);old=mats.copy();rear=np.array(['Back' in x for x in mats]);mats[rear]=front
  edge=rear&(np.abs(face_normals(p,f)[:,2])<.4);mats[edge]=str(dst)
  write_mesh(st,prim.GetPath(),p,f,n,mats,uv);changes.append({'mesh':str(prim.GetPath()),'front_data_identical':True,'back_textured_faces':int(rear.sum()),'moderate_textured_wall_faces':int(edge.sum()),'geometry_unchanged':True})
elif tier=='iron':
 interior=shader_material(st,'Iron2_HollowInterior',[.115,.111,.104],.30 if int(number)>=3 else .47)
 fittings=shader_material(st,'Iron2_Reinforcements',[.145,.140,.130],.56)
 prim=st.GetPrimAtPath(root.AppendChild('Iron2_Border_Satin'));p,f,n,mats,uv=read_mesh(prim)
 back=face_normals(p,f)[:,2]<-.9;bf=f[back];original=bf.copy();keep=~back
 write_mesh(st,prim.GetPath(),p,f[keep],n[keep],mats[keep],{k:a[keep] for k,a in uv.items()})
 # Subdivide the installed rear panel once, preserving its exact perimeter.
 used=np.unique(bf);mapping={int(k):i for i,k in enumerate(used)};q=p[used].tolist();ff=np.array([[mapping[int(v)] for v in tri] for tri in bf]);cache={};new=[]
 def mid(a,b):
  key=tuple(sorted((int(a),int(b))))
  if key not in cache:cache[key]=len(q);q.append(((np.array(q[a])+q[b])/2).tolist())
  return cache[key]
 for a,b,c in ff:
  ab=mid(a,b);bc=mid(b,c);ca=mid(c,a);new.extend([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])
 q=np.array(q);ff=np.array(new);edges={}
 for tri in ff:
  for a,b in zip(tri,np.roll(tri,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append((int(a),int(b)))
 boundary=np.unique(np.array([v[0] for v in edges.values() if len(v)==1]).ravel())
 def dish(x,y):
  r2=(x/2.1611)**2+((y-.195)/2.65)**2
  return -.325+.39*max(0,1-r2)
 if int(number)>=2:
  # A dense radial surface avoids the shading crease from a two-segment bowl.
  ids,counts=np.unique(original,return_counts=True);pole_id=ids[np.argmax(counts)]
  contour=p[ids[ids!=pole_id],:2];origin=p[pole_id,:2]
  angles=np.arctan2(contour[:,1]-origin[1],contour[:,0]-origin[0]);order=np.argsort(angles);contour=contour[order];angles=angles[order]
  radii=np.linalg.norm(contour-origin,axis=1)
  def dish(x,y):
   d=np.array([x,y])-origin;r=np.linalg.norm(d);a=np.arctan2(d[1],d[0])
   rb=np.interp(a,np.r_[angles-2*np.pi,angles,angles+2*np.pi],np.tile(radii,3));t=r/rb
   return -.325+.39*max(0,1-t*t)
  if int(number)>=3:
   seg_a=contour;seg_v=np.roll(contour,-1,axis=0)-contour
   def dish(x,y):
    xy=np.array([x,y]);v=xy-seg_a;t=np.clip(np.sum(v*seg_v,axis=1)/np.maximum(np.sum(seg_v*seg_v,axis=1),1e-12),0,1);dist=np.linalg.norm(v-t[:,None]*seg_v,axis=1).min()
    u=np.clip(dist/.34,0,1);blend=u*u*(3-2*u);ellipse=max(0,1-(x/2.6)**2-((y-.195)/3.1)**2)
    return -.325+.39*ellipse*blend
  sectors=len(contour);rings=18 if int(number)>=3 else 12;q=[[origin[0],origin[1],dish(*origin)]]
  for j in range(1,rings+1):
   t=j/rings;xy=origin+t*(contour-origin)
   q.extend([[x,y,-.325+.39*(1-t*t)] for x,y in xy])
  ff=[]
  for k in range(sectors):ff.append([0,1+(k+1)%sectors,1+k])
  for j in range(rings-1):
   for k in range(sectors):
    a=1+j*sectors+k;b=1+j*sectors+(k+1)%sectors;c=a+sectors;d=b+sectors
    ff.extend([[a,b,d],[a,d,c]])
  q=np.array(q);ff=np.array(ff)
  if face_normals(q,ff)[:,2].mean()>0:ff=ff[:,::-1]
  boundary=np.arange(len(q)-sectors,len(q))
 q[:,2]=[dish(x,y) for x,y,_ in q];q[boundary,2]=-.325
 write_mesh(st,root.AppendChild('Iron2_HollowRearFace'),q,ff,normals(q,ff,True),[interior]*len(ff))
 if int(number)>=3:
  rim_mat=shader_material(st,'Iron2_RearRolledRim',[.06,.058,.052],.55)
  centers=np.c_[origin+.965*(contour[::4]-origin),np.full(len(contour[::4]),-.32)];rr=.055;K=len(centers);sidecount=12;rp=[];rf=[]
  for i,c in enumerate(centers):
   tangent=centers[(i+1)%K]-centers[(i-1)%K];tangent/=np.linalg.norm(tangent);axis=np.array([0.,0.,1.]);radial=np.cross(tangent,axis)
   for a in np.arange(sidecount)*2*np.pi/sidecount:rp.append(c+rr*(np.cos(a)*axis+np.sin(a)*radial))
  for i in range(K):
   for k in range(sidecount):
    a=i*sidecount+k;b=i*sidecount+(k+1)%sidecount;c=((i+1)%K)*sidecount+k;d=((i+1)%K)*sidecount+(k+1)%sidecount;rf.extend([[a,b,d],[a,d,c]])
  simple_mesh(st,'Iron2_RearRolledRim',rp,rf,rim_mat,True)
 for sign in [-1,1]:
  xx=np.linspace(-1.32,1.32,25);yy=.195+sign*.58*xx
  pp,faces=tube_mesh([[x,y,dish(x,y)-.07] for x,y in zip(xx,yy)],.075,12)
  simple_mesh(st,'Iron2_RearBrace'+str(sign).replace('-','M'),pp,faces,fittings,True)
 # The grip sits inside the original depth envelope, above the hollow face.
 yc=.20;anchors=np.array([[0,yc+.65,dish(0,yc+.65)-.04],[0,yc+.45,-.22],[0,yc-.45,-.22],[0,yc-.65,dish(0,yc-.65)-.04]])
 path=[]
 for t in np.linspace(0,1,32):path.append((1-t)**3*anchors[0]+3*(1-t)**2*t*anchors[1]+3*(1-t)*t*t*anchors[2]+t**3*anchors[3])
 pp,faces=tube_mesh(path,.10,16);simple_mesh(st,'Iron2_RaisedRearGrip',pp,faces,fittings,True)
 mounts=[(x,.195+s*.58*x) for s in [-1,1] for x in [-1.1,1.1]]+[(0,yc-.65),(0,yc+.65)]
 for i,(x,y) in enumerate(mounts):
  pp,faces=sphere_mesh([x,y,dish(x,y)-.055],.065,6,12);simple_mesh(st,'Iron2_RearRivet'+str(i+1),pp,faces,fittings,True)
 changes=[{'front_data_identical':True,'replaced_rear_triangles':int(back.sum()),'hollow_rear_triangles':len(ff),'design':'Smooth hollow shield bowl, crossed iron braces, raised iron hand grip, six domed rivets; candidate 03 adds a continuous dark rolled rear rim and a smooth elliptical bowl. Main front faces are unchanged.'}]
else:raise ValueError(tier)
finish(tier,w,out,st,changes)
