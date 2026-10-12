"""Reference divided by measured app lighting, with a full RGB AgX inverse.
The copper reference is chromatic, so the silver solver's scalar inverse is
replaced with a bounded 3x3 Newton solve seeded by the actual AgX color gamut.
"""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, distance_transform_edt, gaussian_filter, binary_erosion
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'silver2_metal_claude'))
from agx import agx
SIZE=1024
M=json.loads((ROOT/'source/mapping.json').read_text())
def read(p):return np.asarray(Image.open(p).convert('RGB'),float)/255
def sample(a,x,y):return np.stack([map_coordinates(a[...,k],[y,x],order=1,mode='nearest') for k in range(3)],-1)
def srgb(v):return np.where(v<=.0031308,v*12.92,1.055*np.maximum(v,0)**(1/2.4)-.055)
def encode(v):return np.uint8(np.clip(srgb(v),0,1)*255+.5)
def inv_agx(target):
    """Color-coupled, log-linear Newton iteration, including out-of-gamut projection."""
    q=np.linspace(-9,3.5,48)
    seed=np.stack(np.meshgrid(q,q,q,indexing='ij'),-1).reshape(-1,3)
    disp=agx(np.exp2(seed));tree=cKDTree(disp)
    _, idx=tree.query(target,workers=-1);v=seed[idx].copy()
    for step in range(8):
        obs=agx(np.exp2(v));err=target-obs
        jac=np.empty((*v.shape[:-1],3,3))
        for c in range(3):
            w=v.copy();w[:,c]+=.025;jac[:,:,c]=(agx(np.exp2(w))-obs)/.025
        # Damp near clipping, where an exact inverse does not exist.
        jt=np.swapaxes(jac,-1,-2);a=jt@jac+np.eye(3)*2e-5;b=np.einsum('nij,nj->ni',jt,err)
        delta=np.linalg.solve(a,b);delta=np.clip(delta,-.65,.65)
        v=np.clip(v+delta,-14,3.5)
    return np.exp2(v)
def to_screen(p):
    camera=np.array([0.,1.8,23.]);forward=np.array([0.,-.55,0.])-camera;forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    d=p-camera;depth=d@forward
    master=np.stack([540+2250*(d@right)/depth,720-2250*(d@up)/depth],-1)
    return master*(47/60)+np.array([180,70])
def raster_positions():
    y,x=np.mgrid[:SIZE,:SIZE]
    rx=(x+.5)/SIZE*941;ry=(y+.5)/SIZE*1672
    wx=(rx-M['center_x'])*M['scale'];wy=-2.455+(1402-ry)*M['scale']
    z=np.zeros_like(wx);cover=np.zeros_like(wx,dtype=bool);rib=np.zeros_like(wx,dtype=np.int8)
    for k,name in enumerate(['central','right','left'],1):
        d=np.load(ROOT/'source'/f'{name}_geometry.npz');P=d['points'];F=d['faces'];roles=d['roles']
        for f in F[roles==0]:
            t=P[f];px=np.stack([(t[:,0]/M['scale']+M['center_x'])/941*SIZE-.5,(1402-(t[:,1]+2.455)/M['scale'])/1672*SIZE-.5],-1)
            low=np.maximum(np.floor(px.min(0)).astype(int),0);hi=np.minimum(np.ceil(px.max(0)).astype(int),SIZE-1)
            xx,yy=np.meshgrid(np.arange(low[0],hi[0]+1),np.arange(low[1],hi[1]+1))
            a=px[1]-px[0];b=px[2]-px[0];den=a[0]*b[1]-a[1]*b[0]
            if abs(den)<1e-8:continue
            u=((xx-px[0,0])*b[1]-(yy-px[0,1])*b[0])/den
            v=(a[0]*(yy-px[0,1])-a[1]*(xx-px[0,0]))/den
            inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1.00001)
            xx,yy=xx[inside],yy[inside];u,v=u[inside],v[inside]
            z[yy,xx]=(1-u-v)*t[0,2]+u*t[1,2]+v*t[2,2];cover[yy,xx]=True;rib[yy,xx]=k
    return rx,ry,wx,wy,z,cover,rib
out=ROOT/sys.argv[1];out.mkdir(parents=True,exist_ok=True);(out/'textures').mkdir(exist_ok=True)
rx,ry,wx,wy,z,cover,rib=raster_positions()
ref=read(ROOT/'source/reference.png');calib=read(ROOT/'source/calibration/app.png');idim=read(ROOT/'source/coverage/app.png')
pos=np.stack([wx,wy,z],-1);scr=to_screen(pos.reshape(-1,3)).reshape(SIZE,SIZE,2)
light=np.zeros((SIZE,SIZE,3))
for k,ch in [(1,0),(2,1),(3,2)]:
    # Fully covered pixels only; extend through the antialiased border.
    mask=(idim[...,ch]-np.max(np.delete(idim,ch,axis=-1),axis=-1)>.15)
    mask=binary_erosion(mask,iterations=1)
    points=calib[mask];print('Inverse calibration',k,len(points),flush=True)
    inv=inv_agx(points)/.12
    field=np.zeros_like(calib);field[mask]=inv
    _,(iy,ix)=distance_transform_edt(~mask,return_indices=True);field=field[iy,ix]
    # Subpixel smoothing prevents texture compensation from amplifying raster noise.
    field=gaussian_filter(field,[.7,.7,0])
    values=sample(field,scr[...,0]-.5,scr[...,1]-.5);light[rib==k]=values[rib==k]
# Extend the reference inside the true silhouette so the background cannot
# darken the edge through filtering. Keep the narrow luminous crest itself.
mask=binary_erosion(ref.max(-1)>.12,iterations=1)
_,(iy,ix)=distance_transform_edt(~mask,return_indices=True)
extended=ref[iy,ix]
final_pass=len(sys.argv)>2 and sys.argv[2].endswith('/02')
fine_sigma=.55 if final_pass else 1.4
fine=gaussian_filter(extended,[fine_sigma,fine_sigma,0]);plain=gaussian_filter(extended,[9.,5.,0])
height=(1402-ry)/(1402-214)
fade=np.clip((height-.19)/(.44-.19),0,1);fade=fade*fade*(3-2*fade)
target_fine=sample(fine,rx,ry);target_plain=sample(plain,rx,ry)
target=target_plain*(1-fade[...,None])+target_fine*fade[...,None]
# A soft shoulder retains cream highlights while reducing the app's glow.
knee,slope=(.85,.65) if final_pass else (.82,.55)
target=np.where(target>knee,knee+(target-knee)*slope,target)
print('Inverse target',int(cover.sum()),flush=True)
total=np.zeros_like(target);total[cover]=inv_agx(target[cover])
gamut_err=np.abs(agx(total[cover])-target[cover])*255
if len(sys.argv)>2:
    prev=ROOT/sys.argv[2];obs=sample(read(prev/'app.png'),scr[...,0]-.5,scr[...,1]-.5)
    prevtotal=np.load(prev/'total.npy');desired=total[cover];actual=inv_agx(obs[cover])
    total[cover]=prevtotal[cover]*np.clip(desired/np.maximum(actual,1e-4),.6,1.7)
    total=gaussian_filter(total,[.6,.6,0])
alb=np.clip(total/np.maximum(light,1e-5),.004,1.0)
emissive_scale=3.0 if final_pass else 2.0
emis=np.clip(total-alb*light,0,emissive_scale)
_,(iy,ix)=distance_transform_edt(~cover,return_indices=True)
alb=alb[iy,ix];emis=emis[iy,ix]
Image.fromarray(encode(alb)).save(out/'textures/copper_color.png',optimize=True)
Image.fromarray(encode(emis/emissive_scale)).save(out/'textures/copper_emissive.png',optimize=True)
np.save(out/'total.npy',total)
np.savez_compressed(ROOT/'source/texture_mapping.npz',positions=pos,screen=scr,cover=cover,ribbon=rib,target=target,light=light)
report=dict(solved_texels=int(cover.sum()),fine_reference_sigma=fine_sigma,highlight_knee=knee,highlight_slope=slope,gamut_mean_error_rgb=gamut_err.mean(0).tolist(),gamut_p95_error=float(np.percentile(gamut_err,95)),emissive_scale=emissive_scale,emissive_mean=emis[cover].mean(0).tolist(),emissive_max=emis[cover].max(0).tolist(),emissive_clipped_fraction=float(((total-alb*light)[cover]>emissive_scale).any(-1).mean()))
(out/'solve.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'settings.json').write_text(json.dumps({'color':[.61,.255,.115],'roughness':.34,'textures':{'diffuseColor':'copper_color.png','emissiveColor':'copper_emissive.png'},'emissive_scale':emissive_scale,'master':True},indent=2)+'\n')
print(json.dumps(report,indent=2))
