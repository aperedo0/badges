from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageOps
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;root=P.parents[1];C=W/'R_layers_full'
meta=json.loads((D/'comparison_geometry.json').read_text())
def rect(path):return Image.open(path).convert('RGB').transform((720,480),Image.Transform.QUAD,tuple(np.array(meta['model_quad']).ravel()),Image.Resampling.BICUBIC)
def panel(items,out,size):
 canvas=Image.new('RGB',(len(items)*size[0],size[1]+34),'#202020');draw=ImageDraw.Draw(canvas)
 for i,(im,label) in enumerate(items):
  if not isinstance(im,Image.Image):im=Image.open(im).convert('RGB')
  im=ImageOps.contain(im,size);x=i*size[0];canvas.paste(im,(x+(size[0]-im.width)//2,34+(size[1]-im.height)//2));draw.text((x+12,12),label,fill='white')
 canvas.save(D/out,quality=95)
panel([(D/'reference_rectified.png','Reference'),(D/'current_P_rectified.png','Before'),(rect(C/'cinema_close.png'),'Saved test plank')],'owner_comparison.jpg',(720,480))
panel([(root/'reference.png','Reference'),(W/'P_physical_fractures/cinema_full.png','Before: one plank'),(C/'cinema_full.png','Saved: one plank only')],'owner_full_chest.jpg',(600,600))
panel([(C/'neutral_close.png','Neutral light'),(C/'clay_graze.png','Real geometry with normal map removed')],'owner_relief.jpg',(700,520))
