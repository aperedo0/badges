"""Construct the reference's two upper facets as actual convex support faces."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image,ImageDraw
import forward
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate19';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose'];base=parts[0];unit=(base[96,1]-base[97,1])/104;intercept=base[96,1]+389*unit;photo=np.array([[282,291],[420,232],[369,371],[455,328]],float);xy=np.c_[(photo[:,0]-627)*unit,intercept-photo[:,1]*unit];edge=xy[2]-xy[1];perp=np.array([-edge[1],edge[0]]);perp/=np.linalg.norm(perp)
Y,X=np.mgrid[340:850:5,350:860:5];shape=X.shape;x=X.ravel();y=Y.ravel();f=forward.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);ray=forward.unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255;panels=[('Actual native cut19',native[Y,X])];reports=[];studio=forward.Studio()
source=Path(forward.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a);code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,absorption,exposure):').replace('absorption=np.array([.16,9.,2.8])*.5;indices=', 'indices=').replace('*.32','*exposure');ns=dict(forward.__dict__);exec(code,ns);optical=ns['optical']
for slope_delta in [.035,.070]:
 result=[];domain_reports=[]
 for p in parts:
  sign=1 if p[:,0].mean()<0 else -1;q=p.copy();coords=xy*np.array([sign,1]);g1=np.array([.35*sign,-.35]);g2=(np.array([.35,-.35])-slope_delta*perp)*np.array([sign,1]);relative_offset=(g1-g2)@coords[1];h=max(np.max(q[:48,2]-q[:48,:2]@g1),np.max(q[:48,2]-q[:48,:2]@g2-relative_offset))+.030
  q[96:139,2]=np.minimum(q[96:139,2],np.minimum(q[96:139,:2]@g1+h,q[96:139,:2]@g2+h+relative_offset)-.020)
  for point in coords:
   z=min(point@g1+h,point@g2+h+relative_offset);idx=np.flatnonzero(np.linalg.norm(q[96:139,:2]-point,axis=1)<1e-5)
   if len(idx):q[96+idx[0],2]=z
   else:q=np.vstack([q,[*point,z]])
  hull=ConvexHull(q);counts=len(forward.planes_of(q)[0]);assert counts<=256;domain_reports.append(dict(planes=counts,forced_upper_reference_vertices=4));result.append(q)
 np.savez_compressed(R/('heart_literal_'+str(slope_delta)+'.npz'),**{f'{i}_points':p for i,p in enumerate(result)});reports.append(dict(slope_delta=slope_delta,domains=domain_reports))
 hulls=[forward.planes_of(p) for p in result]
 for green,blue in [(9,2.8),(6,2.0),(4,1.4)]:
  absorption=np.array([.16,green,blue])/np.ptp(result[0][:,2]);ids,lin=optical(hulls,eye,ray,studio,absorption,.434211563);frame=np.full((len(x),3),.03);frame[ids]=np.clip(forward.agx(lin),0,1);panels.append((f'Literal facets {slope_delta}, absorption {green}/{blue}',frame.reshape(*shape,3)))
W=300;H=324;out=Image.new('RGB',(W*3,H*3),(12,12,15));draw=ImageDraw.Draw(out)
for i,(label,a) in enumerate(panels):
 ox=i%3*W;oy=i//3*H;im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));out.paste(im,(ox,oy+24));draw.text((ox+4,oy+5),label,fill='white')
out.save(R/'heart_literal_facets.png');(R/'heart_literal_facets.json').write_text(json.dumps(dict(status='physical_diagnostic_only_not_native',exact_reference_facet_vertices=photo.tolist(),no_appearance_image_on_gem=True,variants=reports),indent=2));print('Literal physical reference facet diagnostic saved')
