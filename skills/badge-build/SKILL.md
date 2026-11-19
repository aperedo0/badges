---
name: badge-build
description: Build a floating 3D badge (not a coin or the Diamond) from an approved plan as stacked pieces in the owner's open Blender, with tools that make every piece an exact closed solid with real bevels, gold rims and colored areas, prove the stack and the app contract, solve colors through the app's light, write the USDZ and capture it in the simulator. Use only once badge-plan-review has approved the badge's PLAN.md, or to rerun a build after a fix. A new mockup or a rebuild without an approved plan goes to badge-plan first.
---

# Badge build

Build exactly the approved plan (badge-plan, badge-plan-review), as stacked pieces with real depth, in the owner's open Blender. The scripts are in `scripts/`; run Python 3.11 tools with `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` and the writer with Blender's bundled Python, `/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13`. Paths below are relative to `skills/badge-build/`.

## 1. Measure the shapes

* Every shape in mockup pixels, back to front. Circles and straight lines fitted to the mockup's edges; curves through measured points; traced outlines only after simplifying them (straight runs straight, tips sharp) and rounding bumps away.
* Read unclear parts with `pixel_profile.py` instead of trusting any description.
* Mirror symmetric pieces: measure the left half and mirror. Where the mockup's halves differ, average both sides by signed distance to the shape's edge instead.
* **Layering**: wherever two pieces overlap, the one whose edges run unbroken through the crossing is on top (the long blades cross over the ring; a ring laid over them cut each in two). List the crossings; the stack order follows them. A top view check cannot see this.
* **Fills between gold lines**: where gold lines, curls and borders are what is left between enamel fills, trace the fills by color (smoothed: blur, contour, simplify) and set them into one gold plate. Subtracting grown fills from a traced gold area eats every thin curl.
* **Clean line work**: traced gold lines wobble with the shading beside them (spirals came out lumpy and twice as wide). Take the gold with its highlights (warm, green above blue), then `linework.py` (centerline, pruned spurs, smoothed width, even strokes); the enamel is what is not stroke. Fills grow by their slope only up to each stroke's core (the stroke shrunk 2 px), so no line loses width. Draw the strokes over the mockup to check.
* **The piece that forms the outline owns it**: where a later piece (a cloud, a star point) is the badge's edge, it reaches the silhouette exactly (fill gaps under about 28 px), and the base ends 6 px inside it along the outline only. A base left at the silhouette beside it shares its wall or shows a sub-pixel ledge.
* **Checkpoint 1**: `overlay.py PIECES.json MOCKUP OUT name:x0,y0,x1,y1 ...` draws every piece over the mockup with 3x crops. Every edge within 3 px; every visible piece present.

## 2. Write the pieces file

`PIECES.json` (format at the top of `scripts/badge3d.py`): one entry per piece, back to front, each with its outline, top (flat, dome, roof facets, planes through points, or a profile), bevel, gold rim, colored cells, lines between cell groups, and mirrored twins sharing a base. Steps between pieces about 0.03 to 0.08 units; bevels at least about 0.04 units wide.

**Enamel colors come from the mockup itself (the approved method).** Approved badges (Tidal Compass, Astral Navigator, Emerald Trophy: `forge_tide_compass_20261103/prepare_finish.py`, `pack.py`) make enamel a metal with a near black color, so the studio adds no pale reflection, and carry the mockup's own colors in emission solved through the app's AgX. `enamel_fill.py CAND MOCKUP CONFIG OUT` does this per material, sampling only pixels where the build shows that material and never the mockup's gold. One enamel may cover several colored areas (field and ribbons): their exact colors and shading then come from the picture, so a traced edge a few px off still shows the right color. Geometry gives the relief and the gold; the picture gives the fine color.
* **Every enamel material goes in `"glow_only"` in PIECES.json.** badge3d gives those surfaces one fixed shading direction, because the app draws a dark speck wherever one of its lights reflects straight into the camera on a glow only surface (proven on Golden Storm, November 9, 2026). enamel_fill.py and write_usdz.py refuse an enamel that is not on the list.
* **Set `units.width_px` and `units.height_px` to the mockup's size**: enamel colors are mapped over the whole mockup, and enamel_fill.py stops on a mismatch.

**Colored faces stay flat, as real enamel.** A colored face tilted by about 0.04 or more mirrors a bright part of the studio and washes pale. Facets in the mockup are paint areas meeting at a line; depth comes from stacked pieces and their gold edges. Metal may tilt any way. Colored domes stay at about 0.03 or less. For flat solved colors from `palette.py` (not enamel): colored fields in the lower half take roughness about 0.18, since the low left reflector's mirror spot lands near badge (minus 1.5, minus 1.5).

## 3. Build, prove, color

1. `badge3d.py PIECES.json CAND` builds the solids and stacks them (each base is the highest earlier surface under it plus the gap; hidden areas are not meshed).
2. `validate.py CAND` must print no failures: bounds without rescaling (bottom at Y minus 2.455, top at 2.995 unless the badge is as wide as X 3.35), at most 45,000 triangles unless PIECES.json gives a `"budget_reason"` (then say it in the report), Z centered, no coin names, every piece closed with positive volume and a mirrored back, the gem's foil UVs (for a piece named `gem`), per pixel stacking (the right piece on top, at least 0.006 above the next), and no two pieces' outlines running together for more than 30 px (side walls in the same place); failures name the pieces and the spot. Run it once with `--break-shift` and `--break-base` to see it fail.
3. `material_map.py CAND MOCKUP CLASSES OUT` shows the top material per pixel beside the mockup and lists every local miss with its place (OUT_misses.png). Fix each miss or say why it is none (metal highlights read as white). Then the overlay of the pieces over the mockup at every crossing.
4. Colors, in this order, all into one folder DIR: first `palette.py TARGETS.json DIR` for the metals (and a flat color only when there is no picture to sample; it writes `DIR/palette.json` from scratch, solving each paint through the app's measured light, pale lemon rule, capped below the glow level, no emission). Then `enamel_fill.py CAND MOCKUP CONFIG DIR` for every enamel, and merge `DIR/palette_enamel.json` into `DIR/palette.json`. Texture paths are relative to DIR, which write_usdz.py reads. Take targets from the mockup's own colors (median per area, `app_colors.py` prints them).
5. `light_centers.py CAND` must print `centers: 0` (no dark specks on enamel at rest).

## 4. Blender, file, app

1. Write the job file `/tmp/badge_live_job_<badge>.json` (parts, meta, palette, root, blend, scene, prefix, mockup, mockup_width_px) and run `build_live.py` through the bridge: send `BADGE_JOB = '/tmp/badge_live_job_<badge>.json'` followed by the script's text (`ruby_heart_claude_20261107/tools/blender_link.py code FILE` sends a file). It updates the pieces in place (never deletes objects), stands the badge upright beside the mockup and saves the badge's .blend. It refuses, loading nothing:
   * when the open file has unsaved changes, since every load ends with a save and those changes may be the owner's: ask the owner, then rerun with `"allow_unsaved": true` only after they answer (owner rule, November 14, 2026);
   * when another badge's file is open, which would copy that badge's scenes into this one's file: save it, reopen Blender with this badge's file (or empty, for a new badge), and load again.
2. **Sweep it in Blender before any app run** (owner rules, November 9 and 12, 2026): renders of the front, both sides and back beside the mockup, and zoomed views of every part (badge-fresh-review step 0; `golden_storm_fable_20261109/blender_zoom.py` is the working example). Check the plan's "looks right when" lines here first. Fix and repeat until clean. Working versions are judged here; the app is for a version ready to be judged.
3. `write_usdz.py CAND DIR/palette.json PREFIX` with Blender's Python writes `CAND/model.usdz`. It refuses enamel missing from `glow_only` and a file over 5 MB without a `budget_reason`.
4. `app_try.py CAND DATASET KEY` installs it in the preview app (`emerald_trophy_20261025/preview`), builds and captures the rest pose and eight turns into `CAND/app`. **A new badge needs its preview set up first**: a `Badge3DPreview<Key>.dataset` folder (copy a neighbour's `Contents.json` and `coin.usdz`), the key in `PrivateBadgePreview.items`, and for a floating shape the data set on a `.neutral` placement line, all in `Badge3DLiveBadge.swift`; the script checks these and stops if one is missing. It also stops when the app did not load this candidate, so it never captures another badge. `--no-build` reuses the last build and so the model that build packed: use it only to recapture the same candidate.
5. `app_colors.py CAND MOCKUP REVIEW.json OUT.json` measures every material as the app shows it beside the mockup at the same spots. A material far off in lightness is a light problem (a face mirroring a studio light: change its tilt), not a paint problem. Solve gold per region (upper and lower gold are lit differently) and keep gold and yellow apart in hue and lightness.
6. **Check every piece's "looks right when" line from the plan** against the app captures (and the Blender views for angles the app does not shoot). Write each one as PASS or FAIL with the picture that shows it in the version notes. A FAIL is fixed in this version, never left for the reviewer to find; the same line failing three versions in a row means the method is wrong: back to the plan (at most once without the owner; see badge-plan-review).
7. Run badge-fresh-review: its finish gate, then the fresh review. Check the reviewer's size and position claims with landmarks at the same scale before acting on them: glow outside the outline fools its width table.

## Never

* One flat plate with painted areas and tiny bumps for lines.
* A grid of triangles over a picture.
* A piece cut in two by one it should cross over.
* Tilted colored faces.
* Shipping with validate failures, light centers on enamel, or a finish check done only by the builder.
