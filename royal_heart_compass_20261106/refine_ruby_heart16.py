"""A denser physical heart cut from the reference facet junctions."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate15';C=R/'ruby_heart/candidate16'
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());base=D['3_points'].astype(float);unit=(base[96,1]-base[97,1])/(493-389);intercept=base[96,1]+389*unit
junctions=np.array([[627,389],[627,493],[627,650],[627,784],[627,900],[627,970],[420,232],[455,328],[369,371],[421,656],[453,814],[386,850],[232,367],[286,476],[341,541],[290,597],[355,631],[386,707],[462,718],[512,579],[559,702],[547,838],[521,891],[603,934],[565,856],[540,766],[555,460],[515,404],[534,333],[306,356],[273,403],[236,490],[253,554],[327,657],[371,740],[430,785],[529,540],[469,474],[572,621],[479,611],[365,302],[486,252],[581,384],[601,588]],float)
xy=np.c_[(627-junctions[:,0])*unit,intercept-junctions[:,1]*unit];outer=base[:48,:2];boundary=ConvexHull(outer);inside=np.max(xy@boundary.equations[:,:2].T+boundary.equations[:,2],axis=1)<=1e-6;xy=xy[inside];junctions=junctions[inside]
# The seam is inside one ruby, not an outer girdle. Exclude that internal
# half plane when computing crown depth so both lobes meet at the same ridge.
planes=boundary.equations;seam=(abs(planes[:,0])>.9999)&(abs(planes[:,1])<1e-4)&(abs(planes[:,2])<1e-4);planes=planes[~seam]
distance=np.min(-(xy@planes[:,:2].T+planes[:,2]),axis=1);assert distance.min()>0
height=np.sqrt(distance/distance.max())-.002*(xy*xy).sum(1);height/=height.max();back_xy=base[109:122,:2].copy();back_xy[:,0]=abs(back_xy[:,0]);back_distance=np.min(-(back_xy@planes[:,:2].T+planes[:,2]),axis=1);back_valid=back_distance>1e-5;back_xy=back_xy[back_valid];back_distance=back_distance[back_valid];back_height=np.sqrt(back_distance/back_distance.max())-.002*(back_xy*back_xy).sum(1);back_height/=back_height.max();front_z=float(base[:48,2].mean());back_z=float(base[48:96,2].mean());front_depth=float(base[:,2].max()-front_z);back_depth=float(back_z-base[:,2].min());reports=[];out={}
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['mat']=='CrestGem_Rose':
  sign=1 if p[:,0].mean()>0 else -1;outline=outer*np.array([sign,1]);target=xy*np.array([sign,1]);p=np.vstack([np.c_[outline,np.full(48,front_z)],np.c_[outline,np.full(48,back_z)],np.c_[target,front_z+front_depth*height],np.c_[back_xy*np.array([sign,1]),back_z-back_depth*back_height]])
  hull=ConvexHull(p);t=hull.simplices.copy();n=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(n*hull.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
  plane_count=len(np.unique(np.round(hull.equations,3),axis=0));assert plane_count<=256
  active_front=int(sum(96<=v<96+len(xy) for v in hull.vertices));assert active_front>=len(xy)*.85,(active_front,len(xy))
  reports.append(dict(name=g['name'],measured_front_junctions=len(xy),active_front_junctions=active_front,triangles=len(t),approximate_planes=plane_count))
 out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json');shutil.copy2(B/'textures/gold_roughness.png',C/'textures/gold_roughness.png');(C/'cut_report.json').write_text(json.dumps(dict(source='candidate15',gold_bezel_preserved_exactly=True,physical_crown_and_pavilion=True,appearance_photo_used=False,measured_junctions=junctions.tolist(),domains=reports),indent=2));print(json.dumps(reports))
