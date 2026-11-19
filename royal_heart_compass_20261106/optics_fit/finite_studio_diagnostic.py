from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from forward import Studio,planes_of,optical,unit,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];studio=Studio()
Y,X=np.mgrid[355:785:3,380:830:3];shape=X.shape;x=X.ravel();y=Y.ravel();scale=47/60;f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);mx=(x-603)/scale+540;my=(y-69.3)/scale;ray=unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255;sx=118+(x-388)/429*1006;sy=111+(y-361)/409*1002;target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1);panels=[('Reference',target)]
import forward,time
class FiniteStudio(Studio):
 def __init__(self,radius):
  super().__init__();self.radius=radius
 def project(self,o,d):
  if not np.isfinite(self.radius):return d
  along=np.sum(o*d,axis=1);root=np.maximum(along*along+self.radius*self.radius-np.sum(o*o,axis=1),0)
  distance=-along+np.sqrt(root);return unit(o+d*distance[:,None])
 def sharp_at(self,o,d):return np.minimum(self.sample(self.project(o,d),1),24)
 def along_at(self,o,d):
  projected=self.project(o,d)
  return np.minimum(self.sample(projected,1),24)+np.minimum(self.sample(projected,8),3)*.9
source=Path(forward.__file__).read_text();start=source.index('def optical(');end=source.index('\ndef render',start)
code=source[start:end].replace('def optical(','def finite_optical(').replace('studio.sharp(reflect(d,n))','studio.sharp_at(pos,reflect(d,n))').replace('studio.along(bent)','studio.along_at(pos,bent)').replace('studio.along(direction)','studio.along_at(pos,direction)')
ns=dict(forward.__dict__);exec(code,ns);finite_optical=ns['finite_optical'];start=time.time()
for radius in [np.inf,4.5,6.5,9.,14.]:
 ids,lin=finite_optical([planes_of(p) for p in parts],eye,ray,FiniteStudio(radius));a=np.full((len(x),3),.03);a[ids]=np.clip(agx(lin),0,1);panels.append(('Infinite baseline' if not np.isfinite(radius) else str(radius)+' distance',a))
W=300;H=320;out=Image.new('RGB',(W*3,H*2),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 im=Image.fromarray(np.uint8(np.clip(a.reshape(*shape,3),0,1)*255)).resize((W,288));ox=i%3*W;oy=i//3*H;out.paste(im,(ox,oy+24));draw.text((ox+5,oy+5),label,fill='white')
out.save(R/'finite_studio_diagnostic.png');(R/'finite_studio_diagnostic.json').write_text(json.dumps(dict(status='diagnostic_only',geometry_and_material_unchanged=True,environment_reprojected_at_actual_optical_exit_positions=True,no_added_light_energy=True,seconds=time.time()-start),indent=2));print('Finite studio optical diagnosis saved',flush=True)
