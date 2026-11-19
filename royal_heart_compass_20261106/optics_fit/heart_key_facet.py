"""Test real upper crown planes against the measured studio key direction."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
import forward
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate16';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[340:850:5,350:860:5];shape=X.shape;x=X.ravel();y=Y.ravel();f=forward.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);ray=forward.unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255;panels=[('Actual current native',native[Y,X])];reports=[];studio=forward.Studio()
source=Path(forward.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a);code=source[a:b].replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/'+repr(float(np.ptp(parts[0][:,2]))));ns=dict(forward.__dict__);exec(code,ns);optical=ns['optical']
for gradient in [[.122,-.5455],[.35,-.35]]:
 for lift in [.015,.07,.14,.22]:
  result=[];clipped=[]
  for p in parts:
   q=p.copy();sign=np.sign(q[:,0].mean());grad=np.array([gradient[0]*(-sign),gradient[1]])
   # The support plane stays outside every existing girdle vertex, retaining
   # the complete silhouette and the same continuous lobe join.
   h=np.max(q[:48,2]-q[:48,:2]@grad)+lift
   cap=q[96:139,:2]@grad+h;old=q[96:139,2].copy();q[96:139,2]=np.minimum(old,cap);clipped.append(int((old>cap+1e-6).sum()));result.append(q)
  for clamp in [24,80]:
   studio.sharp=lambda d:np.minimum(studio.sample(d,1),clamp)
   ids,lin=optical([forward.planes_of(p) for p in result],eye,ray,studio);frame=np.full((len(x),3),.03);frame[ids]=np.clip(forward.agx(lin),0,1)
   label=f'slope {gradient}, lift {lift}, light cap {clamp}';panels.append((label,frame.reshape(*shape,3)));reports.append(dict(slope=gradient,lift=lift,clamp=clamp,changed_vertices=clipped))
  np.savez_compressed(R/('heart_key_'+str(gradient[0])+'_'+str(lift)+'.npz'),**{f'{i}_points':p for i,p in enumerate(result)})
W=300;H=324;out=Image.new('RGB',(W*3,H*6),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 ox=i%3*W;oy=i//3*H;im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));out.paste(im,(ox,oy+24));draw.text((ox+4,oy+5),label,fill='white')
out.save(R/'heart_key_facets.png');(R/'heart_key_facets.json').write_text(json.dumps(dict(status='physical_diagnostic_only_not_native',geometry_uses_measured_actual_studio_key=True,variants=reports,no_appearance_texture=True),indent=2));print('Physical key facet diagnostic saved',flush=True)
