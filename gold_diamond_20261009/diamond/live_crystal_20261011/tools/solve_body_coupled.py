from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,distance_transform_edt,gaussian_filter
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/silver2_metal_claude')
from invert_color import inverse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'candidates/04';OUT.mkdir(exist_ok=True)
tex=OUT/'textures';tex.mkdir(exist_ok=True)
d=np.load(ROOT/'source/round_geometry.npz');p,f,uv=d['points'],d['faces'],d['uv']
S=1024;A=np.array([.045,.19,.48]);EM=np.array([.008,.02,.035])
cam=np.array([0.,1.8,23]);target=np.array([0.,-.55,0.])
fw=target-cam;fw/=np.linalg.norm(fw);right=np.cross(fw,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,fw)
def project(pos):
 q=pos-cam;dep=q@fw
 return np.stack([540+2250*(q@right)/dep,720-2250*(q@up)/dep],-1)*(47/60)+[180,70]
im=np.asarray(Image.open(ROOT/'candidates/02/front.png').convert('RGB'),float)/255
lo=np.floor(project(p).min(0)).astype(int)-8;hi=np.ceil(project(p).max(0)).astype(int)+8
crop=im[lo[1]:hi[1],lo[0]:hi[0]]
lin=inverse(crop)
L=np.zeros((S,S,3));valid=np.zeros((S,S),bool);visible=np.zeros((S,S),bool)
for tri,chart in zip(p[f],uv):
 gn=np.cross(tri[1]-tri[0],tri[2]-tri[0]);gn/=np.linalg.norm(gn)
 view=cam-tri.mean(0);view/=np.linalg.norm(view)
 if gn@view<.15:continue
 t=np.stack([chart[:,0]*S-.5,(1-chart[:,1])*S-.5],-1)
 bx0,by0=np.maximum(np.floor(t.min(0)).astype(int),0);bx1,by1=np.minimum(np.ceil(t.max(0)).astype(int),S-1)
 if bx1<bx0 or by1<by0:continue
 x,y=np.meshgrid(np.arange(bx0,bx1+1),np.arange(by0,by1+1))
 e1=t[1]-t[0];e2=t[2]-t[0];den=e1[0]*e2[1]-e1[1]*e2[0]
 if abs(den)<1e-10:continue
 b1=((x-t[0,0])*e2[1]-(y-t[0,1])*e2[0])/den
 b2=(e1[0]*(y-t[0,1])-e1[1]*(x-t[0,0]))/den;b0=1-b1-b2
 mask=(b0>=0)&(b1>=0)&(b2>=0)
 X,Y=x[mask],y[mask]
 pos=b0[mask,None]*tri[0]+b1[mask,None]*tri[1]+b2[mask,None]*tri[2]
 q=project(pos)-lo
 light=np.stack([map_coordinates(lin[...,c],[q[:,1],q[:,0]],order=1,mode='nearest') for c in range(3)],-1)/A
 L[Y,X]=light;visible[Y,X]=True
 # Exclude the actual silhouette, extreme tips and tangent-facing texels.
 valid[Y,X]=(gn@view>.35)&(pos[:,1]>-2.30)&(pos[:,1]<2.28)&(np.abs(pos[:,0])<2.97)
start,end=384,640
field=L[:,start:end].copy();mask=valid[:,start:end]
_,ix=distance_transform_edt(~mask,return_indices=True)
field=field[tuple(ix)]
field=np.maximum(gaussian_filter(field,(1.0,.7,0)),.15)
source=Path('/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/all_sides_20261010/candidates/04/usd/0/emissive.png')
old=np.asarray(Image.open(source).convert('RGB'),float)/255
old=np.where(old<=.04045,old/12.92,((old+.055)/1.055)**2.4)*4
body=np.clip((old[:,start:end]-EM)/field,.002,.95)
# A plain culet avoids the old fixed white point; blend back into the body.
height=2.34860635-(np.arange(S)+.5)/S*(2.34860635+2.455)
tip=np.clip((height+2.455)/.28,0,1)[:,None,None]
body=body*tip+np.array([.055,.16,.34])*(1-tip)
full=np.empty((S,S,3))
for col in range(S):full[:,col]=body[:,(col-start)%256]
encoded=np.where(full<=.0031308,full*12.92,1.055*np.maximum(full,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(encoded,0,1)*255+.5)).save(tex/'body_color.png',optimize=True)
np.savez(OUT/'measured_light.npz',light=field,body=body,valid=mask)
report={'calibration':'Candidate 02 native app front with known dielectric body color, no optical texture and no emission. Full coupled RGB AgX inversion used. The former neutral-axis solver diverged on saturated blue; this uses the actual 3D cube and a damped full Jacobian.',
 'appearance':'Previous optical field transferred into light-responsive body color. Fixed white emissive highlights removed; only a small uniform blue emission remains.',
 'body_range':[full.min((0,1)).tolist(),full.max((0,1)).tolist()],'uniform_emission':EM.tolist(),'excluded_outline':True,'live_specular_ior':2.42}
(OUT/'solve.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
