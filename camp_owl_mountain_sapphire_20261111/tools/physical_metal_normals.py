"""Follow real beveled geometry with smooth normals; keep colored faces intact."""
from pathlib import Path
import numpy as np,json,sys,time
C=Path(sys.argv[1]).resolve();R=Path(__file__).resolve().parent.parent;s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and (s.get('pacing_mode')=='continuous' or (s['phase']=='work' and time.time()<s['work_until_epoch']))
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());report=[]
for p in M['parts']:
 n=p['name'];nf=p['front']
 if not nf:continue
 V=D[n+'_v'][:nf];N=D[n+'_n'];roles=np.array([p['materials'][i] for i in D[n+'_m'][:nf]]);metal=np.isin(roles,['Gold','FineGold','GoldEdge','SmoothGold'])
 if metal.any():
  points,inv=np.unique(V.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);face=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);L=np.linalg.norm(face,axis=1);assert (L>1e-14).all();face/=L[:,None];acc=np.zeros_like(points,dtype=np.float64)
  for j in range(3):
   a=V[:,(j+1)%3]-V[:,j];b=V[:,(j+2)%3]-V[:,j];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[:,j],face*ang[:,None])
  acc/=np.linalg.norm(acc,axis=1)[:,None];N[:nf][metal]=acc[F][metal];N[nf:2*nf][metal]=acc[F][metal][:,::-1]*[1,1,-1]
 wall=N[2*nf:];L=np.linalg.norm(wall[...,:2],axis=2);assert (L>1e-8).all();wall[...,:2]/=L[...,None];wall[...,2]=0
 report.append(dict(name=n,real_metal_triangles=int(metal.sum()),walls_constant_through_depth=True))
from true_wall_normals import apply
wall_report=apply(D,M)
np.savez_compressed(C/'parts.npz',**D);(C/'physical_normals.json').write_text(json.dumps(dict(method='Angle weighted actual geometric bevel normals, colored face normals retained, no artificial shallow tilt or side barrel sweep.',parts=report,outward_wall_proof=wall_report,blender_review_pending=True),indent=2)+'\n');print('Actual metal geometry normals and true walls:',len(report),'pieces')
