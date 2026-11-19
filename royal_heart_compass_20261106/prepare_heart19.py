"""Preserve the measured cut and test one calibrated native optical gain."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate18';C=R/'ruby_heart/candidate19';assert not C.exists()
C.mkdir()
for name in ['source','mobile','textures']:shutil.copytree(B/name,C/name)
(C/'review').mkdir()
for name in ['model.usdz','geometry.npz','blender_geometry.npz','groups.json','materials.json','validation.json','checkpoint_validation.json','runtime_gem_validation_compact.json']:
 if (B/name).exists():shutil.copy2(B/name,C/name)
report=json.loads((B/'review/exposure_diagnostic/measurement.json').read_text());exposure=report['predicted_exposure']
source=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift';old=source.read_text();needle='crestStyle == 6 ? 0.32 : crestStyle == 5';assert old.count(needle)==1
backup=R/'runtime_before_rose_measured_exposure19.swift';assert not backup.exists();shutil.copy2(source,backup)
new=old.replace(needle,f'crestStyle == 6 ? {exposure:.9f} : crestStyle == 5');source.write_text(new);shutil.copy2(source,R/'runtime_heart19.swift')
p=C/'checkpoint_validation.json';check=json.loads(p.read_text());check['complete_editable_checkpoint']=str(C/'source/ruby_heart_compact.blend');p.write_text(json.dumps(check,indent=2))
(C/'native_exposure_trial.json').write_text(json.dumps(dict(source='candidate18',geometry_and_material_textures_byte_identical=True,old_exposure=.32,new_exposure=exposure,actual_native_measurement=str(B/'review/exposure_diagnostic/measurement.json'),no_appearance_map_created=True,only_rose_profile_changed=True,studio_and_other_profiles_unchanged=True,custom_metal_shader_unchanged=True,private_swift_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),actual_native_review_required=True),indent=2));print('Heart19 same physical model, measured native exposure',exposure)
