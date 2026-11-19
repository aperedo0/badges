# Test plank review

The strongest current result is wood_master.blend, open in Blender on Test plank master. Only the existing lower front plank is refined. The original editable chest, rig and reference remain in Chest Complete Form Phase 1. Draft candidates remain in comparisons.blend. This is a test for owner judgment, not a finished chest or an exact reference match.

## What changed

The plank now has real recessed surface geometry, localized fractures and chips, an irregular knot check, and complementary fine tangent normals. A closed, stitched mesh replaces the copied front surface. Its 1.28 million triangles are appropriate for an editable master; optimization is separate. Maximum recession is about 0.0398 Blender units across the 1.298 unit planar board height. Every new front vertex is at or behind the original front plane, preserving hardware clearance.

Pigment no longer paints every recess nearly black. Broad chestnut color, age stains, fine scanned fibers, roughness and relief have separate controls. The geometry carries the low frequency height; normals carry only its complementary high frequency detail. A missing band between the earlier mesh and normal resolutions was corrected. Coordinated maps remain 2048 by 768, with float height data and a 16 bit diagnostic height image.

The scanned material alone was too quiet for the reference. Direct reference height reconstruction created false pits and seams. The custom growth channel test was too regular. The current result keeps the more irregular existing anatomy and adds restrained natural fine data from Poly Haven Rough Wood.

## Pictures

review/wood_review.jpg: original reference, baseline and current close render.
review/neutral_before_after.jpg: unchanged lighting and framing.
review/whole_chest_review.jpg: full reference, current test and temporary color context.
review/relief_diagnostics.jpg: neutral, actual gray clay geometry and opposite key light.

Full resolution Cycles images are in final_renders. Temporary surrounding wood, iron and brass colors exist only during those context renders. The saved master keeps surrounding materials original. Cinema lighting is reference inspired, not a measured lighting reconstruction.

## Checks and limits

The saved file comparison verifies the original geometry, material graphs and packed maps, transforms, parents and rig action names at the same evaluated frame. All master edges have two incident faces, and the existing reference object is shared without duplication. See saved_validation.json and master_validation.json. Named close and full chest cameras are saved.

The result has substantially better physical depth than the baseline. Its grain is still rounder and more flowing than the reference, and the knot is still prominent. Crisp broken fiber terraces and lifted splinters need further artistic work if this direction is accepted. Single image height interpretation cannot uniquely recover real surface shape. No finished AAA quality or exact reconstruction is claimed. No material is transferred to another plank before owner approval.

## Free resources

Poly Haven Rough Wood: https://polyhaven.com/a/rough_wood
Poly Haven Wood Cabinet Worn Long: https://polyhaven.com/a/wood_cabinet_worn_long
Poly Haven license: https://polyhaven.com/license
TextureCan wood0034: https://www.texturecan.com/details/288/
TextureCan license: https://www.texturecan.com/terms/

Official CC0 maps and metadata are cached in resources, with SOURCES.json and original download URLs. No paid software, paid assets, additional API subscription, new image generation or subagents were used. See PROJECT_STATE.md for the compact continuation record and EXPERIMENTS.md for the draft findings.

Downloaded cache maps, duplicate Blender backup files and verbose logs stay local and are excluded from Git. Sources, editable models, authored maps, validation records and review images remain available for versioning.

All nine requested final views completed in Cycles. The reference, baseline and current close views, full chest views, temporary color context, clay grazing view and opposed key view were opened and visually inspected. The clay view confirms genuine geometric relief. The opposite key changes the ridge highlights and shadows as expected. Both also expose the remaining rounded grain shape; numerical validation does not remove that artistic gap.
