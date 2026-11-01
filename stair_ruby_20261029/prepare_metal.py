"""Prepare measured metal without abrupt mirror flashes."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,distance_transform_edt
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip()
GAIN=.05

def decode(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
def polygon(points,size):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
trace=json.loads((C/'trace.json').read_text());cfg=json.loads((R/'design.json').read_text());D=np.load(C/'geometry.npz');W,H=trace['reference_size']
reference=np.asarray(Image.open(R/'reference.png').convert('RGB'),float)/255
backup=C/'approved_textures';backup.mkdir(exist_ok=True)
for p in (C/'textures').glob('*.png'):
 if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
meta={'mode':'calibration','calibration_gain':GAIN,'edge_colors':{'silver_edge':[.18,.20,.24],'gold_edge':[.30,.11,.035],'blue_edge':[.018,.06,.14]},'edge_roughness':{'silver_edge':.38,'gold_edge':.40,'blue_edge':.30},'method':'Measured physical metal with broad continuous reflections'}
(C/'metal_finish.json').write_text(json.dumps(meta,indent=2)+'\n')
for role in (['surface'] if cfg.get('dynamic_gems') else ['surface','star']):
 if not (backup/(role+'_color.png')).exists():continue
 old_color=decode(np.asarray(Image.open(backup/(role+'_color.png')).convert('RGB'),float)/255)
 old_emit=decode(np.asarray(Image.open(backup/(role+'_emission.png')).convert('RGB'),float)/255)*8
 N=old_color.shape[0];ty,tx=np.mgrid[:N,:N];rx=(tx+.5)*W/N;ry=(ty+.5)*H/N
 rgb=np.stack([map_coordinates(reference[...,j],[ry,rx],order=1,mode='nearest') for j in range(3)],-1);lum=rgb@np.array([.2126,.7152,.0722])
 gem=map_coordinates(D['detail_gem_mask'].astype(float),[ry,rx],order=0,mode='nearest')>.5
 valid=gem.copy() if role=='star' else map_coordinates(D['mask'].astype(float),[ry,rx],order=0,mode='nearest')>.5
 category=np.ones((N,N),np.int8);category[rgb[...,2]>rgb[...,0]*1.15]=2
 if cfg.get('nonmetal_blue'):category[(rgb[...,2]>rgb[...,0]*1.12)|(lum<.08)]=0
 if cfg.get('metal_hue')=='bronze':category[(rgb[...,0]>rgb[...,2]*1.4)&(rgb[...,0]>.1)]=3
 for region in cfg.get('nonmetal_regions',[]):
  field=map_coordinates(polygon(region,[W,H]).astype(float),[ry,rx],order=0,mode='nearest')>.5;category[field]=0
 for region in cfg.get('metal_regions',[]):
  field=map_coordinates(polygon(region,[W,H]).astype(float),[ry,rx],order=0,mode='nearest')>.5;category[field]=3 if cfg.get('metal_hue')=='bronze' else 1
 if role=='surface':
  category[gem]=0
  bezel=map_coordinates(D['detail_bezel_mask'].astype(float),[ry,rx],order=0,mode='nearest')>.5;category[bezel]=3 if cfg.get('metal_hue')=='bronze' else 1
 else:category[:]=1 if cfg.get('gems_metal') else 4
 category[~valid]=0;desired=np.zeros((N,N,3));rough=np.full((N,N),.53)
 for cat,color,roughness in [(1,[.23,.26,.30],.36),(2,[.025,.09,.22],.26),(3,[.30,.13,.045],.38),(4,[.06,.16,.30],.18)]:
  selected=category==cat;desired[selected]=color;rough[selected]=roughness
 grain=gaussian_filter(lum,.8)-gaussian_filter(lum,3);desired*=1+np.clip(grain,-.1,.1)[...,None]*.08
 target=old_emit+old_color*.4
 _,nearest=distance_transform_edt(~valid,return_indices=True)
 for array in [desired,rough]:array[~valid]=array[tuple(nearest[:,~valid])]
 np.savez_compressed(C/('metal_'+role+'.npz'),desired=desired,target=target,approved_color=old_color,approved_emission=old_emit,category=category,valid=valid,rx=rx,ry=ry,roughness=rough)
 if role=='surface':
  smooth_height=gaussian_filter(D['height'],10.);dy,dx=np.gradient(smooth_height);p=D['reference_points'];scale=trace['reference_scale']
  gx=map_coordinates(dx,[p[:,1],p[:,0]],order=1,mode='nearest')/scale;gy=map_coordinates(dy,[p[:,1],p[:,0]],order=1,mode='nearest')/scale
  slopes=np.c_[-gx,gy];magnitude=np.linalg.norm(slopes,axis=1);slopes*=np.minimum(1,.48/np.maximum(magnitude,1e-8))[:,None]
  hints=np.c_[slopes,np.ones(len(p))];hints/=np.maximum(np.linalg.norm(hints,axis=1)[:,None],1e-8);back=hints.copy();back[:,2]*=-1
  metal_vertex=map_coordinates(gaussian_filter((category>0).astype(float),1),[p[:,1]*N/H,p[:,0]*N/W],order=1,mode='nearest')>.15
  np.savez_compressed(C/'polished_normals.npz',normals=np.vstack([hints,back]).astype(np.float32),metal=np.r_[metal_vertex,metal_vertex])
 Image.fromarray(encode(desired*GAIN)).save(C/'textures'/(role+'_color.png'));Image.fromarray(np.zeros((N,N,3),np.uint8)).save(C/'textures'/(role+'_emission.png'));Image.fromarray(np.uint8(rough*255+.5)).save(C/'textures'/(role+'_roughness.png'))
 print(key,role,'metal texels',int((category>0).sum()),flush=True)
