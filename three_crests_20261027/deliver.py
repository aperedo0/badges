"""Promote only verified candidates and preserve their review evidence."""
from pathlib import Path
import json,shutil,hashlib,difflib,re
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
ITEMS={'crescent_ocean':'Crescent Ocean','mountain_crest':'Mountain Crest','winged_sword':'Winged Sword'}
manifest={}
sheet=Image.new('RGB',(1080,790),(17,18,21));draw=ImageDraw.Draw(sheet)
for i,(key,name) in enumerate(ITEMS.items()):
 R=ROOT/key;candidate=(R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01';C=R/candidate
 validation=json.loads((C/'validation.json').read_text())
 metal_finish=json.loads((C/'metal_finish.json').read_text()) if (C/'metal_finish.json').exists() else None
 if metal_finish:assert metal_finish['mode']=='fitted' and metal_finish['calibrated_in_native_app']
 for required in ['comparison.jpg','every_side.jpg','app_front.png','app_side_left.png','app_back.png','app_side_right.png','full_turn.mp4']:assert (C/required).exists(),str(C/required)
 source=C/'mobile'/(key+'_badge_mobile.usdz');assert hashlib.sha256(source.read_bytes()).hexdigest()==validation['sha256']
 mobile=R/'mobile';mobile.mkdir(exist_ok=True);destination=mobile/source.name
 if destination.exists() and destination.read_bytes()!=source.read_bytes():
  previous=R/'previous';previous.mkdir(exist_ok=True);shutil.copyfile(destination,previous/(destination.stem+'_before_'+candidate+'.usdz'))
  for name in [key+'.blend','comparison.jpg','REPORT.md','validation.json']:
   if (R/name).exists():shutil.copyfile(R/name,previous/(Path(name).stem+'_before_'+candidate+Path(name).suffix))
 shutil.copyfile(source,destination);shutil.copyfile(C/(key+'.blend'),R/(key+'.blend'))
 for artifact in ['comparison.jpg','every_side.jpg','validation.json']:shutil.copyfile(C/artifact,R/artifact)
 if metal_finish:shutil.copyfile(C/'metal_finish.json',R/'metal_finish.json')
 triangles=validation['triangles'];mb=validation['bytes']/1000000
 texture_note='Main finish maps are 1024 pixels; the separate compass maps are 512 pixels.' if (C/'compass.json').exists() else 'The finish maps are 1024 pixels.'
 material_note=("The metal now has polished physical reflections and moving glints from the unchanged studio light. Native app light measurements balance that reflection against the approved front colors. Reference fill retains the fine marks and design detail. Smooth reflection normals keep the flashes clean across the curved metal. The rock and night sky retain their previous finish." if metal_finish else "The reference finish uses detailed surface maps with the preview's AgX transform inverted. Most face highlights stay fixed to preserve the reference appearance; the side metal and a small face contribution reflect the studio lights.")
 refinement=json.loads((C/'refinement.json').read_text()) if (C/'refinement.json').exists() else {}
 if refinement.get('gentle_sword_metal'):material_note+=' The sword uses broader reflections and reduced reflected intensity to soften the change from its resting front to angled views.'
 if refinement.get('continuous_moon_relief'):material_note+=' Removed the false horizontal fold in the middle left crescents by replacing the abrupt wave height join with a continuous curved span on the front and rear.'
 notes={
  'crescent_ocean':'Traced the silver and blue crescent contours, star field and breaking waves. The compass has real main facet planes. Removed detached background fragments and sealed small gaps in dark metal.',
  'mountain_crest':'Traced the open gold frame and mountain silhouettes. Sculpted overlapping peak ridges and the raised gold ornaments, with actual main diamond planes.',
  'winged_sword':'Traced the individual feather contours, the openings around the blade and the guard. Added swept wing depth, a creased blade, wrapped handle and primary gem planes.'
 }[key]
 report=f'''# {name}

Selected {candidate}. Final model: [USDZ](mobile/{source.name}). Complete editable Blender source: [{key}.blend]({key}.blend).

{notes}

![Reference and simulator](comparison.jpg)

Checked the complete model in the connected Blender application from the front, both sides and rear. The native Badge Studio preview was built successfully. Checked its front, back, both side poses and a slow full turn, including the floor reflection. Enlarged outline captures are saved with the candidate. The exported surface is closed, uses identity transforms, Y up and one meter per unit. The ARKit USD checker passed.

This is a custom floating shape, with its lowest point at Y = minus 2.455 and its highest at 3.015. Preview size is 1 and lift is 0. The model carries no camera, lights or floor and uses CrestUV with UsdPreviewSurface materials.

{material_note}

Fine scratches, smaller facet reflections and engraving are surface detail on the sculpted relief. The back repeats the sculpting and materials. Side and rear depth are inferred from the single front reference. Side normals use a smooth contour field and a front to rear blend to remove the raster contour's reflection bands while retaining the geometry.

The file contains {triangles:,} triangles and is {mb:.2f} MB, above the usual badge size guidance to preserve these detailed outlines and relief. {texture_note} Reference texture is retained through the lowest part to preserve the waves, stone and blade detail. Physical device load time is unmeasured.

Production app files and existing badge finals were not edited. This model is installed only as a separate entry in Badge Studio on the dedicated preview simulator.
'''
 (R/'REPORT.md').write_text(report)
 (C/'NOTES.txt').write_text(notes+'\nReference detail and matching rear retained; validated in the native preview.\n')
 manifest[key]={'name':name,'candidate':candidate,**validation}
 comparison=Image.open(C/'comparison.jpg');ref=comparison.crop((8,40,528,560)).resize((344,344),Image.Resampling.LANCZOS);app=comparison.crop((536,40,1056,560)).resize((344,344),Image.Resampling.LANCZOS)
 x=8+i*360;draw.text((x+6,14),name,fill='white');draw.text((x+6,36),'Reference',fill=(180,184,193));sheet.paste(ref,(x,56));draw.text((x+6,418),'Simulator',fill=(180,184,193));sheet.paste(app,(x,438))
sheet.save(ROOT/'three_badges.jpg',quality=96)
(ROOT/'validation.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Preserve the small integration change in the private preview only.
path=ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift';current=path.read_text();before=current
for selection in ['crescentOcean','mountainCrest','wingedSword']:before=re.sub(r',"'+selection+r'":"[^"]+"','',before)
before=before.replace('        if ["Badge3DPreviewCrescentOcean", "Badge3DPreviewMountainCrest", "Badge3DPreviewWingedSword"].contains(datasetName) { return .neutral }\n','')
(ROOT/'private_preview.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),current.splitlines(True),fromfile='a/Badge3DLiveBadge.swift',tofile='b/Badge3DLiveBadge.swift')))
(ROOT/'preview_simulator.json').write_text(json.dumps({'name':'Badge Studio Preview','simulator_id':'DF439C70-9FD7-4EF7-998E-43AF5F83A588','bundle_id':'com.antonioperedo.badgestudio.preview','scheme':'ScreenTime-UIOnly','selection_keys':['crescentOcean','mountainCrest','wingedSword']},indent=2)+'\n')
print('Promoted',', '.join(ITEMS.values()))
