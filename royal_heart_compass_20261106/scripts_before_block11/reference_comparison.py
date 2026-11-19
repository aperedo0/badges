"""Compare the owner's original and native model at an equal visible width."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;keys=sys.argv[1:] or [x['slug'] for x in json.loads((ROOT/'gallery.json').read_text())]
clips={'ruby_heart':.90,'amethyst_crown':.885,'ruby_crown':.82,'emerald_crown':.86,'ocean_navigator':.87}
for key in keys:
 R=ROOT/key;V=R/'candidate10/review';ref=Image.open(R/'reference.png').convert('RGB');native=Image.open(V/('native_front_precheck.png' if (V/'native_front_precheck.png').exists() else 'front.png')).convert('RGB')
 crops=[]
 for image,is_native in [(ref,False),(native,True)]:
  a=np.asarray(image).astype(float)/255;r,g,b=a.transpose(2,0,1);mask=(r>g*1.035)&(g>b*1.06)&(r>.16)
  if is_native:
   roi=np.zeros(mask.shape,bool);roi[250:840,300:906]=True;mask&=roi
  else:mask[int(image.height*clips[key]):]=False
  y,x=np.nonzero(mask);assert len(x)>100
  box=(max(0,int(x.min())-12),max(0,int(y.min())-12),min(image.width,int(x.max())+13),min(image.height,int(y.max())+13))
  crop=image.crop(box);crop=crop.resize((620,round(crop.height*620/crop.width)),Image.Resampling.LANCZOS);crops.append(crop)
 height=max(x.height for x in crops)+55;sheet=Image.new('RGB',(1280,height),(16,17,20));draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(crops,['Your reference','Current model in the simulator'])):
  sheet.paste(im,(i*640+10,40));draw.text((i*640+15,12),label,fill='white')
 sheet.save(V/'reference_comparison.png')
 print(key,'reference comparison saved')
