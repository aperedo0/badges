from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.ndimage import gaussian_filter
from geometry import shield_outline
r=Path(__file__).resolve().parents[1];outline,_,_=shield_outline();outline*=.868
nx,ny=257,321;x0,x1=-2.55,2.55;y0,y1=-3.1,3.1;dx=(x1-x0)/(nx-1);dy=(y1-y0)/(ny-1)
img=Image.new('L',(nx,ny));ImageDraw.Draw(img).polygon([((x-x0)/dx,(y-y0)/dy) for x,y in outline],fill=1);mask=np.array(img,dtype=bool);ids=np.full(mask.shape,-1,int);ids[mask]=np.arange(mask.sum());ys,xs=np.nonzero(mask);count=len(ys)
rows=list(range(count));cols=list(range(count));data=[2/dx**2+2/dy**2]*count
for oy,ox,weight in [(0,-1,-1/dx**2),(0,1,-1/dx**2),(-1,0,-1/dy**2),(1,0,-1/dy**2)]:
    neighbor=ids[ys+oy,xs+ox];valid=neighbor>=0;rows.extend(np.arange(count)[valid]);cols.extend(neighbor[valid]);data.extend([weight]*valid.sum())
matrix=coo_matrix((data,(rows,cols)),shape=(count,count)).tocsr();solution=spsolve(matrix,np.ones(count));field=np.zeros(mask.shape,float);field[mask]=solution;field=gaussian_filter(field,.7);field/=field.max();gy,gx=np.gradient(field,dy,dx)
np.savez_compressed(r/'source/shield_plate_field.npz',height=field.astype(np.float32),gx=gx.astype(np.float32),gy=gy.astype(np.float32),bounds=np.array([x0,x1,y0,y1]))
print('Smooth plate field',mask.sum(),'samples',field.shape,'height range',field.min(),field.max())
