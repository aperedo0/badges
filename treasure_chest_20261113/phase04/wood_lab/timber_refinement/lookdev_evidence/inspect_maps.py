from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageOps,ImageDraw
D=Path(__file__).resolve().parent;B=D.parent/'U_scan_fibers';out=Image.new('RGB',(1200,950),'#222222');draw=ImageDraw.Draw(out)
for i,role in enumerate(['albedo','roughness','normal']):
 im=Image.open(B/(role+'.png')).convert('RGB');q=ImageOps.contain(im,(1200,270));out.paste(q,((1200-q.width)//2,30+i*310));draw.text((10,10+i*310),role+' : unchanged latest baseline',fill='white')
out.save(D/'material_channels.jpg',quality=94)
files={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in B.iterdir() if f.is_file() and f.suffix in ['.blend','.png','.npz','.json']};(D/'source_fingerprints.json').write_text(json.dumps(files,indent=2))
