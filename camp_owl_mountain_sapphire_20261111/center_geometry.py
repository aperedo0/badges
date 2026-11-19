"""Bake the measured horizontal center into vertices while retaining source UVs."""
from pathlib import Path
import json,sys
import numpy as np
R=Path(__file__).resolve().parent
for slug,candidate in [tuple(a.split(':')) for a in sys.argv[1:]]:
 C=R/slug/candidate;note=C/'center_validation.json'
 if note.exists():continue
 D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text())
 vertices=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']])
 shift=float((vertices[:,0].min()+vertices[:,0].max())/2)
 for p in M['parts']:D[p['name']+'_v'][...,0]-=shift
 M['units']['axis']+=shift/M['units']['S']
 np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
 note.write_text(json.dumps(dict(baked_x_translation=-shift,scale_unchanged=True,identity_node_transforms=True,uvs_and_normals_unchanged=True,pixel_mapping_preserved_by_updated_axis=True),indent=2)+'\n')
 print(slug,'centered by',-shift,flush=True)
