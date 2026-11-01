"""Install reviewed family models and scoped placement in the private preview."""
from pathlib import Path
import json,shutil,hashlib,difflib
R=Path(__file__).resolve().parent;F=R/'family'
manifest=json.loads((F/'manifest.json').read_text())
for item in manifest:
    source=F/item['name']/'candidate01/mobile/coin.usdz'
    report=json.loads((source.parents[1]/'validation.json').read_text())
    assert report['sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copyfile(source,item['preview_asset'])
preview=R.parent/'emerald_trophy_20261025/preview/ScreenTime'
path=preview/'Sources/App/Features/Badges/Badge3DLiveBadge.swift'
text=(F/'preview_before.swift').read_text()
old='        if datasetName == "Badge3DPreviewEmeraldSprout" { return Badge3DTierLook(size: 0.96, lift: 0.441) }'
assert old in text
names=', '.join('"'+x['dataset']+'"' for x in manifest)
new='        if ['+names+'].contains(datasetName) { return Badge3DTierLook(size: 0.96, lift: 0.441) }'
path.write_text(text.replace(old,new,1))
(F/'preview_placement.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),path.read_text().splitlines(True),fromfile='a/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift',tofile='b/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift')))
for name,digest in json.loads((F/'unrelated_assets_before.json').read_text()).items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
print('Installed 12 family coins in private preview. Other assets unchanged.')
