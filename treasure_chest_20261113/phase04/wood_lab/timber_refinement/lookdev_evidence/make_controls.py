from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageFont
D=Path(__file__).resolve().parent;W=D.parent;R=D/'renders';meta=json.loads((W/'grain_hierarchy/comparison_geometry.json').read_text());q=np.array(meta['model_quad'])*1600/1200
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
except OSError:font=ImageFont.load_default()
def rect(f):return Image.open(f).convert('RGB').transform((720,480),Image.Transform.QUAD,tuple(q.ravel()),Image.Resampling.BICUBIC)
def sheet(items,name,wh=(720,480)):
 im=Image.new('RGB',(wh[0]*len(items),wh[1]+38),'#202020');d=ImageDraw.Draw(im)
 for i,(p,label) in enumerate(items):
  if not isinstance(p,Image.Image):p=Image.open(p).convert('RGB')
  a=ImageOps.contain(p,wh);im.paste(a,(i*wh[0]+(wh[0]-a.width)//2,38+(wh[1]-a.height)//2));d.text((i*wh[0]+10,9),label,font=font,fill='white')
 im.save(D/name,quality=95)
if all((R/(k+'.png')).exists() for k in ['baseline','direction','smaller_source']):sheet([(W/'grain_hierarchy/reference_rectified.png','Owner reference'),(rect(R/'baseline.png'),'Unchanged wood: existing light'),(rect(R/'direction.png'),'Only key direction changed'),(rect(R/'smaller_source.png'),'Same direction: smaller source')],'lighting_controls.jpg')
if (R/'raw_control.png').exists():
 for k in ['baseline','raw_control']:
  # Corresponding native pixels, no arbitrary sharpening or contrast operations.
  Image.open(R/(k+'.png')).crop((360,210,1110,720)).save(D/(k+'_native_crop.png'))
 sheet([(D/'baseline_native_crop.png','128 samples: denoised'),(D/'raw_control_native_crop.png','Same seed and samples: raw')],'denoise_control.jpg',(750,510))
