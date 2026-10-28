"""Install only the new phoenix entry in the existing private preview."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent;R=ROOT/'phoenix';C=R/(R/'candidate.txt').read_text().strip()
P=ROOT.parent/'emerald_trophy_20261025/preview';swift=P/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'
text=swift.read_text();before=text
if '"bronzePhoenix":"Bronze Phoenix"' not in text:
 text=text.replace('"wingedSword":"Winged Sword"]','"wingedSword":"Winged Sword","bronzePhoenix":"Bronze Phoenix"]',1)
if 'if datasetName == "Badge3DPreviewBronzePhoenix" { return .neutral }' not in text:
 marker='        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }'
 text=text.replace(marker,marker+'\n        if datasetName == "Badge3DPreviewBronzePhoenix" { return .neutral }',1)
if text!=before:
 (ROOT/'private_preview_before.swift').write_text(before)
 swift.write_text(text)
asset=P/'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DPreviewBronzePhoenix.dataset';asset.mkdir(exist_ok=True)
shutil.copyfile(C/'mobile/phoenix_badge_mobile.usdz',asset/'coin.usdz')
(asset/'Contents.json').write_text(json.dumps({'data':[{'filename':'coin.usdz','idiom':'universal'}],'info':{'author':'xcode','version':1}},indent=2)+'\n')
print('Bronze Phoenix installed into private preview source only')
