"""Promote a checked iteration without changing its tested bytes."""
import sys, json, hashlib, shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
candidate = root / f'iterations/{int(sys.argv[1]):02d}'
checks = json.loads((candidate / 'all_checks.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
approval_path = root / 'reports/final_approval.json'
approval = json.loads(approval_path.read_text()) if approval_path.exists() else None
approved = bool(approval and approval['accepted'] and
                approval['iteration'] == int(candidate.name) and
                approval['usdz_sha256'] == sha(candidate / 'mobile/iron_badge_mobile.usdz'))
assert checks['all_pass'] or approved
for revision in ['v3', 'v5']:
    archive = json.loads((root / f'reports/{revision}_archive.json').read_text())
    assert all(sha(root / archive['root'] / p) == h for p, h in archive['files'].items())
# Both complete prior packages are archived before any active deliverable changes.
for name in ['mobile', 'scenes', 'proof']:
    shutil.rmtree(root / name)
    shutil.copytree(candidate / name, root / name)
for name in ['reports', 'logs']:
    shutil.copytree(candidate / name, root / name, dirs_exist_ok=True)
for name in ['build_iron.py', 'verify_crystal.py', 'run_verification.py']:
    shutil.copy2(candidate / 'scripts' / name, root / 'scripts' / name)
shutil.copy2(candidate / 'parameters.json', root / 'parameters.json')
for p in (candidate / 'work').iterdir():
    if p.is_file(): shutil.copy2(p, root / 'work' / p.name)
for p in (root / 'previous/v3/proof/renders').glob('silver*.png'):
    shutil.copy2(p, root / 'proof/renders' / p.name)
for p in (root / 'previous/v3/proof').glob('smoothness_silver*'):
    shutil.copy2(p, root / 'proof' / p.name)
for name in ['app_rest.png', 'app_metrics.json', 'measure_app_output.txt', 'blender_metrics.json', 'blender_metrics.txt', 'all_checks.json']:
    shutil.copy2(candidate / name, root / 'proof' / ('app_iron_rest.png' if name == 'app_rest.png' else name))
assert sha(root / 'mobile/iron_badge_mobile.usdz') == json.loads((candidate / 'app_metrics.json').read_text())['candidate_sha256']
result = {'iteration': int(candidate.name), 'all_pass': checks['all_pass'],
          'accepted': checks['all_pass'] or approved, 'user_approved': approved,
          'usdz_sha256': sha(root / 'mobile/iron_badge_mobile.usdz'),
          'source': str(candidate.relative_to(root)), 'previous_v3_preserved': True,
          'previous_v5_preserved': True}
(root / 'reports/selected_iteration.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
