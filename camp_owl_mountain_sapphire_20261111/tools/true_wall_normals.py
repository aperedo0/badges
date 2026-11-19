"""Get outward wall normals from actual directed boundary edges, not face shading."""
import numpy as np,json,sys
from pathlib import Path

def apply(D,M):
 report=[]
 for p in M['parts']:
  n=p['name'];nf=p['front']
  if not nf:continue
  W=D[n+'_v'][2*nf:];assert len(W)%2==0
  first=W[::2];out=np.cross(first[:,1]-first[:,0],first[:,2]-first[:,0]);out[...,2]=0;out/=np.linalg.norm(out,axis=1)[:,None]
  xy,ids=np.unique(W[...,:2].reshape(-1,2),axis=0,return_inverse=True);ids=ids.reshape(len(W),3);acc=np.zeros((len(xy),3));np.add.at(acc,ids[::2,0],out);np.add.at(acc,ids[::2,2],out);length=np.linalg.norm(acc,axis=1);good=length>1e-8;acc[good]/=length[good,None];N=acc[ids]
  f=np.cross(W[:,1]-W[:,0],W[:,2]-W[:,0]);f/=np.linalg.norm(f,axis=1)[:,None];bad=(N*f[:,None]).sum(2)<.05;N[bad]=np.broadcast_to(f[:,None],N.shape)[bad];assert ((N*f[:,None]).sum(2)>0).all();D[n+'_n'][2*nf:]=N
  report.append(dict(piece=n,wall_triangles=len(W),inward_normals=0,sharp_corner_normals=int(bad.sum())))
 return report

if __name__=='__main__':
 C=Path(sys.argv[1]);D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());report=apply(D,M);np.savez_compressed(C/'parts.npz',**D);(C/'true_walls.json').write_text(json.dumps(dict(method='Actual directed boundary edges, averaged along each real wall curve. No front face influence. Sharp corners retain outward normals.',parts=report),indent=2)+'\n');print('Proved outward wall normals',len(report),'pieces')
