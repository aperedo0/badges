from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter
D=Path(__file__).resolve().parent;W=D.parent;M=np.load(W/'grain_hierarchy/detail_layers.npz');H=np.load(W/'AI_core_definition/master_height.npz')['height'];H=np.asarray(Image.fromarray(H).resize((2016,736),Image.Resampling.BICUBIC),dtype='float32');primary=M['broad']+M['medium']+M['knot']+M['fractures'];secondary=H-primary;dx,dy=5.1/2015,1.3775/735
fields=[primary,secondary,H];names=['Existing structural layers','Added secondary layers','Current combined surface'];im=Image.new('RGB',(1500,710),'#202020');dr=ImageDraw.Draw(im);stats={}
plate=np.load(W/'final_fibers/structure_layers.npz')['plate']>.8
for i,(field,name) in enumerate(zip(fields,names)):
 mid=gaussian_filter(field,(.005/dy,.012/dx));gy,gx=np.gradient(mid,dy,dx);n=np.stack([-gx,gy,np.ones_like(gx)],2);n/=np.linalg.norm(n,axis=2)[:,:,None];light=np.array([-.4,.3,.866]);v=.2+.8*np.maximum(n@light,0);tile=Image.fromarray(np.uint8(v*255)).convert('RGB').resize((1500,215),Image.Resampling.LANCZOS);im.paste(tile,(0,i*235+20));dr.text((10,i*235+4),name,fill='white');stats[name]=dict(mid_gradient_rms_on_broad_faces=float(np.sqrt(np.mean((gx*gx+gy*gy)[plate]))),height_rms_on_broad_faces=float(np.std(field[plate])))
im.save(D/'layer_diagnosis.jpg',quality=97);(D/'layer_diagnosis.json').write_text(json.dumps(dict(values=stats,limits='Numerical normal response only; not a Cycles render or reference measurement'),indent=2));print(json.dumps(stats))
