"""Install only the reviewed Emerald Sprout draft in the private preview."""
from pathlib import Path
import json,shutil,difflib,hashlib,re
R=Path(__file__).resolve().parent;P=R.parent/'emerald_trophy_20261025/preview';cfg=json.loads((R/'draft_design.json').read_text());source=R/cfg['active_candidate']/'mobile/emerald_sprout_badge_mobile.usdz';assert source.exists()
asset=Path(cfg['original_preview_asset']);shutil.copyfile(source,asset)
path=P/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift';before=path.read_text();marker='    static func look(forDatasetName datasetName: String) -> Badge3DTierLook {'
line='        if datasetName == "Badge3DPreviewEmeraldSprout" { return Badge3DTierLook(size: 0.96, lift: '+str(cfg['preview_lift'])+') }'
updated=re.sub(r'^        if datasetName == "Badge3DPreviewEmeraldSprout"[^\n]*\n','',before,flags=re.M)
assert marker in updated;path.write_text(updated.replace(marker,marker+'\n'+line,1))
(R/'preview_placement.patch').write_text(''.join(difflib.unified_diff((R/'preview_before.swift').read_text().splitlines(True),path.read_text().splitlines(True),fromfile='a/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift',tofile='b/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift')))
# Every other coin in the audited family must retain its exact original asset.
for item in json.loads((R/'family_audit.json').read_text()):
 if item['dataset']=='Badge3DPreviewEmeraldSprout':continue
 assert hashlib.sha256(Path(item['source']).read_bytes()).hexdigest()==item['sha256'],item['dataset']
print('Only Emerald Sprout installed; its floating gap is preserved. Other 11 family assets are unchanged.')
