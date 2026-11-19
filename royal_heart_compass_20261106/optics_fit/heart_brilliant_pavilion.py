"""Test broad real pavilion facets instead of a shallow window and narrow radial fans."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical']
variants=[];reports=[]
for depth in [1.,1.5,2.,2.5]:
 for step in [4,8]:
  ps=[]
  for p in parts:
   front=p[:111].copy();rear=float(p[48:96,2].mean());center=np.array([0.,.30]);outline=p[:48,:2]
   # The shared seam is retained exactly on X zero in both domains.
   chosen=np.unique(np.r_[np.arange(0,48,step),np.flatnonzero(abs(outline[:,0])<1e-6)])
   xy=center+(outline[chosen]-center)*.86
   ring=np.c_[xy,np.full(len(xy),rear-.38)]
   ps.append(np.vstack([front,ring,[0.,.30,rear-depth]]))
  hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256
  np.savez_compressed(R/f'heart_brilliant_{depth}_{step}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
  ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1)
  variants.append((f'Broad pavilion depth {depth}, outline step {step}',frame.reshape(*shape,3)));reports.append(dict(depth=depth,outline_step=step,planes=counts))
for j in range(2):
 sheet=Image.new('RGB',(1000,1060),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a) in enumerate(variants[j*4:j*4+4]):
  ox=i%2*500;oy=i//2*530;sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(ox,oy+25));draw.text((ox+5,oy+6),title,fill='white')
 sheet.save(R/f'heart_brilliant_pavilion_{j}.png')
(R/'heart_brilliant_pavilion.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',broad_physical_facets=True,no_appearance_textures=True,variants=reports),indent=2));print('Broad pavilion diagnostic ready',flush=True)
