"""Give the actual sapphire table a gentle tilt and rebuild genuine crown facets."""
from pathlib import Path
import numpy as np,json,shutil
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate24';C=A.parent/'candidate25';assert not C.exists();C.mkdir();D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());old=np.unique(D['gem_v'].reshape(-1,3),axis=0).astype(float);ring=old[ConvexHull(old[:,:2]).vertices,:2];table=old[np.isclose(old[:,2],old[:,2].max()),:2];table=table[ConvexHull(table).vertices];center=table.mean(0);tilt=.14;height=.50+tilt*(table[:,1]-center[1]);assert height.min()>.2
points=np.concatenate([np.c_[ring,np.full(len(ring),.02)],np.c_[ring,np.full(len(ring),-.02)],np.c_[table,height],np.c_[table,-height]]);h=ConvexHull(points);F=h.simplices.copy();V=points[F];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);bad=(N*h.equations[:,:3]).sum(1)<0;F[bad]=F[bad,::-1];V=points[F];N=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);N/=np.linalg.norm(N,axis=1)[:,None];D['gem_v']=V.astype(np.float32);D['gem_n']=np.repeat(N[:,None],3,axis=1).astype(np.float32);D['gem_uv']=np.zeros((len(V),3,2),np.float32);D['gem_m']=np.zeros(len(V),np.int16)
for p in M['parts']:
 if p['name']=='gem':p.update(front=0,triangles=len(V),tilted_table=True)
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for f in ['owner_adjustment.json','optical_profile.json','palette_overrides.json','gold_transfer.json']:shutil.copy2(A/f,C/f)
shutil.copytree(A/'textures',C/'textures');(C/'cut_design.json').write_text(json.dumps(dict(change='Gently tilted real front and rear tables create different optical path lengths and actual crown reflection angles. All facets remain real flat planes on a closed convex sapphire.',table_slope=tilt,table_heights=height.tolist(),xy_girdle_and_table_outlines_preserved=True,gem_triangles=len(V),native_shader_and_exposure_unchanged=True,no_gem_appearance_texture=True,gold_matches_actual_ruby_heart=True,blender_review_pending=True),indent=2)+'\n');print('Tilted real cut25:',len(V),'triangles, depth',2*height.max())
