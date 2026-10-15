# Current five coin models

One owner comparison: `~/Downloads/Coin badge previews.png`. Top row is the reference; bottom row is the unretouched Home crop. All use the wider flat raised rim and recessed face. The shared geometry is documented in `AGENTS.md` section 2.

| Badge | Current USDZ |
| --- | --- |
| Water | `water_match_20261014/clean/mobile/clean_badge_mobile.usdz` |
| Teal hourglass | `hourglass_match_20261014/hourglass_teal/mobile/hourglass_teal_badge_mobile.usdz` |
| Gold hourglass | `hourglass_match_20261014/hourglass_gold/mobile/hourglass_gold_badge_mobile.usdz` |
| Sunrise | `botanical_match_20261014/sunrise/mobile/sunrise_badge_mobile.usdz` |
| Emerald sprout | `botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz` |

Each working folder retains its complete editable Blender scene, canonical geometry and fitted material maps. Its `REPORT.md`, structured build results and model validation record the real app checks. `pack.py <model name>` with Blender's bundled Python rebuilds from the saved geometry/maps; it does not need to rerun tracing or calibration. Geometry changes need a working copy, live Blender inspection and a fresh Home check.

Test context: separate simulator `Badge Coins Preview`, ID `85DF6D3B-6622-491A-8996-3ED0725DB273`, private project `/tmp/achievement_coin_app_20261014/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`. Sunrise is left on Home in the temporary Silver preview slot. The main app repo, installed production badge sources and other simulator were not changed. The private dataset and badge code were restored byte for byte after testing; the installed preview app retains the candidate.

All five USD checks and preview builds passed. Front/back/both side Home poses were visually checked at 4x. The full production three-scheme/test gate was not run for these external asset previews. Cold preview launches may show fallback art during shader compilation; warm relaunches displayed the actual 3D coins. Physical-device performance was not measured.

Remaining visual differences: Water's cyan is paler than its reference, and fine sand/metal grain is softened for phone resolution. Materials on these medallions use reference-fitted color/emission with real relief; the Diamond's separate live gem shader remains untouched.
