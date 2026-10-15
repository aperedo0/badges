from pathlib import Path
import json,numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import PchipInterpolator
from matplotlib.path import Path as Poly
R=Path('/Users/antonioperedo/Desktop/badges/achievement_coins_refine_20261014')
# Reference-matched smooth column profile, including rounded terminal collars.
y=np.array([303,308,314,321,327,332,339,353,382,420,460,485,501,520,544,559,566,571,577,584,592,599,605,612,630,650,667,690,715,756,796,829,844,851,858,865,872,878],float)
r=np.array([13,23,28,28,23,16,18,13,11,13,20,25,26,22,16,12,19,17,25,29,28,22,15,17,22,26,24,18,13,11,12,14,18,25,28,27,23,15],float)
for name in ['hourglass_teal','hourglass_gold']:
 b=R/name;m=json.loads((b/'design.json').read_text());cx,cy,rad=m['circle']
 yy=np.linspace(y[0],y[-1],90);rr=PchipInterpolator(y,r)(yy)
 for j,x in [(4,428),(5,817)]:
  m['features'][j]['blender_lathe']['profile']=np.c_[(cy-yy)*3.015/rad,np.full(len(yy),(x-cx)*3.015/rad),rr*3.015/rad][::-1].tolist()
 for j in [2,3]:
  d=m['features'][j].pop('blender_bar',json.loads((R.parent/'achievement_coins_20261014'/name/'design.json').read_text())['features'][j]['blender_bar']);cxw,cyw,cz=d['center'];w,h,depth=d['dimensions'];cr=min(.125,h*.43)
  points=[]
  for a,xc,yc in [(0,cxw+w/2-cr,cyw+h/2-cr),(90,cxw-w/2+cr,cyw+h/2-cr),(180,cxw-w/2+cr,cyw-h/2+cr),(270,cxw+w/2-cr,cyw-h/2+cr)]:
   for th in np.linspace(a,a+90,10):
    t=np.radians(th);points.append([xc+cr*np.cos(t),yc+cr*np.sin(t)])
  m['features'][j]['blender_plate']={'points':points,'radius':.028,'z':.155,'extrude':.075}
 (b/'design.json').write_text(json.dumps(m,indent=2))
# Larger irregular facets replace the fine checkerboard on leaves and soil.
b=R/'sprout';m=json.loads((b/'design.json').read_text());old=np.load(b/'reliefs.npz');arrays={k:old[k] for k in old.files}
def faceted(i,boundary,height,spacing):
 boundary=np.asarray(boundary);boundary=boundary[np.r_[True,np.linalg.norm(np.diff(boundary,axis=0),axis=1)>.001]]
 if np.linalg.norm(boundary[0]-boundary[-1])<.001:boundary=boundary[:-1]
 poly=Poly(boundary);signed=np.cross(boundary,np.roll(boundary,-1,axis=0)).sum();pad=.003 if signed>0 else -.003;lo=boundary.min(0);hi=boundary.max(0)
 inner=[]
 for row,y in enumerate(np.arange(lo[1]+spacing*.55,hi[1],spacing)):
  for col,x in enumerate(np.arange(lo[0]+spacing*.55,hi[0],spacing)):
   q=np.array([x+(.10 if row%2 else -.06),y+.055*np.sin(col*2+row)])
   if poly.contains_point(q,radius=-.12):inner.append(q)
 pxy=np.concatenate([boundary,np.asarray(inner)])
 tri=Delaunay(pxy).simplices;keep=poly.contains_points(pxy[tri].mean(1),radius=pad)
 for a,c in [(0,1),(1,2),(2,0)]:keep&=poly.contains_points((pxy[tri[:,a]]+pxy[tri[:,c]])/2,radius=pad)
 tri=tri[keep];p=np.c_[pxy,height(pxy)];n=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
 flip=n[:,2]<0;tri[flip]=tri[flip][:,[0,2,1]];n[flip]*=-1;n/=np.linalg.norm(n,axis=1,keepdims=True)
 from collections import Counter
 counts=Counter(tuple(sorted(e)) for t in tri for e in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])])
 edges=[(a,c) for t in tri for a,c in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])] if counts[tuple(sorted((a,c)))]==1]
 rear=p.copy();rear[:,2]=.07;wall=np.array([[a,len(p)+a,len(p)+c] for a,c in edges]+[[a,len(p)+c,c] for a,c in edges])
 points=np.r_[p,rear];wt=points[wall];wn=np.cross(wt[:,1]-wt[:,0],wt[:,2]-wt[:,0]);wn/=np.maximum(np.linalg.norm(wn,axis=1,keepdims=True),1e-9)
 wn=.25*wn+.75*np.array([0,0,1]);wn/=np.linalg.norm(wn,axis=1,keepdims=True)
 arrays[f'{i}_points']=points;arrays[f'{i}_triangles']=np.r_[tri,wall];arrays[f'{i}_normals']=np.r_[np.repeat(n[:,None],3,axis=1),np.repeat(wn[:,None],3,axis=1)]
 m['features'][i]['front_count']=len(tri);m['features'][i]['triangles']=len(tri)+len(wall)
for i,border in [(0,1),(2,3)]:
 boundary=np.asarray(m['features'][border]['blender_curve']['points'])[::3];lo=boundary.min(0);hi=boundary.max(0);center=(lo+hi)/2
 def height(xy):
  d=np.sqrt(((xy-center)/np.maximum((hi-lo)*.62,.1))**2).sum(1)
  return .18+.095*np.clip(1-d*.60,0,1)
 faceted(i,boundary,height,.40)
top=np.asarray(m['features'][8]['blender_curve']['points'])[::3]
a0=np.arctan2(top[-1,1],top[-1,0]);a1=np.arctan2(top[0,1],top[0,0]);angle=np.linspace(a0,a1,16)
arc=np.c_[2.507*np.cos(angle),2.507*np.sin(angle)]
faceted(7,np.r_[top,arc],lambda xy:.16+.065*np.exp(-((xy[:,0]+.1)**2/.8+(xy[:,1]+1.2)**2/1.6)),.46)
np.savez_compressed(b/'reliefs.npz',**arrays);(b/'design.json').write_text(json.dumps(m,indent=2))
print('Inputs refined.')
