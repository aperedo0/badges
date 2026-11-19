"""Add the new private preview entry and its isolated amethyst optical profile."""
from pathlib import Path
import json,shutil,difflib,hashlib
R=Path(__file__).resolve().parent;P=R.parent/'emerald_trophy_20261025/preview/ScreenTime'
runtime=P/'Sources/App/Features/Badges';assets=P/'SupportingFiles/Assets.xcassets'
for filename in ['Badge3DLiveBadge.swift','BadgeCrestGemSurface.metal']:
 source=runtime/filename;backup=R/'runtime_before'/filename;backup.parent.mkdir(exist_ok=True)
 if not backup.exists():shutil.copyfile(source,backup)
checks=R/'unrelated_assets_before.json'
if not checks.exists():checks.write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.glob('Badge3D*.dataset/*.usdz') if 'AuroraMountain' not in str(p)},indent=2)+'\n')
swift=runtime/'Badge3DLiveBadge.swift';s=swift.read_text()
if '"auroraMountain":"Aurora Mountain"' not in s:
 old='"sapphireStairway":"Sapphire Stairway"]';assert old in s;s=s.replace(old,'"sapphireStairway":"Sapphire Stairway","auroraMountain":"Aurora Mountain"]',1)
 marker='        if datasetName == "Badge3DPreviewCrimsonShield" { return .neutral }'
 s=s.replace(marker,marker+'\n        if datasetName == "Badge3DPreviewAuroraMountain" { return .neutral }',1)
if 'case "CrestGem_Amethyst"' not in s:
 old='        case "CrestGem_Ruby": return 2';assert old in s;s=s.replace(old,old+'\n        case "CrestGem_Amethyst": return 3',1)
s=s.replace('crestStyle == 0 ? 0.12 : 0.28','crestStyle == 0 ? 0.12 : crestStyle == 3 ? 0.18 : 0.28')
swift.write_text(s)
shader=runtime/'BadgeCrestGemSurface.metal';s=shader.read_text()
if 'float3(1.54, 1.55, 1.56)' not in s:
 old='float3 indices = profile.y < 0.5 ? float3(1.45, 1.46, 1.475) : float3(1.76, 1.77, 1.79);'
 assert old in s;s=s.replace(old,'float3 indices = profile.y < 0.5 ? float3(1.45, 1.46, 1.475)\n                   : profile.y > 2.5 ? float3(1.54, 1.55, 1.56) : float3(1.76, 1.77, 1.79);',1)
 old=': profile.y < 1.5 ? float3(8.0, 4.0, 0.25) : float3(1.25, 16.0, 12.0);'
 assert old in s;s=s.replace(old,': profile.y < 1.5 ? float3(8.0, 4.0, 0.25)\n                        : profile.y > 2.5 ? float3(0.80, 5.5, 0.12) : float3(1.25, 16.0, 12.0);',1)
s=s.replace('float3(0.80, 5.5, 0.12)','float3(0.90, 12.0, 0.50)')
shader.write_text(s)
asset=assets/'Badge3DPreviewAuroraMountain.dataset';asset.mkdir(exist_ok=True)
shutil.copyfile(R/(R/'candidate.txt').read_text().strip()/'mobile/aurora_mountain_badge_mobile.usdz',asset/'coin.usdz')
(asset/'Contents.json').write_text(json.dumps(dict(data=[dict(filename='coin.usdz',idiom='universal')],info=dict(author='xcode',version=1)),indent=2)+'\n')
patch=''
for filename in ['Badge3DLiveBadge.swift','BadgeCrestGemSurface.metal']:
 before=(R/'runtime_before'/filename).read_text();after=(runtime/filename).read_text()
 patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/ScreenTime/Sources/App/Features/Badges/'+filename,tofile='b/ScreenTime/Sources/App/Features/Badges/'+filename))
(R/'runtime_integration.patch').write_text(patch)
for name,digest in json.loads(checks.read_text()).items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
print('Aurora Mountain installed in private preview. Existing badges and Diamond shader preserved.')
