from pathlib import Path
import json, shutil, hashlib
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'candidates/05';review=out/'review'
old=Path('/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/all_sides_20261010/candidates/04')
poses=['front','right','back','left']
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
sheet=Image.new('RGB',(2424,1270),'#101419');draw=ImageDraw.Draw(sheet)
for row in range(2):
    for col,pose in enumerate(poses):
        if pose=='front':path=(old if row==0 else out)/'front.png'
        elif row==0:path=Path('/Users/antonioperedo/Desktop/badges/all_sides_20261010/inspection_models/updated/diamond')/pose/'app.png'
        else:path=ROOT/'inspection/05'/pose/'front.png'
        im=Image.open(path).crop((300,250,906,850))
        sheet.paste(im,(col*606,70+row*600))
        draw.text((col*606+12,76+row*600),('PREVIOUS ROUND' if row==0 else 'UPDATED')+' '+pose.upper(),fill='white',font=font)
    
draw.text((20,18),'Diamond: equal-size views under the app lighting',fill='white',font=font)
sheet.save(review/'fullsize_comparison.png')
shutil.copyfile(review/'fullsize_comparison.png',ROOT/'comparison.png')
options=Image.new('RGB',(1212,630),'#101419');od=ImageDraw.Draw(options)
for col,num in enumerate(['04','05']):
    im=Image.open(ROOT/'candidates'/num/'front.png').crop((300,250,906,850))
    options.paste(im,(col*606,30))
    od.text((col*606+12,4),'04: DIELECTRIC' if num=='04' else '05: STRONGER REFLECTIONS (SELECTED)',fill='white',font=font)
options.save(ROOT/'material_options.png')
for folder in ['mobile','previous']:(ROOT/folder).mkdir(exist_ok=True)
shutil.copyfile(out/'diamond_badge_mobile.usdz',ROOT/'mobile/diamond_badge_mobile.usdz')
shutil.copyfile(ROOT/'source/proposed.usdz',ROOT/'previous/diamond_badge_mobile.usdz')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=json.loads((out/'package_audit.json').read_text())
review_record={'front_both_sides_back_checked_at_4x':True,'continuous_scroll_video_checked':True,'video_samples':202,'samples_per_second':12,'isolated_outline_specks_or_broken_bright_outline_lines_seen':False,'intentional_interior_live_glints_retained':True,'notes':'Actual side/back scroll poses plus equal-size in-app inspection copies. Four enlarged outline views inspected; all 17 continuous-turn contact sheets reviewed, with enlarged intermediate glint view. Shadow/contact line remains app-owned.'}
(out/'visual_review.json').write_text(json.dumps(review_record,indent=2)+'\n')
delivery={'candidate':'05','sha256':sha(ROOT/'mobile/diamond_badge_mobile.usdz'),'previous_round_sha256':sha(ROOT/'previous/diamond_badge_mobile.usdz'),'simulator':'iPhone 17','simulator_udid':'69A29DD2-C91E-487A-81B9-3B146DF8F07B','scheme':'ScreenTime-UIOnly','bundle_id':'com.antonioperedo.screentime.uidev','project':'/Users/antonioperedo/Desktop/screen_time/ScreenTime.xcodeproj','preview_state':'Final unrotated model installed, shader-warmed, Diamond Home open; temporary full-size inspection models replaced.'}
(ROOT/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
(out/'NOTES.md').write_text('Kept the last full round gem geometry and moved its optical detail into calibrated, light-responsive body color.\nStrengthened real-time facet reflections; fixed emissive glints removed, with only low uniform blue emission for shadow readability.\n')
report='''The revised Diamond keeps the last full round gem's geometry and blue crystal detail. Its optical picture no longer supplies the lighting through an emissive texture: the detail is now calibrated body color, lit by the app, with stronger live facet reflections and a small uniform blue emission for shadow readability. Candidate 05 is left installed and open on Diamond Home in the iPhone 17 simulator (ScreenTime-UIOnly).

[Equal-size front, right, back and left comparison](comparison.png). [Actual Home scroll poses](candidates/05/review/scroll_comparison.png). [Full-turn app video](candidates/05/full_turn.mp4). [Material options](material_options.png): I chose 05 over 04 for its stronger moving reflections while keeping the blue front close to the previous version.

The original round model is preserved in `previous/`; the new model is `mobile/diamond_badge_mobile.usdz`. No approved source model was overwritten. The final package is 246,496 bytes, 122 vertices and 240 triangles. Independent unpacking confirms the geometry, normals and UVs are identical to the previous round model, textures resolve, the mesh is closed, no transforms or lights are included, and ARKit compliance passes. Maximum spin width is 6.24 units; the bottom remains at -2.455.

Testing used the actual app stage, three launches to warm shaders, four Home poses and a continuous turn. Front, both sides and back were inspected at 4× using full-size app testing copies; the full-turn contact sheets were reviewed, including an enlarged moving glint. No isolated outline specks or broken bright outline lines were seen. Intentional interior crystal glints remain, following the owner's request to retain sparkle rather than the general no-sparkle preference in section 3.

The optical pattern still uses body-color detail; this is a real-time approximation of crystal, not traced refraction through transparent diamond. Some softness remains as the rotating badge shrinks and moves toward the top of Home. Equal-size side and back views are sharp, so that softness is not intrinsic to those model faces; its exact app-level cause has not been isolated. The app's contact-shadow line also remains.

The app repo's original Diamond asset was restored byte for byte after each temporary build. The preview stays in the installed simulator app. Final repo verification is recorded in `repo_verified.json`. No app code, branches or commits were changed, and no extra folders were placed in Downloads.
'''
(ROOT/'REPORT.md').write_text(report)
print(json.dumps(delivery))
