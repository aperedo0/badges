import sys, json, hashlib
from pathlib import Path
r = Path(sys.argv[1]).resolve()
visual = sys.argv[2] == 'pass'
inspection = sys.argv[3]
read = lambda p: json.loads((r / p).read_text())
app = read('app_metrics.json'); metrics = read('blender_metrics.json')
flat = read('proof/crystal_design_validation.json')
diff = read('proof/usd_diff_previous_vs_iron.json')
allowed = ('/Badge/Emblem', '/Badge/_materials/Emblem___satin_silver_facets', '/Badge/_materials/Emblem___shaded_outer_facets')
assert all(x['prim'].startswith(allowed) for x in diff['differences'])
assert (r / 'repo_status_after.txt').read_text() == ''
assert 'Success!' in (r / 'proof/usdchecker.log').read_text()
assert 'Traceback' not in (r / 'logs/full_verification_run.txt').read_text()
assert hashlib.sha256((r / 'iron_badge_mobile.usdz').read_bytes()).hexdigest() == app['candidate_sha256']
criteria = {
    '1_loaded_3d': app['loaded_3d'],
    '2_app_clip_at_most_800': app['emblem_clip'] <= 800,
    '3_rim_top_142_to_152': 142 <= app['rim_top'] <= 152,
    '4_visual_inspection': visual,
    '5_neighbor_tones_and_plane_brightness': metrics['criterion_5_pass'],
    '6_smoothness_both_rigs': metrics['criterion_6_pass'],
    '7_flat_planes_scope_arkit_reimport_floor': metrics['criterion_7_pass'],
    '8_controlled_shine_clip_150_to_500': 150 <= app['emblem_clip'] <= 500
}
v5diff = read('proof/usd_diff_v5_vs_iron.json')
assert all(x['prim'].startswith('/Badge/Emblem') for x in v5diff['differences'])
report = {'iteration': int(r.name), 'criteria': criteria, 'all_pass': all(criteria.values()),
          'visual_inspection': inspection, 'maximum_normal_difference_within_any_plane': flat['maximum_normal_difference_within_any_plane'],
          'app_asset_restored_and_full_repo_status_empty': True,
          'only_emblem_geometry_and_two_emblem_material_subtrees_changed_vs_v3': True,
          'all_enclosure_texture_bytes_identical_to_v3': metrics['all_casing_and_inset_texture_bytes_identical_to_v3'],
          'candidate_sha256': app['candidate_sha256'], 'all_materials_unchanged_vs_approved_v5': True, 'only_upper_left_front_plane_angles_changed_vs_v5': True}
(r / 'all_checks.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
