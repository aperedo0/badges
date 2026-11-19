from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
D=Path(__file__).resolve().parent;W=D.parent;KEY=sys.argv[1];F=W/KEY
frames=np.load(F/'normal_frames.npz');oldpos=frames['old_positions'];oldnorm=frames['old_normals'];newpos=frames['positions'];newnorm=frames['normals'];full=np.load(F/'master_height.npz');delta=full['delta'].astype(np.float32);h,w=delta.shape;dx,dy=5.1/(w-1),1.3775/(h-1);XX,YY=np.meshgrid(np.linspace(-2.55,2.55,w,dtype=np.float32),np.linspace(-.84,-2.2175,h,dtype=np.float32))
def norm(v):return v/np.maximum(np.linalg.norm(v,axis=2,keepdims=True),1e-8)
def basis(pos,nv):
 yi=np.broadcast_to(np.interp(YY[:,0],pos[:,0,1],np.arange(len(pos)))[:,None],(h,w));left=np.interp(YY[:,0],pos[:,0,1],pos[:,0,0])[:,None];right=np.interp(YY[:,0],pos[:,0,1],pos[:,-1,0])[:,None];xi=(XX-left)/np.maximum(right-left,.01)*(pos.shape[1]-1);N=norm(np.stack([map_coordinates(nv[:,:,c],[yi,xi],order=1,mode='nearest') for c in range(3)],2));T=norm(np.stack([N[:,:,2],np.zeros((h,w)),-N[:,:,0]],2));B=norm(np.cross(N,T));return T,B,N
T0,B0,N0=basis(oldpos,oldnorm);T1,B1,N1=basis(newpos,newnorm);raw=np.asarray(Image.open(W/'AE_controlled_fibers/normal.png').convert('RGB').resize((4096,1536),Image.Resampling.BICUBIC));oldnormal=norm(raw[32:-32,32:-32].astype(np.float32)/127.5-1);effective=norm(T0*oldnormal[:,:,0,None]+B0*oldnormal[:,:,1,None]+N0*oldnormal[:,:,2,None]);fine=F/'fine_height.npz';detail=delta+(np.load(fine)['height'] if fine.exists() else 0);gy,gx=np.gradient(detail,dy,dx);den=np.maximum(effective[:,:,2],.05);wanted=norm(np.stack([effective[:,:,0]/den-gx,effective[:,:,1]/den+gy,effective[:,:,2]/den],2));mapped=np.stack([np.sum(wanted*T1,2),np.sum(wanted*B1,2),np.sum(wanted*N1,2)],2);mapped[:,:,2]=np.maximum(mapped[:,:,2],.055);mapped=norm(mapped)
half=2.49114990234375+(2.3499999046325684-2.49114990234375)*(YY+2.1605000495910645)/1.2980000376701355;edge=np.minimum.reduce([half-abs(XX),YY+2.1605000495910645,-.862500011920929-YY]);fadeN=np.clip((edge-.012)/.045,0,1);fadeN=fadeN*fadeN*(3-2*fadeN);mapped=norm(oldnormal*(1-fadeN[:,:,None])+mapped*fadeN[:,:,None]);pixels=np.uint8(np.clip(mapped*.5+.5,0,1)*255+.5);pixels[fadeN==0]=raw[32:-32,32:-32][fadeN==0];out=raw.copy();out[32:-32,32:-32]=pixels;Image.fromarray(out).save(F/'normal.png')

assert np.isfinite(mapped).all()
print('Saved complementary normal map',KEY,flush=True)
