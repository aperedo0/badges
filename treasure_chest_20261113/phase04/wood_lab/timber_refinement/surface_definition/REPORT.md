# Selected wood refinement

AW_depth_hierarchy/master.blend is the current best editable checkpoint, saved and loaded in the owner Blender. Existing reference, owner comparison camera and screen layout remain. AE is preserved in baseline.blend and live_before_selection.blend; the original AE file remains byte identical.

## What the rendered comparisons support

The body formations remain longitudinal and have more continuous raised faces. Flow aligned organization connects short interruptions and trims isolated bumps in the medium field. A separate pass aligns crosswise secondary modulation with existing grain, keeping the finer source band. The actual mesh curvature selects rounded raised faces for a continuous profile correction. This reaches the composed geometry that the older structural only mask largely missed. Primary fracture positions and boundary contact regions remain protected.

The knot has a solid core and clearer existing near vertical split. Its internal natural growth and fine fibers use cached healthy wood data. Synthetic patterns that looked like fingerprints, smooth vertical patches, or engraved curves were rejected. The source knot crop was widened after inspection showed that the smaller crop mainly contained damaged pith. Its main defect is excluded from relief, although the residual inner contour is still different from the reference.

Body pigment and roughness outside the core are pixel identical during the organization passes from AI to the selected result. Changes in those body comparisons therefore come from relief and normals under the same light. Core color and roughness remain independently authored from the corresponding cached source channels. Material maps are 4096 by 1536, all packed; normal strength remains one. The wood is nonmetallic, IOR 1.46. No extra polygons or displacement shader was introduced. Full float32 height and geometry height remain editable.

A neutral diagnostic showed how much warm illumination affects the orange appearance. The selected softer warm RGB light retains light positions and sizes; energies approximately preserve the previous emitted luminance. This is an artistic lighting choice, not a reconstruction of the original image lighting. Exact selected values are recorded in lighting_softwarm.json. Exposure and AgX Medium High Contrast are fixed across the controlled comparisons.

## Review images

owner_reference.jpg shows the original and selected chest normalized by projected chest width, without stretching either image. Temporary context materials are explicitly labeled. Only the existing lower test plank is refined; the remaining wood and hardware are placeholders for context. The stage floor is aligned to the existing feet only in the temporary contact context render. A dark camera only world background is used there; the illumination is retained. No surrounding material or transform from that render is saved into the live project.

owner_before_after.jpg shows the starting AE checkpoint and selected result with their respective comparison lights. controlled_organization.jpg holds the light and body material fixed. owner_close_views.jpg shows both bays; owner_plank.jpg shows the complete existing plank. knot_native.jpg and the full resolution PNGs beside the master preserve close detail. equivalent_scale_knot.jpg enlarges corresponding regions from the full chest comparison at the same overall chest scale; centers are approximately aligned without forcing identical knot dimensions. owner_window.jpg preserves the preceding AT Blender window, not the final AW. A final window capture failed; live_validation.json verifies the current AW scene through Blender directly.

All selected Cycles images were opened for visual inspection. Numerical fields were used for diagnosis, never as a substitute for artistic judgment. Approximate alignment and the mockup perspective cannot recover the reference object depth.

## Rejected trials and useful diagnosis

AG and AH establish coordinated fine surfaces and independent material controls. AI reconstructs the core boundary and source gradient normals. AJ creates visible vertical bands through independent column profiles and is rejected. AK organization is too subtle; AM better distinguishes short secondary recesses from major fractures. AN aligns only the crosswise middle band, retaining fine detail. AL polar fibers look like fingerprints. AO becomes too smooth and uniform. AP maps damaged pith too tightly. AQ widens the verified source crop; AR restores actual fine normal assisted fibers with geometry and material held fixed. AS corrects only the structural field and barely reaches many visible caps. AT uses actual mesh frames and was retained before the final hierarchy pass. AU traces the reference anatomy but reads as an engraving; it is rejected rather than retained for nominal shape similarity. AV extends correction onto channel shoulders, but the actual render shows no clear additional artistic gain; AT was retained before AW.

One duplicate background render queue was detected and stopped. A renderer lock and a cache check inside that lock now prevent repeated cached GPU work. Rebuildable geometry and normal frame intermediates stay cached locally. Complete editable masters and numerical source heights remain preserved.

## Preservation and limits

saved_validation.json verifies the original complete scene geometry, material graphs, transforms, parents and action names; other test scene mesh geometry, normals, UVs and material assignments; target topology, UVs, transforms and exact original boundary; closed mesh with two incident faces per edge; packed images and the shared single reference. live_validation.json verifies the actual active owner scene, local mesh and material, packed 4k maps, camera, Cycles and reference image editor. No original source rig or other component was edited. The saved complete checkpoint uses local data, with the unused append library stub removed.

The final width selective hierarchy pass AW is retained after close, right side and full chest draft inspection, followed by inspection of the completed final Cycles renders and equal chest scale comparison. It uses persistence across the grain to reduce the depth prominence of narrow secondary channels, preserving their positions and the fine source band. It does not modify the independent primary fracture layer or core. AT remains a complete previous checkpoint, with an immediate preselection copy in live_before_AW.blend.

The result is unapproved. Some broad formations remain rounder and smoother than the reference, and the knot pith contour is not an exact match. The surrounding chest is unfinished by design at this stage. No similarity score, exact light match or measured reference relief is claimed. The owner decides the next work.

## Sources and continuation

No new download, installation, paid asset, API or subagent was used. Cached official Poly Haven raw_plank_wall displacement, diffuse, roughness and normal data are CC0. Provenance and license links remain in final_fibers/resources/SOURCES.json, including https://polyhaven.com/a/raw_plank_wall and https://polyhaven.com/license. Standard NumPy, SciPy, Pillow and Blender perform the deterministic local processing.

Read PROJECT_STATE.md first in a later conversation. Use the selected mesh and numerical height as the foundation. Do not repeat the rejected profile or core methods, import another reference, start another chest or transfer to other planks without owner direction. The source guarded promotion helper is for the recorded baseline and should not be rerun on the selected live mesh.
