# Silver 2 — original-studio finish options, 2026-10-08

Recommended no-border candidate: **33**. Optional outer-border candidate: **34**, visually closer to the mock outline, with the tone-gap limitation below. Ten numbered candidates25–34 were tested in the real app; stop at the requested cap. **Final24 is still the current final and remains installed. No proposal has been promoted.**

All earlier ring-lit app pictures and brightness numbers are stale. Current original-studio baseline24: white1034, darkest star mean22.353, minimum adjacent gap15.512. Iron2 was not changed: one fresh app screenshot, white0 against its normal1249 cap, real3D/floor gap/reflection confirmed. Legacy coin-region measure outputs are included but are inapplicable to these shapes.

## What changed

One float64 affine color ramp per star plane, plus a gentler longitudinal leaf ramp. Each star has one monotone ramp; no bowls, internal bands, painted spots or normal maps. The final star ramp endpoints are0.72 and1.28 of its plane reflectance (roughly30% perceptual brightness span); each leaf is0.94–1.06. Slight cream lit/cool blue-grey shaded tones and per-plane polish/reflectance make the lower faces read as metal under the original studio. Existing final24 brushing amplitudes are unchanged: star0.055, leaf0.14, roughness0.001.

Independent texture islands with12-pixel padding remove interpolation seams. This changes UV mapping, never geometry positions/normals. Shared shaded-material leaf backs sample a plain island; all leaf-front UVs are byte-identical to24. Actual packed512px PNGs equal the checked external textures. Float64 NPZ authoring fields and 8bit-map precision records are delivered; final visible-plane red channels retain32–61 or more distinct levels, with bilinear interpolation. No dither or new grain.

34 adds only a half-round bead on the **outer star outline**, radius0.030, width0.060 (~4 native pixels; the bright line is narrower). No geometry on inner ridges. It uses the already-existing `Silver2_Outline_Satin` material; the same finish maps as33 are byte-identical. All original vertices/triangles/custom normals are retained exactly as prefixes. It introduces a binding subset `Silver2_Star_Satin/Material_6`; no existing object/mesh/material name changes, additions or removals.

## App results and the remaining limitation

Every candidate received real-app install/build, three launches with15-second waits, actual-3D visual review, whole-badge/face/leaf/floor crops, and a finally restore of exact24 bytes. Source, environment, other assets and HEAD matched the fresh starting fingerprints after each test. See each numbered folder's app_restore_verification.json, app_validation_metrics.json, app_plane_metrics.json and build proof logs.

33 passes the real-app thresholds: white1176<=2000; every star plane mean>=52.211 (required30); minimum adjacent gap28.758 (required25). No visible seam, grain, fold, wide inner glint or extended halo at Home size. The broad star planes are truly flat; leaves retain their curved shine. The floor gap and smooth matching reflection remain intact.

34's legacy fixed triangle masks report white1018, darkest58.333 and gap28.313. Those masks include some of the new border. **With actual projected bead triangles given separate ID11 and removed before the four-pixel flat-plane erosion, the minimum gap is20.577 between planes8/9; darkest54.588. Thus34 is not claimed to pass the25-level requirement.** Both raw and corrected ID masks/measurements are kept. The app's sampled outer highlight has ordinary staircase pixels at4x nearest zoom and a small tip glint; it looks continuous at Home size, with no extended halo.33 has the cleaner outline.

The mock still has brighter, larger soft reflections and more pronounced rolled leaf/outline edges. Several of its star faces are near239–246 mean, versus about196–209 for33's brightest faces. The frozen app environment, fixed normals and allowed highlight range constrain that match; the model does not supply its own lights. These options are the closest tested within ten attempts, rather than a claim of identical rendering. Gentle fixed ramps do not track the light during entrance spin, as explicitly authorized.

## Every iteration

All numbered USDZs pass ARKit, reimport, frame/names checks and ten-plane normal delta0. App status below includes the stricter tone requirements;27 still had a sampling seam,28–30 retained unintended shared back sampling before31 corrected it. Raw stage/point-light smoothness is reported, not mislabeled as the untextured silver threshold.

| Candidate | White /2000 | Darkest true mean /30 | Min true gap /25 | Stage RMS /edge | Point RMS /edge | App numbers |
|---|---:|---:|---:|---:|---:|---|
| 25 | 1089 | 21.754 | 10.153 | 1.468 /47.065 | 1.052 /45.583 | FAIL |
| 26 | 1144 | 45.994 | 10.235 | 1.722 /45.236 | 1.273 /45.056 | FAIL |
| 27 | 1164 | 37.009 | 25.422 | 1.630 /45.740 | 1.182 /45.388 | PASS |
| 28 | 1154 | 37.063 | 25.470 | 1.571 /41.153 | 1.064 /39.398 | PASS |
| 29 | 1057 | 37.063 | 7.924 | 1.761 /43.549 | 1.176 /43.804 | FAIL |
| 30 | 1154 | 52.204 | 22.582 | 1.470 /38.372 | 1.108 /39.401 | FAIL |
| 31 | 1154 | 52.204 | 22.582 | 1.470 /38.372 | 1.108 /39.401 | FAIL |
| 32 | 1061 | 52.204 | 22.618 | 6.672 /33.070 | 6.961 /41.863 | FAIL |
| 33 | 1176 | 52.211 | 28.758 | 1.460 /38.354 | 1.100 /39.440 | PASS |
| 34 | 1018 | 54.588 | 20.577 | 11.889 /14.045 | 14.337 /20.845 | FAIL |

## Geometry and export checks

The frame is unchanged from24: bounds X[-3.0150001,3.0150001], Y[-2.4549999,2.3673847], Z[-0.32499999,0.32499999]; width6.0300002, height4.8223846, thickness0.64999998, bottom-floor gap0.4400001. Y up,1 meter/unit, front+Z, no transforms, centered X/Z0, top below3.015. The float cut/silver coin shell check is N/A for these approved standalone shapes. USDZ contains only the shape and materials; no floor, lights or reflection. The Blender proof scene's six original softboxes and constant world were inspected: no ring environment or ring light; the harsh proof uses the original eight-point test rig. The app studio hash is8967489eee1f7a29c6d319f7901e914f7676bc6d8a1a998db4004067293ffb37.

Ten flat star planes each have max custom-normal difference **0.0**; every original geometry point, index and normal is exact24. Leaves/stems are deliberately curved and retain their existing reference-driven exception to the minimum feature/thickness rules. The optional rounded border is separate curved geometry, explicitly requested. No polished-metal normal maps.

`usdchecker --arkit`: exit0, Success for every candidate (Apple USD emits existing duplicate Connectable registration diagnostics, not compliance failures). `shape_check.py`: all frame/name/normal/compliance checks pass. `reimport_check.py`: pass every numbered candidate. `compare_finish.py`: all original geometry/normal/name/binding IDs preserved; every texture/UV/optional-border difference recorded. `compare_usd.py`: complete comparison against the untouched shipped coin is delivered; expected standalone-shape geometry/IDs replace the coin, rather than attempting coin-shell equality. `precise_identity_check.json`: final original geometry and leaf-front UV identity, plain-back islands, names and package PNG byte equality pass. `verify_plain_finish.py`: world-UV leaf maps and the atlas plain island are constant in the lowest fifth; actual leaf-back routing additionally verified for33/34. The world-row test does not apply to a UV atlas.

Proofs: render_proof stage+point, physical per-plane ID mask and numerical tones, measure_smoothness, actual-app native per-plane mask overlay, full screenshot and nearest zooms, floor comparison, mock/app comparisons. Stage lighting is supplementary; real-app screenshots decide acceptance. Point-rig33 minimum gap24.926 satisfies AGENTS'10-level Blender check; the real-app28.758 satisfies this task's25. The Blender softbox stage has an8/9 gap5.273 and is not the app light. These discrepancies are kept visible.

Texture exception: ramps/brushing were requested. Raw residual RMS is above the untextured0.92/1.00 silver limits, so it is reported and visually checked, as section7 allows for requested textures. Legacy border masks also include the permitted curved bead and inflate RMS; corrected geometry ID masks yield stage1.231 /point1.044 for34. Original raw results remain in proof/smoothness.json, corrected in true_plane_smoothness.json. Edge-excess means remain below61.5/64.6. This mask correction never changes a render or hides a surface problem.

## Size and materials

Candidate33: 42,664 triangles; 3,213,478 bytes (3.213 MB); SHA256 `2f401f6c2bdab9df3bd7924d5a9dd629f43dee86e8a1968a47252b0d27ac9fb0`.

Candidate34: 43,832 triangles; 3,292,778 bytes (3.293 MB); SHA256 `e1dd5bedc2273b036c22b44e007dba520d2b367c5a472811ce24576bcd85eaac`.

Shipped silver baseline: 38,566 triangles, 3,511,448 bytes. Current24:42,664 triangles,3,073,529 bytes. Both proposals remain within2.5–4.5MB, eight512² PNGs.34 adds1,168 outline triangles.

| Material (IDs unchanged) | Linear fallback RGB | Metallic | Roughness |
|---|---|---:|---|
| Silver2_LeafLit_Satin | 0.390, 0.384, 0.372 | 1.0 | 0.32 |
| Silver2_Reveal_Satin | 0.300, 0.291, 0.273 | 1.0 | 0.4 |
| Silver2_StemsLit_Satin | 0.340, 0.330, 0.310 | 1.0 | 0.4 |
| Silver2_StarLit_Satin | 0.600, 0.592, 0.578 | 1.0 | 0.28 (per-plane map) |
| Silver2_StarShaded_Satin | 0.190, 0.200, 0.220 | 1.0 | 0.34 (per-plane map) |
| Silver2_Back_Satin | 0.160, 0.155, 0.146 | 0.95 | 0.45 |
| Silver2_Outline_Satin | 0.280, 0.272, 0.253 | 1.0 | 0.4 |
| Silver2_Channel_Satin | 0.100, 0.098, 0.092 | 1.0 | 0.45 |
| Silver2_LeafShaded_Satin | 0.270, 0.263, 0.248 | 1.0 | 0.32 |

Final per-plane roughness: {"2": 0.42, "4": 0.29, "6": 0.4, "7": 0.31, "8": 0.2, "9": 0.24}; remaining planes0/1/3/5 use0.34. Final mapped reflectance factors: {"0": 1.5, "1": 3.0, "2": 3.3, "3": 2.6, "4": 1.18, "5": 2.5, "6": 1.2}; top9 factor0.60, top0 additionally0.73. Exact color ranges and texture quantization are in atlas_precision.json; the fallback table is not a claim that the mapped surfaces are uniform.

## Rule exceptions and delivery

Owner explicitly requested fixed gentle ramps, subtle warm/cool tint, a2000 rather than1249 white cap, stricter app30/25 tone targets, and a separate optional rounded outer outline. All unaffected rules remain. Existing reference-specific open wreath/thin foliage/curved leaves exceptions are preserved. No existing names could not be kept. Texture UV layout changes are explicitly reported; original geometry remains exact.

Options live in `studio_revision_20261008/delivery/without_border/` and `with_border/`, with USDZ/textures/scenes/reports/proofs. Full ten-candidate records are beside them. Reference comparisons are `delivery/reference_vs_without_border.png`, `reference_vs_with_border.png`; combined `silver_2_studio_options.png`; full app pictures and floor comparison are there too. Current24 stays in mobile/ and is backed up in previous/studio_start24/. Prior ring-era report is preserved at previous/studio_start24/REPORT.md and its app values are stale.

The owner's pick is not installed yet. Final24 was restored after every test and rebuilt/reinstalled in the simulator at completion. Final git/status/fingerprint proof is in baseline/final24_restore_verification.json (PASS: status, HEAD and every starting fingerprint exact); preexisting owner changes remain. No app source, environment, Iron2 asset, original preview asset, branch or commit changes from this task.

Build proof: ScreenTime: ** BUILD SUCCEEDED **; ScreenTime-UIOnly: ** BUILD SUCCEEDED **; ScreenTime-UIOnly simulator: ** BUILD SUCCEEDED **. Tests skipped: presentation lane, no logic changed. Final24 screenshot badge/floor ROI max pixel delta0 versus fresh baseline. Self-review0–7 complete, with34's tone-gap limit disclosed.
