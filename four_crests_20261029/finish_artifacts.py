"""Save delivery links, verified file hashes and compact native comparisons."""
from pathlib import Path
import json,hashlib,difflib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;items=json.loads((ROOT/'badges.json').read_text());records={};rows=[]
previews=Image.new('RGB',(1064,1120),(17,18,21));comparisons=Image.new('RGB',(2128,1136),(17,18,21));draw=ImageDraw.Draw(previews)
private=ROOT.parent/'emerald_trophy_20261025/preview';swift=private/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'
for i,(key,item) in enumerate(items.items()):
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();final=R/'mobile'/(key+'_badge_mobile.usdz');candidate=C/'mobile'/final.name;dataset='Badge3DPreview'+item['selection'][0].upper()+item['selection'][1:];asset=private/'ScreenTime/SupportingFiles/Assets.xcassets'/(dataset+'.dataset/coin.usdz');blob=final.read_bytes();assert blob==candidate.read_bytes()==asset.read_bytes(),key
 validation=json.loads((C/'validation.json').read_text());digest=hashlib.sha256(blob).hexdigest();assert digest==validation['sha256']
 records[key]={'name':item['name'],'candidate':C.name,'usdz':str(final),'blend':str(R/'source'/(key+'.blend')),'report':str(R/'REPORT.md'),'comparison':str(C/'comparison.jpg'),'turn':str(C/'full_turn.mp4'),'sha256':digest,'bytes':len(blob),'triangles':validation['triangles'],'preview_dataset':dataset,'preview_selection':item['selection']}
 x=(i%2)*536;y=(i//2)*560;im=Image.open(C/'app_front.png').convert('RGB').crop((343,297,863,817));previews.paste(im,(x+4,y+32));draw.text((x+12,y+10),item['name'],fill='white');comparisons.paste(Image.open(C/'comparison.jpg'),((i%2)*1064,(i//2)*568))
 rows.append('| '+item['name']+' | [Model]('+key+'/mobile/'+final.name+') | [Blender scene]('+key+'/source/'+key+'.blend) | [Report]('+key+'/REPORT.md) |')
previews.save(ROOT/'all_four_native.jpg',quality=95);comparisons.save(ROOT/'all_four_comparisons.jpg',quality=95)
manifest={'badges':records,'separate_preview_project':str(private/'ScreenTime.xcodeproj'),'bundle_id':'com.antonioperedo.badgestudio.preview','simulator':'Badge Studio Preview','simulator_id':'DF439C70-9FD7-4EF7-998E-43AF5F83A588','selection_survives_reopening':True,'production_app_changed':False,'all_final_files_match_private_preview':True};(ROOT/'deliverables.json').write_text(json.dumps(manifest,indent=2)+'\n')
before=(ROOT/'private_preview_before.swift').read_text();after=swift.read_text();patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift',tofile='b/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'));(ROOT/'private_preview_entries.patch').write_text(patch)
readme='''# Four finished badge crests

All four models are saved and reviewed in the separate **Badge Studio Preview** simulator. Open **Choose badge** on Home to select Frostwing Crystal, Battle Steel, Lunar Compass or Celestial Orbit. Celestial Orbit is selected, and its selection was verified after reopening without launch arguments. The production app was not changed.

[Native preview sheet](all_four_native.jpg) | [Reference comparisons](all_four_comparisons.jpg) | [Verified model manifest](deliverables.json)

| Badge | Final USDZ | Editable source | Evidence and notes |
| :--- | :--- | :--- | :--- |
'''+ '\n'.join(rows)+'''

## Appearance and checks

Built and inspected in the live Blender application with sculpted fronts, matching rears, closed walls and separate faceted crystal details. Native simulator review includes front, rear, both sides, 4x outline crops and a slow complete turn. The silver and bronze have physical reflections that move in the existing studio light. Measured appearance maps preserve the reference finish and fine surface details. The source images define the front appearance; this is a close 3D interpretation, not a claim of identical rendering at every angle.

All files pass closed surface, identity transform, Y up, unit scale, frame bounds, material UV and ARKit USD checks. The models sit at the shared floating height. Detailed contour and rear geometry use about 84,000 to 111,000 triangles and 8 to 10 MB each, above the usual mobile size guidance to retain the requested detail. Each report records the exact counts and evidence.

## Preview and rebuilding

The private project is `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. It has four independent menu entries and assets. `private_preview_entries.patch` records only these new menu and neutral placement entries. `install_preview_asset.py KEY` copies the selected candidate into that existing private project. Final model hashes match the installed private asset files.

The work uses `/tmp/crest_image_env/bin/python` for image and geometry preparation, live Blender through `water_match_20261014/blender_live.py`, and Blender's bundled Python for USD packaging. Sources are in each complete packed Blender scene. `design.json` preserves editable feature locations and depth choices. The full run helpers remain here for rebuilding; do not regenerate a design file after editing it by hand. A material recalibration requires a visibly loaded native badge, never a launch screen.

`record_turn.py` uses fine touch spacing and native simulator video so every angle is captured. The overnight run has no overall time limit. This run ended because all four badges were reviewed and complete; its recovery timer stopped. The saved schedule and checkpoints retain the work history.
''';(ROOT/'README.md').write_text(readme);print('Verified four final models, editable scenes, preview assets and delivery sheets')
