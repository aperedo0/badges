from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageOps
D=Path(__file__).resolve().parent;W=D.parent;G=W/'grain_hierarchy'
meta=json.loads((G/'comparison_geometry.json').read_text())
def rect(path):return Image.open(path).convert('RGB').transform((720,480),Image.Transform.QUAD,tuple(np.array(meta['model_quad']).ravel()),Image.Resampling.BICUBIC)
items=[('Reference',Image.open(G/'reference_rectified.png').convert('RGB')),('Previous saved plank',rect(W/'R_layers_full/cinema_close.png')),('New structure, unchanged material',rect(W/'S_fiber_structure/cinema_close.png')),('Same structure, richer material',rect(W/'T_fiber_material/cinema_close.png'))]
out=Image.new('RGB',(1440,1028),'#202020');draw=ImageDraw.Draw(out)
for i,(label,im) in enumerate(items):x=i%2*720;y=i//2*514;out.paste(im,(x,y+34));draw.text((x+10,y+12),label,fill='white')
out.save(D/'comparison.jpg',quality=95)
