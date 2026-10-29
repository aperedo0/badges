"""Measure the full outer metal edge, excluding background glow."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];cfg=json.loads((R/'design.json').read_text());im=np.array(Image.open(R/'reference.png').convert('RGB'),float)/255;lum=gaussian_filter(im@np.array([.2126,.7152,.0722]),.7)
cx,cy,rx,ry=cfg['disc'];angles=np.arange(720)*2*np.pi/720;rad=np.linspace(.90,1.12,441)
x=cx+np.cos(angles[:,None])*rx*rad;y=cy+np.sin(angles[:,None])*ry*rad;values=map_coordinates(lum,[y,x],order=1,mode='nearest')
background=np.median(values[:,-15:],axis=1);peak=values.max(1);threshold=background+np.maximum(.052,(peak-background)*.11)
valid=(abs(np.sin(angles))<.98)&(abs(np.cos(angles))<.98)
# Select the outermost metal surface rather than an internal bright band.
edge=np.max(np.where(values>threshold[:,None],rad[None,:],0),axis=1);valid&=(edge>.92)&(edge<1.09)
points=np.c_[cx+np.cos(angles)*rx*edge,cy+np.sin(angles)*ry*edge]
def residual(p):
 a,b,c,d=p;q=points[valid];return (np.sqrt(((q[:,0]-a)/c)**2+((q[:,1]-b)/d)**2)-1)*540
fit=least_squares(residual,[cx,cy,rx,ry],loss='soft_l1',f_scale=1.8);a,b,c,d=fit.x;p=np.c_[a+np.cos(angles)*c,b+np.sin(angles)*d]
(R/'measured_disc_ellipse.json').write_text(json.dumps(fit.x.round(3).tolist())+'\n');(R/'measured_disc_outline.json').write_text(json.dumps(p.round(3).tolist())+'\n')
debug=Image.fromarray(np.uint8(im*255));draw=ImageDraw.Draw(debug);draw.line([tuple(q) for q in p]+[tuple(p[0])],fill=(255,80,50),width=2);debug.save(R/'disc_outline_review.png');print(sys.argv[1],fit.x.round(3).tolist(),'median error',float(np.median(abs(residual(fit.x)))))
