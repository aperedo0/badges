"""Real Home screenshots, native zooms, fixed-frame still and reference comparison."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,binary_erosion,distance_transform_edt
sys.path.insert(0,str(Path(__file__).resolve().parent))
from solve import to_screen
ROOT=Path(__file__).resolve().parents[1]
kind,folder=sys.argv[1:3];BASE=ROOT/kind;OUT=BASE/folder
M=json.loads((BASE/'source/mapping.json').read_text());records=M['meshes']
P=np.concatenate([np.load(BASE/'source'/f"{r['name']}.npz")['points'] for r in records]);scr=to_screen(P);lo=scr.min(0);hi=scr.max(0)
im=Image.open(OUT/'app.png').convert('RGB');ref=Image.open(BASE/'source/reference.png').convert('RGB')
box=(303,320,903,970);crop=im.crop(box);crop.save(OUT/'home_crop.png')
cut=ref.crop(tuple(M['reference_bounds']))
h=round(hi[1]-lo[1]);cut=cut.resize((round(cut.width*h/cut.height),h),Image.Resampling.LANCZOS)
left=Image.new('RGB',crop.size,'#08090b');left.paste(cut,((left.width-cut.width)//2,round(lo[1]-box[1])))
panel=Image.new('RGB',(1200,700),'#08090b');panel.paste(left,(0,50));panel.paste(crop,(600,50));draw=ImageDraw.Draw(panel)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
draw.text((25,14),kind.title()+': your reference',font=font,fill='white');draw.text((625,14),'Actual Home render',font=font,fill='white');panel.save(OUT/'reference_vs_app.png')
native=tuple(np.r_[np.floor(lo-5),np.ceil(hi+5)].astype(int));im.crop(native).resize((2*(native[2]-native[0]),2*(native[3]-native[1])),Image.Resampling.NEAREST).save(OUT/'surface_zoom.png')
im.crop((303,710,903,975)).save(OUT/'floor_gap.png')
mapping=np.load(OUT/'texture_mapping.npz');pos=mapping['screen'];mask=binary_erosion(mapping['cover'],iterations=8)
actual=np.asarray(im,float)/255;obs=np.stack([map_coordinates(actual[...,c],[pos[...,1]-.5,pos[...,0]-.5],order=1,mode='nearest') for c in range(3)],-1)
err=np.abs(obs[mask]-mapping['target'][mask])*255
(OUT/'app_color_comparison.json').write_text(json.dumps({'mean_absolute_rgb_error':err.mean(0).tolist(),'mean_error':float(err.mean()),'p95':float(np.percentile(err,95)),'note':'Diagnostics only; native app crops decide acceptance.'},indent=2)+'\n')
# Fixed Home art frame, the same 6.03 units = 108/120 width convention.
center=np.array([540,656])*47/60+[180,70];side=586*120/108*47/60;artbox=tuple(np.round(np.r_[center-side/2,center+side/2]).astype(int))
art=im.crop(artbox);SS=4;alpha=Image.new('L',(art.width*SS,art.height*SS),0);draw=ImageDraw.Draw(alpha)
for r in records:
    d=np.load(BASE/'source'/f"{r['name']}.npz");p=(to_screen(d['points'])-artbox[:2])*SS
    for tri in d['faces']:draw.polygon([tuple(v) for v in p[tri]],fill=255)
alpha=alpha.resize(art.size,Image.Resampling.LANCZOS);av=np.asarray(alpha,float)/255;rgb=np.asarray(art,float)/255
_,(iy,ix)=distance_transform_edt(av>.01,return_indices=True);bg=rgb[iy,ix]
rgb=np.clip((rgb-bg*(1-av[...,None]))/np.maximum(av[...,None],.03),0,1)
rgba=Image.fromarray(np.dstack([np.uint8(rgb*255+.5),np.uint8(av*255+.5)]),'RGBA').convert('RGBa').resize((600,600),Image.Resampling.LANCZOS).convert('RGBA')
rgba.save(OUT/f'BadgeArt_{kind}.png',optimize=True)
small=rgba.convert('RGBa').resize((120,120),Image.Resampling.LANCZOS).convert('RGBA')
tile=Image.new('RGB',(240,120),'#111315');tile.paste(small,(0,0),small);light=Image.new('RGB',(120,120),'#eceef1');light.paste(small,(0,0),small);tile.paste(light,(120,0));tile.save(OUT/'40pt_proof.png')
print(kind,'app mean RGB error',err.mean(0),'native projected bounds',lo,hi)
