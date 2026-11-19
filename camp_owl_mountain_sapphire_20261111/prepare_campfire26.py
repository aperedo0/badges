"""Smooth traced pine curves within a measured reference tolerance."""
from pathlib import Path
import json,time
import numpy as np
from scipy.interpolate import splprep,splev
from shapely.geometry import Polygon,LineString
R=Path(__file__).resolve().parent;A=R/'campfire_night/candidate24';C=R/'campfire_night/candidate26'
s=json.loads((R/'schedule.json').read_text());assert s['phase']=='work' and time.time()+180<s['work_until_epoch'];assert not (C/'PIECES.json').exists();C.mkdir(exist_ok=True)
spec=json.loads((A/'PIECES.json').read_text());report=[]
for p in spec['pieces']:
 if not (p['name'].startswith('pine_') and not p['name'].endswith('trunk')):continue
 assert len(p['outline'])==1
 q=p['outline'][0];original=Polygon(q['exterior'],q.get('holes',[]));curve=original.exterior;sample=np.array([curve.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,max(128,int(curve.length/2)),endpoint=False)])
 chosen=None
 for smooth in [1.25,.8,.4]:
  simplified=original.simplify(smooth,preserve_topology=True);vertices=np.asarray(simplified.exterior.coords)[:-1];xy=[]
  for i,b in enumerate(vertices):
   a=vertices[(i-1)%len(vertices)];c=vertices[(i+1)%len(vertices)];incoming=b-a;outgoing=c-b;la=np.linalg.norm(incoming);lb=np.linalg.norm(outgoing);trim=min(1.5,.25*la,.25*lb);first=b-incoming/la*trim;last=b+outgoing/lb*trim
   for t in np.linspace(0,1,7):xy.append((1-t)**2*first+2*t*(1-t)*b+t*t*last)
  poly=Polygon(xy)
  if poly.is_valid and poly.exterior.hausdorff_distance(curve)<=3.0:chosen=poly;break
 assert chosen is not None,p['name'];new=[dict(exterior=np.asarray(chosen.exterior.coords).tolist(),holes=[])];p['outline']=new
 if len(p.get('cells',[]))==1:p['cells'][0]['shape']=new
 report.append(dict(name=p['name'],maximum_reference_outline_change_px=float(chosen.exterior.hausdorff_distance(curve)),smoothing_scale_px=smooth))
(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n');(C/'enamel_config.json').write_bytes((A/'enamel_config.json').read_bytes());(C/'curve_change.json').write_text(json.dumps(dict(source='candidate24',method='Remove small traced kinks, then connect lines with tangent continuous quadratic curves bounded within3 source pixels. Colors and layout remain tied to the actual reference.',parts=report,native_review_pending=True),indent=2)+'\n');print(report)
