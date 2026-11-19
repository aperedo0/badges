from pathlib import Path
import numpy as np,json
from scipy.ndimage import gaussian_filter,minimum_filter,label,find_objects,distance_transform_edt
from PIL import Image
D=Path(__file__).resolve().parent;A=D/'relief_old';F=D/'relief_planished';F.mkdir(exist_ok=True);a=np.load(A/'fields.npz');H=a['coarse'];h,w=H.shape;dx,dy=18.04/(w-1),.5035/(h-1);d=-gaussian_filter(minimum_filter(H,size=(int(.10/dy)|1,int(.15/dx)|1)),(.009/dy,.025/dx));ratio=-H/np.maximum(d,.0001);regions,count=label((ratio>.60)&(H<-.0007)&(a['mask']>.75));out=H.copy();changed=0
for num,box in enumerate(find_objects(regions),1):
 if box is None:continue
 region=regions[box]==num;n=int(region.sum())
 if n<45 or n>9000:continue
 iy,ix=np.nonzero(region);xx=(ix-ix.mean())*dx;yy=(iy-iy.mean())*dy;z=H[box][region];M=np.c_[xx,yy,np.ones(n)];coef=np.linalg.lstsq(M,z,rcond=None)[0];coef[:2]=np.clip(coef[:2],-.065,.065);plane=M@coef;plane-=max(float(np.median(plane)-np.percentile(z,25)),0);plane=np.clip(plane,float(z.min()),float(z.max()));dist=distance_transform_edt(region,sampling=(dy,dx))[region];blend=np.clip(dist/.008,0,1);blend=blend*blend*(3-2*blend)*.72;out[box][region]=z+(plane-z)*blend;changed+=1
# The operation changes resolved existing depression floors, not their placement or fine pattern.
out=H+gaussian_filter(out-H,(.0012/dy,.002/dx))*a['mask'];Image.fromarray(np.uint16(np.clip((out+.008)/.010,0,1)*65535+.5)).save(F/'coarse16.png');Image.open(A/'fine16.png').save(F/'fine16.png');Image.open(A/'contact_mask.png').save(F/'contact_mask.png');np.savez_compressed(F/'fields.npz',coarse=out,fine=a['fine'],mask=a['mask']);(F/'design.json').write_text(json.dumps(dict(source='Existing medium field with local planar fitting only inside resolved depression floors',regions=changed,blend=.72,existing_locations_edges_and_fine_data_retained=True,extra_features=0,height_range=[float(out.min()),float(out.max())]),indent=2));print('Planished existing resolved floors',changed)
