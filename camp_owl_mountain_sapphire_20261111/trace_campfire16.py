"""Use measured enamel regions to correct the pine silhouettes and flame opening."""
from pathlib import Path
import json,copy,time
import numpy as np
import contourpy
from scipy import ndimage as ndi
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from designs import path,shape
R=Path(__file__).resolve().parent;B=R/'campfire_night';C=B/'candidate16';assert not (C/'parts.npz').exists();C.mkdir(exist_ok=True)
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+300<s['work_until_epoch']
spec=json.loads((B/'candidate14/PIECES.json').read_text());by={p['name']:p for p in spec['pieces']};masks=np.load(B/'pine_face_masks.npz');outlines={}
names=['pine_left_top','pine_left_middle','pine_left_lower','pine_right_top','pine_right_middle','pine_right_lower']
for i,name in enumerate(names):
 field=ndi.gaussian_filter(masks[str(i)].astype(float),1.2)
 contours=contourpy.contour_generator(z=field).lines(.5)
 p=max((Polygon(c).buffer(0) for c in contours if len(c)>4),key=lambda p:p.area)
 p=p.simplify(.7,preserve_topology=True).buffer(7,quad_segs=8).simplify(.5,preserve_topology=True)
 if name.endswith('middle') or name.endswith('lower'):
  upper=name.replace('middle','top') if name.endswith('middle') else name.replace('lower','middle')
  hidden=outlines[upper].buffer(-12)
  # Dark cast shadows are outside the thresholded green face. Continue the
  # buried upper body through them while retaining the traced lower scallops.
  cap=unary_union([p,hidden]).convex_hull.intersection(box(0,0,1254,p.bounds[1]+45))
  p=unary_union([p,hidden,cap]).buffer(0)
 assert p.geom_type=='Polygon' and p.is_valid,(name,p.geom_type)
 outlines[name]=p;by[name]['outline']=shape(p);by[name]['bevel']['width']=4;by[name]['rim']['width']=3;by[name]['rim']['height']=0
# The inner yellow flame already owns the visible curved notch. Open the two
# hidden underlying flame layers so the real log shows through it.
notch=path('M 579 869 C 592 854 606 844 630 845 C 648 844 663 851 675 868 L 704 942 L 553 942 Z')
for name,offset in [('outer_red_flame',12),('middle_amber_flame',6)]:
 p=by[name];g=unary_union([Polygon(q['exterior'],q.get('holes',[])) for q in p['outline']]);g=g.difference(notch.buffer(offset));assert g.geom_type=='Polygon';p['outline']=shape(g);p['edge_skip']=shape(notch.buffer(offset+8))
(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n')
config=json.loads((B/'candidate15/enamel_config.json').read_text());(C/'enamel_config.json').write_text(json.dumps(config,indent=1)+'\n')
(C/'geometry_change.json').write_text(json.dumps(dict(pines='Six separate semantic enamel regions from original reference, smoothed contours and real gold bands; hidden tier overlap preserved',reference_masks=str(B/'pine_face_masks.npz'),flames='The underlying red and amber layers now leave the inner flame notch open for the actual log, with separate hidden side walls',planar_grid_surface=False,native_acceptance_pending=True),indent=2)+'\n')
print('Saved six source matched pine tiers and the real flame notch')
