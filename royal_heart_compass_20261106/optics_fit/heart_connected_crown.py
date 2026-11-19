"""Replace the twin raised lobes with one connected central ruby crown."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical']
variants=[]
for height in [.9,1.1,1.3,1.5]:
 for matching_back in [False,True]:
  result=[]
  for p in parts:
   q=p.copy();q[[96,97,98,99,100,101],2]=np.array([.32,height,height*.86,height*.62,.42,.26])
   if matching_back:
    mid=(q[:48,2].mean()+q[48:96,2].mean())/2
    q=np.vstack([q[:139],np.c_[q[96:139,:2],2*mid-q[96:139,2]]])
   result.append(q)
  hulls=[f.planes_of(p) for p in result];counts=[len(h[0]) for h in hulls]
  assert max(counts)<=256,counts
  np.savez_compressed(R/f'heart_connected_{height}_{int(matching_back)}.npz',**{f'{i}_points':p for i,p in enumerate(result)})
  ids,lin=optical(hulls,eye,ray,studio,np.ptp(result[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1)
  variants.append((f'Connected center {height}, matching rear {matching_back}',frame.reshape(*shape,3),counts))
for j in range(2):
 sheet=Image.new('RGB',(1000,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a,counts) in enumerate(variants[j*4:j*4+4]):
  ox=i%2*500;oy=i//2*530;sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(ox,oy+25));draw.text((ox+5,oy+6),title,fill='white')
 sheet.save(R/f'heart_connected_crown_{j}.png')
(R/'heart_connected_crown.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',whole_ruby_appearance=True,internal_lobe_interface_not_air=True,no_appearance_textures=True,variants=[dict(name=n,planes=c) for n,a,c in variants]),indent=2))
print('Connected crown diagnostic ready',flush=True)
