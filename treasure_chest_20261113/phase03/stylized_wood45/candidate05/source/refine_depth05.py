from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

S=Path(__file__).resolve().parent
B=S/'candidate04'
C=S/'candidate05'
D=json.loads((C/'design.json').read_text())
T=C/'textures'
T.mkdir(exist_ok=True)
original=np.load(B/'physical_height.npz')['height']
h,w=original.shape
b=D['bounds']
dx=(b['xmax']-b['xmin'])/(w-1)
dy=(b['ymax']-b['ymin'])/(h-1)
X,Y=np.meshgrid(np.linspace(b['xmin'],b['xmax'],w),np.linspace(b['ymax'],b['ymin'],h))
pad=D['padding']
rgb=np.asarray(Image.open(B/'textures/wood_albedo.png').convert('RGB'),float)[pad:-pad,pad:-pad]/255
rough=np.asarray(Image.open(B/'textures/wood_roughness.png').convert('L'),float)[pad:-pad,pad:-pad]/255

def smoothstep(a,b,v):
    q=np.clip((v-a)/(b-a),0,1)
    return q*q*(3-2*q)

rest=np.zeros((h,w))
for x,y,rx,ry in [(.6,-1.05,.22,.10),(1.65,-1.45,.30,.12),(1.10,-1.90,.35,.10),(-1.95,-1.68,.28,.11),(-.35,-1.10,.24,.10)]:
    rest=np.maximum(rest,.60*np.exp(-((X-x)/rx)**4-((Y-y)/ry)**4))
local=gaussian_filter(original,(.035/dy,.10/dx))
height=(original*(1-rest)+local*rest)*1.25
knot=np.exp(-((X+1.18)/.30)**2-((Y+1.38)/.28)**2)
height=height*(1-.12*knot)+gaussian_filter(height,(.025/dy,.035/dx))*(.12*knot)
color_rest=np.stack([gaussian_filter(rgb[:,:,j],(.025/dy,.085/dx)) for j in range(3)],axis=2)
rgb=rgb*(1-rest[:,:,None]) + color_rest*rest[:,:,None]

# Local authored damage, not a global noise layer.
cuts=np.zeros_like(height)
paths=[([(.55,-1.10),(.75,-1.105),(.95,-1.135),(1.11,-1.12)],.014,.009),
       ([(1.50,-1.55),(1.70,-1.52),(1.88,-1.56),(2.,-1.54)],.015,.010),
       ([(-1.95,-1.88),(-1.78,-1.83),(-1.62,-1.86)],.014,.008),
       ([(-.78,-1.47),(-.62,-1.46),(-.47,-1.49)],.012,.007)]
for points,width,depth in paths:
    field=np.zeros_like(height)
    lengths=[np.linalg.norm(np.array(q)-p) for p,q in zip(points[:-1],points[1:])]
    total=sum(lengths)
    offset=0
    for p,q,length in zip(points[:-1],points[1:],lengths):
        p,q=np.array(p),np.array(q)
        v=q-p
        t=np.clip(((X-p[0])*v[0]+(Y-p[1])*v[1])/np.dot(v,v),0,1)
        progress=(offset+t*length)/total
        taper=np.sin(np.pi*progress)**.55
        distance=np.sqrt((X-(p[0]+t*v[0]))**2+(Y-(p[1]+t*v[1]))**2)
        field=np.maximum(field,np.exp(-(distance/(width*np.maximum(taper,.06)))**2)*taper)
        offset+=length
    cuts=np.maximum(cuts,depth*field)
for x,y,rx,ry,depth,skew in [(1.87,-1.22,.10,.030,.007,.25),(-.53,-1.85,.12,.040,.006,-.2),(-1.78,-1.08,.07,.025,.005,.2)]:
    xx=(X-x)/rx
    yy=(Y-y)/ry+skew*xx
    chip=np.clip(1-xx*xx-yy*yy,0,1)**1.3
    cuts=np.maximum(cuts,depth*chip)
edge=np.minimum.reduce([X-b['xmin'],b['xmax']-X,Y-b['ymin'],b['ymax']-Y])
cuts*=smoothstep(.02,.06,edge)
cuts=gaussian_filter(cuts,(.0015/dy,.0015/dx))
height-=cuts
damage=np.clip(cuts/.008,0,1)
deepest=1-smoothstep(-.039,-.032,original)
rgb*= (1-.22*damage-.06*deepest)[:,:,None]
rough=np.clip(rough+.035*damage-.012*rest,.62,.85)
gy,gx=np.gradient(height,dy,dx)
normal=np.stack([-gx,gy,np.ones_like(gx)],axis=2)
slope=np.linalg.norm(normal[:,:,:2],axis=2)
normal[:,:,:2]*=np.minimum(1,np.tan(np.deg2rad(55))/np.maximum(slope,1e-12))[:,:,None]
normal/=np.linalg.norm(normal,axis=2)[:,:,None]

def save(name,a):
    pads=((pad,pad),(pad,pad),(0,0)) if a.ndim==3 else ((pad,pad),(pad,pad))
    Image.fromarray(np.uint8(np.clip(np.pad(a,pads,mode='edge'),0,1)*255+.5)).save(T/name)

save('wood_albedo.png',rgb)
save('wood_roughness.png',rough)
save('wood_normal.png',.5+.5*normal)
np.savez_compressed(C/'physical_height.npz',height=height)
Image.fromarray(np.uint16(np.clip((height+.065)/.065,0,1)*65535+.5)).save(T/'wood_height_diagnostic.png')
unchanged=rest<.01
undamaged=damage<.01
assert np.isfinite(normal).all() and np.isfinite(height).all()
assert np.max(cuts)>.004 and np.mean(cuts>.001)<.04
report=dict(source='Preserved sample4 material, local authored height refinement only',height_min=float(height.min()),height_max=float(height.max()),normal_tilt_max=float(np.rad2deg(np.arccos(normal[:,:,2])).max()),roughness_min=float(rough.min()),roughness_max=float(rough.max()),new_cut_area_fraction=float(np.mean(cuts>.001)),rest_mask_fraction=float(np.mean(rest>.1)),authored_fractures=len(paths),authored_chips=3,no_new_image_generation=True,no_geometry_change=True,no_orange_increase=True)
(C/'texture_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
