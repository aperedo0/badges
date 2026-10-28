"""Promote the phoenix after native front and full rotation review."""
from pathlib import Path
import json,shutil,hashlib,difflib
ROOT=Path(__file__).resolve().parent;R=ROOT/'phoenix';C=R/(R/'candidate.txt').read_text().strip()
finish=json.loads((C/'metal_finish.json').read_text());assert finish['mode']=='fitted' and finish['calibrated_in_native_app']
validation=json.loads((C/'validation.json').read_text());source=C/'mobile/phoenix_badge_mobile.usdz'
assert hashlib.sha256(source.read_bytes()).hexdigest()==validation['sha256']
for name in ['app_front.png','app_side_left.png','app_back.png','app_side_right.png','comparison.jpg','every_side.jpg','full_turn.mp4','spin_64.png','spin_80.png']:assert (C/name).exists(),name
dest=R/'mobile';dest.mkdir(exist_ok=True);model=dest/source.name
if model.exists() and model.read_bytes()!=source.read_bytes():
 old=R/'previous';old.mkdir(exist_ok=True);shutil.copyfile(model,old/(model.stem+'_before_'+C.name+'.usdz'))
 for name in ['phoenix.blend','REPORT.md','comparison.jpg','validation.json']:
  if (R/name).exists():shutil.copyfile(R/name,old/(Path(name).stem+'_before_'+C.name+Path(name).suffix))
shutil.copyfile(source,model)
for name in ['phoenix.blend','comparison.jpg','every_side.jpg','turning_views.jpg','validation.json','metal_finish.json']:shutil.copyfile(C/name,R/name)
shutil.copyfile(C/'app_front.png',ROOT/'studio_open.png')
P=ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift'
before=(ROOT/'private_preview_before.swift').read_text();after=P.read_text()
(ROOT/'private_preview.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/Badge3DLiveBadge.swift',tofile='b/Badge3DLiveBadge.swift')))
(ROOT/'preview_simulator.json').write_text(json.dumps({'name':'Badge Studio Preview','simulator_id':'DF439C70-9FD7-4EF7-998E-43AF5F83A588','bundle_id':'com.antonioperedo.badgestudio.preview','scheme':'ScreenTime-UIOnly','selection_key':'bronzePhoenix','selected_badge':'Bronze Phoenix','production_app_changed':False},indent=2)+'\n')
report=f'''# Bronze Phoenix

Selected {C.name}. [Final USDZ](mobile/phoenix_badge_mobile.usdz) and [complete editable Blender scene](phoenix.blend).

Traced the owner's bronze phoenix, swept feather silhouette, circular bronze frame, recessed cracked center, head and tail. Built raised feather vanes and a matching sculpted rear. All three amber diamonds have closed geometry and four real primary planes on each face. Their bezels meet smooth recesses without a stepped height cut.

![Reference and simulator at matching scale](comparison.jpg)

The bronze and amber facets have real moving studio reflections. The bronze uses a gentler polished finish with broad highlights, informed by the owner's sword feedback. Native light measurements balance those reflections against the reference colors. Reference fill preserves the small metal marks, stone cracks, amber glow and fine face detail. Some reference highlights therefore remain fixed. The model is a sculpted relief; the single front picture does not define a fully independent rear design or unseen depth.

Checked the complete model in the connected Blender application from front, both sides and back. Checked the native simulator at rest, early rotation, back and both sides, plus a slow full turn. Enlarged outline captures and the full turn recording are saved in {C.name}. The USDZ is closed, uses UsdPreviewSurface and CrestUV, Y up, one meter per unit, identity transforms, with no lights, cameras, floor or coin material names. The ARKit USD checker passed.

This is a custom floating medallion rather than the standard coin shell: the wings and tail extend beyond its circular frame in the reference. Its lowest point is Y minus 2.455, highest 3.015, width 5.606, preview size 1 and lift 0. Its back and thickness are centered on the spin axis.

The model has {validation['triangles']:,} triangles and is {validation['bytes']/1000000:.2f} MB. This exceeds the usual size guidance to keep the detailed feather outlines, depth and matching rear. Main maps are 1024 pixels and gem maps are 512. The reference's deliberate fractured metal texture, bright outer highlights and lower feather detail are retained instead of removing those details to meet general finish guidance. Physical device loading time is unmeasured.

Only a separate entry in the existing private Badge Studio preview was added. The production app and existing badge models were not edited. Open Choose badge and select Bronze Phoenix.
'''
(R/'REPORT.md').write_text(report)
(C/'NOTES.txt').write_text('Matched bronze phoenix silhouette, recessed cracked center, raised feathers and three planar amber gems.\nGentle moving bronze reflections balanced against measured native studio light; matching rear and closed sides checked.\n')
print('Promoted Bronze Phoenix',validation['sha256'])
