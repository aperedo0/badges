"""Use the main reference facet junctions around one continuous raised keel."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20'
D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];base=parts[0]
unit=(base[96,1]-base[97,1])/104;intercept=base[96,1]+389*unit
photo=np.array([[627,389],[627,493],[627,650],[627,784],[627,900],[627,970],[420,232],[282,291],[369,371],[455,328],[209,453],[274,622],[421,656],[453,814],[386,850]],float)
xy=np.c_[abs(photo[:,0]-627)*unit,intercept-photo[:,1]*unit]
z=np.array([.32,.95,.87,.80,.59,.36,.284,.10,.447,.515,.10,.35,.610,.343,.20])
Y,X=np.mgrid[350:835:3,360:850:3];shape=X.shape;x=X.ravel();y=Y.ravel();axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis)
ray=f.unit(axis[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();studio=f.Studio()
source=Path(f.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a)
code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,thickness):').replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/thickness').replace('*.32','*.434211563');ns=dict(f.__dict__);exec(code,ns);optical=ns['optical']
variants=[];reports=[]
for peak in [.95,1.10,1.25]:
 for back in ['existing','matching']:
  ps=[]
  for p in parts:
   sign=np.sign(p[:,0].mean());qxy=xy*np.array([sign,1]);height=z.copy();height[:6]+=np.array([0,1,.9,.65,.4,.2])*(peak-.95)
   q=np.vstack([p[:96],np.c_[qxy,height]])
   if back=='existing':q=np.vstack([q,p[139:151]])
   else:
    mid=(p[:48,2].mean()+p[48:96,2].mean())/2;q=np.vstack([q,np.c_[qxy,2*mid-height]])
   ps.append(q)
  hulls=[f.planes_of(p) for p in ps];counts=[len(h[0]) for h in hulls];assert max(counts)<=256
  np.savez_compressed(R/f'heart_coherent_{peak}_{back}.npz',**{f'{i}_points':p for i,p in enumerate(ps)})
  ids,lin=optical(hulls,eye,ray,studio,np.ptp(ps[0][:,2]));frame=np.full((len(x),3),.03);frame[ids]=np.clip(f.agx(lin),0,1);variants.append((f'One connected reference cut {peak}, rear {back}',frame.reshape(*shape,3)));reports.append(dict(peak=peak,rear=back,planes=counts))
for j in range(3):
 sheet=Image.new('RGB',(1000,535),(12,12,15));draw=ImageDraw.Draw(sheet)
 for i,(title,a) in enumerate(variants[j*2:j*2+2]):
  sheet.paste(Image.fromarray(np.uint8(a*255)).resize((500,500)),(i*500,30));draw.text((i*500+5,8),title,fill='white')
 sheet.save(R/f'heart_coherent_cut_{j}.png')
(R/'heart_coherent_cut.json').write_text(json.dumps(dict(status='diagnostic_only_not_native',reference_facet_junctions=photo.tolist(),continuous_central_keel=True,appearance_maps=False,variants=reports),indent=2));print('Coherent reference cut diagnostic ready',flush=True)
