"""Test measured uniform ruby color on the unchanged coordinated crystal cut."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate24';C=R/'ruby_heart/candidate25';assert not C.exists();C.mkdir()
for name in ['source','mobile','textures']:shutil.copytree(B/name,C/name)
(C/'review').mkdir()
for name in ['model.usdz','geometry.npz','blender_geometry.npz','groups.json','materials.json','validation.json','checkpoint_validation.json','runtime_gem_validation_compact.json','heart_union_validation.json','physical_cut_review.json','facet_precision_repair.json']:
 if (B/name).exists():shutil.copy2(B/name,C/name)
fit=json.loads((R/'optics_fit/heart24_color_fit.json').read_text());red,blue,gain=fit['fitted_parameters'];P=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges';shader=P/'BadgeCrestGemSurface.metal';swift=P/'Badge3DLiveBadge.swift'
for p in [shader,swift]:shutil.copy2(p,R/('runtime_before_color25_'+p.name))
code=shader.read_text();needle='profile.y > 5.5 ? float3(0.16, 9.0, 0.65)';assert code.count(needle)==1;shader.write_text(code.replace(needle,f'profile.y > 5.5 ? float3({red:.9f}, 9.0, {blue:.9f})'))
code=swift.read_text();needle='crestStyle == 6 ? 0.434211563 : crestStyle == 5';assert code.count(needle)==1;code=code.replace(needle,f'crestStyle == 6 ? {gain:.9f} : crestStyle == 5')
needle='            material.custom.value = SIMD4(isMirrorImage ? 1 : 0, crestStyle, min(8, max(0.5, 1 / thickness)),'
start=code.index(needle);end=code.index('\n',start)
code=code[:end]+'''\n            if crestStyle == 6 {
                print("Badge Rose optics: density=\\(material.custom.value.z) exposure=\\(material.custom.value.w)")
            }'''+code[end:];swift.write_text(code)
for p in [shader,swift]:shutil.copy2(p,R/('runtime_color25_'+p.name))
p=C/'checkpoint_validation.json';d=json.loads(p.read_text());d['complete_editable_checkpoint']=str(C/'source/ruby_heart_compact.blend');p.write_text(json.dumps(d,indent=2))
report=dict(source_geometry='candidate24',model_and_texture_bytes_unchanged=True,genuine_clear_optical_transport_preserved=True,shared_studio_and_other_profiles_unchanged=True,old_uniform_absorption=[.16,9,.65],new_uniform_absorption=[red,9,blue],old_exposure=.434211563,new_exposure=gain,actual_native_profile_log_required=True,reference_color_measurement=str(R/'optics_fit/heart24_color_fit.json'),no_color_or_reflection_image_created=True,not_a_diffuse_body_material=True,shader_sha256=hashlib.sha256(shader.read_bytes()).hexdigest(),native_review_pending=True)
(C/'optical_color_trial.json').write_text(json.dumps(report,indent=2));(C/'source/optical_runtime_parameters.json').write_text(json.dumps(report,indent=2));print('Heart25 unchanged real crystal, measured uniform optical color',red,blue,gain,flush=True)
