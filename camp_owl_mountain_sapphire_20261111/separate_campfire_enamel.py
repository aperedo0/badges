"""Give physical layers their own reference sampled enamel instead of a shared picture."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;C=R/'campfire_night/candidate16'
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());spec=json.loads((C/'PIECES.json').read_text());by={q['name']:q for q in spec['pieces']};mapping={}
def role(name):
 if name=='night_backplate':return 'NightField'
 if name=='purple_mountain_range':return 'EnamelMountain'
 if name=='green_campground':return 'EnamelGround'
 if name=='crescent_moon' or name.startswith('star_'):return 'EnamelMoonlight'
 if name.startswith('small_pine'):return 'EnamelSmallPines'
 if name.startswith('pine_') and name.endswith('top'):return 'EnamelPineTop'
 if name.startswith('pine_') and name.endswith('middle'):return 'EnamelPineMiddle'
 if name.startswith('pine_') and name.endswith('lower'):return 'EnamelPineLower'
 if name.endswith('trunk') or name in ['left_crossed_log','right_crossed_log','upright_front_log']:return 'EnamelWoodBody'
 if name in ['log_end_left','log_end_right','front_log_end']:return 'EnamelWoodEnd'
 if name=='outer_red_flame':return 'EnamelRedFire'
 if name=='middle_amber_flame':return 'EnamelAmberFire'
 if name=='inner_yellow_flame':return 'EnamelYellowFire'
 if name.startswith('stone_'):return 'EnamelStone'
 raise ValueError(name)
for p in M['parts']:
 if 'Enamel' not in p['materials']:continue
 name=p['name'];new=role(name);mapping[name]=new;p['materials']=[new if m=='Enamel' else m for m in p['materials']]
 q=by[name]
 if q.get('material')=='Enamel':q['material']=new
 for cell in q.get('cells',[]):
  if cell['material']=='Enamel':cell['material']=new
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n')
roles=sorted(set(mapping.values())|{'NightField'});config=dict(texture_px=1024,materials={n:dict(roughness=.18,max_display=.93,gold_exclusion_border_px=6) for n in roles});(C/'enamel_config.json').write_text(json.dumps(config,indent=2)+'\n');(C/'enamel_layer_roles.json').write_text(json.dumps(mapping,indent=2)+'\n');print('Separate physical enamel roles:',len(roles))
