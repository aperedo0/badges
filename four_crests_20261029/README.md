# Four finished badge crests

All four models are saved and reviewed in the separate **Badge Studio Preview** simulator. Open **Choose badge** on Home to select Frostwing Crystal, Battle Steel, Lunar Compass or Celestial Orbit. Celestial Orbit is selected, and its selection was verified after reopening without launch arguments. The production app was not changed.

[Native preview sheet](all_four_native.jpg) | [Reference comparisons](all_four_comparisons.jpg) | [Verified model manifest](deliverables.json)

| Badge | Final USDZ | Editable source | Evidence and notes |
| :--- | :--- | :--- | :--- |
| Frostwing Crystal | [Model](frostwing/mobile/frostwing_badge_mobile.usdz) | [Blender scene](frostwing/source/frostwing.blend) | [Report](frostwing/REPORT.md) |
| Battle Steel | [Model](battle_steel/mobile/battle_steel_badge_mobile.usdz) | [Blender scene](battle_steel/source/battle_steel.blend) | [Report](battle_steel/REPORT.md) |
| Lunar Compass | [Model](lunar_compass/mobile/lunar_compass_badge_mobile.usdz) | [Blender scene](lunar_compass/source/lunar_compass.blend) | [Report](lunar_compass/REPORT.md) |
| Celestial Orbit | [Model](celestial_orbit/mobile/celestial_orbit_badge_mobile.usdz) | [Blender scene](celestial_orbit/source/celestial_orbit.blend) | [Report](celestial_orbit/REPORT.md) |

## Appearance and checks

Built and inspected in the live Blender application with sculpted fronts, matching rears, closed walls and separate faceted crystal details. Native simulator review includes front, rear, both sides, 4x outline crops and a slow complete turn. The silver and bronze have physical reflections that move in the existing studio light. Measured appearance maps preserve the reference finish and fine surface details. The source images define the front appearance; this is a close 3D interpretation, not a claim of identical rendering at every angle.

All files pass closed surface, identity transform, Y up, unit scale, frame bounds, material UV and ARKit USD checks. The models sit at the shared floating height. Detailed contour and rear geometry use about 84,000 to 111,000 triangles and 8 to 10 MB each, above the usual mobile size guidance to retain the requested detail. Each report records the exact counts and evidence.

## Preview and rebuilding

The private project is `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. It has four independent menu entries and assets. `private_preview_entries.patch` records only these new menu and neutral placement entries. `install_preview_asset.py KEY` copies the selected candidate into that existing private project. Final model hashes match the installed private asset files.

The work uses `/tmp/crest_image_env/bin/python` for image and geometry preparation, live Blender through `water_match_20261014/blender_live.py`, and Blender's bundled Python for USD packaging. Sources are in each complete packed Blender scene. `design.json` preserves editable feature locations and depth choices. The full run helpers remain here for rebuilding; do not regenerate a design file after editing it by hand. A material recalibration requires a visibly loaded native badge, never a launch screen.

`record_turn.py` uses fine touch spacing and native simulator video so every angle is captured. The overnight run has no overall time limit. This run ended because all four badges were reviewed and complete; its recovery timer stopped. The saved schedule and checkpoints retain the work history.
