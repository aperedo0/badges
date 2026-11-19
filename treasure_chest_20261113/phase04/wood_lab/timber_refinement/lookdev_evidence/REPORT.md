# Wood refinement for owner review

The saved candidate is ../V_lookdev_refinement/master.blend. The owner reviews it. No AI reviewer or subagent was used. The latest U version and the initial live window are preserved. No other plank, hardware material, original rig or geometry changed.

## What the controls showed

The prior key light was almost parallel to the board. Moving only its direction revealed considerably more of the existing fibers and knot interior, but over lit the wood. A smaller source strengthened recess shadows. The selected light then reduces key power and uses a warmer color for a more comparable copper response. Camera, exposure and AgX look remain fixed in the close comparisons. This is a reference inspired light setup, not an exact reconstruction of the reference lighting.

The raw and denoised views come from the same 128 sample render. Raw retains slightly more fine texture, but the same rounded ridge profiles remain. Denoising is not the main cause. See paired_denoise.jpg. A direct GPU render with denoising disabled hit a Metal compiler exception; the working paired method saves Noisy Image through a multilayer EXR and applies the same view transform when making its PNG.

An approximate tangent frame check compared the actual mesh normals with the current full height field. It found local fine band differences. The correction removes the broad component, works mainly on raised plates and the knot core, and preserves the original bevel and boundary normal pixels. The render shows a small local improvement. This is not a new grain design, a normal strength increase or an inference of physical depth from the reference. See normal_control.jpg and normal_sampling_diagnosis.json.

The narrower pixel filter produces only a minor change and does not recover the missing ridge structure. The standard 1.5 filter remains selected. Closest normal texture lookup also gives only small sampling differences and does not restore the missing layered structure. Linear sampling is retained. See pixel_filter_control.jpg and texture_filter_control.jpg.

The right side genuinely receives different light. Visibility samples behind the lock hit its case and backing, blocking the warm key while leaving the cooler fill visible. Farther right, more of the key is clear. The whole plank and right close view show existing fibers there. Those legitimate shadows were not flattened by new paint or geometry. The ray test samples hardware visibility from the front datum; it is not a total irradiance measurement.

## Selected material changes

Only the fine normal texture and a small region inside the existing knot change. The knot uses independently mapped cached diffuse pigment and roughness variation. Its mean roughness changes from about 0.645 to 0.621 within the core mask. Its outline, split and surrounding grain retain the same geometry. Albedo and roughness pixels outside that mask are exact copies of U. There are no new cracks, growth rings, knots, deeper displacement or extra polygons.

The largest visible gain is from illumination. Normal and local material changes are smaller. The reference still has crisper overlapping fibers, more varied broken edges and a denser looking knot interior. Some current ridge transitions remain rounded. Do not claim an exact match or a finished chest.

## Review pictures

owner_comparison.jpg: reference, preserved baseline and saved candidate close view.
owner_full_chest.jpg: reference and both complete chest views.
owner_plank_and_right.jpg: whole plank and the area right of the lock.
lighting_controls.jpg, balanced_lighting.jpg and warmth_control.jpg: unchanged wood under controlled light changes.
normal_control.jpg and core_control.jpg: local material controls with their lighting held fixed.
paired_denoise.jpg and the filter controls: rendering diagnostics.

Full resolution PNGs remain in ../V_lookdev_refinement and renders. Render settings and source fingerprints are recorded beside the images. The approximate plane rectification reuses the established comparison region; it does not prove exact mockup dimensions or depth.

## Preservation and continuation

saved_validation.json in the candidate folder verifies exact target geometry, topology, corner normals, UVs and material assignments, the complete original scene, other parts and materials, shared reference and packed final images. All U files remain byte identical. Geometry remains 641121 vertices and 643262 polygons.

The Blender reference image editor and rendered chest viewport layout are preserved. Review lights are independently owned by the isolated test scene. No source lighting, app, simulator, timer, paid resource, library installation or new image generation was used.

Reuse these scripts and cached maps. render_evidence.py runs the controlled light and normal trials. prepare_local_material.py writes the knot material variation; guard_normal_boundary.py preserves the bevel normals. save_candidate_live.py applies only from the verified U live baseline. render_final.py generates the saved views. validate_saved.py compares reopened files. These are stage specific scripts, not a command to rerun blindly on an already advanced scene.

Stop for owner feedback. Do not apply this material to any other plank or continue a new texture iteration before that review.

All selected final renders and control sheets were opened and visually inspected, including native crops. The selected views use the standard filters. V filter.png and texture_filter.png are diagnostics, not selected appearance changes. The owner is the only reviewer.

Live display confirmation: the MCP offscreen viewport capture returned black in Cycles. A capture of Blender's actual window confirms that the original reference editor and interactive rendered chest are both visible. See live_window.jpg. The display was not changed to a flat comparison picture. Use the native window capture helper if offscreen capture is black again.
