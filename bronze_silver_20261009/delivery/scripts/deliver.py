"""Prepare a new reviewable delivery; copy to a fresh Downloads folder on request."""
from pathlib import Path
import sys,json,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cp(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
if '--downloads' in sys.argv:
    src=ROOT/'delivery';parent=Path('/Users/antonioperedo/Downloads')
    name='BestSpent_Bronze_Silver_2026-10-09';dst=parent/name;i=2
    while dst.exists():dst=parent/f'{name}_{i}';i+=1
    shutil.copytree(src,dst)
    for file in src.rglob('*'):
        if file.is_file():assert sha(file)==sha(dst/file.relative_to(src))
    (ROOT/'downloads_delivery.json').write_text(json.dumps({'path':str(dst),'all_files_verified_byte_for_byte':True},indent=2)+'\n')
    print(dst);sys.exit()
selection={'bronze':sys.argv[1],'silver':sys.argv[2]}
bundle=ROOT/'delivery';assert not bundle.exists(),'Existing delivery is preserved.';bundle.mkdir()
selected={};reports=[]
proof_files=['app.png','home_crop.png','reference_vs_app.png','surface_zoom.png','floor_gap.png','40pt_proof.png','app_color_comparison.json','app_restore_verification.json','independent_validation.json','build.json']
for kind,number in selection.items():
    base=ROOT/kind;candidate=base/'candidates'/number;build=json.loads((candidate/'build.json').read_text());selected[kind]={'candidate':number,'sha256':sha(candidate/'badge.usdz'),'bytes':build['bytes'],'triangles':build['triangles']}
    stem='bronze_sun_mobile' if kind=='bronze' else 'silver_chevrons_mobile'
    cp(candidate/'badge.usdz',base/'mobile'/f'{stem}.usdz')
    cp(candidate/'badge.usdc',base/'master'/f'{stem}.usdc')
    cp(candidate/f'{kind}_badge_master.blend',base/'master'/f'{kind}_badge_master.blend')
    for image in (candidate/'textures').glob('*.png'):cp(image,base/'master/textures'/image.name)
    cp(candidate/f'BadgeArt_{kind}.png',base/'stills'/f'BadgeArt_{kind}.png')
    for f in proof_files:cp(candidate/f,base/'proof'/f)
    slot='Copper (Bronze has no model data set yet)' if kind=='bronze' else 'Silver'
    description=('Eight alternating long/short bronze rays, a closed domed center, two rounded rim lips and a dark channel. Ray crests stay behind the rim.' if kind=='bronze' else 'Two separate downward silver chevrons with closed backs, real broad bevels, flat core faces and directional brushing.')
    choice=('Candidate 03 selected after the measured correction brought the rays back to the reference bronze palette and reduced the upper-ray mismatch.' if kind=='bronze' else 'Candidate 02 selected: the second measured solve refined highlight and bevel contrast without changing the geometry.')
    exceptions=('Kept subdued worked-metal color markings from the reference, setting aside the general preference against fine mottling. The pointed ray tips also intentionally taper below the general 0.6-unit small-part guideline.' if kind=='bronze' else 'Kept fine directional brush marks to match the reference, setting aside the suggested minimum texture-mark width. The 440 triangles are intentional: the silhouette and broad facets are flat and need no dense tessellation.')
    lo,hi=build['bounds'];size=[b-a for a,b in zip(lo,hi)]
    text=f'''# {kind.title()} reference badge — 2026-10-09

{description} {choice}

![Reference and actual Home render](proof/reference_vs_app.png)

The actual RealityKit model was built and installed with the `ScreenTime-UIOnly` scheme on iPhone 17 Simulator. Preview slot: **{slot}**. The full screenshot is [proof/app.png](proof/app.png); the shape's lighting and matching floor reflection show that the 3D model loaded. The screenshot is unretouched; comparison panels only crop, resize the reference, and add labels. The Bronze full screenshot consequently says “Copper.”

One Y-up, meter-scale USDZ with front +Z and no transforms, lights, camera, floor or reflection objects. All meshes are closed and use PreviewSurface materials, matching face-varying BadgeUV coordinates and explicit normals. Independent ARKit compliance, packaged texture hashes, fresh Blender import, and packed master checks passed.

| Property | Final |
| --- | --- |
| Candidate | {number} |
| Triangles | {build['triangles']:,} |
| USDZ size | {build['bytes']/1_000_000:.2f} MB |
| Width / height / thickness | {size[0]:.3f} / {size[1]:.3f} / {size[2]:.3f} units |
| Lowest / highest Y | {lo[1]:.3f} / {hi[1]:.3f} |
| Floor gap | 0.440 units |
| Textures | Two 1024 × 1024 maps |

Fine color texture fades out toward the lowest fifth; backs and downward edge surfaces use plain materials. No normal maps. Colors and supplemental emission were solved against measured app lighting with the unchanged AgX function. Broad highlight placement is reference matched and partly fixed in the maps; physical lighting still changes during the turn. The small texture details soften at Home size, and the fixed coin contact-shadow line remains under the floating shape.

{exceptions}

The two temporarily used app data sets were restored byte for byte after every build. All 641 tracked app files, the original branch, commit and Git status were verified unchanged. No app code or approved final was edited. Bronze still needs its own model data set and table entry for permanent integration; that work belongs to the app owner. The transparent still is supplied as an additional asset, not installed into the app.

Final model: [mobile/{stem}.usdz](mobile/{stem}.usdz). Editable source: [master/{kind}_badge_master.blend](master/{kind}_badge_master.blend). Final SHA-256: `{selected[kind]['sha256']}`.
'''
    (base/'REPORT.md').write_text(text);reports.append(text)
    for folder in ['mobile','master','proof','stills']:shutil.copytree(base/folder,bundle/kind/folder)
    cp(base/'REPORT.md',bundle/kind/'REPORT.md')
    for f in (base/'source').glob('*'):
        if f.is_file():cp(f,bundle/kind/'source'/f.name)
    # Keep lightweight reproducible trial artifacts, without large diagnostic atlases.
    for trial in sorted((base/'candidates').iterdir()):
        for f in ['badge.usdz','badge.usdc','app.png','home_crop.png','reference_vs_app.png','NOTES.md','build.json','solve.json','settings.json','build.log','independent_validation.json','app_restore_verification.json']:
            if (trial/f).exists():cp(trial/f,bundle/kind/'candidates'/trial.name/f)
        for f in (trial/'textures').glob('*.png'):cp(f,bundle/kind/'candidates'/trial.name/'textures'/f.name)
    for f in ['badge.usdz','badge.usdc','settings.json','app.png','build.json']:
        cp(base/'source/calibration'/f,bundle/kind/'source/calibration'/f)
for script in (ROOT/'scripts').glob('*.py'):cp(script,bundle/'scripts'/script.name)
cp(ROOT/'source/app_repo_before.json',bundle/'source/app_repo_before.json')
cp(ROOT/'proof/app_restore_verification.json',bundle/'source/app_restore_verification.json')
(ROOT/'selection.json').write_text(json.dumps(selected,indent=2)+'\n');cp(ROOT/'selection.json',bundle/'selection.json')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
panel=Image.new('RGB',(1200,700),'#08090b');draw=ImageDraw.Draw(panel)
for i,kind in enumerate(['bronze','silver']):
    panel.paste(Image.open(ROOT/kind/'proof/home_crop.png'),(i*600,50));draw.text((i*600+25,14),kind.title()+' — actual Home render',font=font,fill='white')
panel.save(bundle/'Bronze_and_Silver_in_app.png')
compare=Image.new('RGB',(1200,1400),'#08090b')
for i,kind in enumerate(['bronze','silver']):compare.paste(Image.open(ROOT/kind/'proof/reference_vs_app.png'),(0,i*700))
compare.save(bundle/'Reference_vs_app.png')
root_report='''# Bronze and Silver badges

Created from your two reference images and checked inside the app. Open **Bronze_and_Silver_in_app.png** for the Home renders or **Reference_vs_app.png** for the matched-size comparisons. Full unretouched app screenshots are in each badge's `proof/app.png`.

- Bronze: `bronze/mobile/bronze_sun_mobile.usdz`
- Silver: `silver/mobile/silver_chevrons_mobile.usdz`
- Editable Blender files and standalone USD sources with textures are in each `master/` folder.
- Transparent fixed-Home-frame PNGs are in each `stills/` folder.

Bronze was previewed temporarily through Copper because Bronze has no 3D data set yet, so its full app screenshot says Copper. Silver used the Silver slot. All original app assets and all 641 tracked files were verified unchanged after testing. The simulator retains the preview installation.

The per-badge reports cover geometry, file checks, reference-driven exceptions and remaining visual limits. Numbered candidate folders retain the actual screenshots and comparisons. These are new assets; the approved original Silver and Copper models were preserved.

The scripts and mesh data support further editing. `geometry.py` generates source meshes; `solve.py <kind> candidates/<number> [candidates/<previous>]` uses native app measurements to solve materials; Blender runs `export.py -- <kind> candidates/<number>`. `agx.py` is copied unchanged from Silver 2. Bronze's initial calibration used higher ray crests; subsequent material solves remeasured the effective light after lowering those crests behind the rim. Large diagnostic atlas NPZ files are omitted from this delivery and can be regenerated by the solver. App test scripts must always be followed by restoration and verification; they write only the two existing temporary asset files.
'''
(bundle/'REPORT.md').write_text(root_report)
manifest={str(f.relative_to(bundle)):sha(f) for f in sorted(bundle.rglob('*')) if f.is_file()}
(bundle/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared',bundle,'files',len(manifest),'model selection',selected)
