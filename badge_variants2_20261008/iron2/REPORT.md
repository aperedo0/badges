## Four badges available on Home (2026-10-08)

The temporary preview now cycles Silver2 → Iron2 → Silver → Iron. The original coins are exact backup copies in separate preview-only datasets, and both new shape assets are unchanged. All four actual models/reflections and two complete switch cycles passed simulator visual verification with no fallback or missing-floor frames. [Four-badge pictures, video and build proof](../app_install_preview/all_four/README.md). The owner-requested preview remains uncommitted. No earned-badge or model-design changes.

## Home switch correction (2026-10-08)

Fixed the brief old flat coin and disappearing floor during switching. A single persistent renderer keeps the current actual badge/floor visible until the selected actual3D scene is ready. Cold, warm and rapid-tap 60fps recordings pass with zero intermediary artwork or blank-floor frames. Both models and their resting badge/floor pixels are unchanged. [Correction proof, recordings and build checks](../app_install_preview/switch_fix/README.md).

The authorized preview code and two models remain uncommitted. BEHAVIOR_MAP.md is also dirty from outside this badge work and was preserved; current full status is recorded in ../app_install_preview/final_verification.json. Historical clean-status statements below describe the earlier export tests.

## Temporary app preview installed (2026-10-08)

The owner requested keeping Silver2 and Iron2 in the app with a Home switch. Final13 models now replace their own tier dataset files, and `BadgeHeroCard.swift` adds a view-local Badge preview switch, defaulting to Silver2. These three app files deliberately remain uncommitted; HEAD and branch unchanged. This explicit request overrides the usual badge-folder no-app-edit/always-restore rule for this preview only. Originals are backed up in `app_install_preview/`. No earned-tier, accounting, persistence, stage, lighting or other-screen changes. Both device builds and the UIOnly simulator build passed; actual repeated button taps verified both 3D models/reflections.

[Temporary installation proof and pictures](../app_install_preview/README.md). The export-validation reports below describe the earlier testing phase, when original app assets were restored; their clean-status claims are historical, not the current intentional three-file diff.

# Iron 2: revised finish, candidate 13

This revision corrects the material finish while preserving every point, triangle, UV, custom normal, mesh ID and material binding from the first shape delivery. Previous final models and scenes remain in `previous/first_shape_delivery/`. These remain standalone variants, separate from the shipped coin badges.

The shield now uses1024px color maps derived from the reference in linear light, divided by local illumination to recover the worked-metal pattern. Filtering that erased the original scuffs has been removed. Even satin roughness and zero normal maps preserve clean lighting; the requested fine forging lives in color only.

## Size and budget

| Model | Triangles | Bytes | Decimal MB |
|---|---:|---:|---:|
| Original Silver coin |38,566|3,511,448|3.511|
| Iron 2 |38,528|3,815,685|3.816|

Bounds: `[[-2.161102294921875, -2.4549999237060547, -0.32499998807907104], [2.161102294921875, 2.8450000286102295, 0.32499998807907104]]`. Dimensions: `[4.32220458984375, 5.300000190734863, 0.6499999761581421]`. Y-up,1meter/unit, front+Z, no transforms. X/Z centered, thickness0.65, lowestY=-2.455, floating0.44above the app floor. No floor, light or reflection geometry. SHA256 `3c2b245b3074c8f9a72f87630ff6317a581bd0e34e17e364b3f926d93e9517fd`.

## Complete checks

- ARKit checker PASS: [installed CLI output](reports/usdchecker.txt), exit0 and `Success!`. The installed Apple checker also emits duplicate ConnectableAPI registration diagnostics; the bundled Blender checker reports zero errors, failed checks or warnings. This installation diagnostic is also present on the original Silver.
- [Reimport output](reports/reimport_check.txt): expected geometry, UVs, materials and exact triangle total.
- [Shape frame checks](reports/shape_checks.json): all numerical bounds, units, transforms, centering, names and ARKit checks pass.
- [Exact previous-shape comparison](reports/compare_finish.json): every geometry/normal/UV attribute and mesh/material binding ID remains identical. Every material attribute change is enumerated.
- [Comparison with shipped Silver](reports/compare_usd.json) and [raw output](reports/compare_usd.txt) enumerate every added/removed/changed prim. This is an intentional standalone shape, not a silver coin shell match. Coin floor-cut checks are inapplicable: all shape points remain above the floor.
- [Texture checks](reports/texture_checks.json): shader color spaces and `USDZ_UV` readers correct; zero normal maps. [Actual pixel checks](reports/plain_finish_checks.json): every map has exactly0channel difference throughout the lowest fifth. Finish blends back by44%height; back/downward-facing parts remain plain.

Same-camera render differences against the first delivery: [complete pixel table](reports/compare_renders.json); before/after sheets for front, point rig and three-quarter views live in proof/. These quantify changed finish; USD comparison independently proves unchanged geometry.

The plate is intentionally curved. At shared plate points, max custom-normal difference is **0**, preventing independent triangle shading.

| Rig | Curved residual | Grain sigma2.5 | Mottle sigma6 | Mean |5th percentile|
|---|---:|---:|---:|---:|---:|
|stage|20.335|4.239|4.873|65.341|14.140|
|harsh|21.153|4.007|4.622|61.004|13.213|

These are reported texture/curved-surface metrics, not a claim of passing a flat untextured-facet limit. Owner-requested texture uses AGENTS§7.2 exception; the actual app is the visual ground truth. [Raw metrics](reports/smoothness.json).

## Actual app validation

Whole-badge white count **0/1249**. Actual3D confirmed by sculpted outlines and matching reflection. App reviewer: Actual beveled 3D shield, matching reflection. Prefer13 over12: darker broad frame reads worked steel instead of pale outline, with even controlled satin catches and no underdark/uneven stretch. Body12 metallic contrast and resolved real-reference scuffs preserved. White0/1249, no broadhalo, brightdot sparkle, seam or reflection overlap/noise; lowerfade/gap clean. Source studio catch positions and machined accents still differ, no exactmatch claim.

[Matched Home-scale reference comparison](proof/reference_vs_app_home_scale.png): left=reference, middle=candidate12, right=final13. The source is downsampled to the actual shape size; app pixels remain actual screenshots.

[Reference and final only](proof/reference_vs_final_app.png) omits the preceding candidate for easier comparison.

```text
ScreenTime: ** BUILD SUCCEEDED **
ScreenTime-UIOnly: ** BUILD SUCCEEDED **
ScreenTime-UIOnly (simulator): ** BUILD SUCCEEDED **
Tests skipped: presentation lane, no logic changed
```

Exact candidate evidence: [iteration folder](iterations/13/), including build outputs, three explicit tier launches after install, app screenshot, measurements and finally-protected restoration. Simulator69A29DD2-C91E-487A-81B9-3B146DF8F07B, bundlecom.antonioperedo.screentime.uidev, `-BadgeHeroTier iron`. Tests used temporary own-tier asset substitution, one file at a time. Both original app assets restored byte-for-byte.

## Every iteration

|Candidate|App white /1249|Change and outcome|
|---|---:|---|
|[01](iterations/01/)|0|Traced shield silhouette, layered satin border, bowed plate and recessed reveal. Filtered broad forged color/roughness; lower fifth plain. No normal maps.   App: actual 3D verified; whole-box white 0/1249. Both assets restored byte-for-byte, full app repo status clean. See app_measurements.json and the dated app_testing evidence for build proofs.|
|[02](iterations/02/)|0|Two changes from 01: seat the complete plate perimeter and round its center bow to remove stepped border shading and the hard two-tone split; reduce color/roughness texture contrast. Satin border geometry/materials unchanged.   App: actual 3D verified; whole-box white 0/1249. Both assets restored byte-for-byte, full app repo status clean. See app_measurements.json and the dated app_testing evidence for build proofs.|
|[03](iterations/03/)|0|One plate-surface correction: remove the inside width clamp that produced the upper-right diagonal highlight boundary. Bow now tapers continuously to the full seated perimeter; border and restrained texture preserved.   App: actual 3D verified; whole-box white 0/1249. Both assets restored byte-for-byte, full app repo status clean. See app_measurements.json and the dated app_testing evidence for build proofs.|
|[04](iterations/04/)|0|One geometry change from03: a Poisson-solved dome replaces the radial plate height field. The plate has continuous interior curvature and its complete perimeter is seated; reference-shaped satin border and restrained textures preserved.   App: actual 3D verified; whole-box white 0/1249. Both assets restored byte-for-byte, full app repo status clean. See app_measurements.json and the dated app_testing evidence for build proofs.|
|[05](iterations/05/)|0|Replaced the cloudy forging with resolved worked-metal and diagonal tooling marks. Added restrained, baked relief under the prior Iron authorization; maximum tilt 5 degrees, lower fifth remains plain. Geometry and satin outline unchanged.|
|[06](iterations/06/)|0|Sharper resolved forging and diagonal scoring, with a visibly worked satin border. Body tone lowered toward dark iron; relief remains baked and restrained at7degrees maximum, and lower surfaces remain even. All geometry unchanged.|
|[07](iterations/07/)|0|Keep Iron06 resolved worked-metal color/roughness and dark tone; replace grain-derived relief with only shallow intentional scoring. Maximum authored normal tilt3degrees; no pebbled photographic grain in normals. Geometry and clean lower surfaces unchanged.|
|[08](iterations/08/)|0|Retain finer worked-metal color directly from the de-lit reference instead of broadening it into coarse pebbling. Roughness is even0.49(body)/0.40(border); remove all metal normal maps and added scoring relief. Document the reference-driven fine-color-detail exception. Geometry and plain lower fifth unchanged.|
|[09](iterations/09/)|0|Keep Iron08 even roughness, no normal maps and fine color-only reference texture. Increase only its amplitude so worked metal and the border finish read at Home size, with lower fifth still perfectly even.|
|[10](iterations/10/)|0|Retain a wider range of real reference scuffs and forging marks; reduce uniform fine-detail amplitude from0.42to0.35. Color only, even roughness and no normal maps; geometry/reflectionfade unchanged.|
|[11](iterations/11/)|0|Replace blurred 512px normalized color detail with1024px linear-light reference reflectance ratios, retaining the actual worked-metal marks. Keep even roughness and zero normal maps; geometry and all IDs unchanged. App: actual3D verified; white0/1249. Original assets restored and full repo status clean. See app metrics and restoration evidence.|
|[12](iterations/12/)|0|Keep11 reference-derived1024px color texture; change only plate roughness0.49→0.40 for sharper physical metal reflections. Geometry, normals, colors, border satin finish and all IDs unchanged. App: actual3D verified; white0/1249. Original assets restored and full repo status clean. See app metrics and restoration evidence.|
|[13](iterations/13/)|0|Keep12 plate finish and1024px reference texture; lower broad frame tint0.245→0.175 and outer tint0.225→0.190 to remove pale-white-outline appearance. Satin border roughness0.40, geometry, normals, IDs and plain reflection region unchanged. App: actual3D verified; white0/1249. Original assets restored and full repo status clean. See app metrics and restoration evidence.|

Rejected preflights remain in reports/preflight folders; Silver07 failed tone checks before installation. Silver11 is an import diagnostic: its screenshot is pixel-identical to10, disproving the fallback-scalar hypothesis. Experimental Iron normal/roughness maps were rejected for pebbling; the final contains neither.

## Materials

All IDs remain unchanged from the first shape. Colors are linear RGB; mapped roughness takes precedence over its fallback scalar.

|Name|Linear RGB|Metallic|Roughness fallback|Maps|
|---|---|---:|---:|---|
|`Iron2_PlateLeft_Satin`|[0.05, 0.0488, 0.0464]|1.0|0.4|{'diffuseColor': 'Iron2_PlateLeft_Satin_color.png', 'roughness': 'Iron2_PlateLeft_Satin_roughness.png'}|
|`Iron2_Reveal_Satin`|[0.21, 0.203, 0.19]|1.0|0.4|none|
|`Iron2_Border_Satin`|[0.175, 0.17, 0.161]|1.0|0.4|{'diffuseColor': 'Iron2_Border_Satin_color.png', 'roughness': 'Iron2_Border_Satin_roughness.png'}|
|`Iron2_PlateRight_Satin`|[0.05, 0.0488, 0.0464]|1.0|0.4|{'diffuseColor': 'Iron2_PlateLeft_Satin_color.png', 'roughness': 'Iron2_PlateLeft_Satin_roughness.png'}|
|`Iron2_PlateEdge_Satin`|[0.05, 0.0488, 0.0464]|1.0|0.49|none|
|`Iron2_Back_Satin`|[0.05, 0.048, 0.045]|0.95|0.48|none|
|`Iron2_Outline_Satin`|[0.19, 0.184, 0.173]|1.0|0.4|none|
|`Iron2_Channel_Satin`|[0.035, 0.033, 0.03]|1.0|0.5|none|
|`Iron2_Lip_Satin`|[0.19, 0.183, 0.17]|1.0|0.4|none|

Finish recipe/evidence: [settings](settings.json), [texture manifest](reports/finish_maps.json). Maps are512px for Silver and1024px for Iron. Silver star ramps run ridge→outer valley, shaded faces0.34→0.37; lit per-plane values are in the recipe. Iron body roughness is uniform within each map and border roughness0.40.

## Explicit reference exceptions and limits

The owner-requested standalone references use updated AGENTS§2B instead of frozen coin shells/names. Shape-specific IDs deliberately avoid app coin-material overrides. Both body envelopes remain0.65thick; outlines remain satin. The laurel has rolled/cylindrical leaves and stems rather than the shield’s layered frame, an existing reference-specific outline-profile exception. Silver’s thin decorative stems/leaf tips/open wreath override the0.6minimum-feature and filled-silhouette wording; the shield tip/thin border likewise preserve the requested source silhouette. Curved leaves/stems/shield are not claimed to be flat gem planes.

Texture likeness requires the source’s finer1–2screen-pixel forging/scuff marks: this explicitly overrides the standing3–4pixel texture-mark minimum for this reference. Fine detail is bounded color variation only, with filtered sampling; no normal or roughness grain can amplify it into specular sparkle. No new dents are invented or disguised as geometry. The lowest fifth remains deliberately clean for the reflection, so that region is smoother than the reference.

The reference images have different studio lighting from Home. These are functioning physical metallic assets, not a baked image copy; exact highlight locations differ. The app still draws the old coin-width contact-shadow line beneath these floating shapes; this is the accepted AGENTS§7.3 limitation and app code is untouched. Reviewed in the simulator, not on a physical phone. Stills include1080px,360px and120px/40pt@3x with6.03units spanning108of120pixels.

Final full app `git status --porcelain` is empty; both original assets, HEAD and seven protected sources are unchanged. [Restoration proof](../proof/repo_final.json).
