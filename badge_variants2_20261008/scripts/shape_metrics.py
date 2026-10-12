from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion
from measure_smoothness import Emblem,project,raster,load_gray,residual_rms,local_residual_rms
r=Path(__file__).resolve().parents[1]
b=r/'silver2';e=Emblem(b/'reports/Star_geometry.json');facets,px=e.facet_masks(0);ref=json.loads((r/'proof/original_silver_metrics.json').read_text());results={};idimg=Image.new('RGB',(1080,1440));draw=ImageDraw.Draw(idimg)
for gi,g in enumerate(e.groups):
    for f in g:draw.polygon([tuple(q) for q in px[e.indices[f]]],fill=((gi*61+70)%255,(gi*101+80)%255,(gi*43+180)%255))
idimg.save(b/'proof/star_plane_ids.png')
for rig,file in [('stage','front.png'),('harsh','app_light_front.png')]:
    l=load_gray(b/'proof'/file);means={str(gi):float(l[v['mask']].mean()) for gi,v in facets.items()};gaps={f'{i}-{(i+1)%10}':abs(means[str(i)]-means[str((i+1)%10)]) for i in range(10)};result={'plane_means':means,'neighbor_gaps':gaps,'minimum_neighbor_gap':min(gaps.values()),'minimum_plane_mean':min(means.values()),'maximum_plane_mean':max(means.values()),'reference_brightest_facet_mean':ref['brightest_facet_mean'] if rig=='harsh' else None,'tone_gap_pass':min(gaps.values())>=10,'no_dead_plane_pass':min(means.values())>=15}
    if rig=='harsh':result['polish_pass']=max(means.values())<=ref['brightest_facet_mean']
    results[rig]=result
(b/'reports/plane_tones.json').write_text(json.dumps(results,indent=2)+'\n')
# Curved shield: no flat-facet claim. Quantify broad interior and normal continuity.
b=r/'iron2';alltri=[];pointnorm={};maxdiff=0
for part in ['PlateLeft','PlateRight']:
    a=json.loads((b/'reports'/f'{part}_geometry.json').read_text());pts=np.array(a['points']);faces=np.array(a['indices']);ns=np.array(a['normals']).reshape(-1,3,3)
    for fi,region in enumerate(a['regions']):
        if region!='bowed shield plate':continue
        alltri.append(pts[faces[fi]])
        for pi,n in zip(faces[fi],ns[fi]):
            key=tuple(pts[pi]);maxdiff=max(maxdiff,float(np.linalg.norm(n-pointnorm[key]))) if key in pointnorm else maxdiff;pointnorm[key]=n
polys,_=project(np.array(alltri).reshape(-1,3),0);full=raster(polys.reshape(-1,3,2));mask=binary_erosion(full,iterations=5);Image.fromarray(np.uint8(full)*255).save(b/'proof/plate_mask.png');curved={'interpretation':'Continuous curved plate, not planar facets. Cubic residual includes the requested broad forging and physical curved-light gradients; report rather than compare to flat-facet limits.','shared_point_normal_max_difference':maxdiff,'regions':{}}
for rig,file in [('stage','front.png'),('harsh','app_light_front.png')]:
    l=load_gray(b/'proof'/file);curved['regions'][rig]={'pixels':int(mask.sum()),'mean':float(l[mask].mean()),'percentile_5':float(np.percentile(l[mask],5)),'cubic_residual':residual_rms(l,mask),'grain_sigma_2_5':local_residual_rms(l,mask,2.5),'mottle_sigma_6':local_residual_rms(l,mask,6)}
(b/'reports/smoothness.json').write_text(json.dumps(curved,indent=2)+'\n');print('SILVER',json.dumps(results));print('IRON',json.dumps(curved))
