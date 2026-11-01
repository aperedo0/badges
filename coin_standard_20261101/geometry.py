"""Owner requested draft: narrower band from outside and thinner full coin."""
import numpy as np
from pathlib import Path
import json
CFG=json.loads(Path(__file__).with_name("draft_design.json").read_text())
INNER=2.420
OLD_OUTER=3.015
RIM_FACTOR=CFG["radial_rim_width_factor"]
DEPTH_FACTOR=CFG["whole_coin_thickness_factor"]
NEW_OUTER=INNER+(OLD_OUTER-INNER)*RIM_FACTOR

def points_after(points):
 p=np.array(points,float,copy=True);r=np.linalg.norm(p[:,:2],axis=1)
 target=np.where(r>INNER,INNER+(r-INNER)*RIM_FACTOR,r)
 p[:,:2]*=(target/np.maximum(r,1e-20))[:,None];p[:,2]*=DEPTH_FACTOR
 return p

def normals_after(points,normals):
 p=np.asarray(points,float);n=np.asarray(normals,float);r=np.linalg.norm(p[:,:2],axis=1);u=p[:,:2]/np.maximum(r,1e-20)[:,None]
 outside=r>=INNER-1e-6;radial=np.where(outside,RIM_FACTOR,1.)
 tangent=np.where(r>INNER,(INNER+(r-INNER)*RIM_FACTOR)/np.maximum(r,1e-20),1.)
 nr=(n[:,:2]*u).sum(1)[:,None];rad=nr*u;tan=n[:,:2]-rad
 result=np.c_[rad/radial[:,None]+tan/tangent[:,None],n[:,2]/DEPTH_FACTOR]
 result/=np.maximum(np.linalg.norm(result,axis=1)[:,None],1e-20)
 return result
