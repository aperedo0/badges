"""Restore polished gold and give the wave crests broad real reflective faces."""
from pathlib import Path
import ast,json,shutil
import numpy as np
from PIL import Image
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'ocean_navigator/candidate12';C=R/'ocean_navigator/candidate13';assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());S=json.loads((B/'materials.json').read_text());source=(R/'refine_ocean11.py').read_text();tree=ast.parse(source);ns=dict(np=np,shape=shape)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['chain','wave']:
  code=ast.get_source_segment(source,node)
  if node.name=='wave':
   code=code.replace('a=chain(a);b=chain(b);assert a.shape==b.shape','a=chain(a);b=chain(b);assert a.shape==b.shape\n mid=(a+b)/2;a=mid+(a-mid)*1.35;b=mid+(b-mid)*1.35')
   code=code.replace('xy=a[j]*(1-u)+b[j]*u;dome=np.sin(np.pi*u)**.72*np.sin(np.pi*s)**.4','xy=a[j]*(1-u)+b[j]*u;roof=min(2*u,2*(1-u));roof=roof if roof<=.90 else .95-(1-roof)**2/.2;lift=min(height,np.linalg.norm(a[j]-b[j])*(2.94/480)*.35);dome=roof*np.sin(np.pi*s)**.4')
   code=code.replace('.025+height*dome','.025+lift*dome')
  exec(code,ns)
waves=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='waves' for t in node.targets));parts=[]
for i,g in enumerate(G):
 if g['name'].startswith('Smooth broad ocean '):continue
 g=dict(g)
 if g['mat']=='gold_emblem':g['mat']='gold'
 parts.append((g,D[f'{i}_points'].copy(),D[f'{i}_triangles'].copy()))
i=next(i for i,g in enumerate(G) if g['name']=='Double sided navy nautical chart body');body=D[f'{i}_points'];cy=(body[:,1].min()+body[:,1].max())/2;scale=np.ptp(body[:,0])/(2*2.94*.934);unit=2.94/480*scale
for face in [1,-1]:
 for side in [-1,1]:
  for name,a,b,height in waves:
   p,t=ns['wave'](a,b,height);p[:,0]=(p[:,0]-627)*unit*side;p[:,1]=cy+(570-p[:,1])*unit;p[:,2]=face*(.255*scale+p[:,2]*scale)
   if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
   parts.append((dict(name=f'Broad reflective ocean crest {name} {face} {side}',mat='gold',smooth=True),p.astype(np.float32),t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(S,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
old=R/'ocean_navigator/candidate11/textures/chart_color.png';shutil.copy2(old,C/'textures/chart_color.png');rgb=np.asarray(Image.open(old).convert('RGB'),float)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);navy=np.array([.0025,.008,.023]);axis=np.array([.22,.102,.024])-navy;ink=np.clip(((linear-navy)*axis).sum(2)/(axis@axis),0,1);coverage=np.clip(ink/.78,0,1)
Image.fromarray(np.uint8((.12+.88*coverage)*255)).save(C/'textures/chart_metallic.png');Image.fromarray(np.uint8((.68-.34*coverage)*255)).save(C/'textures/chart_roughness.png')
(C/'surface_review.json').write_text(json.dumps(dict(source='candidate12',uniform_matte_emblem_finish_rejected=True,overly_bold_chart_color_rejected=True,original_polished_gold_and_chart_color_restored=True,genuine_chart_metallic_maps_retained=True,wave_has_broad_sloping_faces_and_rounded_ridge=True,real_wave_slope=.7,no_normal_or_appearance_maps_on_waves=True,native_review_pending=True),indent=2));print('Ocean13 polished gold and broad wave faces prepared',len(groups),'parts')
