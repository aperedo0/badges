"""Fit one optical throughput value from actual native pixels, never a texture."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
from scipy.ndimage import label,binary_erosion,map_coordinates
from scipy.optimize import minimize_scalar
R=Path(__file__).resolve().parent;C=R/'ruby_heart/candidate18';V=C/'review/exposure_diagnostic';V.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'silver2_metal_claude'));from agx import agx,agx_inv
native=np.asarray(Image.open(C/'review/front.png').convert('RGB'),float)/255;reference=np.asarray(Image.open(R/'ruby_heart/reference.png').convert('RGB'),float)/255
def goldbox(a,region):
 r,g,b=a.transpose(2,0,1);m=(r>g*1.035)&(g>b*1.08)&(r>.16)&region;lab,n=label(m);sizes=np.bincount(lab.ravel());sizes[0]=0;yy,xx=np.nonzero(lab==sizes.argmax());return np.array([xx.min(),yy.min(),xx.max(),yy.max()],float)
roi=np.zeros(native.shape[:2],bool);roi[330:850,330:880]=True;nb=goldbox(native,roi);rb=goldbox(reference,np.ones(reference.shape[:2],bool));scale=(rb[2]-rb[0])/(nb[2]-nb[0]);H,W=native.shape[:2];yy,xx=np.mgrid[:H,:W];sx=(xx-(nb[0]+nb[2])/2)*scale+(rb[0]+rb[2])/2;sy=(yy-(nb[1]+nb[3])/2)*scale+(rb[1]+rb[3])/2;target=np.stack([map_coordinates(reference[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=2)
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());maskimage=Image.new('L',(W,H));draw=ImageDraw.Draw(maskimage);distance=np.linalg.norm([0,2.35,23]);sine=2.35/distance;cosine=23/distance
for i,g in enumerate(G):
 if g['mat']!='CrestGem_Rose':continue
 p=D[f'{i}_points'];depth=distance-sine*(p[:,1]+.55)-cosine*p[:,2];screen=np.c_[603+1762.5*p[:,0]/depth,633.55-1762.5*(cosine*(p[:,1]+.55)-sine*p[:,2])/depth];hull=ConvexHull(screen);draw.polygon([tuple(screen[k]) for k in hull.vertices],fill=255)
mask=binary_erosion(np.asarray(maskimage)>0,iterations=3)
colored=lambda a:(a[:,:,0]>a[:,:,1]*1.4)&(a[:,:,2]>a[:,:,1]*1.2)&(a[:,:,0]>.2)
valid=mask&colored(native)&colored(target);y,x=np.nonzero(valid);choose=np.arange(0,len(x),3);y=y[choose];x=x[choose]
def inverse(a):
 desired=np.clip(a,1/1024,1-1/1024);log=np.log2(np.maximum(agx_inv(desired),2**-16))
 for _ in range(9):
  base=agx(2**log);jac=[]
  for c in range(3):
   trial=log.copy();trial[:,c]+=.03;jac.append((agx(2**trial)-base)/.03)
  J=np.stack(jac,axis=2)+np.eye(3)[None,:,:]*.0003;update=np.linalg.solve(J,(desired-base)[...,None])[...,0];log=np.clip(log+.7*np.clip(update,-2,2),-16,6)
 return 2**log
linear=inverse(native[y,x]);goal=target[y,x]
def loss(gain):
 error=agx(linear*gain)-goal;return float(np.mean(np.where(abs(error)<.15,error**2,.3*abs(error)-.0225)))
fit=minimize_scalar(loss,bounds=(.65,2.4),method='bounded');gain=float(fit.x);py,px=np.nonzero(mask);pred=native.copy();pred[py,px]=agx(inverse(native[py,px])*gain)
sheet=Image.new('RGB',(1560,620),(15,16,18));draw=ImageDraw.Draw(sheet)
for j,(a,title) in enumerate([(target,'Reference aligned at equal width'),(native,'Actual native exposure 0.32'),(pred,'Predicted global exposure, not native')]):
 im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).crop((340,330,880,850));im.thumbnail((510,570));sheet.paste(im,(j*520,35));draw.text((j*520+5,10),title,fill='white')
sheet.save(V/'comparison.png');report=dict(status='diagnostic_only_not_adopted',actual_native_pixels_used=True,no_material_texture_created=True,one_scalar_optical_throughput_only=True,sample_count=len(x),outline_excluded_pixels=3,uniform_reference_scale=scale,baseline_exposure=.32,predicted_gain=gain,predicted_exposure=.32*gain,loss_before=loss(1),loss_after=loss(gain));(V/'measurement.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
