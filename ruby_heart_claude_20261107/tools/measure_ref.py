"""Classify reference pixels into background, gold and ruby; report outlines."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
im=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)/255
r,g,b=im[...,0],im[...,1],im[...,2]
mx=im.max(-1); mn=im.min(-1); sat=(mx-mn)/np.maximum(mx,1e-6)
bg=(mx<0.22)&(sat<0.6)
gold=(~bg)&(g>0.35*r)&(r>0.25)&(b<0.8*g)&(sat>0.25)
ruby=(~bg)&(g<0.42*r)&(r>0.2)
fg=ndi.binary_fill_holes(ndi.binary_opening(~bg,iterations=2))
lab,n=ndi.label(fg); sizes=ndi.sum(fg,lab,range(1,n+1)); fg=lab==(1+int(np.argmax(sizes)))
gem=ndi.binary_fill_holes(ndi.binary_opening(ruby,iterations=3))
lab,n=ndi.label(gem); sizes=ndi.sum(gem,lab,range(1,n+1)); gem=lab==(1+int(np.argmax(sizes)))
ys,xs=np.nonzero(fg); gy,gx=np.nonzero(gem)
out=dict(outer=dict(x=[int(xs.min()),int(xs.max())],y=[int(ys.min()),int(ys.max())]),
         gem=dict(x=[int(gx.min()),int(gx.max())],y=[int(gy.min()),int(gy.max())]))
# band width along rows: left outer edge vs left gem edge
rows={}
for y in range(200,1000,50):
    o=np.nonzero(fg[y])[0]; gg=np.nonzero(gem[y])[0]
    if len(o) and len(gg): rows[y]=dict(outer=[int(o.min()),int(o.max())],gem=[int(gg.min()),int(gg.max())])
out['rows']=rows
# notch: topmost foreground pixel near the center column
for name,m in (('outer',fg),('gem',gem)):
    col=np.nonzero(m[:,600:655].any(1))[0]
    out[name]['center_top_y']=int(col.min()) if len(col) else None
np.savez_compressed(sys.argv[2],fg=fg,gem=gem,gold=gold)
print(json.dumps(out,indent=1))
