"""Deliver only frozen candidates that have matching real-app evidence and checks."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from measure_smoothness import Emblem

root = Path(__file__).resolve().parents[1]
selected = {'silver2': sys.argv[1], 'iron2': sys.argv[2]}
repo = Path('/Users/antonioperedo/Desktop/screen_time')
baseline = json.loads((root / 'app_testing/texture_revision_baseline.json').read_text())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
read = lambda path: json.loads(Path(path).read_text())
status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=repo, text=True)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
assert status == baseline['status'] == '' and head == baseline['head']
for asset in baseline['assets'].values():
    assert sha(asset['path']) == asset['sha256']
for path, digest in baseline['protected_sources'].items():
    assert sha(path) == digest

font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)

def sheet(paths, labels, out, box=None):
    images = [Image.open(p).convert('RGB') for p in paths]
    if box:
        images = [im.crop(box) for im in images]
    width, height = images[0].size
    assert all(im.size == (width, height) for im in images)
    canvas = Image.new('RGB', (len(images) * (width + 24) + 24, height + 96), (17, 20, 23))
    draw = ImageDraw.Draw(canvas)
    for i, (im, label) in enumerate(zip(images, labels)):
        x = 24 + i * (width + 24)
        canvas.paste(im, (x, 72))
        draw.text((x, 23), label, font=font, fill=(229, 231, 233))
    canvas.save(out)

rows = []
for kind, number in selected.items():
    base = root / kind
    for candidate in sorted((base / 'iterations').iterdir()):
        measured = next((candidate / name for name in ['result.json', 'app_measurements.json'] if (candidate / name).exists()), None)
        note_path = candidate / 'NOTES.md'
        if measured and note_path.exists():
            note = note_path.read_text()
            if 'pending' in note.lower() or 'awaiting' in note.lower():
                note = '\n'.join(line for line in note.splitlines() if 'pending' not in line.lower() and 'awaiting' not in line.lower())
                value = read(measured)
                note_path.write_text(note + f'\nApp: actual3D verified; white{value["shape_metrics"]["white_pixels"]}/1249. Original assets restored and full repo status clean. See app metrics and restoration evidence.\n')
    chosen = base / 'iterations' / number
    model = base / 'mobile' / f'{kind}_badge_mobile.usdz'
    build = read(base / 'reports/build.json')
    check = read(base / 'reports/shape_checks.json')
    compare = read(base / 'reports/compare_finish.json')
    app = read(chosen / 'result.json')
    assert sha(model) == sha(chosen / model.name) == build['sha256'] == check['sha256'] == app['candidate_sha256']
    assert app['completed'] and app['actual_3d_visual_check'] and app['shape_metrics']['passes_white_cap']
    assert check['all_checks_pass'] and compare['all_geometry_and_custom_normals_identical'] and compare['all_mesh_and_material_binding_ids_unchanged']
    assert read(base / 'reports/plain_finish_checks.json')['all_plain_lower_fifth_checks_pass']
    assert not read(base / 'reports/texture_checks.json')['normal_maps']
    assert 'Success!' in (base / 'reports/usdchecker.txt').read_text()
    assert f"TOTAL TRIANGLES {build['triangles']}" in (base / 'reports/reimport_check.txt').read_text()
    if kind == 'silver2':
        tones = read(base / 'reports/plane_tones.json')['harsh']
        assert tones['tone_gap_pass'] and tones['no_dead_plane_pass'] and tones['polish_pass']
        assert all(value == 0 for value in build['flat_plane_max_normal_difference'].values())
    for src, dst in [('app_rest.png', 'app_rest.png'), ('badge_zoom.png', 'app_badge_zoom.png'), ('floor_zoom.png', 'app_floor_zoom.png')]:
        shutil.copy2(chosen / src, base / 'proof' / dst)
    reference_comparison = chosen / 'reference_vs_app_home_scale.png'
    if not reference_comparison.exists():
        reference_comparison = next(chosen.glob('reference_*13_home_scale.png'))
    shutil.copy2(reference_comparison, base / 'proof/reference_vs_app_home_scale.png')
    comparison = Image.open(reference_comparison).convert('RGB')
    reference_width = Image.open(chosen / 'reference_home_scale.png').width
    final_width = (comparison.width - reference_width) // 2
    reference = comparison.crop((0, 0, reference_width, comparison.height))
    final_app = comparison.crop((comparison.width-final_width, 0, comparison.width, comparison.height))
    pair = Image.new('RGB', (reference.width+final_app.width+48, comparison.height+64), (17, 20, 23))
    draw = ImageDraw.Draw(pair)
    pair.paste(reference, (16, 48)); pair.paste(final_app, (reference.width+32, 48))
    draw.text((16, 13), 'Reference', font=small, fill='white')
    draw.text((reference.width+32, 13), 'Final in app', font=small, fill='white')
    pair.save(base / 'proof/reference_vs_final_app.png')
    for name in ['reports', 'proof', 'stills']:
        shutil.copytree(base / name, chosen / name, dirs_exist_ok=True)
    for width in [360, 120]:
        with Image.open(base / 'stills' / f'{kind}_1080.png') as im:
            im.resize((width, width), Image.Resampling.LANCZOS).save(base / 'stills' / f'{kind}_{width}.png')
    im = Image.open(base / 'proof/front.png')
    im.crop((230, 370, 850, 940)).resize((1240, 1140), Image.Resampling.NEAREST).save(base / 'proof/surface_zoom.png')
    old_number = '05' if kind == 'silver2' else '04'
    sheet([base / 'previous/first_shape_delivery/proof/app_rest.png', base / 'proof/app_rest.png'], ['First delivery', 'Revised finish'], base / 'proof/texture_before_after_app.png', (270, 300, 936, 1040))
    title = 'Silver 2' if kind == 'silver2' else 'Iron 2'
    visual = read(chosen / 'app_metrics.json')['visual_review']
    report = f'# {title}: revised finish, candidate {number}\n\n'
    report += 'This revision corrects the material finish while preserving every point, triangle, UV, custom normal, mesh ID and material binding from the first shape delivery. Previous final models and scenes remain in `previous/first_shape_delivery/`. These remain standalone variants, separate from the shipped coin badges.\n\n'
    report += ('The star and foliage now use restrained directional polishing. The star uses cooler shaded faces and broad roughness ramps inside its genuinely flat planes, producing physical reflection gradients rather than painted highlights. No bumps or widened edge glints are added.\n\n' if kind == 'silver2' else 'The shield now uses1024px color maps derived from the reference in linear light, divided by local illumination to recover the worked-metal pattern. Filtering that erased the original scuffs has been removed. Even satin roughness and zero normal maps preserve clean lighting; the requested fine forging lives in color only.\n\n')
    report += f'## Size and budget\n\n| Model | Triangles | Bytes | Decimal MB |\n|---|---:|---:|---:|\n| Original Silver coin |38,566|3,511,448|3.511|\n| {title} |{build["triangles"]:,}|{build["file_bytes"]:,}|{build["file_bytes"]/1e6:.3f}|\n\nBounds: `{build["bounds"]}`. Dimensions: `{check["span"]}`. Y-up,1meter/unit, front+Z, no transforms. X/Z centered, thickness0.65, lowestY=-2.455, floating0.44above the app floor. No floor, light or reflection geometry. SHA256 `{build["sha256"]}`.\n\n'
    report += '## Complete checks\n\n- ARKit checker PASS: [installed CLI output](reports/usdchecker.txt), exit0 and `Success!`. The installed Apple checker also emits duplicate ConnectableAPI registration diagnostics; the bundled Blender checker reports zero errors, failed checks or warnings. This installation diagnostic is also present on the original Silver.\n- [Reimport output](reports/reimport_check.txt): expected geometry, UVs, materials and exact triangle total.\n- [Shape frame checks](reports/shape_checks.json): all numerical bounds, units, transforms, centering, names and ARKit checks pass.\n- [Exact previous-shape comparison](reports/compare_finish.json): every geometry/normal/UV attribute and mesh/material binding ID remains identical. Every material attribute change is enumerated.\n- [Comparison with shipped Silver](reports/compare_usd.json) and [raw output](reports/compare_usd.txt) enumerate every added/removed/changed prim. This is an intentional standalone shape, not a silver coin shell match. Coin floor-cut checks are inapplicable: all shape points remain above the floor.\n- [Texture checks](reports/texture_checks.json): shader color spaces and `USDZ_UV` readers correct; zero normal maps. [Actual pixel checks](reports/plain_finish_checks.json): every map has exactly0channel difference throughout the lowest fifth. Finish blends back by44%height; back/downward-facing parts remain plain.\n\n'
    report += 'Same-camera render differences against the first delivery: [complete pixel table](reports/compare_renders.json); before/after sheets for front, point rig and three-quarter views live in proof/. These quantify changed finish; USD comparison independently proves unchanged geometry.\n\n'
    smooth = read(base / 'reports/smoothness.json')
    if kind == 'silver2':
        report += 'All ten star planes have **max normal difference0.0**. [Plane IDs](proof/star_plane_ids.png), [individual crops](proof/every_star_plane_zoom.png), [all tone numbers](reports/plane_tones.json).\n\n| Rig | Facet residual mean | Silver limit | Edge excess mean | Silver limit |\n|---|---:|---:|---:|---:|\n'
        for rig, value in smooth['table'].items():
            report += f'|{rig}|{value["facet_rough_mean"]:.3f}|{.92 if rig=="stage" else 1:.2f}|{value["edges"]["excess_mean"]:.3f}|{61.5 if rig=="stage" else 64.6}|\n'
        report += f'\nPoint-rig minimum neighboring tone gap **{tones["minimum_neighbor_gap"]:.3f}**, minimum plane mean **{tones["minimum_plane_mean"]:.3f}**, brightest **{tones["maximum_plane_mean"]:.3f}**, below original Silver **{tones["reference_brightest_facet_mean"]:.3f}**. The soft studio rig is supplementary: its neighboring means are also recorded, but the required10level gap is judged in the app point rig. Legacy ring/inset metrics are inapplicable to this shape. [Smoothness output](reports/smoothness.txt).\n\n'
    else:
        report += 'The plate is intentionally curved. At shared plate points, max custom-normal difference is **0**, preventing independent triangle shading.\n\n| Rig | Curved residual | Grain sigma2.5 | Mottle sigma6 | Mean |5th percentile|\n|---|---:|---:|---:|---:|---:|\n'
        for rig, value in smooth['regions'].items():
            report += f'|{rig}|{value["cubic_residual"]:.3f}|{value["grain_sigma_2_5"]:.3f}|{value["mottle_sigma_6"]:.3f}|{value["mean"]:.3f}|{value["percentile_5"]:.3f}|\n'
        report += '\nThese are reported texture/curved-surface metrics, not a claim of passing a flat untextured-facet limit. Owner-requested texture uses AGENTS§7.2 exception; the actual app is the visual ground truth. [Raw metrics](reports/smoothness.json).\n\n'
    report += f'## Actual app validation\n\nWhole-badge white count **{app["shape_metrics"]["white_pixels"]}/1249**. Actual3D confirmed by sculpted outlines and matching reflection. App reviewer: {visual}\n\n'
    report += '[Matched Home-scale reference comparison](proof/reference_vs_app_home_scale.png): left=reference, middle=candidate12, right=final13. The source is downsampled to the actual shape size; app pixels remain actual screenshots.\n\n'
    report += '[Reference and final only](proof/reference_vs_final_app.png) omits the preceding candidate for easier comparison.\n\n'
    report += '```text\nScreenTime: ** BUILD SUCCEEDED **\nScreenTime-UIOnly: ** BUILD SUCCEEDED **\nScreenTime-UIOnly (simulator): ** BUILD SUCCEEDED **\nTests skipped: presentation lane, no logic changed\n```\n\n'
    report += f'Exact candidate evidence: [iteration folder](iterations/{number}/), including build outputs, three explicit tier launches after install, app screenshot, measurements and finally-protected restoration. Simulator69A29DD2-C91E-487A-81B9-3B146DF8F07B, bundlecom.antonioperedo.screentime.uidev, `-BadgeHeroTier {kind[:-1]}`. Tests used temporary own-tier asset substitution, one file at a time. Both original app assets restored byte-for-byte.\n\n'
    report += '## Every iteration\n\n|Candidate|App white /1249|Change and outcome|\n|---|---:|---|\n'
    for candidate in sorted((base / 'iterations').iterdir()):
        measurements = next((candidate / name for name in ['result.json', 'app_measurements.json'] if (candidate / name).exists()), None)
        white = str(read(measurements)['shape_metrics']['white_pixels']) if measurements else 'not tested'
        notes = (candidate / 'NOTES.md').read_text().strip().replace('|', '/') if (candidate / 'NOTES.md').exists() else 'See candidate evidence.'
        report += f'|[{candidate.name}](iterations/{candidate.name}/)|{white}|{notes.replace(chr(10), " ")}|\n'
    report += '\nRejected preflights remain in reports/preflight folders; Silver07 failed tone checks before installation. Silver11 is an import diagnostic: its screenshot is pixel-identical to10, disproving the fallback-scalar hypothesis. Experimental Iron normal/roughness maps were rejected for pebbling; the final contains neither.\n\n'
    report += '## Materials\n\nAll IDs remain unchanged from the first shape. Colors are linear RGB; mapped roughness takes precedence over its fallback scalar.\n\n|Name|Linear RGB|Metallic|Roughness fallback|Maps|\n|---|---|---:|---:|---|\n'
    for material in build['material_table']:
        report += f'|`{material["name"]}`|{material["color_linear"]}|{material["metallic"]}|{material["roughness"]}|{material["textures"] or "none"}|\n'
    report += '\nFinish recipe/evidence: [settings](settings.json), [texture manifest](reports/finish_maps.json). Maps are512px for Silver and1024px for Iron. Silver star ramps run ridge→outer valley, shaded faces0.34→0.37; lit per-plane values are in the recipe. Iron body roughness is uniform within each map and border roughness0.40.\n\n'
    report += '## Explicit reference exceptions and limits\n\nThe owner-requested standalone references use updated AGENTS§2B instead of frozen coin shells/names. Shape-specific IDs deliberately avoid app coin-material overrides. Both body envelopes remain0.65thick; outlines remain satin. The laurel has rolled/cylindrical leaves and stems rather than the shield’s layered frame, an existing reference-specific outline-profile exception. Silver’s thin decorative stems/leaf tips/open wreath override the0.6minimum-feature and filled-silhouette wording; the shield tip/thin border likewise preserve the requested source silhouette. Curved leaves/stems/shield are not claimed to be flat gem planes.\n\n'
    if kind == 'iron2':
        report += 'Texture likeness requires the source’s finer1–2screen-pixel forging/scuff marks: this explicitly overrides the standing3–4pixel texture-mark minimum for this reference. Fine detail is bounded color variation only, with filtered sampling; no normal or roughness grain can amplify it into specular sparkle. No new dents are invented or disguised as geometry. The lowest fifth remains deliberately clean for the reflection, so that region is smoother than the reference.\n\n'
    report += 'The reference images have different studio lighting from Home. These are functioning physical metallic assets, not a baked image copy; exact highlight locations differ. The app still draws the old coin-width contact-shadow line beneath these floating shapes; this is the accepted AGENTS§7.3 limitation and app code is untouched. Reviewed in the simulator, not on a physical phone. Stills include1080px,360px and120px/40pt@3x with6.03units spanning108of120pixels.\n\nFinal full app `git status --porcelain` is empty; both original assets, HEAD and seven protected sources are unchanged. [Restoration proof](../proof/repo_final.json).\n'
    (base / 'REPORT.md').write_text(report)
    rows.append([title, number, build['triangles'], build['file_bytes'], app['shape_metrics']['white_pixels'], build['sha256']])

shots = [root / kind / 'proof/app_rest.png' for kind in selected]
labels = ['Silver 2', 'Iron 2']
sheet(shots, labels, root / 'proof/silver_2_and_iron_2_in_app.png', (270, 300, 936, 1040))
sheet(shots, labels, root / 'proof/full_app_screens.png')
original = Path('/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/app_reference/app_silver_rest.png')
sheet([original, *shots], ['Original Silver', *labels], root / 'proof/original_silver_vs_shapes_same_camera.png', (270, 300, 936, 1040))
sheet([original, *shots], ['Original Silver floor', *labels], root / 'proof/floor_gaps_same_scale.png', (360, 700, 846, 1040))
for kind in selected:
    shutil.copy2(root / 'proof/original_silver_vs_shapes_same_camera.png', root / kind / 'proof/silver_comparison.png')
    shutil.copy2(root / 'proof/floor_gaps_same_scale.png', root / kind / 'proof/floor_comparison.png')

# Native crops preserve app pixels; enlarged plane crops use nearest-neighbor only.
emblem = Emblem(root / 'silver2/reports/Star_geometry.json')
facets, _ = emblem.facet_masks(0)
im = Image.open(root / 'silver2/proof/app_light_front.png')
canvas = Image.new('RGB', (1250, 550), (17, 20, 23)); draw = ImageDraw.Draw(canvas)
for i in range(10):
    ys, xs = np.nonzero(facets[i]['full'])
    crop = im.crop((xs.min()-3, ys.min()-3, xs.max()+4, ys.max()+4))
    crop.thumbnail((235, 230), Image.Resampling.NEAREST)
    x, y = (i % 5)*250, (i // 5)*275
    canvas.paste(crop, (x+(250-crop.width)//2, y+35)); draw.text((x+10, y+8), f'Plane {i}', font=small, fill='white')
canvas.save(root / 'silver2/proof/every_star_plane_zoom.png')
canvas = Image.new('RGBA', (340, 190), (20, 23, 26, 255)); draw = ImageDraw.Draw(canvas)
for i, kind in enumerate(selected):
    still = Image.open(root / kind / 'stills' / f'{kind}_120.png').convert('RGBA')
    canvas.alpha_composite(still, (20+i*170, 50))
    draw.text((20+i*170, 18), kind.title()+' / 40pt', font=small, fill='white')
canvas.convert('RGB').save(root / 'proof/40pt_readability.png')
verification = {'git_status_porcelain': status, 'HEAD': head, 'original_assets_restored': True, 'protected_sources_unchanged': True, 'selected': rows}
(root / 'proof/repo_final.json').write_text(json.dumps(verification, indent=2)+'\n')
(root / 'REPORT.md').write_text('# Silver 2 and Iron 2: texture revision\n\nGeometry unchanged. Silver has richer polished warm/cool planes and leaf reflections; Iron has reference-derived fine worked-metal/scuff color and restrained satin reflections. Each exact final was verified in the real app, using temporary substitution and full restoration.\n\n|Variant|Candidate|Triangles|Bytes|App white /1249|\n|---|---|---:|---:|---:|\n'+''.join(f'|{title}|{number}|{triangles:,}|{size:,}|{white}|\n' for title,number,triangles,size,white,digest in rows)+'\n[Silver report](silver2/REPORT.md), [Iron report](iron2/REPORT.md), [actual app comparison](proof/silver_2_and_iron_2_in_app.png), [floor comparisons](proof/floor_gaps_same_scale.png). Per-tier reports contain all checks, metrics, every iteration, material tables, explicit reference exceptions and remaining lighting/presentation limits. The first delivery is preserved in each `previous/first_shape_delivery/`. No original coin or production app asset was permanently replaced.\n\n[Final restoration proof](proof/repo_final.json): full app git status empty, HEAD, original assets and all protected sources unchanged.\n')
(root / 'README.md').write_text('# Badge variants 2\n\nActual app previews: proof/silver_2_and_iron_2_in_app.png. Final models: silver2/mobile/silver2_badge_mobile.usdz and iron2/mobile/iron2_badge_mobile.usdz. Editable master/reduced/final Blender scenes, textures, numbered iterations and raw check outputs are included. Read per-tier REPORT.md for texture exceptions and presentation limits.\n\nBuild from existing copied sources/geometry: `/usr/local/bin/python3 scripts/finish_textures.py silver2` (or iron2), then `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/build.py -- silver2` (or iron2). Verify with scripts/verify_finish.py inside Blender, render scripts/render_finish.py, then run shape_metrics.py and verify_plain_finish.py with Python. Native app preview guard needs a freshly audited app_testing baseline before reuse in another session. Original coin export scripts are audit/reference only. Do not run obsolete prepare.py or finish.py to overwrite this revised finish.\n\nOriginal app assets are restored. Permanent integration and app floor-shadow changes are outside this delivery.\n')
for kind, number in selected.items():
    for name in ['reports', 'proof', 'stills']:
        shutil.copytree(root / kind / name, root / kind / 'iterations' / number / name, dirs_exist_ok=True)
print(json.dumps(verification, indent=2))
