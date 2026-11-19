# Lower iron test

Scope: the existing Lab Chest Lower Rim below the approved wooden test plank. The owner restricted this round to the bottom portion. Wood rollout, feet, uprights, cuff, other iron and brass are outside this test. BC_final_polish remains the permanent provisional wood benchmark.

Starting Git checkpoint is 2ae680c. baseline.blend captures the complete live state after rendering finished. checkpoint_validation.json proves fresh restoration, exact wood geometry and all artwork required images packed. The unused empty owner_comparison.jpg image is not required by the artwork.

The selected candidate is 09_pitted_iron/master.blend. The selected finish combines sparse custom forming with official ambientCG Metal055A fine surface data and Metal003 pit data under CC0. TextureCan Metal 0009 was evaluated and rejected for a cloudy reflection. Sources and exact download links are in resources/SOURCES.json. Other official CC0 ambientCG maps were evaluated and remain cached. No paid tool, installation, image generation or AI reviewer was used.

final_surface.py retains the selected surface parameters and source fields. build.py reuses the baseline and changes only the target rim. sculpt_rim.py adaptively tessellates the existing closed surface with matching shared edges, adds small localized dents and edge chips, and protects anchors and rivet seats. The final sculpt keeps zero displacement contact coordinates exact. Earlier native normal strength trials remain documented in final_candidate.py. The secondary bump height and the sparse physical dents are independent, with no duplicated identical displacement. Numerical rest and deformation arrays are preserved beside the selected master. Material channels remain independent and editable.

render.py reuses the existing Cycles camera rig. It takes a single rendering mutex. batch.py runs deterministic jobs; IRON_FINAL=1 selects 1600 by 800 closeups and a 1400 square context at 64 samples. Context shaders and diagnostic lights are temporary and never saved into the model scene. Existing source lighting remains. present.py creates comparisons without stretching the images.

promote_live.py is guarded by the initial wood and rim geometry fingerprints and is for one use only. It saves live_before_iron.blend, swaps only the target mesh data, preserves reference and main framing, and shows the final closeup in an existing secondary render window. Do not rerun it on the changed mesh.

Read REPORT.md and the root PROJECT_STATE.md before continuing. The owner alone approves this iron test before any further transfer. Rejected scenes and intermediates remain locally cached; Git preserves the complete starting checkpoint, strongest editable scenes, source maps, numeric data, scripts and review evidence.
