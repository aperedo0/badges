"""Create a new, verified delivery and optionally copy it to Downloads."""
from pathlib import Path
import sys,json,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cp(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
if '--downloads' in sys.argv:
    src=ROOT/'delivery';name='BestSpent_Gold_Diamond_2026-10-09';dst=Path('/Users/antonioperedo/Downloads')/name;i=2
    while dst.exists():dst=dst.parent/f'{name}_{i}';i+=1
    shutil.copytree(src,dst)
    for f in src.rglob('*'):
        if f.is_file():assert sha(f)==sha(dst/f.relative_to(src))
    (ROOT/'downloads_delivery.json').write_text(json.dumps({'path':str(dst),'all_files_verified_byte_for_byte':True},indent=2)+'\n');print(dst);sys.exit()
selection={'gold':sys.argv[1],'diamond':sys.argv[2]};bundle=ROOT/'delivery';assert not bundle.exists();bundle.mkdir();selected={}
proof_files=['app.png','home_crop.png','reference_vs_app.png','surface_zoom.png','floor_gap.png','40pt_proof.png','app_color_comparison.json','app_restore_verification.json','independent_validation.json','build.json']
for kind,n in selection.items():
    base=ROOT/kind;trial=base/'candidates'/n;build=json.loads((trial/'build.json').read_text());selected[kind]={'candidate':n,'sha256':sha(trial/'badge.usdz'),'bytes':build['bytes'],'triangles':build['triangles']}
    assert selected[kind]['sha256']==build['sha256']
    assert json.loads((trial/'independent_validation.json').read_text())['arkit_compliance']=='PASS'
    assert json.loads((trial/'app_restore_verification.json').read_text())['restored_byte_for_byte']
    stem='gold_crown_mobile' if kind=='gold' else 'diamond_crystal_mobile'
    cp(trial/'badge.usdz',base/'mobile'/f'{stem}.usdz');cp(trial/'badge.usdc',base/'master'/f'{stem}.usdc');cp(trial/f'{kind}_badge_master.blend',base/'master'/f'{kind}_badge_master.blend')
    for f in (trial/'textures').glob('*.png'):cp(f,base/'master/textures'/f.name)
    cp(trial/f'BadgeArt_{kind}.png',base/'stills'/f'BadgeArt_{kind}.png')
    for f in proof_files:cp(trial/f,base/'proof'/f)
    lo,hi=build['bounds'];size=[b-a for a,b in zip(lo,hi)]
    description=('Five rounded finials above a curved scalloped front shell, broad rolled valley borders, fine lips and a closed annular band with a real open center. The rear band is lower to preserve the reference view into the cavity.' if kind=='gold' else 'A closed blue crystal with individually flat geometric cuts. Each of the 73 front faces has its own padded texture area, preserving independent material correction at the boundaries. The main outline and visible facet junctions follow the reference.')
    limits=('The five pointed stems occupy the front half of the hollow band, and the reverse uses plain gold materials. The small outer finials and narrow lips deliberately remain smaller than the general 0.6-unit guideline to match the reference. The lower band retains smooth broad gold reflection bands; it carries no fine grain. Bright yellow highlights are paler than the reference under the fixed studio light and AgX transform; this is visible in the comparison.' if kind=='gold' else 'The PreviewSurface crystal is opaque. Its apparent refraction, blue optical bands and spectral highlights come from reference-matched color and emission, rather than transmission through an optically simulated gemstone. The selected front surface uses the solved optical color predominantly as emission, with only 1% of its calibrated reflected component: this removes the colored dots visible in candidates 02 and 03. The front optical pattern stays attached to the faces during a turn; the blue back and edge surfaces respond to the real environment. Facet normals and shape are real geometry. Thin luminous facet lines and the bright lower tip are intentional reference-driven exceptions to the general preferences against inner glints and bright reflection detail. The 172 triangles are sufficient for flat cuts; extra tessellation would not improve them. Candidate 04 follows three material attempts because the final app measurement isolated reflected-light artifacts; this controlled material change replaces that unreliable component rather than guessing another metal color.')
    material_report=('The opening was narrowed after the first app check. The lower wall curve was then made independent of the peak heights and given smooth analytical normals, eliminating the pinched fold visible in the earlier app renders. The new wall was measured again in the app. Broad highlight placement is partly fixed in the maps; physical lighting still responds during the entrance turn.' if kind=='gold' else 'Facets were given separate texture areas after the first app check exposed thin dark lines from shared texture sampling. The final optical-surface pass then removed colored reflection artifacts from the dark facets. [proof/material_options.png](proof/material_options.png) compares the reference, candidate 03 with stronger studio response and selected candidate 04 with smoother optical color.')
    slot='Copper' if kind=='gold' else 'Silver'
    report=f'''# {kind.title()} badge, 2026-10-09

{description} Selected candidate {n}; its changes are recorded in [candidates/{n}/NOTES.md](candidates/{n}/NOTES.md).

![Reference beside the actual Home render](proof/reference_vs_app.png)

The actual model was built, installed and viewed on the iPhone 17 Simulator using `ScreenTime-UIOnly`. The full native screenshot is [proof/app.png](proof/app.png). Because {kind.title()} has no 3D app data set yet, the temporary preview used the **{slot}** slot and the full screenshot retains that tier label. Beveled surfaces, facet lighting, and the matching floor reflection confirm the 3D model is showing. Screenshot pixels are unretouched; panels only crop screenshots, resize the reference and add labels.

ScreenTime-UIOnly: ** BUILD SUCCEEDED **. This was an asset preview, with no app source changes or code tests.

| Property | Final |
| --- | --- |
| Triangles | {build['triangles']:,} |
| USDZ size | {build['bytes']/1_000_000:.2f} MB |
| Width / height / thickness | {size[0]:.3f} / {size[1]:.3f} / {size[2]:.3f} units |
| Lowest / highest Y | {lo[1]:.3f} / {hi[1]:.3f} |
| Floor gap | 0.440 units |
| Textures | Two 1024 by 1024 PNG maps |

Independent ARKit compliance, closed-mesh checks, explicit normals, face-varying BadgeUV coordinates, package texture hashes, fresh Blender import and packed editable-master checks passed. The one USDZ is Y up, meters per unit 1, front +Z, centered on the spin axis, and has no transforms, reserved coin names, lights, cameras, floor or reflection objects.

Materials were solved from measured app lighting using the unchanged Silver 2 AgX function. {material_report} Smooth maps, plain reverse materials and real geometry avoid normal-map grain.

{limits}

The app still draws its existing coin contact line below floating shapes. Permanent {kind.title()} integration needs its own data set, model-table entry and still-art wiring by the app owner. The transparent fixed-Home-frame PNG is supplied without changing app art. All original temporary-slot assets and all 641 tracked app files were restored and verified byte for byte; branch, commit and Git status remain unchanged. Existing approved badges and Downloads folders were preserved.

Final model: [mobile/{stem}.usdz](mobile/{stem}.usdz). Editable model: [master/{kind}_badge_master.blend](master/{kind}_badge_master.blend). SHA-256: `{selected[kind]['sha256']}`.
'''
    (base/'REPORT.md').write_text(report)
    for folder in ['mobile','master','proof','stills']:shutil.copytree(base/folder,bundle/kind/folder)
    cp(base/'REPORT.md',bundle/kind/'REPORT.md')
    for f in (base/'source').glob('*'):
        if f.is_file():cp(f,bundle/kind/'source'/f.name)
    for f in ['badge.usdz','badge.usdc','settings.json','app.png','build.json','build.log']:cp(base/'source/calibration'/f,bundle/kind/'source/calibration'/f)
    for candidate in sorted((base/'candidates').iterdir()):
        for f in ['badge.usdz','badge.usdc','app.png','home_crop.png','reference_vs_app.png','NOTES.md','build.json','solve.json','settings.json','build.log','independent_validation.json','app_restore_verification.json']:
            if (candidate/f).exists():cp(candidate/f,bundle/kind/'candidates'/candidate.name/f)
        for f in (candidate/'textures').glob('*.png'):cp(f,bundle/kind/'candidates'/candidate.name/'textures'/f.name)
for f in (ROOT/'scripts').glob('*.py'):cp(f,bundle/'scripts'/f.name)
for f in ['app_repo_before.json','calibration_build.json']:cp(ROOT/'source'/f,bundle/'source'/f)
cp(ROOT/'proof/app_restore_verification.json',bundle/'source/app_restore_verification.json')
(ROOT/'selection.json').write_text(json.dumps(selected,indent=2)+'\n');cp(ROOT/'selection.json',bundle/'selection.json')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22);panel=Image.new('RGB',(1200,700),'#08090b');draw=ImageDraw.Draw(panel)
for i,k in enumerate(['gold','diamond']):panel.paste(Image.open(ROOT/k/'proof/home_crop.png'),(i*600,50));draw.text((i*600+25,14),k.title()+': actual Home render',font=font,fill='white')
panel.save(bundle/'Gold_and_Diamond_in_app.png');compare=Image.new('RGB',(1200,1400),'#08090b')
for i,k in enumerate(['gold','diamond']):compare.paste(Image.open(ROOT/k/'proof/reference_vs_app.png'),(0,i*700))
compare.save(bundle/'Reference_vs_app.png')
(bundle/'REPORT.md').write_text('''# Gold and Diamond badges

Created from the two supplied references and tested inside Home. Open **Gold_and_Diamond_in_app.png** for the actual Home renders or **Reference_vs_app.png** for matched-size comparisons. Full native app screenshots are in each `proof/app.png`.

- Gold model: `gold/mobile/gold_crown_mobile.usdz`.
- Diamond model: `diamond/mobile/diamond_crystal_mobile.usdz`.
- Editable Blender models and standalone USD sources with textures: each `master/` folder.
- Transparent fixed-Home-frame PNGs: each `stills/` folder.

The previews temporarily used Copper for Gold and Silver for Diamond because the new tiers have no 3D data sets yet. All original app assets and all 641 tracked files were verified unchanged after testing. The simulator retains the preview installation. ScreenTime-UIOnly: ** BUILD SUCCEEDED **.

Each badge report explains its geometry, checks and remaining visual limits. Numbered folders retain real app screenshots and reference comparisons. Existing approved models were preserved.

For editing, run `geometry.py` to generate meshes, then `facet_atlas.py` to repack the diamond's real faces. `solve.py <kind> candidates/<number> [candidates/<previous>]` measures native app lighting and solves maps; Blender runs `export.py -- <kind> candidates/<number>`. `optical_surface.py` derives the smoother final diamond material from the solved candidate 03 data. `agx.py` is copied unchanged from Silver 2. Gold's original calibration and first trial used a wider band opening; the final calibration measures the corrected smooth wall. Large diagnostic atlas NPZ files are omitted from this delivery and must be regenerated to rerun the solver. The editable masters and their textures are complete. App test scripts must always be followed by restoration and verification; they change only the two authorized temporary-slot USDZ files.
''')
manifest={str(f.relative_to(bundle)):sha(f) for f in sorted(bundle.rglob('*')) if f.is_file()};(bundle/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Prepared',bundle,selected)
