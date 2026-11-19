"""Keep traced outer curves while building buried upper bodies without shoulders."""
from pathlib import Path
import json,time,shutil
import numpy as np
import contourpy
from scipy import ndimage as ndi
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from designs import shape
R=Path(__file__).resolve().parent;B=R/'campfire_night';A=B/'candidate16';C=B/'candidate17';assert not C.exists();C.mkdir()
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+120<s['work_until_epoch']
spec=json.loads((A/'PIECES.json').read_text());by={p['name']:p for p in spec['pieces']};masks=np.load(B/'pine_face_masks.npz');faces={};names=['pine_left_top','pine_left_middle','pine_left_lower','pine_right_top','pine_right_middle','pine_right_lower']
for i,name in enumerate(names):
 contours=contourpy.contour_generator(z=ndi.gaussian_filter(masks[str(i)].astype(float),1.2)).lines(.5)
 face=max((Polygon(c).buffer(0) for c in contours if len(c)>4),key=lambda p:p.area).simplify(.7,preserve_topology=True).buffer(7,quad_segs=8).simplify(.5,preserve_topology=True);faces[name]=face;p=face
 if not name.endswith('top'):
  upper=name.replace('middle','top') if name.endswith('middle') else name.replace('lower','middle');q=faces[upper];cut=q.bounds[3]-6;intersection=face.intersection(LineString([(0,cut),(1254,cut)]));assert not intersection.is_empty
  x0,_,x1,_=intersection.bounds;apex=q.representative_point().coords[0];bridge=Polygon([apex,(x0,cut),(x1,cut)])
  p=unary_union([face,bridge]).buffer(.25).buffer(-.25)
  assert p.geom_type=='Polygon',name
  p=Polygon(p.exterior)
 by[name]['outline']=shape(p)
(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n');shutil.copy2(A/'enamel_config.json',C/'enamel_config.json')
(C/'geometry_change.json').write_text(json.dumps(dict(source='candidate16',pine_scallops='Measured enamel face boundaries retained; buried connections use a triangle seated on the actual face cross section, with no convex shoulder caps',other_layers='Same separate enamel roles, seated complete navy backing, corrected rear stone and open flame notch',native_acceptance_pending=True),indent=2)+'\n')
print('Prepared corrected hidden tree joins without changing the measured scallops')
