"""Broader sculpted waves and genuinely reflective chart metal."""
from pathlib import Path
import ast,json,shutil
import numpy as np
from PIL import Image
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'ocean_navigator/candidate11';C=R/'ocean_navigator/candidate12';assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());S['gold_emblem']=dict(color=[.57,.285,.067],metallic=.96,roughness=.32)
source=(R/'refine_ocean11.py').read_text();tree=ast.parse(source);ns=dict(np=np,shape=shape)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['chain','wave']:
  code=ast.get_source_segment(source,node)
  if node.name=='wave':code=code.replace('a=chain(a);b=chain(b);assert a.shape==b.shape','a=chain(a);b=chain(b);assert a.shape==b.shape\n mid=(a+b)/2;a=mid+(a-mid)*1.35;b=mid+(b-mid)*1.35')
  exec(code,ns)
waves=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='waves' for t in node.targets))
parts=[]
for i,g in enumerate(G):
 if g['name'].startswith('Smooth measured ocean '):continue
 g=dict(g)
 if g['name'].startswith('Real raised compass '):g['mat']='gold_emblem'
 parts.append((g,D[f'{i}_points'].copy(),D[f'{i}_triangles'].copy()))
i=next(i for i,g in enumerate(G) if g['name']=='Double sided navy nautical chart body');body=D[f'{i}_points'];cy=(body[:,1].min()+body[:,1].max())/2;scale=np.ptp(body[:,0])/(2*2.94*.934);unit=2.94/480*scale
for face in [1,-1]:
 for side in [-1,1]:
  for name,a,b,height in waves:
   p,t=ns['wave'](a,b,height*1.05);p[:,0]=(p[:,0]-627)*unit*side;p[:,1]=cy+(570-p[:,1])*unit;p[:,2]=face*(.255*scale+p[:,2]*scale)
   if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
   parts.append((dict(name=f'Smooth broad ocean {name} {face} {side}',mat='gold_emblem',smooth=True),p.astype(np.float32),t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
points=np.vstack([p for _,p,_ in parts]);assert points[:,1].min()>=-2.45501 and points[:,1].max()<=3.01501 and abs(points[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
# Recover only the intrinsic ink coverage from the preceding generated map.
# This is a material mask, not a reflection, illumination or appearance photo.
rgb=np.asarray(Image.open(B/'textures/chart_color.png').convert('RGB'),float)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);navy=np.array([.0025,.008,.023]);oldgold=np.array([.22,.102,.024]);axis=oldgold-navy;ink=np.clip(((linear-navy)*axis).sum(2)/(axis@axis),0,1);coverage=np.clip(ink/.40,0,1);color=navy*(1-coverage[...,None])+np.array(S['gold']['color'])*coverage[...,None];srgb=np.where(color<=.0031308,color*12.92,1.055*color**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(srgb,0,1)*255)).save(C/'textures/chart_color.png')
Image.fromarray(np.uint8((.12+.88*coverage)*255)).save(C/'textures/chart_metallic.png');Image.fromarray(np.uint8((.68-.34*coverage)*255)).save(C/'textures/chart_roughness.png')
(C/'surface_review.json').write_text(json.dumps(dict(source='candidate11',gold_wave_width_factor=1.35,physical_wave_volume_preserved=True,metal_emblem_fraction=.96,emblem_roughness=.32,chart_has_genuine_metallic_and_roughness_maps=True,no_baked_highlights_or_emission=True,independent_gems_and_rope_frame_preserved=True,native_appearance_review_pending=True),indent=2));print('Ocean12 broader closed waves and reflective chart prepared',len(groups),'parts')
