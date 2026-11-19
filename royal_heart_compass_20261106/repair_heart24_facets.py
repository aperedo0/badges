"""Triangulate each exact cut face around its center to avoid narrow float slivers."""
from pathlib import Path
import json,shutil
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;C=R/'ruby_heart/candidate24';archive=C/'precision_before_retriangulation';assert not archive.exists();archive.mkdir()
for name in ['geometry.npz','blender_geometry.npz','validation.json','model.usdz','runtime_gem_validation_compact.json']:
 if (C/name).exists():shutil.copy2(C/name,archive/name)
shutil.copytree(C/'source',archive/'source')
D=np.load(C/'geometry.npz');original=np.load(R/'optics_fit/heart_plane_cut_0.65_1.7.npz');G=json.loads((C/'groups.json').read_text());report=[];out={};gem=0
for i,g in enumerate(G):
 p=D[f'{i}_points'];t=D[f'{i}_triangles']
 if g['mat']=='CrestGem_Rose':
  exact=original[f'{gem}_points'].copy();exact[:,2]+=json.loads((C/'physical_cut_review.json').read_text())['global_z_center_shift'];h=ConvexHull(exact);planes=np.unique(np.round(h.equations,10),axis=0);points=list(exact);tri=[]
  for eq in planes:
   normal=eq[:3];indices=np.flatnonzero(abs(exact@normal+eq[3])<2e-8);assert len(indices)>=3
   center=exact[indices].mean(0);reference=np.array([0.,1,0]) if abs(normal[1])<.9 else np.array([1.,0,0]);u=np.cross(normal,reference);u/=np.linalg.norm(u);v=np.cross(normal,u);rel=exact[indices]-center;order=np.argsort(np.arctan2(rel@v,rel@u));indices=indices[order];mid=len(points);points.append(center)
   for a,b in zip(indices,np.roll(indices,-1)):
    face=[mid,int(a),int(b)]
    if np.cross(exact[a]-center,exact[b]-center)@normal<0:face=face[::-1]
    tri.append(face)
  p=np.asarray(points,np.float32);t=np.array(tri,np.int32);normal=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);area=np.linalg.norm(normal,axis=1);assert area.min()>1e-9;normal/=area[:,None];offset=(normal*p[t[:,0]]).sum(1);violation=float((p@normal.T-offset).max());assert violation<9e-6,violation
  report.append(dict(name=g['name'],exact_cut_planes=len(planes),triangles=len(t),maximum_float32_support_violation=violation));gem+=1
 out[f'{i}_points']=p;out[f'{i}_triangles']=t
np.savez_compressed(C/'geometry.npz',**out);(C/'facet_precision_repair.json').write_text(json.dumps(dict(original_positions_and_cut_planes_preserved=True,new_center_vertices_on_actual_facet_planes=True,renderer_tolerance_unchanged=True,reason='Arbitrary hull triangulation created narrow triangles whose Float32 normals exceeded the strict heart tolerance',domains=report),indent=2));print('Exact face center triangulation prepared',report,flush=True)
