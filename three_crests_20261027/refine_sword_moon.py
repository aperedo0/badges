"""Prepare copies for softer sword reflections and continuous moon relief."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter

ROOT=Path(__file__).resolve().parent
for key,previous,candidate in [('winged_sword','candidate04','candidate05'),('crescent_ocean','candidate08','candidate09')]:
 R=ROOT/key;old=R/previous;C=R/candidate
 if C.exists():raise RuntimeError('Candidate already exists: '+str(C))
 C.mkdir();(C/'mobile').mkdir()
 for name in ['geometry.npz','trace.json','finish.npz','compass.json','target_reference.png','material_fit.json']:
  if (old/name).exists():shutil.copyfile(old/name,C/name)
 for name in ['approved_textures','textures']:shutil.copytree(old/name,C/name)
 (R/'candidate.txt').write_text(candidate+'\n')
 (C/'refinement.json').write_text(json.dumps({'gentle_sword_metal':key=='winged_sword','continuous_moon_relief':key=='crescent_ocean','previous_candidate':previous},indent=2)+'\n')
 if key!='crescent_ocean':continue
 with np.load(C/'geometry.npz') as data:arrays={k:data[k] for k in data.files}
 z=arrays['height'].copy();trace=json.loads((C/'trace.json').read_text());H,W=z.shape
 # The earlier wave body began at one horizontal row, introducing a false
 # fold through both metal arcs. Replace that join by a C1 continuous span.
 a,b=530,760;t=np.linspace(0,1,b-a+1)[:,None];length=b-a
 derivative=np.gradient(gaussian_filter(z,(5,3)),axis=0)
 da=np.clip(derivative[a],-.001,.001);db=np.clip(derivative[b],-.001,.001)
 patch=(2*t**3-3*t**2+1)*z[a]+(t**3-2*t**2+t)*length*da+(-2*t**3+3*t**2)*z[b]+(t**3-t**2)*length*db
 # Keep the celestial field, independent compass and right wave untouched.
 xx=np.arange(W);weight=np.clip((780-xx)/80,0,1)[None,:]
 weight=weight*weight*(3-2*weight)
 z[a:b+1]=z[a:b+1]*(1-weight)+patch*weight
 arrays['height']=z
 p=arrays['reference_points'];n=len(p)
 depth=map_coordinates(z,[p[:,1],p[:,0]],order=1,mode='nearest')
 arrays['points'][:n,2]=depth;arrays['points'][n:,2]=-depth
 wall=arrays['wall_points'];scale=trace['reference_scale'];lo=trace['reference_bounds'][0];cx=trace['reference_center'][0]
 rx=cx+wall[:,0]/scale;ry=lo[1]+(3.015-wall[:,1])/scale
 wall[:,2]=np.sign(wall[:,2])*map_coordinates(z,[ry,rx],order=1,mode='nearest')
 # Share exact depth values with the adjoining face to keep the mesh closed.
 lookup={(float(q[0]),float(q[1]),int(np.sign(q[2]))):q[2] for q in arrays['points']}
 for q in wall:q[2]=lookup[(float(q[0]),float(q[1]),int(np.sign(q[2])))]
 arrays['wall_points']=wall
 np.savez_compressed(C/'geometry.npz',**arrays)
 print(key,'continuous relief saved',flush=True)
