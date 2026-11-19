"""Numeric optical diagnosis. Reference images never become gemstone materials."""
from pathlib import Path
import sys,json,time
import numpy as np
from scipy.spatial import ConvexHull
from scipy.ndimage import map_coordinates
from PIL import Image
R=Path(__file__).resolve().parent;ROOT=R.parent
sys.path.insert(0,str(ROOT.parent/'silver2_metal_claude'))
from agx import agx

def unit(v):return v/np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-15)
def reflect(d,n):return d-2*np.sum(d*n,axis=-1,keepdims=True)*n
def refract(d,n,eta):
 dot=np.sum(n*d,axis=-1);k=1-eta**2*(1-dot**2)
 out=eta*d-(eta*dot+np.sqrt(np.maximum(k,0)))[:,None]*n
 return np.where((k>=0)[:,None],out,0)
def fresnel(c,ni,nt):
 c=np.clip(c,0,1);s=(ni/nt)**2*(1-c*c);ct=np.sqrt(np.maximum(1-s,0))
 a=(ni*c-nt*ct)/np.maximum(ni*c+nt*ct,1e-12);b=(ni*ct-nt*c)/np.maximum(ni*ct+nt*c,1e-12)
 return np.where(s>=1,1,(a*a+b*b)/2)
class Studio:
 def __init__(self):
  rgb=np.load(R/'studio.npz')['rgb'].astype(float);self.mips=[rgb]
  for i in range(8):
   a=self.mips[-1];h,w=a.shape[:2];self.mips.append(a[:h//2*2,:w//2*2].reshape(h//2,2,w//2,2,3).mean((1,3)))
 def sample(self,d,level):
  # The native stage turns half a circle around world Y.
  d=d*np.array([-1,1,-1]);u=(.5+np.arctan2(d[:,0],-d[:,2])/(2*np.pi))%1;v=.5-np.arcsin(np.clip(d[:,1],-1,1))/np.pi
  a=self.mips[level];h,w=a.shape[:2];x=u*w-.5;y=np.clip(v*h-.5,0,h-1)
  # Horizontal wrap, vertical clamp, at texel centers like the Metal sampler.
  x0=np.floor(x).astype(int);x1=x0+1;y0=np.floor(y).astype(int);y1=np.minimum(y0+1,h-1);fx=x-x0;fy=y-y0
  return a[y0,x0%w]*(1-fx)[:,None]*(1-fy)[:,None]+a[y0,x1%w]*fx[:,None]*(1-fy)[:,None]+a[y1,x0%w]*(1-fx)[:,None]*fy[:,None]+a[y1,x1%w]*fx[:,None]*fy[:,None]
 def sharp(self,d):return np.minimum(self.sample(d,1),24)
 def along(self,d):return self.sharp(d)+np.minimum(self.sample(d,8),3)*.9

def planes_of(points):
 eq=ConvexHull(points).equations;eq=np.unique(np.round(eq,8),axis=0)
 return eq[:,:3],-eq[:,3]
def interval(hull,o,d):
 n,w=hull;gap=w[None,:]-o@n.T;gap=np.where(abs(gap)<=1e-5,0,gap);approach=d@n.T;parallel=abs(approach)<1e-6
 distance=gap/np.where(parallel,1,approach)
 entry=np.where((approach<0)&~parallel,distance,-np.inf);exit=np.where((approach>0)&~parallel,distance,np.inf)
 ei=entry.argmax(1);xi=exit.argmin(1);ids=np.arange(len(o));lo=entry[ids,ei];hi=exit[ids,xi]
 valid=(hi>=-1e-5)&(lo<=hi+1e-5)&~np.any(parallel&(gap < -1e-5),1)
 return valid,lo,np.maximum(hi,0),n[ei],n[xi]
def outer(hulls,o,d):
 a,b=[interval(h,o,d) for h in hulls];va,la,ha,na,xa=a;vb,lb,hb,nb,xb=b
 usea=va&(~vb|(np.maximum(la,0)<=np.maximum(lb,0)));lo=np.where(usea,la,lb);hi=np.where(usea,ha,hb);entry=np.where(usea[:,None],na,nb);exit=np.where(usea[:,None],xa,xb)
 otherlo=np.where(usea,lb,la);otherhi=np.where(usea,hb,ha);othern=np.where(usea[:,None],xb,xa);otherv=np.where(usea,vb,va)
 merge=otherv&(otherlo<=hi+2e-5)&(otherhi>hi);hi=np.where(merge,otherhi,hi);exit=np.where(merge[:,None],othern,exit)
 return va|vb,lo,hi,entry,exit

def optical(hulls,o,d,studio):
 valid,lo,_,n,_=outer(hulls,o,d);valid&=(lo>0);ids=np.flatnonzero(valid);o=o[ids];d=d[ids];n=n[ids];lo=lo[ids]
 pos=o+d*lo[:,None];f=fresnel(-np.sum(n*d,1),1,1.77);out=f[:,None]*studio.sharp(reflect(d,n));weight=np.repeat((1-f)[:,None],3,axis=1);direction=refract(d,n,1/1.77)
 absorption=np.array([.16,9.,2.8])*.5;indices=[1.76,1.77,1.79]
 for hit in range(6):
  ok,_,distance,_,normal=outer(hulls,pos,direction);distance=np.where(ok,distance,0);pos=pos+direction*distance[:,None];weight*=np.exp(-absorption*distance[:,None]*.99)
  share=fresnel(np.sum(normal*direction,1),1.77,1)
  green=refract(direction,-normal,1.77);rgb=[]
  for channel,index in enumerate(indices):
   bent=refract(direction,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent)
   rgb.append(studio.along(bent)[:,channel])
  out+=weight*(1-share)[:,None]*np.stack(rgb,axis=1);weight*=share[:,None];direction=reflect(direction,normal)
 return ids,(out+weight*studio.along(direction))*.32

def render(res=160):
 C=ROOT/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');g=json.loads((C/'groups.json').read_text());hulls=[planes_of(D[f'{i}_points']) for i,a in enumerate(g) if a['mat']=='CrestGem_Rose'];assert len(hulls)==2
 # A camera ray is aimed at each point on a world XY sampling plane. This
 # is diagnostic projection, not a native screenshot or accepted fit.
 yy,xx=np.mgrid[0:res,0:res];xy=np.c_[(xx.ravel()/(res-1)-.5)*6.5,2.975-yy.ravel()/(res-1)*5.6,np.zeros(res*res)];origin=np.broadcast_to([0,1.8,23.],xy.shape).copy();direction=unit(xy-origin)
 start=time.time();ids,lin=optical(hulls,origin,direction,Studio());display=np.clip(agx(lin),0,1);image=np.full((res*res,3),.045);image[ids]=display
 Image.fromarray(np.uint8(image.reshape(res,res,3)*255)).save(R/'heart_forward_diagnostic.png')
 (R/'forward_status.json').write_text(json.dumps(dict(status='diagnostic_only',native_validated=False,reference_fit_performed=False,resolution=res,surface_rays=len(ids),seconds=time.time()-start,omissions=['Sparse internal cleavage paths','Spatial optical density noise','Native raster projection and coverage']),indent=2))
 print('Forward diagnostic saved. Native calibration required before fitting.',time.time()-start,flush=True)
if __name__=='__main__':render(int(sys.argv[1]) if len(sys.argv)>1 else 160)
