"""Trial cloth appearance fit, preserving all geometry and moving optics."""
from pathlib import Path
import shutil,json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent;B=R/'ruby_crown/candidate14';C=R/'ruby_crown/candidate15'
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
for name in ['geometry.npz','blender_geometry.npz','groups.json','materials.json']:shutil.copy2(B/name,C/name)
for p in (B/'textures').glob('*'):shutil.copy2(p,C/'textures'/p.name)
a=np.asarray(Image.open(B/'review/cloth_fit_diagnostic/proposed_cloth_appearance_fit.png').convert('RGB'),float)/255;linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);rng=np.random.default_rng(771);noise=gaussian_filter(rng.normal(size=a.shape[:2]),(1.4,.35),mode='wrap');noise/=noise.std();linear*=np.clip(1+.16*noise,.55,1.45)[...,None];srgb=np.where(linear<=.0031308,linear*12.92,1.055*np.maximum(linear,0)**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(srgb,0,1)*255)).save(C/'textures/velvet_fold_color.png')
report=dict(source='candidate14',trial_not_accepted=True,cloth_reference_appearance_fit=True,pure_physical_albedo_not_proven=True,gemstones_and_metal_untouched=True,all_geometry_and_corner_attributes_preserved=True,emission_used=False,cloth_uses_original_uvs_and_physical_normal_map=True,unobserved_cloth_completed_smoothly=True,back_has_corresponding_cloth_tones=True,reference_illumination_removed_exactly=False,required='Actual native front, both sides, back and full turn review. Reject if this cloth appearance fit looks painted during rotation.')
(C/'cloth_appearance_fit.json').write_text(json.dumps(report,indent=2));print('Ruby15 cloth trial prepared; geometry, gold, all192 optical stones and their shader are unchanged')
