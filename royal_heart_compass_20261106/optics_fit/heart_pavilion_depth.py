"""Measure actual first exit behavior while testing a deeper physical pavilion."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
import forward
R=Path(__file__).resolve().parent;C=R.parent/'ruby_heart/candidate20';D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());parts=[D[f'{i}_points'].astype(float) for i,g in enumerate(G) if g['mat']=='CrestGem_Rose']
Y,X=np.mgrid[340:850:6,350:860:6];shape=X.shape;x=X.ravel();y=Y.ravel();f=forward.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],f);ray=forward.unit(f[None,:]+np.c_[(x-603)/1762.5,np.zeros(len(x)),np.zeros(len(x))]+((633.3-y)/1762.5)[:,None]*up);eye=np.broadcast_to([0,1.8,23.],ray.shape).copy();panels=[];reports=[];studio=forward.Studio()
source=Path(forward.__file__).read_text();a=source.index('def optical(');b=source.index('\ndef render',a);code=source[a:b].replace('def optical(hulls,o,d,studio):','def optical(hulls,o,d,studio,absorption):').replace('absorption=np.array([.16,9.,2.8])*.5;indices=','indices=').replace('*.32','*.434211563');ns=dict(forward.__dict__);exec(code,ns);optical=ns['optical']
for multiple in [1,1.5,2,2.5,3,3.5]:
 result=[]
 for p in parts:
  q=p.copy();rear=q[48:96,2].mean();back=q[:,2]<rear-1e-5;q[back,2]=rear+(q[back,2]-rear)*multiple;result.append(q)
 low=min(p[:,2].min() for p in result);high=max(p[:,2].max() for p in result);shift=-(low+high)/2
 for q in result:q[:,2]+=shift
 hulls=[forward.planes_of(p) for p in result];ok,lo,_,normal,_=forward.outer(hulls,eye,ray);ids=np.flatnonzero(ok&(lo>0));direction=forward.refract(ray[ids],normal[ids],1/1.77);position=eye[ids]+ray[ids]*lo[ids,None];_,_,distance,_,outward=forward.outer(hulls,position,direction);share=forward.fresnel(np.sum(direction*outward,axis=1),1.77,1);row=dict(pavilion_depth_multiplier=multiple,total_depth=high-low,global_z_center_shift=shift,first_internal_hit_total_reflection_fraction=float(np.mean(share>.99999)),first_hit_median_path=float(np.median(distance)));reports.append(row)
 for green,blue in [(9,2.8),(6,2)]:
  absorption=np.array([.16,green,blue])/(high-low);ids,lin=optical(hulls,eye,ray,studio,absorption);frame=np.full((len(x),3),.03);frame[ids]=np.clip(forward.agx(lin),0,1);panels.append((f'Depth {multiple}, absorption {green}/{blue}',frame.reshape(*shape,3)))
 np.savez_compressed(R/('heart_pavilion_'+str(multiple)+'.npz'),**{f'{i}_points':p for i,p in enumerate(result)},global_z_shift=np.array(shift))
W=300;H=324;out=Image.new('RGB',(W*3,H*4),(12,12,15));draw=ImageDraw.Draw(out)
for i,(name,a) in enumerate(panels):
 ox=i%3*W;oy=i//3*H;im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).resize((W,300));out.paste(im,(ox,oy+24));draw.text((ox+4,oy+5),name,fill='white')
out.save(R/'heart_pavilion_depth.png');(R/'heart_pavilion_depth.json').write_text(json.dumps(dict(status='physical_diagnostic_only_not_native',no_appearance_maps=True,reference_education='https://www.gia.edu/gia-news-research-value-factors-gem-cutting-styles-definitions',variants=reports),indent=2));print(json.dumps(reports),flush=True)
