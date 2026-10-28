"""Add only the requested badge to the existing private preview copy."""
from pathlib import Path
import sys,json,shutil,re
ROOT=Path(__file__).resolve().parent;key=sys.argv[1]
items={'crescent_ocean':('crescentOcean','Crescent Ocean'),'mountain_crest':('mountainCrest','Mountain Crest'),'winged_sword':('wingedSword','Winged Sword')}
selection,name=items[key]
P=ROOT.parent/'emerald_trophy_20261025/preview';swift=P/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'
old=swift.read_text();s=old
line=re.search(r'static let items: \[String: String\] = (\{?\[.*?\])',s).group(1)
if '"'+selection+'"' not in line:s=s.replace(line,line[:-1]+',"'+selection+'":"'+name+'"]',1)
marker='        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }'
entry='        if ["Badge3DPreviewCrescentOcean", "Badge3DPreviewMountainCrest", "Badge3DPreviewWingedSword"].contains(datasetName) { return .neutral }'
if entry not in s:s=s.replace(marker,marker+'\n'+entry,1)
if s!=old:swift.write_text(s)
asset=P/'ScreenTime/SupportingFiles/Assets.xcassets'/('Badge3DPreview'+selection[0].upper()+selection[1:]+'.dataset');asset.mkdir(exist_ok=True)
R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
shutil.copyfile(C/'mobile'/(key+'_badge_mobile.usdz'),asset/'coin.usdz')
(asset/'Contents.json').write_text(json.dumps({'data':[{'filename':'coin.usdz','idiom':'universal'}],'info':{'author':'xcode','version':1}},indent=2))
print(name,'installed into private preview source only')
