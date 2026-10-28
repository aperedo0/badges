# Emerald Trophy

Open **Badge Studio Preview**, then **Badge Studio**. On Home, **Choose badge** contains **Emerald Trophy** and the other saved badges. The reconstructed trophy is left selected facing forward. Scroll to see its matching back and metal sides.

The selected model is `mobile/emerald_trophy_badge_mobile.usdz`, and the editable complete scene is `emerald_trophy.blend`. Candidate07 copies the complete saved arrow background onto the reconstructed trophy, retaining the matched gold rim. `rim_comparison.jpg` shows that change in the app. `comparison.jpg` shows the reference beside the native Home view. `refinement.jpg` compares the previous and reconstructed models. Candidate07 contains the current pose checks and recording. `background_comparison.jpg` compares the arrow and trophy in the app. Previous delivered models remain in `previous/`.

The complete approved shell geometry remains unchanged. The owner requested rim finish now uses the trophy cup grain, warmer gold and smoother reflections. The green field uses the exact Emerald Archer maps and finish. Floating placement is size 0.96 and lift 0.56, putting the lowest world point at minus 2.455. The rim width is unchanged.

Rebuilding uses the saved reference and the live Blender connection:

1. Run `trace_reference.py` with the image Python environment. It traces the contours, constructs curved relief and folded sheet depth, defines real gem facets, and creates neutral calibration maps.
2. Run `build_traced_live.py` through `water_match_20261014/blender_live.py code`, then package with `pack.py candidate05` using Blender's bundled Python. Install only in the separate preview, build, and capture a native front view as `candidate05/app_calibration.png`.
3. Run `solve_reference.py`, followed by `finish_reference.py`, with the image Python environment. These fit the reference surface maps to the app measurement and apply the selected reference dominant finish.
4. Run `apply_reference_finish.py` through the live connection to save the complete colored Blender scene. Package with `pack.py candidate05`, then run `validate.py candidate05` using Blender's bundled Python.
5. Copy the result into the private preview's `Badge3DPreviewEmeraldTrophy.dataset/coin.usdz`, build and run that private project, then use native captures and `review_reference.py` for the comparison and outline review.

The image Python environment is `/tmp/archer_image_env/bin/python`. Blender's bundled Python is `/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I`. Temporary geometry is rebuilt in `/tmp/emerald_trophy_20261025`. The final scene contains its own packed maps and can be opened independently of that temporary directory.

The private project is `preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`, simulator identifier `DF439C70-9FD7-4EF7-998E-43AF5F83A588`. Launch arguments `-hasCompletedOnboarding YES -CoinBadgePreview emeraldTrophy` select this badge. `setup_preview.py` can reconstruct the separate preview if it is lost; do not run it over private work you need to retain. The production application repository was not written by this task.

To rebuild the selected rim finish from candidate05:

1. Run `prepare_rim_match.py` with the image Python environment, then `pack_rim_match.py` with Blender's bundled Python. The packer verifies that the crest, geometry, UVs and all other maps remain identical.
2. Run `rim_match_live.py` through the live Blender connection to save the complete matching scene. Run `validate.py candidate06` with Blender's bundled Python.
3. Install the candidate06 model only into the private preview data set, build and run, then capture with `capture_rim_match.py` and compare with `review_rim_match.py`.

To reproduce the exact arrow background from candidate06, run `match_arrow_background.py` with Blender's bundled Python. It copies the complete saved arrow field material and both native USD field meshes. Run `match_arrow_background_live.py` through the live Blender connection to create the complete editable scene. Validate with `validate.py candidate07`. Install only in the private preview, then capture using `capture_background_match.py` and compare using `review_background_match.py`.
