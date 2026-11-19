from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;W=D.parent
meta=json.loads((D/'comparison_geometry.json').read_text())
items=[('Reference',D/'reference_rectified.png',None),('Previous layered wood',D/'layered_H_rectified.png',None),('Current fractured wood',D/'current_P_rectified.png',None),('Restored grain softer',W/'Q_layers_soft/cinema_close.png',meta['model_quad']),('Restored grain fuller',W/'R_layers_full/cinema_close.png',meta['model_quad'])]
out=Image.new('RGB',(1800,1284),'#202020');draw=ImageDraw.Draw(out)
for i,(label,path,quad) in enumerate(items):
 im=Image.open(path).convert('RGB')
 if quad:im=im.transform((720,480),Image.Transform.QUAD,tuple(np.array(quad).ravel()),Image.Resampling.BICUBIC)
 im=im.resize((900,600),Image.Resampling.LANCZOS)
 if i<3:im=im.resize((600,400),Image.Resampling.LANCZOS);x=i*600;y=0
 else:x=(i-3)*900;y=442
 out.paste(im,(x,y+34));draw.text((x+12,y+12),label,fill='white')
out=out.crop((0,0,1800,1076));out.save(D/'candidate_comparison.jpg',quality=95)
