"""Measure Home lighting and solve the relief's color, with edge-safe targets."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'silver2_metal_claude'))
from agx import agx,agx_inv,refine
SIZE=512
CAM_POS=np.array([0.,1.8,23.]);TARGET=np.array([0.,-.55,0.])
F=TARGET-CAM_POS;F/=np.linalg.norm(F);R=np.cross(F,[0,1,0]);R/=np.linalg.norm(R);U=np.cross(R,F)

def project(points):
    p=np.asarray(points)*.96+np.array([0,-2.895*.04,0])
    d=p-CAM_POS;depth=d@F
    master=np.stack([540+2250*(d@R)/depth,720-2250*(d@U)/depth],-1)
    return master*47/60+np.array([180,70])

def sample(im,x,y):
    return np.stack([map_coordinates(im[...,c],[y,x],order=1,mode='nearest') for c in range(3)],-1)

def encode(v):
    v=np.clip(v,0,1);v=np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)
    return np.uint8(v*255+.5)

def decode_image(path):
    v=np.asarray(Image.open(path).convert('RGB'),float)/255
    return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)

def inverse(target):
    """Coupled log-RGB inverse. Neutral-axis corrections diverge on cyan/gold."""
    lin=np.clip(agx_inv(target),2**-12,64.)
    best=lin.copy();best_error=np.full(target.shape[:-1],np.inf)
    for _ in range(16):
        value=agx(lin);error=target-value
        cost=(error*error).sum(-1)
        better=cost<best_error;best[better]=lin[better];best_error=np.minimum(cost,best_error)
        jacobian=np.empty(lin.shape[:-1]+(3,3))
        for c in range(3):
            changed=lin.copy();changed[...,c]*=1.035
            jacobian[...,c]=(agx(changed)-value)/np.log(1.035)
        lhs=np.einsum('...ji,...jk->...ik',jacobian,jacobian)+np.eye(3)*.00003
        rhs=np.einsum('...ji,...j->...i',jacobian,error)
        delta=np.linalg.solve(lhs,rhs)
        lin=np.clip(lin*np.exp(np.clip(delta,-.7,.7)),2**-12,64.)
    return best

def solve(name,feedback=None):
    base=ROOT/name
    design=json.loads((base/'design.json').read_text())
    geometry=json.loads((base/'front_geometry.json').read_text())
    shot=feedback or name+'_calibration'
    calib=np.asarray(Image.open('/tmp/achievement_coins_20261014/'+shot+'.png').convert('RGB'),float)/255
    ref=np.asarray(Image.open(design['reference']).convert('RGB'),float)/255
    sigma=6. if name=='sunrise' else 3. if name.startswith('hourglass') else 1.2
    ref=gaussian_filter(ref,(sigma,sigma,0))
    cover=np.zeros((SIZE,SIZE),bool);pos=np.zeros((SIZE,SIZE,3));roles=np.full((SIZE,SIZE),-1,np.int16)
    role_names=[]
    # Rasterize the topmost actual surface into its planar UV atlas.
    for group in geometry:
        if group['role'] not in role_names:role_names.append(group['role'])
        role=role_names.index(group['role'])
        for tri,uv in zip(np.asarray(group['points']),np.asarray(group['uv'])):
            px=np.stack([uv[:,0]*SIZE-.5,(1-uv[:,1])*SIZE-.5],-1)
            lo=np.maximum(np.floor(px.min(0)).astype(int),0);hi=np.minimum(np.ceil(px.max(0)).astype(int),SIZE-1)
            gx,gy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
            e1,e2=px[1]-px[0],px[2]-px[0];den=e1[0]*e2[1]-e1[1]*e2[0]
            if abs(den)<1e-10:continue
            a=((gx-px[0,0])*e2[1]-(gy-px[0,1])*e2[0])/den
            b=(e1[0]*(gy-px[0,1])-e1[1]*(gx-px[0,0]))/den
            inside=(a>=-1e-4)&(b>=-1e-4)&(a+b<=1.0001)
            if not inside.any():continue
            x,y=gx[inside],gy[inside]
            p=(1-a[inside]-b[inside])[:,None]*tri[0]+a[inside,None]*tri[1]+b[inside,None]*tri[2]
            keep=(~cover[y,x])|(p[:,2]>=pos[y,x,2])
            x,y,p=x[keep],y[keep],p[keep]
            pos[y,x]=p;cover[y,x]=True;roles[y,x]=role
    positions=pos[cover];screen=project(positions)
    obs=sample(calib,screen[:,0]-.5,screen[:,1]-.5)
    if feedback:
        assert name!='clean','Feedback fitting needs color-driven metallic returns.'
        old_color=decode_image(base/'pkg/textures/Relief_color.png')[cover]
        old_emission=decode_image(base/'pkg/textures/Relief_emission.png')[cover]
        light=np.clip((inverse(obs)-old_emission)/np.maximum(old_color,1e-6),.03,2000.)
    else:light=np.clip((agx_inv(obs) if name=='clean' else inverse(obs))/.15,.03,80.)
    cx,cy,r=design['circle'];rx=cx+positions[:,0]*r/3.015;ry=cy-positions[:,1]*r/3.015
    target=sample(ref,rx,ry)
    target=np.where(target>.82,.82+(target-.82)*.45,target)
    # Never solve a reference's hairline highlight onto a thin silhouette.
    target_full=np.zeros((SIZE,SIZE,3));target_full[cover]=target
    light_full=np.ones((SIZE,SIZE,3));light_full[cover]=light
    for rid,role in enumerate(role_names):
        mask=roles==rid;distance=distance_transform_edt(mask)
        threshold=min(5,float(distance.max())*.65)
        inside=mask&(distance>=threshold)
        if inside.sum()<16:continue
        _,(iy,ix)=distance_transform_edt(~inside,return_indices=True)
        edge=mask&(distance<5)
        source=target_full[iy,ix]
        # Harmonic continuation approximated by normalized Gaussian extension.
        w=gaussian_filter(inside.astype(float),3)
        continuation=np.stack([gaussian_filter(target_full[...,c]*inside,3)/np.maximum(w,1e-6) for c in range(3)],-1)
        good=w>.01
        target_full[edge]=np.where(good[edge,None],continuation[edge],source[edge])
        light_full[edge]=light_full[iy[edge],ix[edge]]
    target=target_full[cover];light=light_full[cover]
    total=inverse(target)
    albedo=np.clip(total/light,.002 if name=='clean' else 1e-6,1.)
    emission=np.clip(total-albedo*light,0,1.)
    color=np.zeros((SIZE,SIZE,3));glow=np.zeros_like(color)
    color[cover]=albedo;glow[cover]=emission
    # Fill beyond the outer disk so no mip level introduces a dark stroke.
    _,(iy,ix)=distance_transform_edt(~cover,return_indices=True)
    color=color[iy,ix];glow=glow[iy,ix]
    pkg=base/'pkg';(pkg/'textures').mkdir(parents=True,exist_ok=True)
    Image.fromarray(encode(color)).save(pkg/'textures/Relief_color.png')
    Image.fromarray(encode(glow)).save(pkg/'textures/Relief_emission.png')
    np.savez_compressed(base/'solve_state.npz',positions=pos,cover=cover,roles=roles,color=color,emission=glow,target=target_full,light=light_full)
    print(name,'solved',int(cover.sum()),'texels; mean emission',np.round(emission.mean(0),3),flush=True)

if __name__=='__main__':
    for name in sys.argv[1:]:solve(name)
