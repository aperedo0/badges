from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;phase=sys.argv[1];C=D/'aov'/phase;F=np.load(C/'passes.npz');scope=F['Iron_SurfaceAlpha'][:,:,0]>.999;stats=json.loads((C/'statistics.json').read_text());ref=Image.open(D.parents[1]/'reference.png').convert('RGB').crop((505,933,740,1024));items=[(ref,'Original reference'),(Image.open(C/'beauty.png').convert('RGB'),'Diagnostic beauty, matching camera')]
for name in F.files:
 a=F[name].copy()
 if 'Normal' in name:a=a*.5+.5
 elif name.startswith('Iron_Base'):a=np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
 a[~scope]=.16;im=Image.fromarray(np.uint8(np.clip(a[::-1],0,1)*255+.5));s=stats[name];label=name.replace('Iron_','')+'  '+('constant ' if max(s['std'])<1e-6 else '')+f"{min(s['min']):.3f} to {max(s['max']):.3f}";items.append((im,label));im.save(C/(name+'.png'))
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',13)
except OSError:font=ImageFont.load_default()
out=Image.new('RGB',(1680,1050),'#242424');dr=ImageDraw.Draw(out)
for i,(im,label) in enumerate(items):
 x=i%4*420;y=i//4*210;im=ImageOps.contain(im,(410,178),Image.Resampling.LANCZOS);out.paste(im,(x+(420-im.width)//2,y+29+(178-im.height)//2));dr.text((x+6,y+6),label,fill='white',font=font)
out.save(C/'diagnostic_sheet.jpg',quality=97);print('Saved AOV sheet',phase)
