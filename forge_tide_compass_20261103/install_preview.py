from pathlib import Path
import sys,json,re,shutil,difflib,hashlib
from pace import work
work(1)
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();item=json.loads((ROOT/'badges.json').read_text())[key]
P=ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime';swift=P/'Sources/App/Features/Badges/Badge3DLiveBadge.swift';assets=P/'SupportingFiles/Assets.xcassets'
backup=ROOT/'private_preview_before.swift'
if not backup.exists():shutil.copyfile(swift,backup)
audit=ROOT/'other_assets_before.json'
if not audit.exists():audit.write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.glob('Badge3D*.dataset/*.usdz')},indent=2)+'\n')
s=swift.read_text();line=re.search(r'static let items: \[String: String\] = (\[.*?\])',s).group(1);selection=item['selection']
if '"'+selection+'"' not in line:s=s.replace(line,line[:-1]+',"'+selection+'":"'+item['name']+'"]',1)
dataset='Badge3DPreview'+selection[0].upper()+selection[1:];entry='        if datasetName == "'+dataset+'" { return .neutral }';marker='        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }'
if entry not in s:assert marker in s;s=s.replace(marker,marker+'\n'+entry,1)
swift.write_text(s)
(ROOT/'preview_integration.patch').write_text(''.join(difflib.unified_diff(backup.read_text().splitlines(True),s.splitlines(True),fromfile='a/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift',tofile='b/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift')))
dest=assets/(dataset+'.dataset');dest.mkdir(exist_ok=True);shutil.copyfile(C/'mobile'/(key+'_badge_mobile.usdz'),dest/'coin.usdz');(dest/'Contents.json').write_text(json.dumps(dict(data=[dict(filename='coin.usdz',idiom='universal')],info=dict(author='xcode',version=1)),indent=2)+'\n')
for p,digest in json.loads(audit.read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest
print(item['name'],'installed in separate preview only')
