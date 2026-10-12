"""Continuous closed trefoil ribbon traced from the platinum reference."""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import root
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'platinum'
# Follow the same ribbon continuously around all three lobes.
control=np.array([[178,78],[224,95],[249,132],[251,173],[233,219],
 [201,262],[160,299],[115,320],[76,317],[51,295],[46,262],
 [59,226],[86,198],[119,178],[154,166],[194,169],[232,184],
 [270,209],[301,244],[313,278],[302,309],[275,325],[240,327],
 [203,310],[171,286],[145,259],[125,226],[111,190],[106,153],
 [113,120],[135,93],[157,81],[178,78]],float)
chord=np.linalg.norm(np.diff(control,axis=0),axis=1);times=np.r_[0,np.cumsum(chord)];times/=times[-1]
curve=CubicSpline(times,control,bc_type='periodic')
probe=np.arange(512)/512;xy=curve(probe);crossings=[]
for i in range(512):
 a=xy[i];b=xy[(i+1)%512]-a
 for j in range(i+10,512):
  if i+512-j<10:continue
  c=xy[j];d=xy[(j+1)%512]-c;den=b[0]*d[1]-b[1]*d[0]
  if abs(den)<1e-8:continue
  q=c-a;u=(q[0]*d[1]-q[1]*d[0])/den;v=(q[0]*b[1]-q[1]*b[0])/den
  if 0<u<1 and 0<v<1:
   sol=root(lambda t:curve(t[0])-curve(t[1]),[(i+u)/512,(j+v)/512]);assert sol.success
   crossings.append(sorted(sol.x.tolist()))
assert len(crossings)==3,crossings
anchors=sorted(t for pair in crossings for t in pair)
# Alternating depth at the six crossings gives a true trefoil, not stacked rings.
values=np.array([.57,-.57,.57,-.57,.57,-.57])
zcurve=CubicSpline(np.r_[anchors,anchors[0]+1],np.r_[values,values[0]],bc_type='periodic',extrapolate='periodic')
M={'scale':5.75/320,'center_x':179.,'reference_bottom':351.,'reference_top':54.,'reference_bounds':[19,54,339,351],
 'roughness':.30,'image_size':[356,376],'projection':'reference plane at Z=0; camera [0,1.8,23]'}
N=768;J=28;t=np.arange(N)/N;c=curve(t);v=curve(t,1);v/=np.linalg.norm(v,axis=1,keepdims=True);side=np.stack([-v[:,1],v[:,0]],-1)
angle=np.arange(J)*2*np.pi/J
shape_x=np.sign(np.cos(angle))*np.abs(np.cos(angle))**.38
shape_z=np.sign(np.sin(angle))*np.abs(np.sin(angle))**.38
# A wide smooth face and a narrow rounded bevel around both ribbon edges.
half_width=24.5;half_depth=.125
pixels=c[:,None,:]+side[:,None,:]*half_width*shape_x[None,:,None]
zz=zcurve(t)[:,None]+half_depth*shape_z[None,:]
x0=(pixels[...,0]-M['center_x'])*M['scale'];y0=-2.455+(M['reference_bottom']-pixels[...,1])*M['scale']
p=np.stack([x0*(1-zz/23),1.8+(y0-1.8)*(1-zz/23),zz],-1).reshape(-1,3)
lo=p.min(0);hi=p.max(0);offset=np.array([-(lo[0]+hi[0])/2,-2.455-lo[1],-(lo[2]+hi[2])/2]);p+=offset;M['world_offset']=offset.tolist()
f=[];roles=[]
for j in range(N):
 for k in range(J):
  a=j*J+k;b=((j+1)%N)*J+k;d=j*J+(k+1)%J;e=((j+1)%N)*J+(k+1)%J
  f.extend([[a,b,e],[a,e,d]]);roles.extend([0 if np.sin((k+.5)*2*np.pi/J)>0 else 1]*2)
f=np.array(f);volume=np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()/6
if volume<0:f=f[:,::-1]
area=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);normal=np.zeros_like(p)
for k in range(3):np.add.at(normal,f[:,k],area)
normal/=np.linalg.norm(normal,axis=1,keepdims=True)
uv=np.stack([pixels[...,0]/356,1-pixels[...,1]/376],-1).reshape(-1,2)
name='PlatinumKnot_ContinuousBeveledRibbon'
np.savez_compressed(BASE/'source'/f'{name}.npz',points=p,faces=f,normals=normal[f],uv=uv,roles=np.array(roles))
M['crossings']=[{'parameters':pair,'reference_pixel':curve(pair[0]).tolist(),'depths':[float(zcurve(q)) for q in pair]} for pair in crossings]
M['meshes']=[{'name':name,'triangles':len(f),'smooth':True,'bounds':[p.min(0).tolist(),p.max(0).tolist()]}]
assert p[:,1].max()<=3.015,(p.min(0),p.max(0))
assert max(abs(p[:,0].min()),abs(p[:,0].max()))<=3.35
(BASE/'source/mapping.json').write_text(json.dumps(M,indent=2)+'\n')
print(json.dumps(M,indent=2))
