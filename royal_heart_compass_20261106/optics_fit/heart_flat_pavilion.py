"""Compare closed flat back ruby cuts, removing the nested rear dome geometry."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate21';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical']
sheet=Image.new('RGB',(1500,1590),(12,12,15));draw=ImageDraw.Draw(sheet);reports=[]
for i,(scale,depth) in enumerate((s,d) for s in [1.,.65,.4] for d in [.06,.3,.7]):
 ps=[]
 for p in parts:
  q=p[:111].copy();front=float(q[:48,2].mean());q[96:111,2]=front+(q[96:111,2]-front)*scale;q[48:96,2]=front-depth;ps.append(q)
 hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256
 np.savez_compressed(R/f'heart_flat_{scale}_{depth}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
 ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1)
 ox=i%3*500;oy=i//3*530;sheet.paste(Image.fromarray(np.uint8(frame.reshape(*shape,3)*255)).resize((500,500)),(ox,oy+25));draw.text((ox+6,oy+6),f'Crown {scale}, closed flat back depth {depth}',fill='white');reports.append(dict(crown=scale,depth=depth,planes=counts))
sheet.save(R/'heart_flat_pavilion.png');(R/'heart_flat_pavilion.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',closed_ruby_volume=True,removed_rear_dome_geometry=True,original_clear_optical_shader=True,no_appearance_maps=True,variants=reports),indent=2));print('Flat back cut diagnostic ready',flush=True)
