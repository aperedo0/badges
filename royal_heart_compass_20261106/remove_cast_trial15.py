"""Remove the cast support that failed the native side view review."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent;C=R/'ruby_crown/candidate15';groups=json.loads((C/'groups.json').read_text());keep=[i for i,g in enumerate(groups) if not g['name'].startswith('Ruby continuous cast acanthus foundation')];removed=[g['name'] for i,g in enumerate(groups) if i not in keep];assert len(removed)==4
for name in ['geometry.npz','blender_geometry.npz']:
 data=np.load(C/name);out={}
 for new,old in enumerate(keep):
  for suffix in ['points','triangles','normals','uv']:
   key=f'{old}_{suffix}'
   if key in data:out[f'{new}_{suffix}']=data[key]
 np.savez_compressed(C/name,**out)
(C/'groups.json').write_text(json.dumps([groups[i] for i in keep],indent=2));report=json.loads((C/'cloth_appearance_fit.json').read_text());report.update(all_geometry_and_corner_attributes_preserved=False,all_retained_geometry_and_corner_attributes_preserved=True,rejected_cast_supports_removed=removed,reason='Native14turn showed flat gold panels from the cast support. Retain individual sculpted leaves.');(C/'cloth_appearance_fit.json').write_text(json.dumps(report,indent=2));print('Removed four failed cast supports. All remaining gold and optical geometry preserved.')
