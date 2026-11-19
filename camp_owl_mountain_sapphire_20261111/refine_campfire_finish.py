"""Continue the saved cause test with bounded smooth metal normals."""
from pathlib import Path
import json,shutil,time
import numpy as np
R=Path(__file__).resolve().parent
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()<s['work_until_epoch']
B=R/'campfire_night';a=B/'candidate12';original=B/'candidate10';c=B/'candidate13';assert not c.exists();c.mkdir()
for name in ['parts.npz','parts.json','palette_enamel.json','center_validation.json','enamel_config.json']:
 if (a/name).exists():shutil.copy2(a/name,c/name)
shutil.copytree(a/'textures',c/'textures')
D=dict(np.load(c/'parts.npz'));O=np.load(original/'parts.npz');M=json.loads((c/'parts.json').read_text());changes=0
for p in M['parts']:
 if 'Enamel' not in p['materials'] or 'Gold' not in p['materials']:continue
 name=p['name'];materials=list(p['materials']);gi=materials.index('Gold');sel=D[name+'_m']==gi
 n=O[name+'_n'][sel].astype(float);flat=np.zeros_like(n);flat[...,2]=np.where(D[name+'_v'][sel].mean(1)[:,2]>=0,1,-1)[:,None]
 n=.30*n+.70*flat;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-9)
 D[name+'_n'][sel]=n.astype(np.float32)
 materials[gi]='SmoothGold';p['materials']=materials;changes+=int(sel.sum())
np.savez_compressed(c/'parts.npz',**D);(c/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
pal=json.loads((B/'palette_base.json').read_text());pal['SmoothGold']=dict(albedo=[.83,.43,.045],metallic=1,roughness=.30);(B/'palette_base.json').write_text(json.dumps(pal,indent=2)+'\n')
merged=dict(pal);merged.update(json.loads((c/'palette_enamel.json').read_text()));(c/'palette.json').write_text(json.dumps(merged,indent=2)+'\n')
(c/'finish_change.json').write_text(json.dumps(dict(source_geometry='candidate10',source_enamel='candidate12',geometry_and_uvs_unchanged=True,fine_border_normal_source_weight=.30,fine_border_normal_face_weight=.70,fine_gold_roughness=.30,broad_setting_and_gold_beads_unchanged=True,changed_faces=changes,native_review_pending=True),indent=2)+'\n')
(c/'NOTES.md').write_text('Continues the successful flat normal cause test with a bounded curved reflection on fine gold borders, while preserving the broad setting and gold beads. Restores amber and log colors through the saved narrower gold exclusion mask. Native finish and motion acceptance are pending.\n')
print('Prepared Campfire13:',changes,'fine border faces, geometry unchanged')
