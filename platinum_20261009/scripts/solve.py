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
def raster_facets(BASE,M):
    rx=np.zeros((SIZE,SIZE));ry=rx.copy();pos=np.zeros((SIZE,SIZE,3));cover=np.zeros((SIZE,SIZE),bool)
    frame=Image.new('L',(1206,2622),0);draw=ImageDraw.Draw(frame)
    d=np.load(BASE/'source/DiamondCrystal_CutFacets.npz');p=d['points'];f=d['faces'];uv=d['face_uv'];offset=np.array(M['world_offset'])
    for tri in f:draw.polygon([tuple(v) for v in to_screen(p[tri])],fill=255)
    for i in np.where(d['roles']==0)[0]:
        q=np.stack([uv[i,:,0]*SIZE-.5,(1-uv[i,:,1])*SIZE-.5],-1);lo=np.maximum(np.floor(q.min(0)).astype(int),0);hi=np.minimum(np.ceil(q.max(0)).astype(int),SIZE-1)
        x,y=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));a=q[1]-q[0];b=q[2]-q[0];den=a[0]*b[1]-a[1]*b[0]
        u=((x-q[0,0])*b[1]-(y-q[0,1])*b[0])/den;v=(a[0]*(y-q[0,1])-a[1]*(x-q[0,0]))/den;inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1.00001)
        x,y,u,v=x[inside],y[inside],u[inside],v[inside];world=(1-u-v)[:,None]*p[f[i,0]]+u[:,None]*p[f[i,1]]+v[:,None]*p[f[i,2]]
        original=world-offset;planeX=original[:,0]*23/(23-original[:,2]);planeY=1.8+(original[:,1]-1.8)*23/(23-original[:,2])
        rx[y,x]=planeX/M['scale']+M['center_x'];ry[y,x]=M['reference_bottom']-(planeY+2.455)/M['scale'];pos[y,x]=world;cover[y,x]=True
    return rx,ry,pos,cover,np.asarray(frame)>0
def extend_facet_light(light,cover,scr,BASE,M):
    d=np.load(BASE/'source/DiamondCrystal_CutFacets.npz')
    for rec in M['atlas_faces']:
        x,y,w,h=rec['rect'];points=to_screen(d['points'][d['faces'][rec['face']]]);s=scr[y:y+h,x:x+w];inside=cover[y:y+h,x:x+w];dist=[]
        for j,a in enumerate(points):
            b=points[(j+1)%3];edge=b-a;dist.append(np.abs(edge[0]*(s[...,1]-a[1])-edge[1]*(s[...,0]-a[0]))/np.linalg.norm(edge))
        safe=inside&(np.min(dist,axis=0)>=1.6)
        if not safe.any():continue
        _,(iy,ix)=distance_transform_edt(~safe,return_indices=True);patch=light[y:y+h,x:x+w];border=inside&~safe;patch[border]=patch[iy,ix][border]
    return light
def raster(BASE,M):
    if M.get('atlas')=='per_face':return raster_facets(BASE,M)
    yy,xx=np.mgrid[:SIZE,:SIZE];rx=(xx+.5)/SIZE*M['image_size'][0];ry=(yy+.5)/SIZE*M['image_size'][1]
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
    offset=np.array(M.get('world_offset',[0,0,0]));originalz=z-offset[2]
    wx=wx*(1-originalz/23)+offset[0];wy=1.8+(wy-1.8)*(1-originalz/23)+offset[1]
    return rx,ry,np.stack([wx,wy,z],-1),cover,np.asarray(frame)>0
if __name__=='__main__':
    kind,folder=sys.argv[1:3];BASE=ROOT/kind;OUT=BASE/folder;OUT.mkdir(parents=True,exist_ok=True);(OUT/'textures').mkdir(exist_ok=True)
    M=json.loads((BASE/'source/mapping.json').read_text());rx,ry,pos,cover,mask=raster(BASE,M)
    scr=to_screen(pos.reshape(-1,3)).reshape(SIZE,SIZE,2);calib=read(BASE/'source/calibration/app.png');ref=read(BASE/'source/reference.png')
    mask=binary_erosion(mask,iterations=2);valid=mask&(calib.max(-1)<.98)
    linear=np.zeros_like(calib);linear[valid]=inv_agx(calib[valid])/.12
    _,(iy,ix)=distance_transform_edt(~valid,return_indices=True);linear=gaussian_filter(linear[iy,ix],[.45,.45,0]);light=sample(linear,scr[...,0]-.5,scr[...,1]-.5)
    inside=ref.max(-1)>.07;_,(iy,ix)=distance_transform_edt(~inside,return_indices=True);ext=ref[iy,ix]
    fine=gaussian_filter(ext,[.65,.65,0]);sigma=1.8;plain=gaussian_filter(ext,[sigma,sigma,0])
    height=(M['reference_bottom']-ry)/(M['reference_bottom']-M['reference_top']);fade=np.clip((height-.19)/(.44-.19),0,1);fade=fade**2*(3-2*fade)
    target=sample(fine,rx,ry)*fade[...,None]+sample(plain,rx,ry)*(1-fade[...,None])
    target=np.where(target>.84,.84+(target-.84)*.65,target)
    total=np.zeros_like(target);print('Solving',kind,int(cover.sum()),flush=True);total[cover]=inv_agx(target[cover])
    if len(sys.argv)>3:
        prev=BASE/sys.argv[3];obs=sample(read(prev/'app.png'),scr[...,0]-.5,scr[...,1]-.5)
        # Measure the effective light again from known albedo and emission.
        # This also handles changed ray normals without assuming proportional
        # response across the point where albedo reaches one and emission starts.
        previous_cfg=json.loads((prev/'settings.json').read_text());previous_albedo=decode(read(prev/'textures/color.png'))
        previous_scale=json.loads((prev/'settings.json').read_text()).get('emissive_scale',3.)
        previous_emission=decode(read(prev/'textures/emissive.png'))*previous_scale
        oldcover=np.load(prev/'texture_mapping.npz')['cover']
        if M.get('atlas')=='per_face' and previous_cfg.get('atlas')!='per_face':
            xx=rx/1254*SIZE-.5;yy=ry/1254*SIZE-.5
            previous_albedo=sample(previous_albedo,xx,yy);previous_emission=sample(previous_emission,xx,yy);oldcover=map_coordinates(oldcover.astype(float),[yy,xx],order=0,mode='nearest')>.5
        actual=inv_agx(obs[cover]);measured=(actual-previous_emission[cover])/np.maximum(previous_albedo[cover],.003)
        valid_old=oldcover[cover]
        values=light[cover];values[valid_old]=np.maximum(measured[valid_old],1e-5);light[cover]=values
    if M.get('atlas')=='per_face':light=extend_facet_light(light,cover,scr,BASE,M)
    emission_scale=6. if kind=='diamond' else 3.
    # Saturated gold and blue need channels below the old 0.003 floor.
    # A positive floor leaves pale gold and colored dots under strong specular light.
    alb=np.clip(total/np.maximum(light,1e-5),0.,1.);emission=np.clip(total-alb*light,0,emission_scale)
    _,(iy,ix)=distance_transform_edt(~cover,return_indices=True);alb=alb[iy,ix];emission=emission[iy,ix]
    Image.fromarray(encode(alb)).save(OUT/'textures/color.png',optimize=True);Image.fromarray(encode(emission/emission_scale)).save(OUT/'textures/emissive.png',optimize=True)
    np.savez_compressed(OUT/'total.npz',total=total)
    np.savez_compressed(OUT/'texture_mapping.npz',positions=pos,screen=scr,cover=cover,target=target,light=light,screen_mask=mask)
    settings={'color':[.45,.49,.56],'roughness':M['roughness'],'textures':{'diffuseColor':'color.png','emissiveColor':'emissive.png'},'emissive_scale':emission_scale,'master':True}
    if M.get('atlas'):settings['atlas']=M['atlas']
    (OUT/'settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    report={'solved_texels':int(cover.sum()),'emission_clipped_fraction':float(((total-alb*light)[cover]>emission_scale).any(-1).mean()),'reference_sigma':.65,'texture_size':SIZE,'refine_from':sys.argv[3] if len(sys.argv)>3 else None}
    (OUT/'solve.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
