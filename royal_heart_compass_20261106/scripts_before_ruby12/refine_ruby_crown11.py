"""Refine the preserved tenth crown using measured reference projection."""
from pathlib import Path
import json,shutil,numpy as np
from scipy.optimize import root
from ruby_reference_leaves import leaves
from reference_projection import CrownReference
from sculpted_gold import frame
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'ruby_crown/candidate10';C=R/'ruby_crown/candidate11'
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());spec=json.loads((B/'materials.json').read_text());spec['red_velvet']['color']=[.12,.0006,.008];spec['red_fold_velvet']=dict(spec['red_velvet']);spec['gold']['color']=[.70,.36,.10]
projector=CrownReference(D,G,627,1022,1010);gem_indices=[i for i,g in enumerate(G) if g['name']=='Large central ruby jewel independent gemstone'];front=next(i for i in gem_indices if D[f'{i}_points'][:,2].mean()>0);back=next(i for i in gem_indices if i!=front)
original=D[f'{front}_points'].astype(float);center=(original[:,1].min()+original[:,1].max())*.5
# The actual inner ruby is at Y550 through851 in the owner's photograph.
def trial(parameters,p=original):
 q=p.copy();q[:,1]=center+(q[:,1]-center)*parameters[0]+parameters[1];return q
def residual(parameters):
 pixel=projector.pixel(trial(parameters));return [pixel[:,1].min()-550,pixel[:,1].max()-851]
solution=root(residual,[.875,-.24]);assert solution.success
front_gem=trial(solution.x);front_gem[:,0]*=1.04
oldfront=np.c_[original,np.ones(len(original))];mirror=np.linalg.lstsq(oldfront,D[f'{back}_points'],rcond=None)[0];assert np.max(abs(oldfront@mirror-D[f'{back}_points']))<1e-5
back_gem=np.c_[front_gem,np.ones(len(front_gem))]@mirror
plane=np.linalg.lstsq(np.c_[front_gem[:4,:2],np.ones(4)],front_gem[:4,2],rcond=None)[0]
parts=[];removed=[]
for i,g in enumerate(G):
 name=g['name']
 if name.startswith('Reference flowing ruby acanthus') or name in ['Acanthus raised sculpted vein','Side fleur scroll','Pave gold bead seat','Central border brilliant','Ruby crown clean sculpted central gold setting']:
  removed.append(name);continue
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy();g=dict(g)
 if i==front:p=front_gem.astype(np.float32)
 if i==back:p=back_gem.astype(np.float32)
 if 'velvet cushion' in name:g['mat']='red_fold_velvet';g['cloth_grid']=[144,40]
 if name in ['Top fleur curved petal','Top fleur lower curl']:p[:,0]*=.76
 parts.append((g,p,t))

def append(name,p,t,face,material='gold',smooth=True):
 if face<0:p=np.c_[p,np.ones(len(p))]@mirror
 if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
 parts.append((dict(name=name,mat=material,smooth=smooth),p.astype(np.float32),t))
for face in [1,-1]:
 for side in [-1,1]:
  for j,(p,t) in enumerate(leaves()):
   if side>0:p[:,0]=1254-p[:,0];t=t[:,::-1]
   append(f'Ruby measured closed acanthus leaf {face} {side} {j}',projector.surface(p),t,face)
 outer=np.array([[627,467],[798,684],[627,905],[456,684]],float);inner=np.array([[627,550],[752,690],[627,851],[502,690]],float)
 p,t=frame(outer,inner,.10);append(f'Ruby measured continuous pave gold setting {face}',projector.plane_surface(p,plane),t,face)
 # Sixteen closely spaced brilliants per sloping edge, each a real convex cut.
 corners=(outer+inner)*.5
 for edge in range(4):
  for j,f in enumerate(np.linspace(.035,.965,16)):
   xy=corners[edge]*(1-f)+corners[(edge+1)%4]*f
   c=projector.plane_surface(np.array([[*xy,.112]]),plane)[0];normal=shape.norm([-plane[0],-plane[1],1]);shape.PARTS=[]
   shape.sphere('Pave bead seat',c-normal*.015,.035,N=10,M=6,scale=(1,1,.5))
   shape.gem('Pave optical brilliant',c,.028,.028,.043,'CrestGem_Ice',normal)
   for a in shape.PARTS:append(f'Ruby fine pave {face} {edge} {j} '+a['name'],a['p'],a['t'],face,a['mat'],a['smooth'])
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p;out[f'{i}_triangles']=t;groups.append(g)
allp=np.vstack([p for _,p,_ in parts]);assert allp[:,1].min()>=-2.45501 and allp[:,1].max()<=3.01501 and abs(allp[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(spec,indent=2));shutil.copy2(B/'textures/gold_roughness.png',C/'textures/gold_roughness.png')
(C/'foliage_report.json').write_text(json.dumps(dict(source='candidate10',generic_parts_replaced=len(removed),closed_new_leaves=60,reference_projector_scale=projector.k,reference_projector_floor=projector.bottom,gem_y_scale=float(solution.x[0]),gem_y_shift=float(solution.x[1]),pave_stones=128,all_upper_stones_remain_red=True,top_fleur_width_scale=.76,no_appearance_photo_maps=True),indent=2))
print('Ruby11',len(groups),'editable parts',sum(len(t) for _,_,t in parts),'triangles. Reference projected stone limits',projector.pixel(front_gem).min(0),projector.pixel(front_gem).max(0))
