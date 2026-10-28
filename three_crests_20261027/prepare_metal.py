"""Prepare polished metal and a dim physical calibration render."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,distance_transform_edt
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
GAIN=.05
def decode(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
trace=json.loads((C/'trace.json').read_text());cfg=json.loads((R/'design.json').read_text());D=np.load(C/'geometry.npz');W,H=trace['reference_size']
reference=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255
refinement=json.loads((C/'refinement.json').read_text()) if (C/'refinement.json').exists() else {}
backup=C/'approved_textures';backup.mkdir(exist_ok=True)
for p in (C/'textures').glob('*.png'):
 if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
meta={'mode':'calibration','calibration_gain':GAIN,'edge_colors':{'silver_edge':[.32,.36,.42],'gold_edge':[.64,.32,.065],'blue_edge':[.025,.095,.23]},'edge_roughness':{'silver_edge':.20,'gold_edge':.20,'blue_edge':.18},'method':'Physical metallic reflections fitted against the approved front under the actual studio light'}
if refinement.get('gentle_sword_metal'):
 meta['edge_colors']={'silver_edge':[.19,.215,.25],'blue_edge':[.018,.065,.15]}
 meta['edge_roughness']={'silver_edge':.40,'blue_edge':.36}
 meta['refinement']='Broader reflections with less abrupt angular brightening'
(C/'metal_finish.json').write_text(json.dumps(meta,indent=2)+'\n')
def polygon(points,size):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
for role in ['surface','star']:
 if not (backup/(role+'_color.png')).exists():continue
 old_color=decode(np.asarray(Image.open(backup/(role+'_color.png')).convert('RGB'),float)/255)
 old_emit=decode(np.asarray(Image.open(backup/(role+'_emission.png')).convert('RGB'),float)/255)*8
 N=old_color.shape[0];ty,tx=np.mgrid[:N,:N]
 if role=='surface':rx=(tx+.5)*W/N;ry=(ty+.5)*H/N
 else:
  outline=np.array(cfg['facets'][0]['outline']);lo=outline.min(0)-8;hi=outline.max(0)+8
  rx=lo[0]+(tx+.5)*(hi[0]-lo[0])/N;ry=lo[1]+(ty+.5)*(hi[1]-lo[1])/N
 rgb=np.stack([map_coordinates(reference[...,j],[ry,rx],order=1,mode='nearest') for j in range(3)],-1);lum=rgb@np.array([.2126,.7152,.0722])
 valid=map_coordinates(D['mask'].astype(float),[ry,rx],order=0,mode='nearest')>.5
 category=np.ones((N,N),np.int8)
 if key=='winged_sword':
  blue=(abs(rx-626)/39+abs(ry-312)/75<1.02)|((abs(rx-626)<39)&(ry>139)&(ry<260));category[blue]=2
 elif key=='crescent_ocean':
  blue=rgb[...,2]>rgb[...,0]*1.15;category[blue]=2
  if role=='surface':
   ellipse=((rx-891)/253)**2+((ry-479)/254)**2<1
   field=ellipse&(((rgb[...,2]>rgb[...,0]*1.12)&(rgb[...,2]>rgb[...,1]*1.03))|(lum<.10))
   category[field]=0
   outline=np.array(cfg['facets'][0]['outline']);star_mask=polygon(outline,[W,H]);star=map_coordinates(star_mask.astype(float),[ry,rx],order=0,mode='nearest')>.5;category[star]=0
 elif key=='mountain_crest':
  radius=np.sqrt((rx-650)**2+(ry-551)**2)
  gold=((radius>400)&(radius<485))|((ry>650)&(abs(rx-650)>520-(ry-650)*1.15))
  for feature in cfg.get('facets',[]):gold|=map_coordinates(polygon(feature['outline'],[W,H]).astype(float),[ry,rx],order=0,mode='nearest')>.5
  gold|=map_coordinates(polygon([[651,699],[817,880],[650,1106],[486,881]],[W,H]).astype(float),[ry,rx],order=0,mode='nearest')>.5
  category[:]=0;category[gold]=3
 if role=='star':
  outline=np.array(cfg['facets'][0]['outline']);star=map_coordinates(polygon(outline,[W,H]).astype(float),[ry,rx],order=0,mode='nearest')>.5;valid &= star
 category[~valid]=0
 desired=np.zeros((N,N,3));rough=np.full((N,N),.53)
 for cat,color,roughness in [(1,[.48,.52,.58],.20),(2,[.032,.12,.32],.19),(3,[.62,.32,.075],.20)]:
  selected=category==cat;desired[selected]=color;rough[selected]=roughness
 if role=='star':rough[valid]=.12
 if key=='winged_sword':rough[(category==2)&(ry<265)]=.22;rough[(category==2)&(ry>265)]=.12
 if refinement.get('gentle_sword_metal'):
  rough[category==1]=.40;rough[category==2]=.34
  desired*=.48
 # Small neutral reflectance grain retains the original finish without fixed light bands.
 grain=gaussian_filter(lum,.8)-gaussian_filter(lum,3)
 desired*=1+np.clip(grain,-.1,.1)[...,None]*.08
 target=old_emit+old_color*.4
 # Fill atlas padding from the nearest surface for stable mipmaps.
 _,nearest=distance_transform_edt(~valid,return_indices=True)
 for array in [desired,rough]:array[~valid]=array[tuple(nearest[:,~valid])]
 np.savez_compressed(C/('metal_'+role+'.npz'),desired=desired,target=target,approved_color=old_color,approved_emission=old_emit,category=category,valid=valid,rx=rx,ry=ry,roughness=rough)
 if role=='surface':
  smooth_height=gaussian_filter(D['height'],10.);dy,dx=np.gradient(smooth_height);p=D['reference_points'];scale=trace['reference_scale']
  gx=map_coordinates(dx,[p[:,1],p[:,0]],order=1,mode='nearest')/scale;gy=map_coordinates(dy,[p[:,1],p[:,0]],order=1,mode='nearest')/scale
  slope_limit=.48 if refinement.get('gentle_sword_metal') else .82
  slopes=np.c_[-gx,gy];slopes*=np.minimum(1,slope_limit/np.maximum(np.linalg.norm(slopes,axis=1),1e-8))[:,None]
  hints=np.c_[slopes,np.ones(len(p))];hints/=np.maximum(np.linalg.norm(hints,axis=1)[:,None],1e-8)
  back=hints.copy();back[:,2]*=-1
  metal_vertex=map_coordinates(gaussian_filter((category>0).astype(float),1),[p[:,1]*N/H,p[:,0]*N/W],order=1,mode='nearest')>.15
  np.savez_compressed(C/'polished_normals.npz',normals=np.vstack([hints,back]).astype(np.float32),metal=np.r_[metal_vertex,metal_vertex])
 Image.fromarray(encode(desired*GAIN)).save(C/'textures'/(role+'_color.png'))
 Image.fromarray(np.zeros((N,N,3),np.uint8)).save(C/'textures'/(role+'_emission.png'))
 Image.fromarray(np.uint8(rough*255+.5)).save(C/'textures'/(role+'_roughness.png'))
 print(key,role,'polished metal texels',int((category>0).sum()),flush=True)
