"""Restore metal normals from the actual bevel geometry, not a constant shallow tilt."""
from pathlib import Path
import json,shutil,numpy as np
R=Path(__file__).resolve().parent;A=R/'campfire_night/candidate26';C=A.parent/'candidate27';assert not C.exists();C.mkdir()
for name in ['PIECES.json','parts.json','parts.npz','palette_enamel.json','enamel_config.json','center_validation.json']:
 shutil.copy2(A/name,C/name)
shutil.copytree(A/'textures',C/'textures')
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());changes={}
for p in M['parts']:
 name=p['name'];nf=p['front'];V=D[name+'_v'][:nf];N=D[name+'_n'];mi=D[name+'_m'];roles=np.array([p['materials'][i] for i in mi[:nf]])
 metal=np.isin(roles,['Gold','FineGold','GoldEdge','SmoothGold'])
 if not metal.any():continue
 pts,inv=np.unique(V.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3)
 edges1=V[:,1]-V[:,0];edges2=V[:,2]-V[:,0];face=np.cross(edges1,edges2);lens=np.linalg.norm(face,axis=1);assert (lens>0).all();face/=lens[:,None]
 accum=np.zeros_like(pts,dtype=np.float64)
 # Angle weighted normals follow actual broad bevels; color faces retain their proven flat normals.
 for j in range(3):
  a=V[:,(j+1)%3]-V[:,j];b=V[:,(j+2)%3]-V[:,j];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(accum,F[:,j],face*ang[:,None])
 length=np.linalg.norm(accum,axis=1);assert (length>0).all();accum/=length[:,None];new=accum[F]
 N[:nf][metal]=new[metal];N[nf:2*nf][metal]=new[metal][:,::-1]*[1,1,-1]
 changes[name]=dict(metal_triangles=int(metal.sum()),median_tilt=float(np.median(np.linalg.norm(new[metal][...,:2],axis=2))))
np.savez_compressed(C/'parts.npz',**D)
(C/'palette_overrides.json').write_text(json.dumps(dict(FineGold=dict(albedo=[.83,.43,.045],metallic=1,roughness=.26)),indent=2)+'\n')
(C/'normal_method.json').write_text(json.dumps(dict(method='Angle weighted actual geometric bevel normals. No constant shallow contour tilt. Colored faces and true vertical walls retained unchanged.',changes=changes,blender_render_review_pending=True),indent=2)+'\n')
print('Prepared27. All geometry and UVs unchanged; restored actual metal bevel normals.')
