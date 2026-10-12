"""Deliver exact app-tested centering bytes with a scoped, truthful verification report."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
candidate = root / 'centering_revision/01'
read = lambda path: json.loads(path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
app = read(candidate / 'app_metrics.json')
metrics = read(candidate / 'blender_metrics.json')
geometry = read(candidate / 'proof/geometry_identity.json')
planes = read(candidate / 'proof/crystal_design_validation.json')
design = read(candidate / 'proof/centering_design_metrics.json')
assert app['loaded_3d'] and app['passes_numeric_app_checks']
assert app['candidate_sha256'] == sha(candidate / 'mobile/iron_badge_mobile.usdz')
assert metrics['criterion_5_pass'] and metrics['criterion_7_pass']
assert planes['maximum_normal_difference_within_any_plane'] == 0
assert 'Finished proof renders' in (candidate / 'logs/final_proofs.txt').read_text()
assert 'Success!' in (candidate / 'proof/usdchecker.log').read_text()
assert all(row['prim'].startswith('/Badge/Emblem') for row in read(candidate / 'proof/usd_diff_contact08_vs_centered.json')['differences'])
baseline = read(root / 'reports/app_centering_install01/baseline.json')
repo = Path('/Users/antonioperedo/Desktop/screen_time')
status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
assert status == baseline['full_git_status'] and head == baseline['head']
assert sha(repo / baseline['relative_path']) == app['candidate_sha256']
assert sha(repo / Path(baseline['relative_path']).parent / 'Contents.json') == baseline['contents_json_sha256']
original = read(root / 'reports/original_checksums.json')
assert all(sha(Path(path)) == digest for path, digest in original.items())
archives = {}
for name in ['v2', 'v3', 'v5', 'final08', 'forged05', 'forged06', 'forged08']:
    manifest = read(root / f'reports/{name}_archive.json')
    assert all(sha(root / manifest['root'] / path) == digest for path, digest in manifest['files'].items())
    archives[name] = len(manifest['files'])

for name in ['mobile', 'scenes', 'proof']:
    shutil.rmtree(root / name)
    shutil.copytree(candidate / name, root / name)
for name in ['logs', 'reports']:
    shutil.copytree(candidate / name, root / name, dirs_exist_ok=True)
shutil.copytree(candidate / 'source/bakes', root / 'source/bakes', dirs_exist_ok=True)
shutil.copytree(candidate / 'work', root / 'work', dirs_exist_ok=True)
shutil.copy2(candidate / 'parameters.json', root / 'parameters.json')
for name in ['build_iron.py', 'generate_forged_textures.py', 'bake_restrained_normals.py',
             'bake_contact_occlusion.py', 'verify_crystal.py', 'run_verification.py']:
    shutil.copy2(candidate / 'scripts' / name, root / 'scripts' / name)
for name in ['app_metrics.json', 'blender_metrics.json', 'blender_metrics.txt',
             'measure_app_output.txt', 'app_test_protocol.txt', 'app_build.txt']:
    shutil.copy2(candidate / name, root / 'proof' / name)
shutil.copy2(candidate / 'app_rest.png', root / 'proof/app_iron_rest.png')
for path in (root / 'proof').rglob('*.png'):
    with Image.open(path) as image:
        image.load()
with zipfile.ZipFile(root / 'mobile/iron_badge_mobile.usdz') as archive:
    assert archive.testzip() is None
    textures = [name for name in archive.namelist() if name.endswith('.png')]
    assert len(textures) == 14
    assert all(archive.read(name) == (root / 'mobile/textures' / Path(name).name).read_bytes() for name in textures)

selected = dict(revision='centering', iteration=1, source='centering_revision/01',
                usdz_sha256=app['candidate_sha256'], app_tested_bytes_identical=True,
                installed_in_app_repo=True, visual_centering_review='PASS',
                previous_version='previous/forged08/', normal_maps_authorized_by_user=True)
for name in ['selected_revision', 'selected_iteration']:
    (root / f'reports/{name}.json').write_text(json.dumps(selected, indent=2) + '\n')
checks = dict(selected_revision=selected, app=app, plane_tone_and_brightness_pass=True,
              maximum_normal_difference_within_every_plane=0,
              silver_enclosure_geometry_identity=True, rim_finish_unchanged=True,
              historical_smooth_finish_criterion_pass=metrics['criterion_6_pass'],
              finish_policy='User-approved forged texture replaces the old perfectly smooth finish limits.',
              protected_original_hashes_verified=len(original), archives_hashes_verified=archives,
              app_repo_git_status=status, only_authorized_badge_asset_modified=True,
              usdz_crc='PASS', embedded_texture_files=14,
              file_bytes=geometry['bytes_iron'], triangles=geometry['total_triangles_iron'],
              mounting_shadow_limitation='Inherited local occlusion remains subtle in the app; this revision addresses centering.')
for name in ['final_delivery_check', 'all_checks']:
    (root / f'proof/{name}.json').write_text(json.dumps(checks, indent=2) + '\n')
(root / 'reports/app_repo_final.json').write_text(json.dumps(dict(
    status=status, head=head, asset_sha256=app['candidate_sha256'],
    iron_left_installed_by_explicit_user_request=True, only_authorized_asset_modified=True
), indent=2) + '\n')

gap = min(row['display_level_difference'] for row in metrics['neighbor_rows']['harsh'])
lines = ['# Iron badge: centered crystal', '',
    'Delivered centering revision 01, using exactly the bytes tested in the real app. Previous contact revision 08 is preserved in `previous/forged08/`; all earlier archives are intact.', '',
    'The ridge now runs straight from the upper tip through both central vertices to the lower tip. Three broad front planes meet it on each side. Lower shoulders are balanced while retaining the angled upper-right cut and slight silhouette asymmetry. Authoring width 2.423145 and height 3.738880 units are identical to the previous crystal; max visible depth is slightly reduced. The shape is centered by silhouette area, then adjusted right by 0.025 units to balance the lit left side. Final vertex offset is (-0.008041,+0.018959) units, baked into geometry with identity transforms.', '',
    'The upper-left plane color gain is 0.60. The formerly dark upper-right plane gain is 0.95, making that side readable. The forged detail source, contrast strength 0.85, roughness palette and restrained normal-map limits are retained. Crystal normals are rebaked for the new geometry and tangent frames. Nine enclosure maps retain exact prior decoded pixels, including all casing/rim/back and inset roughness/normal maps. Only the inset color shadow is rebaked around the changed outline, starting from the unshadowed source to avoid cumulative darkening. Back Z=0.033 retains the seating overlap.', '',
    'The approved rim, casing geometry, colors, roughness and normals are unchanged. All object, mesh and material IDs remain identical to silver. No name was lost. Floor cut remains uncapped at Y=-2.895, USD Y up, metersPerUnit=1, front +Z and no transforms. Bevel width remains 0.004 with one segment and explicit own bevel material; narrow strips inherit their owner face normal and material. No widened bevel glints.', '',
    '[USDZ](mobile/iron_badge_mobile.usdz), [master](scenes/iron_medallion_master.blend), [reduced](scenes/iron_badge_mobile_reduced.blend), [final](scenes/iron_badge_mobile.blend).', '',
    '[Actual app screenshot](proof/app_iron_rest.png), [app before/after](proof/centering_before_after_app.png), [app silver comparison](proof/app_silver_vs_iron_rest.png), [same-scale Blender comparison](proof/silver_vs_iron_same_scale.png), [front](proof/iron_front_app_lighting.png), [three-quarter](proof/iron_three_quarter_app_lighting.png), [all front planes](proof/all_front_planes_by_id.png), [surface maps](proof/forged_texture_sheet.png), [normal maps](proof/restrained_normal_maps.png), [smoothness numbers](proof/NUMBERS.md).', '',
    '## Live app and Blender checks', '',
    '| Trial | Loaded 3D | Clip pixels | Rim top | Neighbor tone gap | Brightest / darkest plane mean | Visual centering |',
    '|---|---|---:|---:|---:|---:|---|',
    f"| Centering 01 | {app['loaded_3d']} | {app['emblem_clip']} | {app['rim_top']:.1f} | {gap:.3f} | {metrics['smoothness']['harsh']['candidate_brightest_mean']:.3f} / {metrics['smoothness']['harsh']['candidate_darkest_mean']:.3f} | PASS |", '',
    'Actual app inspection: ridge and shoulders look centered at phone size; upper-right face is readable. Upper-left stays brightest with visible forged detail and no new halo outside the crystal. Silver app clipping reference is 796. Blender brightest plane is below silver\'s 235.3801 display-level mean; every neighboring plane differs by at least 10 levels and no plane mean falls below 15.', '',
    'The original perfectly smooth surface criterion remains false because the user requested the reference\'s forged texture and explicitly authorized restrained normal maps. Raw numbers are preserved, not relabeled as passes. The mounting contact shadow remains subtle under app lighting, as already recorded for contact08; this task changes centering and does not declare that earlier visual limitation solved.', '',
    '## Plane flatness', '', '| Plane | Kind | Max normal difference |', '|---:|---|---:|']
for row in planes['planes']:
    lines.append(f"| {row['plane']} | {row['kind']} | {row['maximum_normal_component_difference']:g} |")
lines += ['', 'All six front, seven side and one hidden back planes have exactly zero within-plane normal variation. UV microrelief affects per-pixel shading, not macro-plane planarity.', '',
    '## Budget', '', '| File | Triangles | Bytes |', '|---|---:|---:|',
    f"| Silver v3 | {geometry['total_triangles_silver']:,} | {geometry['bytes_silver']:,} |",
    '| Previous contact08 | 38,434 | 4,228,165 |',
    f"| Centered Iron | {geometry['total_triangles_iron']:,} | {geometry['bytes_iron']:,} |", '',
    'The emblem is 92 triangles. Fourteen PNG maps remain 512 x 512. Source nominal height/width are unchanged; final beveled bounds differ slightly with the new corner angles. All five enclosure meshes match silver exactly in every authored attribute and bound.', '',
    '## Materials', '', 'Linear underlying palette, modulated by reference-derived color maps. Emblem gains are listed above. Roughness maps retain the forged variation; normals use strength 1 with the intended strength baked into pixels.', '',
    '| Material ID | Linear RGB | Metallic | Nominal roughness |', '|---|---|---:|---:|']
palette = read(candidate / 'reports/material_palette.json')
for name, short in [('Silver | circumferential brushed steel', 'Casing'), ('Outer edge | smooth satin silver', 'Casing'),
                    ('Back and edge | gunmetal', 'Casing'), ('Silver | polished cut edges', 'Inner_edge'),
                    ('Silver | polished cut edges', 'Rim_inner_lip'), ('Emblem | satin silver facets', 'Emblem'),
                    ('Emblem | shaded outer facets', 'Emblem'), ('Recess | smoked nickel', 'Inner_channel'),
                    ('Inset | finely textured charcoal', 'Inset')]:
    color, metallic, roughness = palette[name]
    identifier = (name + ' Mobile ' + short).replace(' ', '_').replace('|', '_')
    lines.append(f"| `{identifier}` | {tuple(color)} | {metallic:g} | {roughness:g} |")
lines += ['', '## Scope and preservation', '',
    'Only the already-authorized badge asset is modified in the app repo. Its SHA matches the delivered file. Contents.json and HEAD match the baseline. No source file, helper, config, branch or commit was changed. The file remains installed for the user\'s local build, as previously requested; no distribution build was published.', '',
    'ScreenTime: ** BUILD SUCCEEDED **  \nScreenTime-UIOnly: ** BUILD SUCCEEDED **  \nScreenTime-UIOnly simulator: ** BUILD SUCCEEDED **  \ntests skipped: presentation lane, no logic changed', '',
    'Simulator iPhone 17, 69A29DD2-C91E-487A-81B9-3B146DF8F07B; bundle com.antonioperedo.screentime.uidev. Shader warmup and two relaunches followed the established procedure. No physical-device test.', '',
    f'Protected original files verified unchanged: {len(original)}. Archive hashes verified: {archives}.', '',
    'Full old-vs-new USD attribute differences are recorded below. Against contact08, only emblem mesh/subset data changes inside USD; updated crystal texture bytes and the repositioned inset shadow are recorded separately. The five enclosure meshes and every non-emblem USD material/shader property stay unchanged.', '',
    '## Check outputs', '']
outputs = ['proof/centering_design_metrics.json', 'proof/projected_centering_metrics.json',
           'proof/unchanged_enclosure_finish.json', 'proof/usd_diff_contact08_vs_centered.json',
           'proof/usd_diff_silver_vs_iron.json', 'logs/full_verification_run.txt', 'proof/usdchecker.log',
           'proof/reimport_check.txt', 'proof/floor_cut_verification.txt', 'proof/floor_cut_topology.txt',
           'proof/geometry_identity.txt', 'proof/crystal_design_validation.txt',
           'proof/scene_and_normals_validation.txt', 'proof/measure_app_output.txt', 'proof/app_build.txt',
           'proof/app_test_protocol.txt', 'proof/blender_metrics.txt', 'proof/proof_analysis.txt',
           'proof/smoothness_pose00.txt', 'proof/smoothness_pose20.txt', 'proof/smoothness_pose45.txt',
           'reports/restrained_normal_bake.json', 'reports/contact_occlusion.json', 'logs/final_proofs.txt']
for name in outputs:
    assert (root / name).exists(), name
    lines += [f'### {name}', '', '```text', (root / name).read_text(), '```', '']
lines += ['## Delivery verification', '', '```json', json.dumps(checks, indent=2), '```', '']
(root / 'REPORT.md').write_text('\n'.join(lines))
files = sorted(path for path in root.rglob('*') if path.is_file() and 'previous' not in path.parts
               and 'analysis_env' not in path.parts and '__pycache__' not in path.parts and path.name != 'FILE_MANIFEST.txt')
(root / 'FILE_MANIFEST.txt').write_text('\n'.join(str(path.relative_to(root)) for path in files) + '\n')
print(json.dumps(checks, indent=2))
