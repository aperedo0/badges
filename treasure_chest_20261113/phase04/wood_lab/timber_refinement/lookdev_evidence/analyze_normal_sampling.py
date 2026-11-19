from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
D=Path(__file__).resolve().parent;W=D.parent;U=W/'U_scan_fibers';A=np.load(D/'actual_surface.npz');pos=A['positions'].astype(float);nv=A['normals'].astype(float);height=np.load(U/'master_height.npz')['height'].astype(float);h,w=height.shape;dx=5.1/(w-1);dy=1.3775/(h-1);X,Y=np.meshgrid(np.linspace(-2.55,2.55,w),np.linspace(-.84,-2.2175,h))
def normalize(v):return v/np.maximum(np.linalg.norm(v,axis=2,keepdims=True),1e-8)
def ss(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
gi=np.interp(Y[:,0],pos[:,0,1],np.arange(len(pos)))[:,None];gi=np.broadcast_to(gi,(h,w));left=np.interp(Y[:,0],pos[:,0,1],pos[:,0,0])[:,None];right=np.interp(Y[:,0],pos[:,0,1],pos[:,-1,0])[:,None];gj=(X-left)/np.maximum(right-left,.01)*(pos.shape[1]-1)
N=normalize(np.stack([map_coordinates(nv[:,:,c],[gi,gj],order=1,mode='nearest') for c in range(3)],2));T=normalize(np.stack([N[:,:,2],np.zeros((h,w)),-N[:,:,0]],2));B=normalize(np.cross(N,T));gy,gx=np.gradient(height,dy,dx);wanted=normalize(np.stack([-gx,gy,np.ones((h,w))],2));desired=np.stack([np.sum(wanted*T,2),np.sum(wanted*B,2),np.sum(wanted*N,2)],2)
old=normalize(np.asarray(Image.open(U/'normal.png').convert('RGB'),float)[16:-16,16:-16]/127.5-1);effective=normalize(T*old[:,:,0,None]+B*old[:,:,1,None]+N*old[:,:,2,None]);error=np.degrees(np.arccos(np.clip(np.sum(effective*wanted,2),-1,1)))
L=np.load(W/'grain_hierarchy/detail_layers.npz');plate=1-ss(.003,.014,-L['medium']-L['knot']);plate*=1-ss(.001,.012,-L['fractures']);core=1-ss(.85,1.15,np.hypot((X+1.31)/.145,(Y+1.35)/.17));mask=np.maximum(plate,core*.8)
# Correct only the fine directional discrepancy. Broad grain shading stays intact.
delta=desired-old;wide=np.stack([gaussian_filter(delta[:,:,c],(.020/dy,.045/dx)) for c in range(3)],2);correction=(delta-wide)*mask[:,:,None];fixed=normalize(old+correction)
newN=normalize(T*fixed[:,:,0,None]+B*fixed[:,:,1,None]+N*fixed[:,:,2,None]);after=np.degrees(np.arccos(np.clip(np.sum(newN*wanted,2),-1,1)))
visible=(X>-2.15)&(X<-.35)&(Y>-2.1)&(Y<-.9)&(plate>.8)
report=dict(method='Approximate tangent frame from actual mesh vertex normals, compared with current full height. Not an inference of target shape from the reference.',before_angle_error_median=float(np.median(error[visible])),before_angle_error_p95=float(np.percentile(error[visible],95)),after_angle_error_median=float(np.median(after[visible])),after_angle_error_p95=float(np.percentile(after[visible],95)),normal_change_median=float(np.median(np.degrees(np.arccos(np.clip(np.sum(old*fixed,2),-1,1)))[visible])),geometry_changed=False,source_height_changed=False,broad_normal_delta_removed=True,visual_benefit='Not yet tested. This is a numerical diagnostic, not proof of an artistic improvement.')
(D/'normal_sampling_diagnosis.json').write_text(json.dumps(report,indent=2));np.savez_compressed(D/'normal_sampling.npz',corrected=fixed.astype('float32'),correction=correction.astype('float32'),mask=mask.astype('float32'))
print(json.dumps(report))
