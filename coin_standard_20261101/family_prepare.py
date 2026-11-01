"""Snapshot the audited coin family before applying the approved dimensions."""
from pathlib import Path
import json, hashlib, shutil, zipfile
from pxr import Usd, UsdGeom

R = Path(__file__).resolve().parent
F = R / 'family'
F.mkdir(exist_ok=True)
audit = json.loads((R / 'family_audit.json').read_text())
manifest = []
for item in audit:
    name = item['dataset'].removeprefix('Badge3DPreview')
    c = F / name / 'candidate01'
    for part in ['mobile', 'source', 'review']:
        (c / part).mkdir(parents=True, exist_ok=True)
    original = F / name / 'original.usdz'
    source = Path(item['source'])
    if name == 'EmeraldSprout':
        source = R / 'original/mobile/emerald_sprout_original.usdz'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256'], name
    if not original.exists():
        shutil.copyfile(source, original)
    assert hashlib.sha256(original.read_bytes()).hexdigest() == item['sha256']
    pkg = F / 'work' / name
    pkg.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(original) as archive:
        archive.extractall(pkg)
        usd = next(n for n in archive.namelist() if n.endswith(('.usd', '.usda', '.usdc')))
    stage = Usd.Stage.Open(str(pkg / usd))
    UsdGeom.SetStageUpAxis(stage, 'Z')
    stage.GetRootLayer().Export(str(pkg / 'blender_import.usdc'))
    manifest.append(dict(name=name, selection=name[0].lower()+name[1:], dataset=item['dataset'],
                         preview_asset=item['source'], original_sha256=item['sha256']))
(F / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
preview = R.parent/'emerald_trophy_20261025/preview/ScreenTime'
placement = preview/'Sources/App/Features/Badges/Badge3DLiveBadge.swift'
if not (F/'preview_before.swift').exists():
    shutil.copyfile(placement, F/'preview_before.swift')
snap = F/'unrelated_assets_before.json'
if not snap.exists():
    family_paths = {x['preview_asset'] for x in manifest}
    untouched = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (preview/'SupportingFiles/Assets.xcassets').glob('Badge3D*.dataset/*.usdz')
                 if str(p) not in family_paths}
    snap.write_text(json.dumps(untouched, indent=2)+'\n')
print('Prepared', len(manifest), 'complete original coins. Approved Sprout dimensions: rim 0.8, depth 0.7.')
