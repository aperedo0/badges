"""Pack each real flat facet into its own padded texture rectangle."""
from pathlib import Path
import json,numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'diamond';path=BASE/'source/DiamondCrystal_CutFacets.npz';d=dict(np.load(path));front=np.where(d['roles']==0)[0];xy=np.stack([d['uv'][:,0],1-d['uv'][:,1]],-1)*1024
shapes={}
for i in front:
    p=xy[d['faces'][i]];lengths=np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1);j=int(lengths.argmax());axis=(p[(j+1)%3]-p[j])/lengths[j];up=np.array([-axis[1],axis[0]]);q=np.stack([(p-p[j])@axis,(p-p[j])@up],-1);shapes[int(i)]=q-q.min(0)
def pack(scale):
    free=[(0,0,1024,1024)];places={}
    sizes={i:np.ceil(q.max(0)*scale+12).astype(int) for i,q in shapes.items()}
    for i in sorted(sizes,key=lambda i:(max(sizes[i]),np.prod(sizes[i])),reverse=True):
        w,h=sizes[i];choices=[]
        for k,(x,y,rw,rh) in enumerate(free):
            for rotated,(ww,hh) in enumerate([(w,h),(h,w)]):
                if ww<=rw and hh<=rh:choices.append((min(rw-ww,rh-hh),max(rw-ww,rh-hh),k,rotated,int(ww),int(hh)))
        if not choices:return None
        _,_,k,rot,w,h=min(choices);x,y,_,_=free[k];places[i]=(x,y,w,h,rot);new=[]
        for a,b,c,e in free:
            if x>=a+c or x+w<=a or y>=b+e or y+h<=b:new.append((a,b,c,e));continue
            if x>a:new.append((a,b,x-a,e))
            if x+w<a+c:new.append((x+w,b,a+c-x-w,e))
            if y>b:new.append((a,b,c,y-b))
            if y+h<b+e:new.append((a,y+h,c,b+e-y-h))
        free=[]
        for k,r in enumerate(new):
            a,b,c,e=r
            if not any(j!=k and a>=s[0] and b>=s[1] and a+c<=s[0]+s[2] and b+e<=s[1]+s[3] and (r!=s or j<k) for j,s in enumerate(new)):free.append(r)
    return places
for scale in [1.,.95,.90,.85,.80,.75,.70,.65]:
    places=pack(scale)
    if places:break
assert places
faceuv=d['uv'][d['faces']].copy();records=[]
for i,(x,y,w,h,rot) in places.items():
    q=shapes[i]*scale
    if rot:q=q[:,::-1]
    q=q+[x+6,y+6];faceuv[i]=np.stack([q[:,0]/1024,1-q[:,1]/1024],-1);records.append({'face':i,'rect':[x,y,w,h]})
d['face_uv']=faceuv;np.savez_compressed(path,**d)
M=json.loads((BASE/'source/mapping.json').read_text());M['atlas']='per_face';M['atlas_scale']=scale;M['atlas_faces']=records;(BASE/'source/mapping.json').write_text(json.dumps(M,indent=2)+'\n');print('Packed',len(front),'facets, scale',scale)
