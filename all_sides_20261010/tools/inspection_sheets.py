from pathlib import Path
import sys
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_erosion,binary_dilation
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'manifest.json').read_text());sel=json.loads((ROOT/(sys.argv[sys.argv.index('--selection')+1] if '--selection' in sys.argv else 'selection.json')).read_text())
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
camera=np.array([0.,1.8,23.]);forward=np.array([0.,-.55,0.])-camera;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
def project(p):
 d=p-camera;z=d@forward
 return np.stack([540+2250*(d@right)/z,720-2250*(d@up)/z],-1)*47/60+[180,70]
for tier,num in sel.items():
 w=Path(m[tier]['work']);out=w/'candidates'/num;review=out/'review';review.mkdir(exist_ok=True)
 for version in ['current','updated']:
  for pose in ['right','back','left']:
   folder=ROOT/'inspection_models'/version/tier/pose;photo=folder/'app.png'
   if not photo.exists():continue
   cached=review/(version+'_'+pose+'_full_4x.png')
   if cached.exists() and cached.stat().st_mtime>max(photo.stat().st_mtime,(folder/'geometry.npz').stat().st_mtime):continue
   d=np.load(folder/'geometry.npz');screen=project(d['points']);im=Image.open(photo).convert('RGB');mask=Image.new('L',im.size);draw=ImageDraw.Draw(mask)
   for tri in d['faces']:draw.polygon([tuple(p) for p in screen[tri]],fill=255)
   a=np.array(mask)>0;edge=binary_dilation(a^binary_erosion(a),iterations=12);ys,xs=np.where(a);box=(xs.min()-16,ys.min()-16,xs.max()+17,ys.max()+17)
   crop=im.crop(box);crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST).save(review/(version+'_'+pose+'_full_4x.png'))
   patches=[]
   for y in range(max(0,box[1]),min(im.height,box[3]),150):
    for x in range(max(0,box[0]),min(im.width,box[2]),150):
     if edge[y:y+150,x:x+150].any():patches.append((x,y))
   for k in range(0,len(patches),4):
    sheet=Image.new('RGB',(1200,1260),'#101419');sd=ImageDraw.Draw(sheet)
    for i,(x,y) in enumerate(patches[k:k+4]):
     cell=im.crop((x,y,x+150,y+150)).resize((600,600),Image.Resampling.NEAREST);xx=(i%2)*600;yy=(i//2)*630;sheet.paste(cell,(xx,yy+30));sd.text((xx+8,yy+3),tier+' '+version+' '+pose+' '+str((x,y)),font=font,fill='white')
    sheet.save(review/(version+'_'+pose+'_edges4x_'+str(k//4+1)+'.png'))
 # Same-size app comparisons use front as installed and the large side/back inspection copies.
 sheet=Image.new('RGB',(4*606,2*800+95),'#101419');sd=ImageDraw.Draw(sheet)
 for j,version in enumerate(['current','updated']):
  for i,pose in enumerate(['front','right','back','left']):
   path=(w/'current/front.png' if version=='current' else out/'front.png') if pose=='front' else ROOT/'inspection_models'/version/tier/pose/'app.png'
   if path.exists():sheet.paste(Image.open(path).crop((300,180,906,980)),(i*606,j*800+95))
   sd.text((i*606+16,j*800+100),('CURRENT' if j==0 else 'UPDATED')+' '+pose.upper(),font=font,fill='#d9e2ed')
 sd.text((24,20),tier.upper()+' - FRONT / RIGHT / BACK / LEFT IN THE APP',font=font,fill='white')
 sd.text((24,56),'Side and rear models held at full size for inspection. The actual Home scroll turn is captured separately.',font=font,fill='#a4b0c0')
 sheet.save(review/'fullsize_comparison.png')
 print(tier,'inspection sheets updated')
