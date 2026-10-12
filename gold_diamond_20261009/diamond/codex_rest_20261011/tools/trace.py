"""Read-only numerical reproduction of the shader's resting rays for diagnosis."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[1]
MODEL=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'baseline_model/gem_planes.npz'
LABEL=(sys.argv[3]+'_') if len(sys.argv)>3 else ''
data = np.load(MODEL)
normals = data['normals'].astype(np.float16).astype(float)
offsets = data['offsets'].astype(np.float16).astype(float)
environment = np.load(ROOT/'diagnostics/environment.npy')
mips = [environment]
while min(mips[-1].shape[:2]) > 1:
    p = mips[-1]
    mips.append((p[::2,::2]+p[1::2,::2]+p[::2,1::2]+p[1::2,1::2])/4)

def normalize(a):
    return a / np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-12)

def refract(d,n,index):
    dot = (d*n).sum(-1)
    k = 1-index*index*(1-dot*dot)
    return np.where((k>=0)[:,None],index*d-(index*dot+np.sqrt(np.maximum(k,0)))[:,None]*n,0)

def fresnel(c, a, b):
    sine = (a/b)**2*(1-c*c)
    transmitted = np.sqrt(np.maximum(0,1-sine))
    perpendicular=(a*c-b*transmitted)/np.maximum(a*c+b*transmitted,1e-12)
    parallel=(a*transmitted-b*c)/np.maximum(a*transmitted+b*c,1e-12)
    return np.where(sine>=1,1,(perpendicular**2+parallel**2)/2)

def lookup(direction,level):
    # The stage rotates model and camera by pi around Y. These are the actual
    # world-space lookup coordinates used by lightMapPosition in Metal.
    world=direction*np.array([-1,1,-1])
    uv=np.column_stack((.5+np.arctan2(world[:,0],-world[:,2])/(2*np.pi),.5-np.arcsin(np.clip(world[:,1],-1,1))/np.pi))
    image=mips[level]
    xy=np.array([np.clip(uv[:,1]*image.shape[0]-.5,0,image.shape[0]-1),(uv[:,0]*image.shape[1]-.5)%image.shape[1]])
    return np.column_stack([map_coordinates(image[:,:,c],xy,order=1,mode='wrap') for c in range(3)]),uv

def light(d):
    sharp,uv=lookup(d,1);tent,_=lookup(d,7)
    return np.minimum(sharp,24)+np.minimum(tent,3)*2.2,uv

# One ray every two master pixels, with the app's exact fixed camera.
x,y=np.meshgrid(np.arange(210,871,2),np.arange(340,941,2))
camera=np.array([0,1.8,23.]);forward=normalize(np.array([0,-.55,0])-camera)
right=normalize(np.cross(forward,[0,1,0]));up=np.cross(right,forward)
directions=normalize(forward+(x.ravel()-540)[:,None]/2250*right-(y.ravel()-720)[:,None]/2250*up)
approach=directions@normals.T;gap=offsets-camera@normals.T
with np.errstate(divide='ignore',invalid='ignore'):
    distances=gap/approach
entry_dist=np.max(np.where(approach<0,distances,-np.inf),axis=1)
exit_dist=np.min(np.where(approach>0,distances,np.inf),axis=1)
valid=(entry_dist<=exit_dist)&(entry_dist>0)
indices=np.flatnonzero(valid);entry_plane=np.argmax(np.where(approach<0,distances,-np.inf),axis=1)[valid]
position=camera+directions[valid]*entry_dist[valid,None];incident=directions[valid];normal=normalize(normals[entry_plane])
surface=fresnel(-(normal*incident).sum(-1),1,2.423)
reflection=incident-2*(incident*normal).sum(-1)[:,None]*normal
surface_color=surface[:,None]*np.minimum(lookup(reflection,1)[0],24)
direction=refract(incident,normal,1/2.423);weight=np.repeat((1-surface)[:,None],3,axis=1)
unabsorbed=weight.copy();collected=np.zeros_like(weight);without_absorption=np.zeros_like(weight)
true_light=np.zeros_like(weight);true_weights=np.zeros_like(weight);path=np.zeros(len(weight));events=[]
history=[]
center_mask=(np.abs(x.ravel()[valid]-540)<85)&(y.ravel()[valid]>605)&(y.ravel()[valid]<780)
wing_mask=(np.abs(x.ravel()[valid]-540)>110)&(y.ravel()[valid]>605)&(y.ravel()[valid]<780)
for hit in range(int(sys.argv[1]) if len(sys.argv)>1 else 3):
    approach=direction@normals.T;gap=offsets-position@normals.T
    with np.errstate(divide='ignore',invalid='ignore'):
        distance=np.where((approach>1e-4)&(gap>=-.004),np.maximum(gap,0)/approach,np.inf)
    facet=distance.argmin(1);travel=distance[np.arange(len(weight)),facet]
    found=np.isfinite(travel);travel=np.where(found,travel,0)
    position+=direction*travel[:,None];path+=travel
    weight*=np.exp(-travel[:,None]*[.34,.16,.035])
    normal=normals[facet];f=fresnel((direction*normal).sum(-1),2.423,1)
    exiting=(f<1)&found
    green=refract(direction,-normal,2.423)
    colors=[]
    for c,index in enumerate([2.38,2.423,2.47]):
        bent=refract(direction,-normal,index)
        bent=np.where((np.linalg.norm(bent,axis=1)>0)[:,None],bent,green)
        values,uv=light(bent);colors.append(values[:,c])
        if c==1: events.append({'hit':hit,'rays':indices[exiting],'uv':uv[exiting],'weights':(unabsorbed*(1-f)[:,None])[exiting]})
    values=np.column_stack(colors);share=weight*(1-f)[:,None]*exiting[:,None]
    plain=unabsorbed*(1-f)[:,None]*exiting[:,None]
    collected+=share*values;without_absorption+=plain*values
    true_light+=plain*values;true_weights+=plain
    weight*=f[:,None];unabsorbed*=f[:,None]
    direction-=2*(direction*normal).sum(-1)[:,None]*normal
    history.append({"hits":hit+1,"center":float((collected@np.array([.2126,.7152,.0722]))[center_mask].mean()),"wings":float((collected@np.array([.2126,.7152,.0722]))[wing_mask].mean()),"center_no_abs":float((without_absorption@np.array([.2126,.7152,.0722]))[center_mask].mean()),"wings_no_abs":float((without_absorption@np.array([.2126,.7152,.0722]))[wing_mask].mean())})
fallback,uv=light(direction);residual=weight*fallback
final=surface_color+collected+residual
no_abs=surface_color+without_absorption+unabsorbed*fallback

middle=((np.abs(x.ravel()[valid]-540)<85)&(y.ravel()[valid]>605)&(y.ravel()[valid]<780))
bright=((np.abs(x.ravel()[valid]-540)>110)&(y.ravel()[valid]>605)&(y.ravel()[valid]<780))
luma=lambda a:a@np.array([.2126,.7152,.0722])
stats={}
for name,mask in [('pavilion_center',middle),('pavilion_wings',bright),('whole',np.ones(len(weight),bool))]:
    stats[name]={'pixels':int(mask.sum()),'radiance':float(luma(final)[mask].mean()),'absorption_off':float(luma(no_abs)[mask].mean()),'residual_share_of_light':float(luma(residual)[mask].sum()/luma(final)[mask].sum()),'residual_green_ray_weight':float(unabsorbed[mask,1].mean()),'true_exit_green_weight':float(true_weights[mask,1].mean()),'mean_path':float(path[mask].mean()),'true_exit_radiance':float(luma(true_light/np.maximum(true_weights,1e-6))[mask].mean())}
(ROOT/('diagnostics/'+LABEL+'trace_stats_'+(sys.argv[1] if len(sys.argv)>1 else '3')+'.json')).write_text(json.dumps(stats,indent=2))
escaped_before_limit=np.zeros(len(weight),bool)
for event in events[:3]: escaped_before_limit[np.isin(indices,event['rays'])]=True
np.savez(ROOT/('diagnostics/'+LABEL+'ray_evidence_'+(sys.argv[1] if len(sys.argv)>1 else '3')+'.npz'),x=x,y=y,valid=valid,escaped_before_limit=escaped_before_limit,final=final,no_abs=no_abs,residual=residual,weight=weight,unabsorbed=unabsorbed,true_light=true_light,true_weights=true_weights,uv=uv,middle=middle)
canvas=np.clip(environment/(environment+1),0,1)
image=Image.fromarray(np.uint8(canvas**(1/2.2)*255));draw=ImageDraw.Draw(image)
for event in events:
    chosen=np.isin(event['rays'],indices[middle])&(event['weights'][:,1]>.02)
    for u,v in event['uv'][chosen][::6]:
        px,py=u*1024,v*512;draw.ellipse((px-2,py-2,px+2,py+2),fill=(255,65,20))
for u,v in uv[middle][::8]:
    px,py=u*1024,v*512;draw.ellipse((px-1,py-1,px+1,py+1),fill=(255,0,255))
image.save(ROOT/('diagnostics/'+LABEL+'center_environment_directions_'+(sys.argv[1] if len(sys.argv)>1 else '3')+'.png'))
print(json.dumps(stats,indent=2));print(json.dumps(history,indent=2))
(ROOT/"diagnostics/depth_history.json").write_text(json.dumps(history,indent=2))
