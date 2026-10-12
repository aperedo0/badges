"""Measure actual app lighting and solve reference color + emission for each texel."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt,binary_erosion
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from agx import agx
SIZE=1024
def inv_agx(target):
    q=np.linspace(-10,3.7,48);seed=np.stack(np.meshgrid(q,q,q,indexing='ij'),-1).reshape(-1,3);tree=cKDTree(agx(np.exp2(seed)))
    _,idx=tree.query(target,workers=-1);v=seed[idx].copy()
    for _ in range(8):
        obs=agx(np.exp2(v));err=target-obs;jac=np.empty((len(v),3,3))
        for c in range(3):
            w=v.copy();w[:,c]+=.025;jac[:,:,c]=(agx(np.exp2(w))-obs)/.025
        jt=np.swapaxes(jac,-1,-2);a=jt@jac+np.eye(3)*2e-5;b=np.einsum('nij,nj->ni',jt,err)
        delta=np.linalg.solve(a,b);v=np.clip(v+np.clip(delta,-.65,.65),-14,3.7)
    return np.exp2(v)
def to_screen(p):
    camera=np.array([0.,1.8,23.]);f=np.array([0.,-.55,0])-camera;f/=np.linalg.norm(f);r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f);d=p-camera;depth=d@f
    return np.stack([540+2250*(d@r)/depth,720-2250*(d@u)/depth],-1)*47/60+[180,70]
def read(p):return np.asarray(Image.open(p).convert('RGB'),float)/255
def sample(a,x,y):return np.stack([map_coordinates(a[...,c],[y,x],order=1,mode='nearest') for c in range(3)],-1)
def encode(a):
    a=np.clip(a,0,1);a=np.where(a<=.0031308,a*12.92,1.055*a**(1/2.4)-.055);return np.uint8(a*255+.5)
def decode(a):
    return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def raster(BASE,M):
    yy,xx=np.mgrid[:SIZE,:SIZE];rx=(xx+.5)/SIZE*1254;ry=(yy+.5)/SIZE*1254
    wx=(rx-M['center_x'])*M['scale'];wy=-2.455+(M['reference_bottom']-ry)*M['scale'];z=np.full((SIZE,SIZE),-1e6)
    frame=Image.new('L',(1206,2622),0);draw=ImageDraw.Draw(frame)
    for record in M['meshes']:
        d=np.load(BASE/'source'/f"{record['name']}.npz");p=d['points'];f=d['faces'];uv=d['uv'];role=d['roles']
        screen=to_screen(p)
        for tri in f:
            draw.polygon([tuple(v) for v in screen[tri]],fill=255)
        for tri in f[role==0]:
            pts=p[tri];pixel=np.stack([uv[tri,0]*SIZE-.5,(1-uv[tri,1])*SIZE-.5],-1)
            lo=np.maximum(np.floor(pixel.min(0)).astype(int),0);hi=np.minimum(np.ceil(pixel.max(0)).astype(int),SIZE-1)
            x,y=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
            a=pixel[1]-pixel[0];b=pixel[2]-pixel[0];den=a[0]*b[1]-a[1]*b[0]
            if abs(den)<1e-9:continue
            u=((x-pixel[0,0])*b[1]-(y-pixel[0,1])*b[0])/den;v=(a[0]*(y-pixel[0,1])-a[1]*(x-pixel[0,0]))/den
            inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1.00001);x,y=x[inside],y[inside];u,v=u[inside],v[inside]
            zz=(1-u-v)*pts[0,2]+u*pts[1,2]+v*pts[2,2];z[y,x]=np.maximum(z[y,x],zz)
    cover=z>-1e5;z[~cover]=0
    return rx,ry,np.stack([wx,wy,z],-1),cover,np.asarray(frame)>0
if __name__=='__main__':
    kind,folder=sys.argv[1:3];BASE=ROOT/kind;OUT=BASE/folder;OUT.mkdir(parents=True,exist_ok=True);(OUT/'textures').mkdir(exist_ok=True)
    M=json.loads((BASE/'source/mapping.json').read_text());rx,ry,pos,cover,mask=raster(BASE,M)
    scr=to_screen(pos.reshape(-1,3)).reshape(SIZE,SIZE,2);calib=read(BASE/'source/calibration/app.png');ref=read(BASE/'source/reference.png')
    mask=binary_erosion(mask,iterations=2);valid=mask&(calib.max(-1)<.98)
    linear=np.zeros_like(calib);linear[valid]=inv_agx(calib[valid])/.12
    _,(iy,ix)=distance_transform_edt(~valid,return_indices=True);linear=gaussian_filter(linear[iy,ix],[.45,.45,0]);light=sample(linear,scr[...,0]-.5,scr[...,1]-.5)
    inside=ref.max(-1)>.07;_,(iy,ix)=distance_transform_edt(~inside,return_indices=True);ext=ref[iy,ix]
    fine=gaussian_filter(ext,[.8,.8,0]);plain=gaussian_filter(ext,[6.,6.,0])
    height=(M['reference_bottom']-ry)/(M['reference_bottom']-M['reference_top']);fade=np.clip((height-.19)/(.44-.19),0,1);fade=fade**2*(3-2*fade)
    target=sample(fine,rx,ry)*fade[...,None]+sample(plain,rx,ry)*(1-fade[...,None])
    target=np.where(target>.84,.84+(target-.84)*.65,target)
    total=np.zeros_like(target);print('Solving',kind,int(cover.sum()),flush=True);total[cover]=inv_agx(target[cover])
    if len(sys.argv)>3:
        prev=BASE/sys.argv[3];obs=sample(read(prev/'app.png'),scr[...,0]-.5,scr[...,1]-.5)
        # Measure the effective light again from known albedo and emission.
        # This also handles changed ray normals without assuming proportional
        # response across the point where albedo reaches one and emission starts.
        previous_albedo=decode(read(prev/'textures/color.png'))
        previous_emission=decode(read(prev/'textures/emissive.png'))*3.
        actual=inv_agx(obs[cover]);measured=(actual-previous_emission[cover])/np.maximum(previous_albedo[cover],.003)
        light[cover]=np.maximum(measured,1e-5)
    alb=np.clip(total/np.maximum(light,1e-5),.003,1.);emission=np.clip(total-alb*light,0,3.)
    _,(iy,ix)=distance_transform_edt(~cover,return_indices=True);alb=alb[iy,ix];emission=emission[iy,ix]
    Image.fromarray(encode(alb)).save(OUT/'textures/color.png',optimize=True);Image.fromarray(encode(emission/3.)).save(OUT/'textures/emissive.png',optimize=True)
    np.savez_compressed(OUT/'total.npz',total=total)
    np.savez_compressed(OUT/'texture_mapping.npz',positions=pos,screen=scr,cover=cover,target=target,light=light,screen_mask=mask)
    settings={'color':[.50,.27,.09] if kind=='bronze' else [.45,.46,.48],'roughness':.38,'textures':{'diffuseColor':'color.png','emissiveColor':'emissive.png'},'emissive_scale':3.,'master':True}
    if kind=='bronze':settings['channel_color']=[.035,.009,.002]
    (OUT/'settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    report={'solved_texels':int(cover.sum()),'emission_clipped_fraction':float(((total-alb*light)[cover]>3).any(-1).mean()),'reference_sigma':.8,'texture_size':SIZE,'refine_from':sys.argv[3] if len(sys.argv)>3 else None}
    (OUT/'solve.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
