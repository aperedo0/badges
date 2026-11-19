"""Keep detailed faces; replace subpixel rolled lips with finished side walls."""
from pathlib import Path
import json,sys,numpy as np,time
R=Path(__file__).resolve().parent.parent;C=Path(sys.argv[1]).resolve()
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and (s.get('pacing_mode')=='continuous' or (s['phase']=='work' and time.time()<s['work_until_epoch']))
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());report=[]
for p in M['parts']:
 name=p['name'];nf=p['front']
 if not nf:continue
 V=D[name+'_v'][:nf].copy();N=D[name+'_n'][:nf].copy();UV=D[name+'_uv'][:nf].copy();mi=D[name+'_m'][:nf].copy();names=p['materials']
 enamel=np.array([names[i].startswith('Enamel') or names[i]=='NightField' for i in mi]);N[enamel]=[0,0,1]
 # Welding uses the exact float32 values that the USD writer retains.
 points,inv=np.unique(V.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3)
 edges=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]);_,idx,count=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True);E=edges[idx[count==1]]
 normal=np.zeros_like(points);tex=np.zeros((len(points),2),float);cnt=np.zeros(len(points));np.add.at(normal,F.ravel(),N.reshape(-1,3));np.add.at(tex,F.ravel(),UV.reshape(-1,2));np.add.at(cnt,F.ravel(),1);normal/=np.linalg.norm(normal,axis=1,keepdims=True);tex/=cnt[:,None]
 # Directed front boundary edges leave the solid on their left.
 tangent=points[E[:,1],:2]-points[E[:,0],:2];out=np.c_[tangent[:,1],-tangent[:,0],np.zeros(len(E))];out/=np.linalg.norm(out,axis=1,keepdims=True)
 vertex_out=np.zeros_like(points);np.add.at(vertex_out,E[:,0],out);np.add.at(vertex_out,E[:,1],out);length=np.linalg.norm(vertex_out,axis=1);valid=length>0;vertex_out[valid]/=length[valid,None]
 side=.7*normal+.3*vertex_out;side/=np.linalg.norm(side,axis=1,keepdims=True)
 wall=[];wn=[];wuv=[]
 for a,b in E:
  A=points[a];B=points[b];Ab=A*[1,1,-1];Bb=B*[1,1,-1]
  wall.extend([[A,Ab,B],[B,Ab,Bb]])
  wn.extend([[side[a],side[a]*[1,1,-1],side[b]],[side[b],side[a]*[1,1,-1],side[b]*[1,1,-1]]])
  wuv.extend([[tex[a],tex[a],tex[b]],[tex[b],tex[a],tex[b]]])
 side_index=names.index('Side') if 'Side' in names else len(names)
 if 'Side' not in names:names.append('Side')
 D[name+'_v']=np.concatenate([V,(V*[1,1,-1])[:,::-1],np.asarray(wall)]).astype(np.float32)
 D[name+'_n']=np.concatenate([N,(N*[1,1,-1])[:,::-1],np.asarray(wn)]).astype(np.float32)
 D[name+'_uv']=np.concatenate([UV,UV[:,::-1],np.asarray(wuv)]).astype(np.float32)
 D[name+'_m']=np.concatenate([mi,mi,np.full(len(wall),side_index)]).astype(np.int16)
 old=p['triangles'];p['triangles']=len(D[name+'_m']);report.append(dict(name=name,before=old,after=p['triangles'],flat_enamel_faces=int(enamel.sum()),rolled_lips_removed=True))
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');(C/'surface_edge_change.json').write_text(json.dumps(dict(geometry_faces_and_relief_preserved=True,thin_roll_replaced_with_continuous_wall=True,wall_finish='Side, rough metal with normals blended toward the corresponding face',flat_enamel_proof='Candidate21 removed the three persistent native flame dark pixels by changing only its colored face normals',parts=report,native_review_pending=True),indent=2)+'\n');print('Cleaned',len(report),'parts')
