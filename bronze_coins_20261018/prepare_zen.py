"""Extract stone silhouettes and intrinsic fine grain, never painted lighting."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import (gaussian_filter, gaussian_filter1d, binary_fill_holes,
                           binary_closing, label, map_coordinates)
from scipy.spatial import ConvexHull,Delaunay

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'zen_balance'
image=np.asarray(Image.open(ROOT/'references/zen_balance.png').convert('RGB'),float)/255
r,g,b=np.moveaxis(image,-1,0)
bronze=(r>g*1.14)&(g>b*1.12)&(r>.12)
shapes={}
regions=[('Upper balancing stone',(453,280,793,458),.220),
         ('Middle balancing stone',(373,456,874,660),.235),
         ('Lower balancing stone',(287,658,958,878),.245)]
for name,(x0,y0,x1,y1),depth in regions:
    mask=binary_fill_holes(binary_closing(bronze[y0:y1,x0:x1],iterations=2))
    labels,n=label(mask)
    counts=np.bincount(labels.ravel());counts[0]=0
    mask=labels==counts.argmax()
    y,x=np.where(mask)
    # Dark contact shadows must not become dents in the physical stone.
    boundary=np.c_[x,y]
    hull=boundary[ConvexHull(boundary).vertices]
    gy,gx=np.indices(mask.shape)
    mask=(Delaunay(hull).find_simplex(np.c_[gx.ravel(),gy.ravel()])>=0).reshape(mask.shape)
    center=np.array([(x.min()+x.max())/2,(y.min()+y.max())/2])
    angles=np.arange(96)*2*np.pi/96
    distances=np.arange(0,max(mask.shape),.4)
    radii=[]
    for a in angles:
        xy=center[:,None]+np.array([np.cos(a),np.sin(a)])[:,None]*distances
        inside=map_coordinates(mask.astype(float),[xy[1],xy[0]],order=1,mode='constant')>.5
        radii.append(distances[np.where(~inside)[0][0]])
    radii=gaussian_filter1d(radii,.9,mode='wrap')
    outline=center+[x0,y0]+np.c_[np.cos(angles),np.sin(angles)]*radii[:,None]
    if name=='Lower balancing stone':
        bottom=(outline[:,1]-outline[:,1].min())/np.ptp(outline[:,1])
        outline[:,1]+=8*bottom**3
    shapes[name]={'outline_pixels':outline.round(3).tolist(),'center_pixels':(center+[x0,y0]).tolist(),'depth':depth}

# A broad rounded foundation continues behind the rim instead of reading as
# a fourth floating pebble. Its face extends down past the visible aperture.
angles=np.arange(96)*2*np.pi/96
outline=np.c_[623+390*np.cos(angles),970+102*np.sin(angles)]
shapes['Broad bronze resting plinth']={'outline_pixels':outline.round(3).tolist(),'center_pixels':[623,970],'depth':.110}
(OUT/'stone_outlines.json').write_text(json.dumps(shapes,indent=2)+'\n')

size=512
yy,xx=np.indices((size,size))
sx=623+((xx+.5)/size*6.03-3.015)*455/2.42
sy=576+(3.015-(yy+.5)/size*6.03)*(-455/2.42)
lum=np.log(np.maximum(image.mean(-1),.025))
detail=gaussian_filter(lum,1.1)-gaussian_filter(lum,13)
grain=map_coordinates(detail,[sy,sx],order=1,mode='nearest')
grain=np.clip(grain/.16,-2,2)
def encode(v):
    v=np.clip(v,0,1)
    return np.uint8(np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)*255+.5)
textures=OUT/'textures'
color=np.array([.55,.265,.115])[None,None,:]*np.exp(grain[:,:,None]*.055)
Image.fromarray(encode(color)).save(textures/'bronze_color.png')
rough=np.clip(.36+grain*.017,.30,.42)
Image.fromarray(np.uint8(rough*255+.5)).save(textures/'bronze_roughness.png')
color=np.array([.012,.014,.016])[None,None,:]*np.exp(grain[:,:,None]*.025)
Image.fromarray(encode(color)).save(textures/'backdrop_color.png')
print('Three reference stone silhouettes, connected foundation and intrinsic bronze grain prepared.')
