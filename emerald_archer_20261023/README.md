# Emerald Archer

The editable complete badge is `emerald_archer.blend`. The current model is `mobile/emerald_archer_badge_mobile.usdz`. The previous finish is preserved in `previous/` and candidate01. Both numbered candidates contain their own models and source scenes.

In the simulator named **Badge Studio Preview**, open BestSpent, then Home, then **Choose Badge**, then **Emerald Archer**. This is the existing separate preview app, with its own project at `/tmp/achievement_coin_app_20261014/ScreenTime.xcodeproj`. No production app assets or code were installed or edited by this task. The older Badge Coins Preview simulator remains available with its data preserved. The fresh simulator has identifier `4EFF2D4A-6118-4EDC-ABD2-648E8C3364D1`.

The separate preview adds one picker entry and data set. `preview_picker.patch` records those changes. It also gives this entry up to 90 seconds to finish its first frame under heavy host load, instead of switching permanently to flat art after six seconds. That wait is confined to this entry in the private debug preview. Existing lights, floor, image processing, rim anisotropy, glint shield, and other badges retain their rendering.

Placement is size 0.96 and lift 0.56. The complete circular shell spans Y from minus 3.015 to 3.015. Its world bottom is minus 2.455. This model must use the floating coin placement.

The shell geometry, UVs, normals, material graphs, fine brushing maps, and compact inner glint maps are copied exactly from Emerald Sprout. `validation.json` checks that preservation, the closed circular shell, matching sculpted back, identity transforms, Y up, meter units, finite normals, and absence of lights or cameras. The package also passes Apple's ARKit USD checker.

The 37 laurel leaves have a raised center crease and six modeled vein lines each. The bow has two sculpted swept limbs, repeated feather details, five gold emerald settings, and a matching back. The arrow has individual feather plates, four turned shaft collars, and a faceted green inlay in its swept head. Emerald materials use ordinary physical shading and a small color fill on the bright facets. They do not use the app's Diamond shader.

The final metal colors are uniform tones guided by the real Home lighting measurement. The field retains only subtle intrinsic fine grain. No broad studio light bands or artificial rim highlights are painted into these materials.

Rebuild with the installed Blender MCP add on connected:

1. Run `prepare.py` with Python containing numpy, scipy, and Pillow.
2. Run `build_live.py` through `water_match_20261014/blender_live.py code` to build the complete native scene and export mesh arrays into `/tmp/emerald_archer_20261023`.
3. Run `finish_materials.py` to regenerate the final uniform material maps. It copies the design metadata and field roughness from candidate01.
4. Run `update_materials_live.py` through the same live helper to save candidate02's complete scene with the final maps.
5. Run `pack.py candidate02` and `validate.py candidate02` with `/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I`. The packer uses native USD tooling and preserves the source shell.

`fit_materials.py` preserves the measurement method. Its initial spatial maps were reduced to uniform metal tones because the field developed cloudy patches. The final maps are reproducible through `finish_materials.py` without repeating the measurement.
