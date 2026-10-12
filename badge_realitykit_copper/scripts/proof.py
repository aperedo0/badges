"""Native app crops and reference comparisons; no Blender image is used as proof."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates, binary_erosion
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/sys.argv[1]
app=Image.open(OUT/'app.png').convert('RGB')
ref=Image.open(ROOT/'source/reference.png').convert('RGB')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
box=(403,325,803,940)
reference=Image.new('RGB',(400,615),'#08090b')
cut=ref.crop((126,213,835,1404));cut.thumbnail((240,403),Image.Resampling.LANCZOS)
reference.paste(cut,((400-cut.width)//2,49))
crop=app.crop(box);crop.save(OUT/'home_crop.png')
panel=Image.new('RGB',(800,665),'#08090b');panel.paste(reference,(0,50));panel.paste(crop,(400,50))
d=ImageDraw.Draw(panel);d.text((30,13),'Your reference',font=font,fill='white');d.text((430,13),'Actual Home render',font=font,fill='white')
panel.save(OUT/'reference_vs_app.png')
app.crop((474,366,735,790)).resize((783,1272),Image.Resampling.NEAREST).save(OUT/'surface_zoom.png')
app.crop((403,723,803,967)).save(OUT/'floor_gap.png')
if '--images-only' in sys.argv:sys.exit(0)
# Compare colors strictly inside the projected geometry, away from antialiasing.
m=np.load(ROOT/'source/texture_mapping.npz');scr=m['screen'];mask=m['cover'];target=m['target'];rib=m['ribbon']
actual=np.asarray(app,float)/255
obs=np.stack([map_coordinates(actual[...,c],[scr[...,1]-.5,scr[...,0]-.5],order=1,mode='nearest') for c in range(3)],-1)
rows=[]
for k,name in [(1,'central'),(2,'right'),(3,'left')]:
    inside=binary_erosion(rib==k,iterations=8)
    err=np.abs(obs[inside]-target[inside])*255
    rows.append({'ribbon':name,'mean_absolute_rgb_error':err.mean(0).tolist(),'mean_error':float(err.mean()),'p95':float(np.percentile(err,95))})
(OUT/'app_color_comparison.json').write_text(json.dumps({'ribbons':rows,'note':'Diagnostics only. Same-size image and native crops decide visual acceptance.'},indent=2)+'\n')
print(json.dumps(rows,indent=2))
