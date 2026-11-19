from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;C=R/'amethyst_crown/candidate19';G=json.loads((C/'groups.json').read_text());g=next(g for g in G if 'band_grid' in g)
a=np.asarray(Image.open(C/'textures/velvet_color.png').convert('RGB'),float)/255;linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);h,w=a.shape[:2];v,u=np.mgrid[0:h,0:w];u=(u+.5)/w;v=1-(v+.5)/h
phase=g['quilt_vertical_phase'];a1=(48*u+phase*v)%1;b1=(48*u-phase*v)%1;distance=np.minimum(np.minimum(a1,1-a1),np.minimum(b1,1-b1));thread=1-.18*np.exp(-.5*(distance/.025)**2);linear*=thread[...,None];rgb=np.where(linear<=.0031308,linear*12.92,1.055*np.maximum(linear,0)**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).save(C/'textures/quilted_band_color.png');print('Intrinsic stitched textile color saved; no lighting or photo appearance included')
