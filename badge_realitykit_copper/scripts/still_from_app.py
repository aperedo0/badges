"""Prepare fixed-frame tier art from the measured real-app render.
No app artwork or source files are changed. 600 px asset, 120 px/40 pt proof.
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/sys.argv[1]
camera=np.array([0.,1.8,23.]);f=np.array([0.,-.55,0])-camera;f/=np.linalg.norm(f)
r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f)
def project(p):
    d=p-camera;depth=d@f
    return np.stack([540+2250*(d@r)/depth,720-2250*(d@u)/depth],-1)*47/60+[180,70]
side=586*120/108*47/60;center=np.array([540,656])*47/60+[180,70]
box=tuple(np.round(np.r_[center-side/2,center+side/2]).astype(int))
im=Image.open(OUT/'app.png').convert('RGB').crop(box)
SS=4;mask=Image.new('L',(im.width*SS,im.height*SS),0);draw=ImageDraw.Draw(mask)
for name in ['central','right','left']:
    d=np.load(ROOT/'source'/f'{name}_geometry.npz');p=(project(d['points'])-box[:2])*SS
    for tri in d['faces']:
        draw.polygon([tuple(v) for v in p[tri]],fill=255)
mask=mask.resize(im.size,Image.Resampling.LANCZOS)
a=np.asarray(mask,float)/255;rgb=np.asarray(im,float)/255
# Remove the smoothly varying stage contribution at the antialiased edge.
_,(iy,ix)=distance_transform_edt(a>0.01,return_indices=True)
bg=rgb[iy,ix];color=np.clip((rgb-bg*(1-a[...,None]))/np.maximum(a[...,None],.03),0,1)
rgba=np.dstack([np.uint8(color*255+.5),np.uint8(a*255+.5)])
art=Image.fromarray(rgba,'RGBA').convert('RGBa').resize((600,600),Image.Resampling.LANCZOS).convert('RGBA')
art.save(OUT/'BadgeArt_copper_flame.png',optimize=True)
small=art.convert('RGBa').resize((120,120),Image.Resampling.LANCZOS).convert('RGBA');small.save(OUT/'BadgeArt_copper_flame_40pt.png',optimize=True)
proof=Image.new('RGB',(240,120),'#111315');proof.paste(small,(0,0),small)
white=Image.new('RGB',(120,120),'#eceef1');white.paste(small,(0,0),small);proof.paste(white,(120,0));proof.save(OUT/'40pt_proof.png')
print('Prepared fixed Home frame',box,'600px art and native 120px/40pt proof')
