"""Trace the owner's reference into three closed, smoothly rolled copper ribbons.

Run with system Python. USD/Blender export is a separate, reproducible step.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label, gaussian_filter1d, map_coordinates
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
im = np.asarray(Image.open(ROOT/'source/reference.png').convert('RGB'))
labels, _ = label(im.max(-1) > 35)
components = sorted([i for i in range(1, labels.max()+1) if (labels==i).sum()>1000], key=lambda i: -int((labels==i).sum()))
scale = 5.30 / (1402-214)
cx = (127+833)/2
ridge_points = {
    'Central': [(214,448),(300,413),(400,404),(500,432),(600,492),(700,539),(800,556),(900,533),(1000,474),(1100,406),(1200,376),(1300,403),(1402,497)],
    'Right': [(720,735),(800,759),(900,772),(1000,754),(1100,694),(1200,610),(1300,548),(1392,556)],
    'Left': [(622,334),(700,336),(800,308),(900,237),(1000,183),(1100,172),(1200,196),(1239,224)],
}
records = []
for comp, name, rows in zip(components, ['Central','Right','Left'], [241,151,151]):
    ys, xs = np.where(labels==comp)
    y0,y1 = int(ys.min()),int(ys.max())
    yy = np.arange(y0,y1+1)
    left=np.array([np.where(labels[y]==comp)[0].min() for y in yy],float)
    right=np.array([np.where(labels[y]==comp)[0].max() for y in yy],float)
    # A subpixel edge fit suppresses raster stair steps without changing the outline.
    left=gaussian_filter1d(left,2.0);right=gaussian_filter1d(right,2.0)
    for endpoint in [0,-1]:
        mid=(left[endpoint]+right[endpoint])/2
        left[endpoint]=right[endpoint]=mid
    t=np.linspace(0,1,rows)
    # Cosine row spacing concentrates geometry at the pointed ends.
    t=(1-np.cos(np.pi*t))/2
    y=y0+(y1-y0)*t
    l=np.interp(y,yy,left);r=np.interp(y,yy,right)
    l[0]=r[0]=(left[0]+right[0])/2;l[-1]=r[-1]=(left[-1]+right[-1])/2
    rp=np.asarray(ridge_points[name],float)
    ridge=PchipInterpolator(rp[:,0],rp[:,1])(y)
    fraction=np.clip((ridge-l)/np.maximum(r-l,1e-5),.12,.88)
    cross=19
    # Include the real crest in every row; each flank gets nine subdivisions.
    us=np.concatenate([np.linspace(0,1,10)[:-1,None]*fraction[None,:], fraction[None,:]+np.linspace(0,1,10)[:,None]*(1-fraction[None,:])],axis=0).T
    x=l[:,None]+(r-l)[:,None]*us
    Y=np.broadcast_to(y[:,None],x.shape)
    a=np.where(us<=fraction[:,None],us/np.maximum(fraction[:,None],1e-5),(1-us)/np.maximum(1-fraction[:,None],1e-5))
    # Rounded edges, broad cambered flanks, a gently rolled central crest.
    shape=np.sin(np.clip(a,0,1)*np.pi/2)**.72
    tip=np.clip((r-l)*scale/.32,0,1)
    tip=tip*tip*(3-2*tip)
    front=(.014+.311*shape)*tip[:,None]
    back=(-.014-.311*shape)*tip[:,None]
    xy=np.stack([(x-cx)*scale, -2.455+(1402-Y)*scale],-1)
    points=[];fidx=np.empty((rows,cross),int);bidx=np.empty_like(fidx)
    for i in range(rows):
        if i in [0,rows-1]:
            idx=len(points);points.append([xy[i,0,0],xy[i,0,1],0.]);fidx[i,:]=idx;bidx[i,:]=idx
        else:
            for j in range(cross):
                fidx[i,j]=len(points);points.append([*xy[i,j],front[i,j]])
                bidx[i,j]=len(points);points.append([*xy[i,j],back[i,j]])
    faces=[];roles=[]
    def add(a,b,c,role):
        if len({int(a),int(b),int(c)})==3:faces.append([a,b,c]);roles.append(role)
    for i in range(rows-1):
        for j in range(cross-1):
            a,b,c,d=fidx[i,j],fidx[i,j+1],fidx[i+1,j],fidx[i+1,j+1]
            add(a,c,b,0);add(b,c,d,0)
            a,b,c,d=bidx[i,j],bidx[i,j+1],bidx[i+1,j],bidx[i+1,j+1]
            add(a,b,c,1);add(b,d,c,1)
        for j in [0,cross-1]:
            a,b,c,d=fidx[i,j],fidx[i+1,j],bidx[i,j],bidx[i+1,j]
            if j==0:add(a,c,b,2);add(b,c,d,2)
            else:add(a,b,c,2);add(b,d,c,2)
    points=np.array(points);faces=np.asarray(faces,dtype=np.int32);roles=np.asarray(roles)
    # Smooth area-weighted normals, without a normal texture.
    tri=points[faces];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.zeros_like(points)
    for k in range(3):np.add.at(norm,faces[:,k],n)
    norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-10)
    # World-planar UV: an exact, stable mapping from the reference to the material.
    uv=np.stack([(points[:,0]/scale+cx)/im.shape[1],1-(1402-(points[:,1]+2.455)/scale)/im.shape[0]],-1)
    np.savez_compressed(ROOT/'source'/f'{name.lower()}_geometry.npz',points=points,faces=faces,normals=norm,uv=uv,roles=roles)
    records.append(dict(name=name,triangles=len(faces),bounds=[points.min(0).tolist(),points.max(0).tolist()],rows=rows,cross=cross))
metadata=dict(scale=scale,center_x=cx,reference_bottom=1402,reference_top=214,floor=-2.895,bottom=-2.455,meshes=records)
(ROOT/'source/mapping.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata,indent=2))
