"""Read only content verification after the owner authorized storage cleanup."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
inventory = json.loads((HERE / 'inventory.json').read_text())
report = json.loads((HERE / 'report.json').read_text())
deleted = {x['path'] for x in report['deleted']}
checked = 0
failures = []


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


for group in inventory['duplicates']:
    for relative in group['paths']:
        if relative in deleted:
            continue
        p = ROOT / relative
        if not p.is_file() or digest(p) != group['hash']:
            failures.append(relative)
        checked += 1
for item in report['deleted']:
    assert not (ROOT / item['path']).exists(), item['path']
    if 'retained' in item:
        p = ROOT / item['retained']
        if not p.is_file() or digest(p) != item['retained_sha256']:
            failures.append(item['retained'])
        checked += 1
pause = json.loads((ROOT / 'camp_owl_mountain_sapphire_20261111/progress.json').read_text())
assert pause['status'] == 'paused'
assert not list(ROOT.rglob('.storage_clone_*'))
result = dict(files_checked=checked, changed_or_missing=failures,
              pause_saved=True, no_temporary_clones_left=True,
              badge_building_resumed=False)
(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
assert not failures
