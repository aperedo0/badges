import sys,json,subprocess,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron');sys.path.insert(0,str(r/'scripts'));import measure_smoothness as ms
for pose in (0,20,45):
 images={f'iron_{rig}':str(r/f'proof/renders/iron_{rig}_{pose}.png') for rig in ('stage','harsh') if (r/f'proof/renders/iron_{rig}_{pose}.png').exists()}
 cmd=[sys.executable,str(r/'scripts/measure_smoothness.py'),'--emblem',str(r/'proof/emblem_iron.json'),'--pose',str(pose),'--out',str(r/f'proof/smoothness_pose{pose:02d}.json')]+[f'{k}={v}' for k,v in images.items()]
 with open(r/f'proof/smoothness_pose{pose:02d}.txt','w') as out:subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,check=True)
 # Individual zooms cover every visible plane, including narrow side facets.
 emblem=ms.Emblem(r/'proof/emblem_iron.json');facets,px=emblem.facet_masks(pose,erode=1,min_pixels=25)
 full=Image.open(r/f'proof/renders/iron_harsh_{pose}.png').convert('RGB');tiles=[]
 for gi,spec in sorted(facets.items()):
  ys,xs=np.nonzero(spec['full']);box=(max(0,int(xs.min())-5),max(0,int(ys.min())-5),min(full.width,int(xs.max())+6),min(full.height,int(ys.max())+6))
  crop=full.crop(box);crop=crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST)
  dest=r/f'proof/facet_crops/pose{pose:02d}';dest.mkdir(parents=True,exist_ok=True);crop.save(dest/f'facet_{gi:02d}.png')
  tile=Image.new('RGB',(330,370),(30,30,30));draw=ImageDraw.Draw(tile);draw.text((8,8),f'Iron facet {gi}; pose {pose}; zoom 4x',fill='white');crop.thumbnail((314,335));tile.paste(crop,(8,30));tiles.append(tile)
 sheet=Image.new('RGB',(330*3,370*((len(tiles)+2)//3)),(30,30,30))
 for i,tile in enumerate(tiles):sheet.paste(tile,((i%3)*330,(i//3)*370))
 sheet.save(r/f'proof/all_facets_pose{pose:02d}.png')
 # Rim and inset unmodified 4x pixel crops.
 for name,box in [('rim_left',(246,470,318,850)),('rim_top',(440,373,640,427)),('rim_right',(760,470,835,850)),('inset_left',(319,510,425,790)),('inset_right',(660,510,758,790)),('whole_crystal',(417,449,665,883))]:
  crop=full.crop(box);crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST).save(r/f'proof/{name}_zoom_pose{pose:02d}.png')
for pose in (0,20):
 cmd=[sys.executable,str(r/'scripts/measure_smoothness.py'),'--emblem',str(r/'proof/emblem_silver.json'),'--pose',str(pose),'--out',str(r/f'proof/smoothness_silver_pose{pose:02d}.json')]+[f'silver_{rig}={r}/proof/renders/silver_{rig}_{pose}.png' for rig in ('stage','harsh')]
 with open(r/f'proof/smoothness_silver_pose{pose:02d}.txt','w') as out:subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,check=True)
subprocess.run([sys.executable,str(r/'scripts/make_proof_sheets.py'),str(r/'proof/renders'),str(r/'proof')],check=True)
subprocess.run([sys.executable,str(r/'scripts/compare_renders.py'),str(r/'proof/renders'),str(r/'proof/render_diff_silver_vs_iron.json'),str(r/'proof')],check=True)
# Same crop, native resolution and placement in both columns: no rescale between tiers.
box=(230,355,850,1015);sheet=Image.new('RGB',(1260,700),(20,20,20));draw=ImageDraw.Draw(sheet)
for i,key in enumerate(('silver','iron')):
 draw.text((i*640+10,8),f'{key.title()} - same camera, scale and app point lights',fill='white');sheet.paste(Image.open(r/f'proof/renders/{key}_harsh_0.png').convert('RGB').crop(box),(i*640,30))
sheet.save(r/'proof/silver_vs_iron_same_scale.png')
shutil.copy2(r/'proof/renders/iron_harsh_0.png',r/'proof/iron_front_app_lighting.png');shutil.copy2(r/'proof/renders/iron_harsh_45.png',r/'proof/iron_three_quarter_app_lighting.png')
# Surface inputs are uniformly constant: no baked noise can reach the shader.
textures={}
for p in (r/'mobile/textures').glob('*.png'):
 a=np.array(Image.open(p).convert('RGB'));colors=np.unique(a.reshape(-1,3),axis=0);assert len(colors)==1,(p,len(colors));textures[p.name]={'size':list(a.shape[:2][::-1]),'unique_rgb_colors':len(colors),'rgb8':colors[0].tolist()}
(r/'proof/texture_uniformity.json').write_text(json.dumps(textures,indent=2))
print('Proof sheets, individual facet/rim/inset crops, smoothness numbers, and uniform-texture verification complete.')
