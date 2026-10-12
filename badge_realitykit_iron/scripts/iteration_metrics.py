import sys,json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion
r=Path(sys.argv[1]).resolve();root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'));import measure_smoothness as ms
mask=np.load(r/'proof/plane_ids.npy');d=json.loads((r/'reports/crystal_design.json').read_text());verification=json.loads((r/'proof/crystal_design_validation.json').read_text())
front_count=d['front_planes'];faces=d['front_faces'];normals=np.array(verification['front_plane_normal_vectors']);adjacent=[(i,j) for i in range(front_count) for j in range(i+1,front_count) if len(set(faces[i])&set(faces[j]))==2]
silver=json.loads((root/'proof/smoothness_silver_pose00.json').read_text())
report={'mask_method':'Blender-emitted scene-linear polygon IDs, full coverage only, eroded 3 pixels; all front panels required; visible side walls with at least 250 eroded pixels included','neighbor_minimum_display_levels':10,'front_plane_rows':{},'neighbor_rows':{},'smoothness':{},'thresholds':{'stage_facet':.92,'stage_edge_excess':61.5,'harsh_facet':1.,'harsh_edge_excess':64.6},'planes':front_count}
for rig in ['stage','harsh']:
 img=np.asarray(Image.open(r/f'proof/renders/iron_{rig}_0.png').convert('RGB'),float);luma=img@np.array([.2126,.7152,.0722]);rows=[];valid={}
 for pi in range(len(verification['planes'])):
  inner=binary_erosion(mask==pi+1,iterations=3);n=int(inner.sum())
  if pi<front_count:assert n>=250,(pi,n)
  if n<250:continue
  valid[pi]=inner
  rows.append({'plane':pi,'kind':verification['planes'][pi]['kind'],'pixels':n,'mean_luma':float(luma[inner].mean()),'max_rgb':float(img[inner].max())})
 report['front_plane_rows'][rig]=rows
 neighbors=[]
 for i,j in adjacent:
  if i not in valid or j not in valid:continue
  difference=abs(float(luma[valid[i]].mean()-luma[valid[j]].mean()));angle=float(np.degrees(np.arctan2(np.linalg.norm(np.cross(normals[i],normals[j])),normals[i]@normals[j])))
  neighbors.append({'a':i,'b':j,'same_side':(i in d['left_front_planes'])==(j in d['left_front_planes']),'display_level_difference':difference,'angle_degrees':angle})
 report['neighbor_rows'][rig]=neighbors
 data=json.loads((r/'proof/smoothness_pose00.json').read_text())['table'][f'iron_{rig}']
 report['smoothness'][rig]={'facet_mean':data['facet_rough_mean'],'edge_excess_mean':data['edges']['excess_mean'],'passes':data['facet_rough_mean']<=report['thresholds'][rig+'_facet'] and data['edges']['excess_mean']<=report['thresholds'][rig+'_edge_excess']}
 brightest=max(x['mean'] for x in silver['table'][f'silver_{rig}']['facets'].values());report['smoothness'][rig]['silver_brightest_facet_mean']=brightest
 report['smoothness'][rig]['candidate_brightest_mean']=max(x['mean_luma'] for x in rows);report['smoothness'][rig]['candidate_darkest_mean']=min(x['mean_luma'] for x in rows)
report['criterion_5_pass']=all(x['display_level_difference']>=10 for x in report['neighbor_rows']['harsh']) and max(x['mean_luma'] for x in report['front_plane_rows']['harsh'])<=report['smoothness']['harsh']['silver_brightest_facet_mean'] and min(x['mean_luma'] for x in report['front_plane_rows']['harsh'])>=15
report['criterion_6_pass']=all(x['passes'] for x in report['smoothness'].values());report['criterion_7_pass']=verification['maximum_normal_difference_within_any_plane']==0
# The latest request intentionally replaces the old uniform surfaces.
report['finish']='Reference-derived forged texture; historical smoothness limits are diagnostic only.'
# ID PNG is a labelled diagnostic, not a modified beauty proof.
colors=np.array([[0,0,0]]+[(int(60+(i*71)%190),int(60+(i*113)%190),int(60+(i*151)%190)) for i in range(len(verification['planes']))],np.uint8)
canvas=Image.fromarray(colors[mask]);draw=ImageDraw.Draw(canvas)
for i in range(front_count):
 y,x=np.nonzero(binary_erosion(mask==i+1,iterations=3));draw.text((int(x.mean()),int(y.mean())),str(i),fill='white')
canvas.save(r/'proof/plane_ids.png')
(r/'blender_metrics.json').write_text(json.dumps(report,indent=2));(r/'blender_metrics.txt').write_text(json.dumps(report,indent=2))
print(json.dumps({'front_means_harsh':[round(x['mean_luma'],1) for x in report['front_plane_rows']['harsh']], 'minimum_neighbor_difference':min(x['display_level_difference'] for x in report['neighbor_rows']['harsh']),'smoothness':report['smoothness'],'criterion_5_pass':report['criterion_5_pass'],'criterion_6_pass':report['criterion_6_pass'],'criterion_7_pass':report['criterion_7_pass']},indent=2))
