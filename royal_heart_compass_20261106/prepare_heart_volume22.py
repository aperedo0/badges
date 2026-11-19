"""Test homogeneous ruby light scattering, keeping its real refracted paths."""
from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;B=R/'ruby_heart/candidate21';C=R/'ruby_heart/candidate22';assert not C.exists()
C.mkdir()
for name in ['source','mobile','textures']:shutil.copytree(B/name,C/name)
(C/'review').mkdir()
for name in ['model.usdz','geometry.npz','blender_geometry.npz','groups.json','materials.json','validation.json','checkpoint_validation.json','runtime_gem_validation_compact.json']:
 if (B/name).exists():shutil.copy2(B/name,C/name)
source=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/BadgeCrestGemSurface.metal'
backup=R/'runtime_before_heart_volume22.metal';assert not backup.exists();shutil.copy2(source,backup);code=source.read_text()
old='float3 entryPoint, float3 entryDirection, float3 entryWeight, float3 indices, float3 absorption, bool ice, bool clearStone)'
new='float3 entryPoint, float3 entryDirection, float3 entryNormal, float3 entryWeight, float3 indices, float3 absorption, float densityScale, bool ice, bool clearStone)'
assert code.count(old)==1;code=code.replace(old,new)
old='    bool rose = planes.get_height() > 2;\n    int hitBudget'
new='''    bool rose = planes.get_height() > 2;
    float3 previousNormal = entryNormal;
    float scattering = rose ? 0.65 * densityScale : 0.0;
    float3 volumeIllumination = float3(0.0);
    if (rose) {
        // The final environment mip averages the actual studio map. It is
        // incident illumination for the volume, never an appearance image.
        float lastMip = float(max(1u, studio.map.get_num_mip_levels()) - 1u);
        volumeIllumination = float3(studio.map.sample(cLightSampler, float2(0.5), level(lastMip)).rgb) * 0.92;
    }
    int hitBudget'''
assert code.count(old)==1;code=code.replace(old,new)
old='            density += clearStone ? 0.96 + 0.06 * crestNoise(samplePosition * 3.0) : crestOpticalDensity(samplePosition);'
new=old+'''
            if (rose) {
                float travelled = facet.distance * (float(step) + 0.5) / 4.0;
                // Local slab distances use the two actual boundary facets.
                // They approximate incoming attenuation without another
                // traversal of every hull plane for each volume sample.
                float fromEntry = abs(dot(direction, previousNormal)) * travelled;
                float fromExit = abs(dot(direction, facet.normal)) * (facet.distance - travelled);
                float depth = min(fromEntry, fromExit);
                float3 extinction = absorption + float3(scattering);
                float3 incidentLight = volumeIllumination * exp(-extinction * depth);
                collected += weight * exp(-extinction * travelled) * incidentLight
                           * (scattering * facet.distance / 4.0);
            }'''
assert code.count(old)==1;code=code.replace(old,new)
old='        weight *= exp(-absorption * facet.distance * density / 4.0);'
new='''        if (rose) weight *= exp(-(absorption * density / 4.0 + float3(scattering)) * facet.distance);
        else weight *= exp(-absorption * facet.distance * density / 4.0);
        previousNormal = facet.normal;'''
assert code.count(old)==1;code=code.replace(old,new)
old='refractedDirection, float3(1.0 - surfaceReflection), indices, absorption, profile.y < 0.5, profile.y > 4.5'
new='refractedDirection, facetNormal, float3(1.0 - surfaceReflection), indices, absorption, profile.z, profile.y < 0.5, profile.y > 4.5'
assert code.count(old)==1;code=code.replace(old,new)
source.write_text(code);shutil.copy2(source,R/'runtime_heart_volume22.metal')
p=C/'checkpoint_validation.json';check=json.loads(p.read_text());check['complete_editable_checkpoint']=str(C/'source/ruby_heart_compact.blend');p.write_text(json.dumps(check,indent=2))
(C/'ruby_volume_review.json').write_text(json.dumps(dict(source='candidate21',owner_confirmed_issue='Large pink heart shape inside the red edge',geometry_unchanged=True,uniform_true_volume_scattering=True,normalized_scattering=.65,illumination_from_actual_studio_environment=True,no_reference_or_position_color_map=True,no_painted_reflections=True,attenuation_approximation='Distances to the actual entry and exit facets, with isotropic mean incident light',only_continuous_rose_volume_changed=True,other_optical_profiles_preserved=True,source_shader_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),trial_shader_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),native_review_pending=True),indent=2));print('Heart22 homogeneous physical ruby volume prepared',flush=True)
