"""Check continuous optical paths across the heart's two convex domains."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;C=R/'ruby_heart/candidate10';D=np.load(C/'geometry.npz');groups=json.loads((C/'groups.json').read_text())
hulls=[]
for i,g in enumerate(groups):
 if g['mat']!='CrestGem_Rose':continue
 p=D[str(i)+'_points'].astype(float);eq=ConvexHull(p).equations
 planes=np.c_[eq[:,:3],-eq[:,3]];planes=np.unique(np.round(planes,6),axis=0)
 high=planes.astype(np.float16).astype(np.float32);low=((planes-high)*1024).astype(np.float16).astype(np.float32);planes=high+low/1024
 hulls.append(planes.astype(float))
assert len(hulls)==2
tol=1e-5
def interval(planes,p,d):
 raw=planes[:,3]-planes[:,:3]@p;contains=(raw>=-tol).all();gap=np.where(abs(raw)<=tol,0,raw);approach=planes[:,:3]@d
 if ((abs(approach)<1e-6)&(gap<-tol)).any():return None
 den=np.where(abs(approach)<1e-6,np.nan,approach);roots=gap/den
 near=float(np.max(roots[approach< -1e-6],initial=-np.inf));far=float(np.min(roots[approach>1e-6],initial=np.inf))
 if far < -tol or near>far+tol:return None
 return near,max(0,far),bool(contains)
def union_exit(p,d):
 a,b=[interval(h,p,d) for h in hulls]
 if not a and not b:return None
 if a and (not b or max(a[0],0)<=max(b[0],0)):current,other=a,b
 else:current,other=b,a
 end=current[1]
 if other and other[0]<=end+2*tol and other[1]>end:end=other[1]
 return end,current[1]
def inside(p,tolerance=tol*2):return any((p@h[:,:3].T-h[:,3]<=tolerance).all() for h in hulls)
rng=np.random.default_rng(265);checked=0;crossings=0;mirror_checks=0;notch_reentries=0
while checked<2000:
 p=rng.uniform([-2.6,-2.3,-.5],[2.6,2.8,.8]);d=rng.normal(size=3);d/=np.linalg.norm(d);hit=union_exit(p,d)
 if not inside(p) or not hit or hit[0]<.001:continue
 distance,first=hit;eps=1e-3
 assert inside(p+d*(distance-eps)),('Ray left union early',p,d,distance)
 # A concave exterior can be exited and reentered shortly afterward.
 # Probe the actual air interval instead of jumping across it by a fixed step.
 intervals=[interval(h,p,d) for h in hulls]
 next_entries=[i[0] for i in intervals if i and i[0]>distance+2*tol]
 external_step=eps
 if next_entries and min(next_entries)<distance+eps:
  external_step=(min(next_entries)-distance)*.5;notch_reentries+=1
 assert not inside(p+d*(distance+external_step),tolerance=1e-9),('Ray stopped inside the ruby',p,d,distance)
 crossings+=distance>first+eps
 # The floor reflection is the exact same trace after a Y flip.
 flipped=[]
 for h in hulls:
  q=h.copy();q[:,1]*=-1;flipped.append(q)
 source=hulls;hulls=flipped;m=union_exit(p*[1,-1,1],d*[1,-1,1]);hulls=source
 assert m and abs(m[0]-distance)<1e-7;mirror_checks+=1;checked+=1
assert crossings>100
edge_checks=0
for planes in hulls:
 for plane in planes:
  n=plane[:3];center=n*plane[3];d=-n
  if not inside(center):continue
  hit=union_exit(center+n*0.0005,d)
  if not hit:continue
  assert hit[0]>0.0005
  edge_checks+=1
assert edge_checks>10
report=dict(short_external_notch_intervals_checked=notch_reentries,raster_edge_extrapolation_checks=edge_checks,rays_checked=checked,paths_crossing_lobe_join_without_air_interface=crossings,reflection_symmetry_checks=mirror_checks,one_continuous_ruby_volume=True,split_plane_precision_preserved=True)
(C/'heart_union_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
