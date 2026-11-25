"""Register the delivered model in the independent Badge Studio preview project."""
from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1]
private=root.parent/'emerald_trophy_20261025/preview/ScreenTime'
registry=private/'Sources/App/Features/Badges/Badge3DLiveBadge.swift'
text=registry.read_text()
if '"rubyHourglass":' not in text:
    marker='"blueHourglass":"Blue Hourglass"'
    assert marker in text
    text=text.replace(marker,marker+',"rubyHourglass":"Ruby Hourglass"',1)
if '"Badge3DPreviewRubyHourglass"' not in text:
    marker='"Badge3DPreviewBlueHourglass",'
    assert marker in text
    text=text.replace(marker,marker+' "Badge3DPreviewRubyHourglass",',1)
if text!=registry.read_text():registry.write_text(text)
asset=private/'SupportingFiles/Assets.xcassets/Badge3DPreviewRubyHourglass.dataset'
asset.mkdir(exist_ok=True)
(asset/'Contents.json').write_text(json.dumps({'data':[{'filename':'coin.usdz','idiom':'universal'}],'info':{'author':'xcode','version':1}},indent=2)+'\n')
shutil.copy2(root/'mobile/ruby_hourglass.usdz',asset/'coin.usdz')
