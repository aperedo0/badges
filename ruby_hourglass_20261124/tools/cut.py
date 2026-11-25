"""Construct four closed solids in app coordinates from the owner's drawing."""
from pathlib import Path
from collections import Counter
import json,sys
import numpy as np
from PIL import Image
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon

root=Path(__file__).resolve().parents[1]
out=root/(sys.argv[1] if len(sys.argv)>1 else json.loads((root/'design.json').read_text())['candidate'])
out.mkdir(exist_ok=True)
scale=5.45/1245
def unit(v): return v/np.linalg.norm(v,axis=-1,keepdims=True)
def rotate(p): return np.array([-p[1],p[0]])

def cut(stations):
    points=np.unique([(sx*w*scale,2.995-(row-87)*scale,sz*z)
        for w,row,z in stations for sx in (1,-1) for sz in (1,-1)],axis=0)
    h=ConvexHull(points)
    faces=h.simplices.copy()
    for i,(a,b,c) in enumerate(points[faces]):
        if np.dot(np.cross(b-a,c-a),h.equations[i,:3])<0:faces[i]=faces[i,::-1]
    unneeded=set(range(len(points)))-set(h.vertices)
    if unneeded: print('interior stations:', sorted(set((round(abs(points[i,0])/scale),round(87+(2.995-points[i,1])/scale)) for i in unneeded)))
    lookup={int(v):i for i,v in enumerate(h.vertices)}
    faces=np.array([[lookup[int(k)] for k in f] for f in faces])
    points=points[h.vertices]
    a,b,c=points[faces].transpose(1,0,2)
    return dict(points=points,triangles=faces,normals=unit(np.cross(b-a,c-a)))

def rail():
    p,k,q=np.array([[125.,205.],[412.,700.],[121.,1218.]])
    u=unit(k-p);v=unit(q-k)
    r=43.;t=r*np.tan(np.arccos(np.dot(u,v))/2)
    t0=k-u*t;t1=k+v*t
    center=t0+rotate(u)*r
    angle=np.linspace(np.arctan2(*(t0-center)[::-1]),np.arctan2(*(t1-center)[::-1]),19)
    arc=np.column_stack([np.cos(angle),np.sin(angle)])
    path=np.vstack([p,center+r*arc,q])
    tan=np.vstack([u,np.column_stack([-arc[:,1],arc[:,0]]),v])
    direction=np.column_stack([-tan[:,1],tan[:,0]])
    lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))]
    w=np.interp(lengths,[0,lengths[-1]*.49,lengths[-1]],[28.8,32.5,28.8])
    def cap_dirs(n, tangent):
        return np.asarray([n*np.cos(a)+tangent*np.sin(a) for a in np.linspace(0,np.pi,49)[1:-1]])
    end=cap_dirs(direction[-1],v);start=cap_dirs(-direction[0],-u)
    centers=np.vstack((path,np.tile(path[-1],(len(end),1)),path[::-1],np.tile(path[0],(len(start),1))))
    outward=np.vstack((direction,end,-direction[::-1],start))
    widths=np.r_[w,np.full(len(end),w[-1]),w[::-1],np.full(len(start),w[0])]
    s=np.r_[lengths,np.full(len(end),lengths[-1]),lengths[::-1],np.zeros(len(start))]
    across=np.r_[np.ones(len(path)),end@direction[-1],-np.ones(len(path)),start@direction[0]]
    bevel=.085 if out.name in ('candidate04','candidate05') else .058
    depth=.165
    profile=[]
    for side in (-1,1):
        angles=np.linspace(np.pi/2,0,8) if side<0 else np.linspace(0,np.pi/2,8)
        for a in angles:
            profile.append((bevel*(1-np.cos(a)),side*(depth-bevel+bevel*np.sin(a)),np.cos(a),side*np.sin(a)))
    vertices=[];normals=[];uv=[];faces=[];n=len(centers)
    for inset,z,nx,nz in profile:
        xy=centers+outward*(widths-inset/scale)[:,None]
        vertices.extend(np.column_stack(((xy[:,0]-558)*scale,2.995-(xy[:,1]-87)*scale,np.full(n,z))))
        normals.extend(np.column_stack((nx*outward[:,0],-nx*outward[:,1],np.full(n,nz))))
        uv.extend(np.column_stack((.5+across*.48*(widths-inset/scale)/32.5,s/lengths[-1])))
    for j in range(len(profile)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            faces.extend([(a,b,b+n),(a,b+n,a+n)])
    for ring in [0,len(profile)-1]:
        offset=ring*n
        xy=np.asarray(vertices[offset:offset+n])[:,:2]
        lut={tuple(p):i+offset for i,p in enumerate(xy)}
        for tri in constrained_delaunay_triangles(Polygon(xy)).geoms:
            faces.append(tuple(lut[pt] for pt in list(tri.exterior.coords)[:3]))
    vertices=np.asarray(vertices);normals=np.asarray(normals);faces=np.asarray(faces)
    for i,(a,b,c) in enumerate(vertices[faces]):
        if np.dot(np.cross(b-a,c-a),normals[faces[i]].mean(axis=0))<0:faces[i]=faces[i,::-1]
    return dict(points=vertices,triangles=faces,normals=normals,uv=np.asarray(uv))

upper=[(316,87,.14),(211,137,.66),(395,191,.085),(294,212,.69),(158,212,.98),
       (197,247,.87),(128,281,.96),(65,698,.035),(0,698,.19)]
lower=[(328,1332,.14),(213,1270,.65),(403,1235,.085),(315,1236,.56),(300,1177,.69),(155,1175,.98),
       (197,1130,.87),(109,1100,.95),(63,696.4,.032),(0,696.4,.18)]
left=rail()
right={k:v.copy() for k,v in left.items()};right['points'][:,0]*=-1;right['normals'][:,0]*=-1;right['triangles']=right['triangles'][:,::-1]
geometry={'Upper_Ruby':cut(upper),'Lower_Ruby':cut(lower),'Left_Bronze_Rail':left,'Right_Bronze_Rail':right}
report={}
for name,obj in geometry.items():
    p,t=obj['points'],obj['triangles']
    a,b,c=p[t].transpose(1,0,2)
    area=np.linalg.norm(np.cross(b-a,c-a),axis=1)
    assert min(area)>1e-12,(name,min(area))
    edges=Counter((int(f[i]),int(f[(i+1)%3])) for f in t for i in range(3))
    assert all(n==1 and edges[(b,a)]==1 for (a,b),n in edges.items()),name
    volume=np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6
    assert volume>0
    report[name]=dict(vertices=len(p),triangles=len(t),volume=round(volume,5),bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()])
(out/'geometry.json').write_text(json.dumps({k:{key:np.round(val,9).tolist() for key,val in obj.items()} for k,obj in geometry.items()},separators=(',',':')))
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
rng=np.random.default_rng(84)
grain=gaussian_filter(rng.normal(size=(512,512)),(11,1.3));grain/=grain.std()
fine=gaussian_filter(rng.normal(size=(512,512)),(3,.6));fine/=fine.std()
Image.fromarray(np.uint8(np.clip((.41 if out.name in ('candidate04','candidate05') else .34)+.011*grain+.005*fine,.29,.46)*255)).save(out/'BronzeBrush.png')
print({k:v['triangles'] for k,v in report.items()})
