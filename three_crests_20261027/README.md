# Three reference crests

Open **Badge Studio** in the **Badge Studio Preview** simulator. On Home, choose **Choose badge**, then **Crescent Ocean**, **Mountain Crest**, or **Winged Sword**. Scroll the list if needed. Slowly scroll Home upward to turn the badge. Scroll back to the top for its front.

The final USDZ and complete Blender source for each badge are in its named folder. Each folder also contains a short report, the reference comparison and every side in the simulator. `three_badges.jpg` compares all three references with the native preview at matching sizes.

These are sculpted relief models with finished backs and continuous side walls. Their polished metal now has moving reflections and glints from the unchanged studio light. Reference fill preserves the fine marks and front colors, balanced against measured physical reflections in the native app. The reports record file sizes and material limitations.

The separate preview project is at `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. The original production repository was not edited. `private_preview.patch` records the three new menu entries and their placement in the private copy.

Rebuilding requires Blender 5.2 with the live MCP add on at local port 9876, its bundled Python with USD, and a Python environment with NumPy, Pillow and SciPy. The reference images, geometry, finish maps, source scripts and the exact AgX cube used for matching are kept here. `display_transform.py` uses the saved cube. The candidate selection is in each badge's `candidate.txt`, defaulting to `candidate01` when absent.

Run `build_reference.py NAME` and `finish_maps.py NAME` with the image Python environment. The trace prepares continuous side normals, and the crescent finish also builds its separate planar compass. Run `rebuild.py NAME` with the normal Python environment and the Blender application open. It builds through the live connection, saves all five Blender views, packages with Blender's USD Python, validates and copies the candidate into the private preview source. Use XcodeBuildMCP to build and run that private project. `capture_poses.py` saves native screenshots, `turn_swipe.py` performs the full rotation during a recording, and `review.py` makes the equal scale comparisons. `deliver.py` promotes verified candidates.

The owner requested 30 minute work blocks separated by 20 minute breaks. `schedule.json` records the current block. The temporary recovery timer checks this chat and internet connectivity every 10 minutes, queues a continuation after a stall and respects the breaks. It ends when `COMPLETE` exists or the five hour window expires. `recovery_timer.jsonl` records its checks.

For the moving metal finish, preserve the approved candidate and run `prepare_metal.py NAME` with the image Python environment. It prepares the real metal colors, polished roughness and smooth reflection normals. Build that candidate through `rebuild.py NAME`, then build the private preview and use `capture_front.py NAME` to save `app_calibration.png`. Run `fit_metal.py NAME` with the image Python environment, rebuild, and check the front, spin, back and sides in the simulator. `capture_glints.py NAME` saves additional early spin poses. The original approved materials are kept in each new candidate's `approved_textures` folder.

Review the moving finish in [the spin preview](metal_glints.mp4), [the turning poses](metal_glints.jpg), and [the approved front comparison](metal_front_comparison.jpg).

The sword and moon refinements are compared in [the resting and turning views](sword_moon_fixes.jpg), with [an enlarged moon surface comparison](moon_surface_detail.jpg). The sword keeps moving glints but uses broader, gentler reflections. The moon removes the false horizontal fold where the old wave height began abruptly. Their previous models remain in the respective `previous` folders. The mountain finish is unchanged by this refinement.
