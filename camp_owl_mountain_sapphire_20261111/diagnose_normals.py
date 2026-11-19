from pathlib import Path
import json,shutil
import numpy as np
R=Path(__file__).resolve().parent;B=R/'campfire_night';a=B/'candidate10';c=B/'candidate11';c.mkdir(exist_ok=True)
for p in a.iterdir():
 if p.is_file():shutil.copy2(p,c/p.name)
shutil.copytree(a/'textures',c/'textures',dirs_exist_ok=True)
D=dict(np.load(c/'parts.npz'));M=json.loads((c/'parts.json').read_text());changed=0
for p in M['parts']:
 if p['name']=='outer_gold_setting':continue
 n=p['name'];normals=D[n+'_n'];mi=D[n+'_m']; gold=p['materials'].index('Gold') if 'Gold' in p['materials'] else -1
 sel=mi==gold
 normal=normals[sel];normal[...,0:2]=0;normal[...,2]=np.where(normal[...,2]>=0,1,-1);normals[sel]=normal;changed+=int(sel.sum())
np.savez_compressed(c/'parts.npz',**D)
(c/'normal_diagnosis.json').write_text(json.dumps(dict(source='candidate10',only_fine_gold_normals_changed=True,flat_normals_for_diagnosis=True,positions_uvs_materials_textures_unchanged=True,changed_faces=changed,native_review_pending=True),indent=2)+'\n')
g=json.loads((R/'gallery.json').read_text());row=next(q for q in g if q['slug']=='campfire_night');row['candidate']='candidate11';(R/'gallery.json').write_text(json.dumps(g,indent=2)+'\n')
print('Prepared flat normal cause test:',changed)
