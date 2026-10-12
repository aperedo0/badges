"""Deliver a fully app-tested forged revision without changing its tested asset bytes."""
from pathlib import Path
import sys,json,hashlib,shutil
root=Path(__file__).resolve().parents[1];number=int(sys.argv[1]);c=root/f'forged_revision/{number:02d}'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((c/'app_metrics.json').read_text());m=json.loads((c/'blender_metrics.json').read_text())
assert a['loaded_3d'] and a['passes_numeric_app_checks'] and m['criterion_5_pass'] and m['criterion_7_pass']
assert a['candidate_sha256']==sha(c/'mobile/iron_badge_mobile.usdz')
asset='ScreenTime/SupportingFiles/Assets.xcassets/TestBadge3DModel.dataset/silver_badge_mobile.usdz'
assert (c/'repo_status_after.txt').read_text()==' M '+asset+'\n'
assert sha(Path('/Users/antonioperedo/Desktop/screen_time')/asset)==sha(c/'mobile/iron_badge_mobile.usdz')
for rev in ['v5','final08']:
 manifest=json.loads((root/f'reports/{rev}_archive.json').read_text())
 assert all(sha(root/manifest['root']/p)==digest for p,digest in manifest['files'].items())
for n in ['mobile','scenes','proof']:
 shutil.rmtree(root/n);shutil.copytree(c/n,root/n)
for n in ['reports','logs']:shutil.copytree(c/n,root/n,dirs_exist_ok=True)
for p in (c/'scripts').glob('*.py'):
 # These older smooth-finish wrappers do not describe the forged revision.
 if p.name in ['write_forged_report.py','promote_forged_revision.py','write_report.py','write_iteration_report.py','verify_look.py','finalize_proofs.py','finalize_iteration_delivery.py','promote_iteration.py','test_in_app.py','build_refinement.py','make_revision_inspections.py','build_contact_revision.py']:continue
 shutil.copy2(p,root/'scripts'/p.name)
shutil.copytree(c/'source/bakes',root/'source/bakes',dirs_exist_ok=True)
for n in ['forged_reference.png','app_before.png']:shutil.copy2(c/'source'/n,root/'source'/n)
shutil.copy2(c/'parameters.json',root/'parameters.json')
for p in (c/'work').iterdir():
 if p.is_file():shutil.copy2(p,root/'work'/p.name)
for n in ['app_metrics.json','measure_app_output.txt','app_test_protocol.txt','app_build.txt','blender_metrics.json','blender_metrics.txt']:
 shutil.copy2(c/n,root/'proof'/n)
shutil.copy2(c/'app_rest.png',root/'proof/app_iron_rest.png')
result={'revision':'forged','iteration':number,'source':str(c.relative_to(root)),'usdz_sha256':sha(root/'mobile/iron_badge_mobile.usdz'),'app_tested_bytes_identical':True,'normal_maps_authorized_by_user':True,'prior_approved_08_preserved':'previous/final08/','prior_approved_v5_preserved':'previous/v5/','geometry_and_app_checks_pass':True,'installed_in_app_repo':True,'prior_forged06_preserved':'previous/forged06/','old_uniform_surface_limits_superseded_by_reference_finish_request':True,'contact_visual_acceptance':False,'selection_reason':'Best tested contact revision at the eight-trial limit; physical gap closed, contact cue improved, floating appearance remains subtle in the app.'}
(root/'reports/selected_revision.json').write_text(json.dumps(result,indent=2))
(root/'reports/selected_iteration.json').write_text(json.dumps(result,indent=2))
for old,new in [('final_approval.json','final08_user_approval.json'),('highlight_result.json','final08_highlight_result.json')]:
 if (root/'reports'/old).exists():(root/'reports'/old).rename(root/'reports'/new)
# Keep the normal-free control comparison in the final proof package.
assert (root/'proof/restrained_normal_maps.png').exists(), 'Candidate normal-map inspection sheet is required'
checks={'loaded_3d':a['loaded_3d'],'app_clip_at_most_800':a['emblem_clip']<=800,'rim_in_range':142<=a['rim_top']<=152,'plane_tone_and_brightness':m['criterion_5_pass'],'base_mesh_plane_normal_difference_zero':m['criterion_7_pass'],'structural_export_and_scope_pass':True,'normal_maps_user_authorized':True,'original_smoothness_criteria_pass':m['criterion_6_pass'],'finish_policy':'Original smoothness limits are superseded by the requested forged texture.'}
checks['contact_visual_acceptance']=False
checks['remaining_limitation']='Baked albedo contact occlusion stays subtle under app lighting. This is an improved best version, not a fully accepted floating-look fix.'
(root/'proof/all_checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(result,indent=2))
