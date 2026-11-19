"""Correct measured compass proportions and restore the broad inner dial band."""
from pathlib import Path
import json, shutil
import numpy as np
import build_geometry as shape
R=Path(__file__).resolve().parent
B=R/'ocean_navigator/candidate13'; C=R/'ocean_navigator/candidate14'
assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz'); G=json.loads((B/'groups.json').read_text())
body=D[f'{next(i for i,g in enumerate(G) if g["name"]=="Double sided navy nautical chart body")}_points']
cy=float((body[:,1].min()+body[:,1].max())/2)
scale=float(np.ptp(body[:,0])/(2*2.94*.934))
parts=[]
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy(); t=D[f'{i}_triangles'].copy()
 if g['name']=='Concentric engraved gold frame' and np.max(np.linalg.norm(p[:,:2]-[0,cy],axis=1))<2.2:continue
 if g['name']=='Fine engraved nautical dial tick':continue
 if g['name'].startswith('Real raised compass '):
  face=np.sign(p[:,2].mean())
  p[:,:2]=[0,cy]+(p[:,:2]-[0,cy])*.88
  p[4,2]=face*(abs(p[:4,2].mean())+.16*scale)
  t=shape.orient_hull(p)
 parts.append((dict(g),p,t))
shape.PARTS.clear()
a=np.arange(384)*2*np.pi/384
for face in [1,-1]:
 shape.contour_band('Measured raised inner nautical dial band '+str(face),np.c_[np.cos(a)*2.015,cy+np.sin(a)*2.015],.085,face*.155,.080)
 for k in range(120):
  angle=k*2*np.pi/120
  u=np.array([np.cos(angle),np.sin(angle),0.])
  center=np.array([0.,cy,face*.206])
  shape.tube('Inner dial incised radial mark '+str(face)+' '+str(k),[center+u*1.987,center+u*2.043],.0027,'gold_recess',4)
for g in shape.PARTS:
 p=g.pop('p');t=g.pop('t')
 if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
 parts.append((g,p,t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
np.savez_compressed(C/'geometry.npz',**out)
(C/'groups.json').write_text(json.dumps(groups,indent=2))
shutil.copy2(B/'materials.json',C/'materials.json')
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'measured_shape_review.json').write_text(json.dumps(dict(source='candidate13',reference_center_pixels=[627,570],reference_inner_band_radius_pixels=360,model_inner_band_radius=2.015,model_inner_band_width=.085,compass_length_factor=.88,compass_actual_ridge_height=.16*scale,physical_gold_only=True,source_gems_and_frame_preserved=True,native_review_pending=True),indent=2))
print('Ocean14 measured dial and compass geometry prepared',len(parts),'pieces')
