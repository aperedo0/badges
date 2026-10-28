"""Give the side metal continuous normals independent of raster contour steps."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates

def prepare(root,candidate):
 trace=json.loads((candidate/'trace.json').read_text());path=candidate/'geometry.npz'
 with np.load(path) as data:arrays={key:data[key] for key in data.files}
 v=arrays['wall_points'];scale=trace['reference_scale'];lo,hi=np.array(trace['reference_bounds']);cx=trace['reference_center'][0]
 reference=np.c_[cx+v[:,0]/scale,lo[1]+(3.015-v[:,1])/scale]
 smooth=gaussian_filter(arrays['sdf'],4.)
 gy,gx=np.gradient(smooth)
 nx=-map_coordinates(gx,[reference[:,1],reference[:,0]],order=1,mode='nearest')
 ny=map_coordinates(gy,[reference[:,1],reference[:,0]],order=1,mode='nearest')
 xy=np.c_[nx,ny];xy/=np.maximum(np.linalg.norm(xy,axis=1)[:,None],1e-6)
 normals=np.c_[xy*.82,np.sign(v[:,2])*.57]
 normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-6)
 arrays['wall_normal_hints']=normals.astype(np.float32)
 np.savez_compressed(path,**arrays)
 print(root.name,'continuous side normal hints prepared',len(normals),flush=True)
if __name__=='__main__':
 root=Path(__file__).resolve().parent/sys.argv[1]
 candidate=root/((root/'candidate.txt').read_text().strip() if (root/'candidate.txt').exists() else 'candidate01')
 prepare(root,candidate)
