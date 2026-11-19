"""Test a dense polished ruby body under the existing native studio lights."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate21';C=R/'ruby_heart/candidate23';assert not C.exists()
C.mkdir()
for name in ['source','mobile','textures']:shutil.copytree(B/name,C/name)
(C/'review').mkdir()
for name in ['model.usdz','geometry.npz','blender_geometry.npz','groups.json','materials.json','validation.json','checkpoint_validation.json','runtime_gem_validation_compact.json']:
 if (B/name).exists():shutil.copy2(B/name,C/name)
P=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges';shader=P/'BadgeCrestGemSurface.metal';swift=P/'Badge3DLiveBadge.swift'
for path in [shader,swift]:shutil.copy2(path,R/('runtime_before_dense23_'+path.name))
code=(R/'runtime_before_heart_volume22.metal').read_text()
old='    surface.set_emissive_color(half3(color * profile.w));'
new='''    if (profile.y > 5.5 && profile.y < 6.5) {
        // Dense, highly included ruby is represented by a lit body lobe
        // plus a reduced clear transport lobe. Both use the real geometry.
        // The native studio supplies the body light and surface reflections.
        surface.set_base_color(half3(0.30h, 0.002h, 0.060h));
        surface.set_metallic(0.0h);
        surface.set_roughness(0.13h);
        surface.set_specular(0.96h);
        surface.set_clearcoat(0.0h);
        surface.set_emissive_color(half3(throughGem * profile.w * 0.15));
    } else {
        surface.set_emissive_color(half3(color * profile.w));
    }'''
assert code.count(old)==1;code=code.replace(old,new);shader.write_text(code)
code=swift.read_text();old='var material = try CustomMaterial(surfaceShader: crestStyle == nil ? surfaceShader : crestSurfaceShader, lightingModel: .unlit)';new='var material = try CustomMaterial(surfaceShader: crestStyle == nil ? surfaceShader : crestSurfaceShader, lightingModel: crestStyle == 6 ? .lit : .unlit)';assert code.count(old)==1;swift.write_text(code.replace(old,new))
for path in [shader,swift]:shutil.copy2(path,R/('runtime_dense23_'+path.name))
p=C/'checkpoint_validation.json';check=json.loads(p.read_text());check['complete_editable_checkpoint']=str(C/'source/ruby_heart_compact.blend');p.write_text(json.dumps(check,indent=2))
(C/'dense_ruby_review.json').write_text(json.dumps(dict(source_geometry='candidate21',owner_confirmed_issue='Large pink heart shape inside red edge',geometry_unchanged=True,material_representation='Dense polished ruby body with native physical surface shading and reduced traced internal transmission',native_lit_body_color=[.30,.002,.060],surface_roughness=.13,dielectric_specular=.96,metallic=0,clear_transport_weight=.15,real_refracted_paths_preserved=True,not_a_full_spectral_volume_solution=True,no_appearance_image_or_fixed_reflection=True,shared_studio_unchanged=True,other_profiles_unchanged=True,shader_sha256=hashlib.sha256(shader.read_bytes()).hexdigest(),native_review_pending=True),indent=2));print('Heart23 dense polished ruby material prepared',flush=True)
