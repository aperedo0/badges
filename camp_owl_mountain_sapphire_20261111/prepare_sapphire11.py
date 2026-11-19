"""Intersect real cut planes rather than fanning a triangulated crown."""
from pathlib import Path
import numpy as np,json,time
from scipy.spatial import ConvexHull,HalfspaceIntersection
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from designs import path
R=Path(__file__).resolve().parent
s=json.loads((R/'schedule.json').read_text());assert s['phase']=='work' and time.time()+180<s['work_until_epoch']
A=R/'sapphire_teardrop/candidate10';C=R/'sapphire_teardrop/candidate11';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());U=M['units'];S=U['S']
outline=path('M 626 252 C 739 379 875 553 881 704 C 883 834 775 945 626 945 C 480 945 368 835 370 704 C 374 555 515 379 626 252 Z');curve=outline.exterior
ring=np.array([curve.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,128,endpoint=False)])
ring=np.c_[(ring[:,0]-U['axis'])*S,2.995-(ring[:,1]-U['top'])*S];ring=np.asarray(orient(Polygon(ring),sign=1).exterior.coords)[:-1]
old=np.unique(D['gem_v'].reshape(-1,3),axis=0);table=old[np.isclose(old[:,2],.64),:2];table=table[ConvexHull(table).vertices];table=np.asarray(orient(Polygon(table),sign=1).exterior.coords)[:-1];planes=[]
for p,q in zip(ring,np.roll(ring,-1,axis=0)):
 n=np.array([q[1]-p[1],p[0]-q[0]]);n/=np.linalg.norm(n);planes.append([*n,0,-float(n@p)])
for p,q in zip(table,np.roll(table,-1,axis=0)):
 n=np.array([q[1]-p[1],p[0]-q[0]]);n/=np.linalg.norm(n);edge=float(n@p);support=float(np.max(ring@n));slope=(support-edge)/(.64-.16);offset=support+slope*.16;planes.extend([[*n,slope,-offset],[*n,-slope,-offset]])
planes.extend([[0,0,1,-.64],[0,0,-1,-.64]]);inside=np.r_[Polygon(ring).centroid.coords[0],0.];hs=np.asarray(planes,float);assert np.max(hs[:,:3]@inside+hs[:,3])<0
points=HalfspaceIntersection(hs,inside).intersections;h=ConvexHull(points);f=h.simplices.copy();v=points[f];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);bad=np.sum(n*h.equations[:,:3],axis=1)<0;f[bad]=f[bad,::-1];v=points[f];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.linalg.norm(n,axis=1,keepdims=True)
D['gem_v']=v.astype(np.float32);D['gem_n']=np.repeat(n[:,None,:],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(v),3,2),np.float32);D['gem_m']=np.zeros(len(v),np.int16)
for p in M['parts']:
 if p['name']=='gem':p.update(triangles=len(v),front=0,physical_pavilion=False,broad_convex_crown=True)
 if p['name']=='solid_gold_teardrop_setting':
  name=p['name'];nf=p['front'];N=D[name+'_n'][:2*nf];sign=np.where(D[name+'_v'][:2*nf].mean(1)[:,2]>=0,1,-1);N[:,:,:2]*=.3;N[:,:,2]=.7*sign[:,None]+.3*N[:,:,2];N/=np.linalg.norm(N,axis=2,keepdims=True)
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');over=json.loads((A/'palette_overrides.json').read_text());over['Gem']={'material_name':'CrestGem_SapphireClear'};(C/'palette_overrides.json').write_text(json.dumps(over,indent=2)+'\n')
(C/'cut_design.json').write_text(json.dumps(dict(source='candidate10 frame',method='Six real crown planes on each side, broad table planes and128 smooth outline support planes',construction_planes=len(hs),closed_convex=True,real_refraction_profile=18,no_appearance_texture=True,frame_bevel_normals='Blend toward the actual broad face to suppress subpixel edge flashes',native_acceptance_pending=True),indent=2)+'\n');print('Real convex cut',len(points),'vertices',len(v),'triangles',len(hs),'construction planes')
