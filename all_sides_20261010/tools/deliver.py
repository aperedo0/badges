from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'manifest.json').read_text())
selection=json.loads((ROOT/'selection.json').read_text())
assert 'gold' in selection
details={
 'iron':('Recessed iron shield back with a continuous rolled rim, crossed braces and a raised grip.','The installed front geometry, normals, UVs and materials are unchanged; the app front crop is pixel identical.','59,392 triangles preserve the existing detailed front while adding a smooth back; this exceeds the triangle guideline. Small rivets are present but subtle at Home size.'),
 'bronze':('Rear dome, rays, channel and rolled lips now match the front relief and texture.','The original front geometry, normals, UVs and materials are unchanged. Grazing edge pixels can differ because the rear relief is now present.','46,176 triangles slightly exceed the guideline to preserve the installed front tessellation and matching rear lips.'),
 'steel':('Both chevrons have matching rear relief and brushing; lower-chevron fine detail is restored.','Upper-chevron texture and geometry are unchanged. Lower broad shading and the protected outline band are retained.','The blur came from the model texture pipeline, not the app. The original solve blends a 0.8-pixel detail field into a 6-pixel smoothed field between 19% and 44% of total height, weakening the lower chevron. Matching upper-chevron fine detail was restored in the lower interior in both color and emission maps. The bottom texture-fade guidance was set aside for fine brushing so the twins remain equally sharp.'),
 'silver':('Rear star, laurel leaves and stems match the front shape, relief and metal look.','Original front geometry, normals, UVs and material bindings are unchanged, including the solved star material. Grazing edge pixels can differ with the added rear relief.','The reference-matched front metal solution is retained; rear star UVs follow the corresponding mirrored facets.'),
 'gold':('A true circular crown band with a continuous curved crown wall, eight round finials and the reference five-point front silhouette.','The installed gold texture and original peak design are retained, with the front shell projected along the original camera rays onto the round wall. The band and wall geometry changed; the front is judged against the original app picture. The lowest wall row is seated in the band with reference shading normals retained, and the band texture is continuous through both side joins.','The circular band is tilted 17.179 degrees about X, baked into the vertices. Its radius after the 0.995 uniform fit is 2.6318 units. This physical tilt turns with the badge, exposing the inside from a different angle at the back. A constant tilt toward the viewer would need Claude to tilt the app spin axis, as described in AGENTS.md section 7. The rear intermediate finials are slightly shorter so their caps remain hidden behind the front valleys at rest. The circular band reaches Y = -2.7878 at its far edge, below the shared floating-height guideline but above the hard floor; the reference projection takes precedence over that guideline. 74,272 triangles preserve the source finials and smooth rolled details around the entire crown, exceeding the triangle guideline while remaining below 5 MB.'),
 'platinum':('The knot now carries matching polished metal across the front, back and walls.','The original geometry and broad front texture are retained. Only narrow perimeter bevel and wall shading changed to prevent flashing edges.','The rear polish is transferred from the native app front along the continuous ribbon, with front-hidden sections completed from neighboring visible sections. Rear albedo and emission are solved against measured rear app lighting. Dense sampling across the wide ribbon retains the front brushing that a vertex-only transfer softened. Broad side walls keep an inset source color texture with roughness 0.88 and no emission; thin lips use a continuous dark metal finish to prevent bright broken outlines. The original continuous knot geometry remains intact, so its crossings are naturally viewed from the opposite side at the back.'),
 'diamond':('Closed, full-volume round brilliant with a table, crown, girdle, pavilion and culet; blue crystal optics wrap around every quadrant.','The flat original geometry was replaced. The installed blue optical field is reprojected onto the real facets, retaining its crystal identity and sparkle.','Angular/height UV mapping avoids collapsed side projections. Optical-field quadrant transitions coincide with physical facet boundaries. Broad crystalline white highlights are intentional; isolated outline specks are not. Only 240 triangles are needed for the deliberately planar gem facets.')
}
photos=ROOT/'pictures';photos.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',28)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
overview=Image.new('RGB',(3*606+150,len(selection)*660+95),'#101419');draw=ImageDraw.Draw(overview)
for i,label in enumerate(['CURRENT FRONT','UPDATED FRONT','UPDATED BACK']):draw.text((150+i*606+20,24),label,font=font,fill='white')
rows=[]
for j,(tier,number) in enumerate(selection.items()):
 w=Path(manifest[tier]['work']);out=w/'candidates'/number
 for pose in ['front','right','back','left']:assert (out/(pose+'.png')).exists()
 assert (out/'full_turn.mp4').exists()
 build=json.loads((out/'build.json').read_text());package=out/(tier+'_badge_mobile.usdz')
 assert hashlib.sha256(package.read_bytes()).hexdigest()==build['sha256']
 mobile=w/'mobile';previous=w/'previous';mobile.mkdir(exist_ok=True);previous.mkdir(exist_ok=True)
 source=w/'source/installed.usdz';backup=previous/'installed.usdz'
 if backup.exists():assert backup.read_bytes()==source.read_bytes()
 else:shutil.copyfile(source,backup)
 final=mobile/package.name;shutil.copyfile(package,final)
 comparison=out/'review/fullsize_comparison.png';assert comparison.exists()
 picture=photos/('BestSpent_'+tier.title()+'_All_Sides_20261010.png');shutil.copyfile(comparison,picture)
 change,preservation,extra=details[tier]
 (out/'NOTES.md').write_text(change+'\n'+preservation+'\n')
 report=f'''{tier.title()} candidate {number}, 2026-10-10

{change}

{preservation}

{extra}

App comparison: [front, right, back and left](candidates/{number}/review/fullsize_comparison.png). Top row is installed/current; bottom row is updated. The side and back screenshots use independent rotated inspection copies held at full size under unchanged app lighting. The delivered model has no transforms and faces +Z. [Actual Home scroll poses](candidates/{number}/review/scroll_comparison.png) and [slow full turn](candidates/{number}/full_turn.mp4) are separate.

Four full-size poses inspected at 4x, with dense intermediate turn samples retained at 4x. No isolated white outline dots or broken bright edge segments were observed in the reviewed app views. Existing front surface grain is retained where the owner requested an unchanged front, taking precedence over the smooth-surface guidance.

Package: {build['triangles']:,} triangles; {build['bytes']/1_000_000:.2f} MB; ARKit compliance checks passed. Frame, spin-axis bounds and material UV readers checked against the app contract. The package and all texture dependencies were independently unpacked and verified.

Final model: [mobile/{package.name}](mobile/{package.name}). Original installed model: [previous/installed.usdz](previous/installed.usdz). Approved parent-folder finals were not modified. The app repo was restored byte for byte after temporary tests; no app code, branch or commit changed.
'''
 assert '\u2014' not in report
 (w/'REPORT.md').write_text(report)
 draw.text((12,j*660+120),tier.title(),font=small,fill='#cbd5e4')
 paths=[w/'current/front.png',out/'front.png',ROOT/'inspection_models/updated'/tier/'back/app.png']
 for i,path in enumerate(paths):overview.paste(Image.open(path).crop((300,220,906,880)),(150+i*606,j*660+95))
 rows.append(f'| {tier.title()} | [model]({final}) | [pictures]({picture}) | {build["triangles"]:,} | {build["bytes"]/1_000_000:.2f} MB |')
overview.save(photos/'BestSpent_Badges_Overview_20261010.png')
report='''Seven badge revisions, 2026-10-10

Iron, Bronze, Steel, Silver, Gold, Platinum and Diamond were revised and tested in the app. Gold has a true circular tilted band and retains the original five-point front style; Platinum has a calibrated rear polish matching the front.

Only PNG pictures are delivered to Downloads. Models, source copies, app screenshots, inspection crops and recordings remain in the Desktop badge workspace.

| Badge | USDZ | App comparison | Triangles | Size |
| --- | --- | --- | ---: | ---: |
'''+ '\n'.join(rows)+'''

Steel blur: the original texture solve fades fine brushing toward the bottom, blending sigma 0.8 detail with sigma 6 smoothing between 19% and 44% of total badge height. The lower interior now receives matching upper-chevron detail, while broad lighting, the upper texture and a protected nine-texel outline band stay unchanged. See the Steel report and sharpness.json.

Validation: real app front/right/back/left screenshots, full-size rotated inspection copies, 4x edge pages, slow Home turns with one-pixel gesture steps, and 12-samples-per-second intermediate frames retained at 4x. The four-pose comparison labels distinguish held inspection poses from the actual shrinking scroll turn. No app lights or code were edited. No isolated white outline specks or broken bright outline segments were observed in the reviewed views; the Diamond's broad crystal highlights are intentional.

All seven packages are below 5 MB. Gold and Iron exceed the triangle guideline to retain the source detail while completing their geometry around the back; Bronze slightly exceeds it to retain the source tessellation and matching lips. Original front grain was kept where requested. The app's existing contact-shadow line under floating shapes remains an app-side limitation.

The independently unpacked package checks, front-data comparison and complete rotation bounds are in package_verification.json, front_data_audit.json and contract_audit.json. The actual packaged Gold band circles and 17.179-degree tilt are verified in gold_circle_audit.json. The original app branch, HEAD, status and 661 source files were verified unchanged in app_repo_verified.json. Mobile folders here are revision copies; approved finals and installed repo assets remain untouched.
'''
assert '\u2014' not in report
(ROOT/'REPORT.md').write_text(report)
print('Prepared seven revision models, seven app comparisons and one overview.')
