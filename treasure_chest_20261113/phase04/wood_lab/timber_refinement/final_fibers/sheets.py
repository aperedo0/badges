from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,numpy as np,sys
D=Path(__file__).resolve().parent;W=D.parent
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
except OSError:font=ImageFont.load_default()
def row(items,out,wh=(720,480)):
 im=Image.new('RGB',(wh[0]*len(items),wh[1]+36),'#202020');dr=ImageDraw.Draw(im)
 for i,(p,label) in enumerate(items):
  if not isinstance(p,Image.Image):p=Image.open(p).convert('RGB')
  a=ImageOps.contain(p,wh);im.paste(a,(i*wh[0]+(wh[0]-a.width)//2,36+(wh[1]-a.height)//2));dr.text((i*wh[0]+10,9),label,font=font,fill='white')
 im.save(D/out,quality=96)
def rect(p):
 q=np.array(json.loads((W/'grain_hierarchy/comparison_geometry.json').read_text())['model_quad']);return Image.open(p).convert('RGB').transform((720,480),Image.Transform.QUAD,tuple(q.ravel()),Image.Resampling.BICUBIC)
if __name__=='__main__':
 if sys.argv[1]=='light':row([(D/'plank_old.png','Starting V lighting'),(D/'plank_balanced.png','Only front fill rebalanced')],'lighting_comparison.jpg',(1000,500))
 else:
  keys=sys.argv[1:];row([(W/'grain_hierarchy/reference_rectified.png','Owner reference')]+[(rect(W/k/'close_balanced.png'),k) for k in keys],'structure_comparison.jpg')
  for k in keys:
   im=Image.open(W/k/'close_balanced.png').convert('RGB');im.crop((285,170,850,555)).save(D/(k+'_native.jpg'),quality=99)
