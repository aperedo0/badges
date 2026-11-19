The 28 changed badges keep their approved appearance with fewer separate drawing parts. Meshes decrease from 363 to 170, and material sections from 510 to 194. The same 1,706,616 triangles remain. Combined model size changes from 142.44 MB to 93.21 MB.

All 35 distinct current gallery models were inventoried against the private preview and production assets. Six existing models remain byte identical. Five were already compact: Crimson Shield, Diamond, Mountain Crest, Platinum and Winged Sword. Steel already has two meshes; its trial changed native highlights, so it was rejected and its approved original was retained. Astral Navigator retains its approved 23 mesh final. Every other model now has at most 12 meshes.

The reviewed exports are in [mobile](mobile). Each changed badge also has its own mobile folder, a previous copy, a complete editable Blender checkpoint, validation, six native comparison poses, enlarged details and a full rotation recording. The original approved sources and all production assets remain preserved. The private Badge Studio Preview was updated with the optimized models.

The cleanup combines compatible material batches. It preserves every oriented triangle corner position, normal, named UV set and other vertex attributes, plus its effective material. Material graphs and texture file bytes are unchanged. The coin casing and inset prims are copied intact with their runtime names. Optical gems remain separate closed meshes; runtime logs confirm all 19 affected optical stones and their reflections received their gem shaders. No shared lighting, material tuning, placement or shader code changes were needed.

The originals were compared in the actual preview at matching scroll positions, with resting front, early turn, both sides, back and a slow complete turn. Complete pose pairs and focused rendering differences were inspected, including enlarged local differences. Full four times comparison images are retained for every pose. The Blender working copies were inspected live; their final standalone files were checked in an isolated background process to verify packed image bytes and restore unique canonical names. Original source camera conventions were retained. Incorrect picker captures were rejected and replaced after verifying the displayed badge title; gesture positions were measured to avoid comparing different angles.

This is object and material batching, preserving existing approved artwork rather than rebuilding its mockup. Existing polygon counts and texture resolutions deliberately remain unchanged. Some individual files grow slightly because their array layout changes, although the combined size falls. Emerald Trophy remains above 5 MB and Sapphire Stairway slightly above 5 MB to retain their approved detail. This reduces file and object overhead; actual iPhone frame rates and the unchanged optical rendering cost were not benchmarked.

Production integration is an asset replacement only. [exports.json](exports.json) maps each reviewed file and hash to its production target. There are 27 production replacements and one private only Original Iron variant. Do not substitute Original Iron for the production Iron badge, which is Crimson Shield. Existing placement and runtime material handling stay as they are. The separate simulator preview is installed; production integration has not been performed by this task.

Badge | Meshes before | Meshes after | Sections before | Sections after | Result
:-- | --: | --: | --: | --: | :--
Astral Navigator | 23 | 23 | 23 | 23 | Prior compact final retained
[Aurora Mountain](badges/aurora_mountain/REPORT.md) | 27 | 11 | 27 | 11 | Reviewed
[Battle Steel](badges/battle_steel/REPORT.md) | 8 | 5 | 8 | 5 | Reviewed
[Bronze](badges/bronze/REPORT.md) | 14 | 4 | 28 | 4 | Reviewed
[Bronze Phoenix](badges/bronze_phoenix/REPORT.md) | 7 | 4 | 7 | 4 | Reviewed
[Celestial Orbit](badges/celestial_orbit/REPORT.md) | 6 | 3 | 6 | 3 | Reviewed
[Copper](badges/copper/REPORT.md) | 3 | 3 | 9 | 3 | Reviewed
[Crescent Ocean](badges/crescent_ocean/REPORT.md) | 5 | 4 | 5 | 4 | Reviewed
Crimson Shield | 6 | 6 | 6 | 6 | Already compact, retained
Diamond | 1 | 1 | 1 | 1 | Already compact, retained
[Ember Forge](badges/ember_forge/REPORT.md) | 33 | 7 | 36 | 7 | Reviewed
[Emerald Archer](badges/emerald_archer/REPORT.md) | 17 | 9 | 19 | 11 | Reviewed
[Emerald Sprout](badges/emerald_sprout/REPORT.md) | 22 | 9 | 42 | 11 | Reviewed
[Emerald Trophy](badges/emerald_trophy/REPORT.md) | 7 | 4 | 9 | 6 | Reviewed
[Frostwing Crystal](badges/frostwing_crystal/REPORT.md) | 8 | 6 | 8 | 6 | Reviewed
[Gold](badges/gold/REPORT.md) | 21 | 4 | 24 | 4 | Reviewed
[Golden Sands](badges/golden_sands/REPORT.md) | 22 | 9 | 42 | 11 | Reviewed
[Island Sunset](badges/island_sunset/REPORT.md) | 11 | 6 | 13 | 8 | Reviewed
[Lightning Compass](badges/lightning_compass/REPORT.md) | 5 | 3 | 7 | 5 | Reviewed
[Lunar Compass](badges/lunar_compass/REPORT.md) | 7 | 4 | 7 | 4 | Reviewed
Mountain Crest | 3 | 3 | 3 | 3 | Already compact, retained
[Original Iron](badges/iron/REPORT.md) | 17 | 11 | 19 | 11 | Reviewed
Platinum | 1 | 1 | 5 | 5 | Already compact, retained
[Ruby Winged Crest](badges/ruby_winged_crest/REPORT.md) | 11 | 9 | 11 | 9 | Reviewed
[Sapphire Stairway](badges/sapphire_stairway/REPORT.md) | 14 | 12 | 14 | 12 | Reviewed
[Silver](badges/silver/REPORT.md) | 6 | 6 | 16 | 6 | Reviewed
[Star Ascent](badges/star_ascent/REPORT.md) | 7 | 4 | 9 | 6 | Reviewed
[Steel](badges/steel/REPORT.md) | 2 | 2 | 4 | 4 | Original retained after native review
[Sunrise Path](badges/sunrise_path/REPORT.md) | 24 | 5 | 46 | 7 | Reviewed
[Teal Sands](badges/teal_sands/REPORT.md) | 22 | 9 | 42 | 11 | Reviewed
[Tidal Compass](badges/tidal_compass/REPORT.md) | 17 | 6 | 20 | 6 | Reviewed
[Torch Sunburst](badges/torch_sunburst/REPORT.md) | 5 | 3 | 7 | 5 | Reviewed
[Water Drop](badges/water_drop/REPORT.md) | 12 | 7 | 22 | 9 | Reviewed
Winged Sword | 3 | 3 | 3 | 3 | Already compact, retained
[Zen Balance](badges/zen_balance/REPORT.md) | 5 | 3 | 7 | 5 | Reviewed

Validation and rebuild scripts are local to this folder. `compact.py` uses Blender’s bundled USD Python and the preserved baseline files. `blender_prepare.py` and `blender_review.py` use the live add on; `check_blender_files.py` finalizes only the standalone working copies. `install_preview.py` installs validated copies into the private preview. `capture.py` requires the intended badge to be visibly selected first, and checks the cached file hash as well as the actual scroll pose. The production application is never written by these scripts.
