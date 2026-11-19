# Plank review checkpoint

Selected: ../AE_controlled_fibers/master.blend. Loaded in the owner Blender with the original reference retained. The owner requested this stopping point. No further artistic edits are running. Starting V is recoverable in baseline.blend and its untouched original directory.

## Evidence and selection

Unchanged material under a warmer front fill loses the previous cool right cast. Lighting alone leaves broad shoulders and internal faces too smooth. Existing raw, denoised and filtering controls from lookdev_evidence remain relevant. New coverage emission shows that detail masking covers most broad faces, so mask omission is not the main cause. Gray clay reveals actual relief but rounded primary profiles.

W was too quiet. X introduced scallops. Y added short broken fiber plates but left the core pressed and quiet. Z adds scanned weathered height; AA adds independent pigment and roughness using the same geometry, giving some richness but not enough internal structure. AB locally straightens channel shoulders, preserving centers, bottom depths, core outline and primary fractures. AC integrates a cached scan normal as a diagnostic; broad streaks and distracting highlights make it a regression. AD adds a stronger directional fiber hierarchy; actual renders show excessive busyness. AE reduces the new amplitudes and partially fills the core horizontal interruption, with independent chestnut pigment. AF recomputes absolute height shading against the actual mesh basis; no clear visual gain, so AE is retained.

All these comparisons were rendered with Cycles and actually opened for visual evaluation. The close comparison uses the established approximate planar correspondence. It cannot measure true depth or reconstruct unknown original lighting from one picture.

## Selected construction

Original U geometry and V material form the foundation. The numerical additions use grain flow from existing anatomy, irregular finite raised strips, multiscale small directional relief and localized compressed core fibers. Primary fracture locations remain. Only the existing grid vertices move; original source vertices and contact boundary are fixed. Complementary normal detail is projected into the actual updated mesh tangent basis, retaining original boundary normal pixels. It does not add a second copy of displaced structure. Material properties remain independently editable.

Normal strength stays one. Packed color, roughness and normal maps remain 2048 by 768. Main source height is high precision numerical data, not a low precision PNG displacement. Dielectric wood remains metallic zero, IOR 1.46. No additional polygons, subdivision modifiers, displacement shader or new focal knot.

Isolated fill changes to warm frontal illumination; key and rear remain V. Other chest components, including original materials and rig, are not edited. Dark iron, brass and surrounding wood in the full context image are temporary background render proxies, not live material assignments.

## Review images

owner_window.jpg is the actual Blender window. owner_comparison.jpg shows reference, baseline and selected with their respective starting and final lights. The separate lighting_comparison.jpg holds the material constant to isolate the fill change. The live Blender view shows both exposed bays. The owner requested the saved stopping point before the final whole plank and temporary full context rerenders finished; those jobs were stopped. The completed 2400 by 1776 close render remains beside the selected master and covers the knot and left bay. right_balanced.png shows the right bay independently.

## Limits

The match remains unapproved. Broad shoulders are still rounder than the reference; the core has less dense broken endgrain and a different internal outline; some orange response remains more uniform. The horizontal core interruption is reduced but remains visible. Temporary context materials are only representative. No exact lighting match or inferred physical reference dimensions are claimed. Owner judgment is the next action.

## Resources and recovery

Official Poly Haven sources and CC0 licensing are recorded in resources/SOURCES.json. Cached medieval_wood and raw_plank_wall data were inspected and adapted; no paid asset, API, extra subscription or image generation was used. Reusable processing uses the existing temporary Python environment and native Blender. No subagents or AI reviewers were used.

Checkpoint, design parameters, full height, surface height, normal frames and material maps remain editable. Scripts are deterministic and preserve source geometry. The final saved checkpoint is checked by validate_final.py; saved_validation.json records its result.
