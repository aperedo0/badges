"""Move the physical crown apex toward the reference's upper central junction."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
import forward
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate16';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[340:850:5,350:860:5];shape=X.shape;x=X.ravel();y=Y.ravel();f=forward.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);ray=forward.unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy()
native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255;panels=[('Actual current native',native[Y,X])];reports=[];studio=forward.Studio()
source=Path(forward.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a);code=source[a:b].replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.16,9.,2.8])/'+repr(float(np.ptp(parts[0][:,2]))));ns=dict(forward.__dict__);exec(code,ns);optical=ns['optical']
for k in [0,.15,.3,.45,.6]:
 result=[];counts=[]
 for p in parts:
  q=p.copy();fz=q[:48,2].mean();q[96:139,2]=fz+(q[96:139,2]-fz)*np.exp(k*(q[96:139,1]-.8));sign=np.sign(q[:,0].mean());grad=np.array([.35*(-sign),-.35]);h=np.max(q[:48,2]-q[:48,:2]@grad)+.015;q[96:139,2]=np.minimum(q[96:139,2],q[96:139,:2]@grad+h);result.append(q);counts.append(dict(active_front=int(sum(96<=i<139 for i in ConvexHull(q).vertices)),planes=len(forward.planes_of(q)[0])))
 for exposure in [.32,.52]:
  ids,lin=optical([forward.planes_of(p) for p in result],eye,ray,studio);frame=np.full((len(x),3),.03);frame[ids]=np.clip(forward.agx(lin*exposure/.32),0,1);panels.append((f'Upper crown bias {k}, exposure {exposure}',frame.reshape(*shape,3)))
 np.savez_compressed(R/('heart_crown_bias_'+str(k)+'.npz'),**{f'{i}_points':p for i,p in enumerate(result)});reports.append(dict(bias=k,domains=counts))
W=300;H=324;out=Image.new('RGB',(W*3,H*4),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 ox=i%3*W;oy=i//3*H;im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));out.paste(im,(ox,oy+24));draw.text((ox+4,oy+5),label,fill='white')
out.save(R/'heart_crown_bias.png');(R/'heart_crown_bias.json').write_text(json.dumps(dict(status='physical_diagnostic_not_native',no_appearance_map=True,variants=reports),indent=2));print('Physical apex diagnostic saved')
