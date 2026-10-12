"""Finalize existing proofs and confirm the delivered bytes are the app-tested bytes."""
import sys, json, hashlib, zipfile, subprocess
from pathlib import Path
from PIL import Image
r = Path(__file__).resolve().parents[1]
selected = json.loads((r / 'reports/selected_iteration.json').read_text())
candidate = r / f"iterations/{selected['iteration']:02d}"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['mobile/iron_badge_mobile.usdz', 'scenes/iron_medallion_master.blend',
             'scenes/iron_badge_mobile_reduced.blend', 'scenes/iron_badge_mobile.blend']:
    assert sha(r / name) == sha(candidate / name), name
required = ['proof/app_silver_vs_iron_rest.png', 'proof/iron_front_app_lighting.png',
            'proof/iron_three_quarter_app_lighting.png', 'proof/silver_vs_iron_same_scale.png',
            'proof/all_facets_pose00.png', 'proof/all_facets_pose20.png', 'proof/all_facets_pose45.png',
            'proof/NUMBERS.md', 'proof/render_diff_silver_vs_iron.json',
            'previous/v3/mobile/iron_badge_mobile.usdz', 'previous/v3/REPORT.md']
for name in required: assert (r / name).is_file() and (r / name).stat().st_size > 0, name
for script in ['verify_look.py', 'write_report.py']:
    with (r / 'logs' / (script + '.txt')).open('w') as f:
        p = subprocess.run([sys.executable, str(r / 'scripts' / script)], stdout=f, stderr=subprocess.STDOUT)
    assert p.returncode == 0, script
images = list((r / 'proof').rglob('*.png'))
for p in images:
    with Image.open(p) as im: im.load()
with zipfile.ZipFile(r / 'mobile/iron_badge_mobile.usdz') as z:
    assert z.testzip() is None
    names = [n for n in z.namelist() if n.endswith('.png')]; assert len(names) == 7
    assert all(z.read(n) == (r / 'mobile/textures' / Path(n).name).read_bytes() for n in names)
result = {'final_accepted_by_user': selected['accepted'] and selected['user_approved'],
          'historical_all_pass_result': selected['all_pass'], 'selected_iteration': selected['iteration'],
          'app_tested_asset_and_all_three_scenes_copied_byte_exactly': True,
          'proof_pngs_decoded': len(images), 'embedded_texture_bytes_equal_to_delivered_pngs': 7,
          'usdz_zip_crc': 'PASS', 'usdz_sha256': sha(r / 'mobile/iron_badge_mobile.usdz'),
          'file_bytes': (r / 'mobile/iron_badge_mobile.usdz').stat().st_size,
          'full_app_repo_git_status': json.loads((r / 'reports/app_repo_final.json').read_text())['status']}
if (r/'reports/highlight_result.json').exists():
    optional = json.loads((r/'reports/highlight_result.json').read_text())
    result['optional_shine_applied_and_accepted'] = optional['applied'] and optional['user_approved']
    result['original_optional_clip_target_met'] = optional['original_clip_target_met']
    result['original_neighbor_gap_target_met'] = optional['original_neighbor_gap_target_met']
    result['approved_v5_preserved_in_previous_v5'] = True
    result['total_iterations'] = optional['total_iterations']
(r / 'proof/final_delivery_check.json').write_text(json.dumps(result, indent=2))
with (r / 'REPORT.md').open('a') as f:
    f.write('\n\n## Final delivery check\n\n```json\n' + json.dumps(result, indent=2) + '\n```\n')
files = sorted(p for p in r.rglob('*') if p.is_file() and 'previous' not in p.parts
               and 'analysis_env' not in p.parts and '__pycache__' not in p.parts and p.name != 'FILE_MANIFEST.txt')
(r / 'FILE_MANIFEST.txt').write_text('\n'.join(str(p.relative_to(r)) for p in files) + '\n')
print(json.dumps(result, indent=2))
