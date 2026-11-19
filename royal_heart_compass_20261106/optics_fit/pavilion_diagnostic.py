from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from forward import Studio,planes_of,optical,unit,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];studio=Studio()
Y,X=np.mgrid[355:785:3,380:830:3];shape=X.shape;x=X.ravel();y=Y.ravel();scale=47/60;f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);mx=(x-603)/scale+540;my=(y-69.3)/scale;ray=unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255;sx=118+(x-388)/429*1006;sy=111+(y-361)/409*1002;target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1);panels=[('Reference',target)]
for factor in [1.,1.5,2.,2.5,3.]:
 new=[]
 for p in parts:
  q=p.copy();first=len(q)-26;z0=float(np.median(q[48:96,2]));q[-13:,2]=z0+(q[-13:,2]-z0)*factor;new.append(q)
 ids,lin=optical([planes_of(p) for p in new],eye,ray,studio);a=np.full((len(x),3),.03);a[ids]=np.clip(agx(lin),0,1);panels.append((str(factor)+' pavilion depth',a))
W=300;H=320;out=Image.new('RGB',(W*3,H*2),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 im=Image.fromarray(np.uint8(np.clip(a.reshape(*shape,3),0,1)*255)).resize((W,288));ox=i%3*W;oy=i//3*H;out.paste(im,(ox,oy+24));draw.text((ox+5,oy+5),label,fill='white')
out.save(R/'pavilion_diagnostic.png');print('Physical pavilion variants saved; no installed model changed')
