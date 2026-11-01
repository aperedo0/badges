# Approved slimmer coin family

All 12 audited coins now use the dimensions the owner approved on Emerald Sprout: the rim band is 20 percent narrower from the outside, and the complete badge is 30 percent thinner through its depth. These are reductions from the original, applied once. Emerald Sprout itself retains the approved model byte for byte.

The shared casing has outer radius 2.896, inner radius 2.420, band width 0.476 and depth 0.651. Each existing emblem keeps its original width inside the rim. All relief depths follow the same 0.7 depth factor. Custom normals follow the changed geometry.

Every full coin was imported and inspected in live Blender, including its shell, front, back and both sides. The exported geometry matches the inspected Blender points. All 12 pass ARKit USD validation and closed casing checks. Material graphs, texture files, UV sets, topology and names are preserved. This deliberately supersedes the prior frozen dimensions with the owner's express approval.

The separate Badge Studio Preview was built successfully and every actual loaded model was verified byte for byte. Native screenshots cover the resting front, early turn, both side views, back and end of a slow full turn. The all coin front, early turn, back and side contact sheets were visually reviewed. The original studio, runtime materials and glint shield are unchanged. No unrelated badge asset or production app file was changed.

The preview placement is size 0.96 and lift 0.441 for these 12 data sets only. This retains the lowest world point at negative 2.455. Production integration must carry both the new model and placement; the patch is `preview_placement.patch`.

Each name has its preserved `original.usdz` and final `candidate01/` containing `mobile/coin.usdz`, `source/coin.blend`, native and Blender captures, and validation records. The reusable bare shell is `template/shell_template.usdz`, with geometry and dimensions beside it. `AGENTS.md` records this new standard. Old templates and earlier Sprout trials remain preserved.

Contact sheet order, left to right, top to bottom: Emerald Archer, Emerald Sprout, Emerald Trophy, Golden Sands; Island Sunset, Lightning Compass, Star Ascent, Sunrise Path; Teal Sands, Torch Sunburst, Water Drop, Zen Balance.

[All fronts](simulator_front.png) | [Early turns](simulator_early_turn.png) | [First sides](simulator_side_left.png) | [Backs](simulator_back.png) | [Other sides](simulator_side_right.png).

Rebuild with `family_prepare.py`, then `family_live.py` through the local Blender connection. Inspect the Blender captures before running `family_pack.py`, `family_template.py` and `family_install.py`. Use Blender's bundled Python for the USD and OpenImageIO scripts. The final install targets only the separate private preview.
