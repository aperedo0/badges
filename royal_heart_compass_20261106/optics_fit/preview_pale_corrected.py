from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from forward import planes_of,optical,Studio,unit,agx
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate05';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());base=[D[f'{i}_points'] for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];F=np.load(R/'heart_cut_pale_corrected.npz');fit=[F[f'{i}_points'] for i in range(2)]
y,x=np.mgrid[355:780:2,380:830:2];shape=x.shape;x=x.ravel();y=y.ravel();f=unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);scale=47/60;mx=(x-603)/scale+540;my=(y-69.3)/scale;d=unit(f[None,:]+np.c_[(mx-540)/2250,np.zeros(len(x)),np.zeros(len(x))]+((720-my)/2250)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],d.shape).copy();panels=[]
ref=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'),float)/255;sx=118+(x-388)/429*1006;sy=111+(y-361)/409*1002;target=np.stack([map_coordinates(ref[:,:,i],[sy,sx],order=1,mode='constant') for i in range(3)],axis=1);panels.append(target)
for parts in [base,fit]:
 ids,lin=optical([planes_of(p) for p in parts],eye,d,Studio());a=np.full((len(x),3),.035);a[ids]=np.clip(agx(lin),0,1);panels.append(a)
Image.fromarray(np.concatenate([np.uint8(np.clip(a.reshape(*shape,3),0,1)*255) for a in panels],axis=1)).save(R/'pale_corrected_comparison.png')
