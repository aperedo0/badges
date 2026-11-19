"""Replace the nested rear crown with one coordinated physical jewel cut."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate20';C=R/'ruby_heart/candidate24';assert not C.exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');cut=np.load(R/'optics_fit/heart_plane_cut_0.65_1.7.npz');G=json.loads((B/'groups.json').read_text());out={};reports=[];gem=0
ps=[cut[f'{i}_points'] for i in range(2)];shift=-float((min(p[:,2].min() for p in ps)+max(p[:,2].max() for p in ps))/2)
for i,g in enumerate(G):
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['mat']=='CrestGem_Rose':
  p=cut[f'{gem}_points'].copy();h=ConvexHull(p);t=h.simplices.copy();normal=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=(normal*h.equations[:,:3]).sum(1)<0;t[flip]=t[flip,::-1]
  planes=len(np.unique(np.round(h.equations,7),axis=0));assert planes<=256
  reports.append(dict(name=g['name'],facet_planes=planes));gem+=1
 p[:,2]+=shift;out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t
assert gem==2
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(G,indent=2));shutil.copy2(B/'materials.json',C/'materials.json')
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
shader=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/BadgeCrestGemSurface.metal';old=shader.read_text();assert hashlib.sha256(shader.read_bytes()).hexdigest()=='5f8a7c42248e1996608b59a78d980d0554550eb47a799311dfb318e60848c26d'
shutil.copy2(shader,R/'runtime_before_plane24.metal');needle='profile.y > 5.5 ? float3(0.16, 9.0, 2.8)';assert old.count(needle)==1;shader.write_text(old.replace(needle,'profile.y > 5.5 ? float3(0.16, 9.0, 0.65)'));shutil.copy2(shader,R/'runtime_plane24.metal')
(C/'physical_cut_review.json').write_text(json.dumps(dict(source_gold_setting='candidate20',one_coordinated_crown_and_pavilion_field=True,old_shallow_twin_pavilion_domes_removed=True,whole_heart_ruby_optical_volume=True,outer_silhouette_preserved=True,crown_slope=.65,pavilion_depth=1.7,uniform_absorption=[.16,9,.65],original_clear_optical_transport_preserved=True,dense_body_and_scattering_trials_rejected=True,no_gem_appearance_images_or_body_diffuse_lobe=True,global_z_center_shift=shift,domains=reports,native_review_pending=True),indent=2));print('Heart24 coordinated physical ruby cut prepared',reports,flush=True)
