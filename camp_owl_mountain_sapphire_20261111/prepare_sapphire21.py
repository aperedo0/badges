"""Keep the clean flat back and give the real crown enough height for bold facets."""
from pathlib import Path
import numpy as np,json,shutil
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate20';C=A.parent/'candidate21';assert not C.exists();C.mkdir();D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text())
# Undo the previous whole model centering for a reproducible cut change.
shift=json.loads((A/'cut_design.json').read_text())['centering_shift']
for part in M['parts']:D[part['name']+'_v'][...,2]-=shift
v=D['gem_v'];upper=v[...,2]>.02001;v[...,2]=np.where(upper,.02+(v[...,2]-.02)*(.88/.48),v[...,2]);n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];D['gem_n']=np.repeat(n[:,None],3,axis=1).astype(np.float32)
allv=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']]);shift=-(allv[:,2].min()+allv[:,2].max())/2
for part in M['parts']:D[part['name']+'_v'][...,2]+=shift
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for file in ['palette_overrides.json','optical_profile.json']:shutil.copy2(A/file,C/file)
(C/'cut_design.json').write_text(json.dumps(dict(change='Same measured front table and outline, real crown height0.88 above girdle, flat rear. Steeper actual facets replace shallow glass angles. Native optical parameters unchanged.',centering_shift=float(shift),no_appearance_texture=True,no_app_changes=True,blender_review_pending=True),indent=2)+'\n');print('Prepared steeper real crown21')
