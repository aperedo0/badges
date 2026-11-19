from pathlib import Path
import shutil,json
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import MultiPoint
R=Path(__file__).resolve().parent
# First save a separate color diagnosis. Do not change geometry in this test.
a=R/'campfire_night/candidate11';c=R/'campfire_night/candidate12';c.mkdir(exist_ok=True)
for p in a.iterdir():
 if p.is_file() and p.name!='model.usdz':shutil.copy2(p,c/p.name)
config=json.loads((R/'campfire_night/enamel_config.json').read_text());config['materials']['Enamel']['gold_exclusion_border_px']=6
(c/'enamel_config.json').write_text(json.dumps(config,indent=2)+'\n')
# A real pavilion replaces the broad mirrored rear table. Preserve the frame and seat.
a=R/'sapphire_teardrop/candidate06';c=R/'sapphire_teardrop/candidate07';c.mkdir(exist_ok=True)
for p in a.iterdir():
 if p.is_file() and p.name not in ['model.usdz','export_validation.json','topology_validation.json','validation.json','runtime_gem_vertices.json']:shutil.copy2(p,c/p.name)
D=dict(np.load(a/'parts.npz'));M=json.loads((a/'parts.json').read_text());old=D['gem_v'].reshape(-1,3);table=np.unique(old[np.isclose(old[:,2],.64)],axis=0)
girdle=MultiPoint(old[np.isclose(old[:,2],.16),:2]).convex_hull.exterior
g=np.array([girdle.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,16,endpoint=False)])
apex=np.array([[0,float(table[:,1].mean()),-.64]])
points=np.vstack([np.c_[g,np.full(16,.16)],np.c_[g,np.full(16,-.16)],table,apex]);h=ConvexHull(points);faces=h.simplices.copy();v=points[faces];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);bad=np.sum(n*h.equations[:,:3],axis=1)<0;faces[bad]=faces[bad,::-1];v=points[faces];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.linalg.norm(n,axis=1,keepdims=True)
D['gem_v']=v.astype(np.float32);D['gem_n']=np.repeat(n[:,None,:],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(v),3,2),np.float32);D['gem_m']=np.zeros(len(v),np.int16)
for p in M['parts']:
 if p['name']=='gem':p.update(triangles=len(v),front=0,physical_pavilion=True)
np.savez_compressed(c/'parts.npz',**D);(c/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
(c/'pavilion_design.json').write_text(json.dumps(dict(front_table_preserved=True,closed_convex_real_pavilion=True,girdle_planes=16,back='Faceted pavilion with actual culet, rather than a second table',no_appearance_texture=True,vertices=len(points),triangles=len(v),facet_planes=len(np.unique(np.round(h.equations,5),axis=0)),native_review_pending=True),indent=2)+'\n')
print('Prepared separate enamel filter test and real pavilion gem')
