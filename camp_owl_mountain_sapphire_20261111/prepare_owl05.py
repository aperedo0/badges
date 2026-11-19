"""Keep amber glass separate from cream and blue so gold filtering cannot substitute neighboring colors."""
from pathlib import Path
import numpy as np,json,shutil,shapely
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent;A=R/'amber_owl/candidate04';C=A.parent/'candidate05';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());spec=json.loads((A.parent/'PIECES.json').read_text());specs={p['name']:p for p in spec['pieces']};roles_used=set();report=[]
for p in M['parts']:
 n=p['name'];names=p['materials'];mi=D[n+'_m'];roles=np.array([names[i] for i in mi],dtype=object);mask=roles=='Enamel'
 if mask.any():
  if n=='blue_enamel_backplate':role='EnamelOwlBlue'
  elif n=='top_four_point_star':role='EnamelOwlLemon'
  elif any(k in n for k in ['amber','beak']):role='EnamelOwlAmber'
  else:role='EnamelOwlCream'
  roles[mask]=role
  if 'brow_blade' in n:
   shape=specs[n]['cells'][1]['shape'];upper=shapely.union_all([Polygon(a['exterior'],a.get('holes',[])) for a in shape]);uv=D[n+'_uv'].mean(1);px=uv[:,0]*1254;py=(1-uv[:,1])*1254;sel=mask&shapely.contains_xy(upper,px,py);roles[sel]='EnamelOwlAmber'
  roles_used.update(roles[mask]);newnames=sorted(set(roles));p['materials']=newnames;D[n+'_m']=np.array([newnames.index(a) for a in roles],np.int16);report.append(dict(piece=n,colored_roles=sorted(set(roles[mask]))))
 if n.endswith('_dark_pupil'):
  V=D[n+'_v'];xy=V[...,:2];lo=xy.reshape(-1,2).min(0);hi=xy.reshape(-1,2).max(0);center=(lo+hi)/2;rad=(hi-lo)/2;r2=(((xy-center)/rad)**2).sum(2);delta=.06*np.maximum(0,1-r2);V[...,2]+=np.sign(V[...,2])*delta
  nf=p['front'];v=V[:nf];points,inv=np.unique(v.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);face=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];acc=np.zeros_like(points,dtype=np.float64)
  for j in range(3):
   a=v[:,(j+1)%3]-v[:,j];b=v[:,(j+2)%3]-v[:,j];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];angle=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[:,j],face*angle[:,None])
  acc/=np.linalg.norm(acc,axis=1)[:,None];D[n+'_n'][:nf]=acc[F];D[n+'_n'][nf:2*nf]=acc[F][:,::-1]*[1,1,-1]
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
cfg=dict(texture_px=1024,materials={role:dict(roughness=.18,max_display=.93,gold_exclusion_border_px=6) for role in sorted(roles_used)});cfg['materials']['EnamelOwlBlue']['gold_exclusion_border_px']=10000;(C/'enamel_config.json').write_text(json.dumps(cfg,indent=2)+'\n')
(C/'color_role_fix.json').write_text(json.dumps(dict(cause='One shared enamel role sampled blue, cream and orange together. Gold hue exclusion also removed genuine amber glass and filled it from other colors. Separate roles with only border gold exclusion preserve the intended amber and cream.',pieces=report,pupils='Real cap depth increased by0.06 units with new geometry normals, to catch fixed studio highlights.',blender_review_pending=True),indent=2)+'\n')
print('Prepared Owl05:',sorted(roles_used),'and two real domed pupils')
