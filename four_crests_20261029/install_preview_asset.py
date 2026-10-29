"""Add a separate reference crest to the existing private preview."""
from pathlib import Path
import json,sys,shutil,re
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();item=json.loads((ROOT/'badges.json').read_text())[key];selection=item['selection'];name=item['name']
P=ROOT.parent/'emerald_trophy_20261025/preview';swift=P/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift';before=swift.read_text();s=before
if not (ROOT/'private_preview_before.swift').exists():(ROOT/'private_preview_before.swift').write_text(before)
line=re.search(r'static let items: \[String: String\] = (\{?\[.*?\])',s).group(1)
if '"'+selection+'"' not in line:s=s.replace(line,line[:-1]+',"'+selection+'":"'+name+'"]',1)
dataset='Badge3DPreview'+selection[0].upper()+selection[1:];entry='        if datasetName == "'+dataset+'" { return .neutral }';marker='        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }'
if entry not in s:s=s.replace(marker,marker+'\n'+entry,1)
if s!=before:swift.write_text(s)
asset=P/'ScreenTime/SupportingFiles/Assets.xcassets'/(dataset+'.dataset');asset.mkdir(exist_ok=True);shutil.copyfile(C/'mobile'/(key+'_badge_mobile.usdz'),asset/'coin.usdz');(asset/'Contents.json').write_text(json.dumps({'data':[{'filename':'coin.usdz','idiom':'universal'}],'info':{'author':'xcode','version':1}},indent=2)+'\n');print(name,'installed into private preview source only')
