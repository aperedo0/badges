# Gold and Diamond badges

Created from the two supplied references and tested inside Home. Open **Gold_and_Diamond_in_app.png** for the actual Home renders or **Reference_vs_app.png** for matched-size comparisons. Full native app screenshots are in each `proof/app.png`.

- Gold model: `gold/mobile/gold_crown_mobile.usdz`.
- Diamond model: `diamond/mobile/diamond_crystal_mobile.usdz`.
- Editable Blender models and standalone USD sources with textures: each `master/` folder.
- Transparent fixed-Home-frame PNGs: each `stills/` folder.

The previews temporarily used Copper for Gold and Silver for Diamond because the new tiers have no 3D data sets yet. All original app assets and all 641 tracked files were verified unchanged after testing. The simulator retains the preview installation. ScreenTime-UIOnly: ** BUILD SUCCEEDED **.

Each badge report explains its geometry, checks and remaining visual limits. Numbered folders retain real app screenshots and reference comparisons. Existing approved models were preserved.

For editing, run `geometry.py` to generate meshes, then `facet_atlas.py` to repack the diamond's real faces. `solve.py <kind> candidates/<number> [candidates/<previous>]` measures native app lighting and solves maps; Blender runs `export.py -- <kind> candidates/<number>`. `optical_surface.py` derives the smoother final diamond material from the solved candidate 03 data. `agx.py` is copied unchanged from Silver 2. Gold's original calibration and first trial used a wider band opening; the final calibration measures the corrected smooth wall. Large diagnostic atlas NPZ files are omitted from this delivery and must be regenerated to rerun the solver. The editable masters and their textures are complete. App test scripts must always be followed by restoration and verification; they change only the two authorized temporary-slot USDZ files.
