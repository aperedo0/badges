# Refined coin previews

[Updated comparison](</Users/antonioperedo/Downloads/Coin badge previews.png>): mockups above actual Home renders. The earlier previews remain in `../achievement_coins_20261014/`.

Water and sunrise now have dark charcoal insets. Their previous nonmetallic inset materials scattered enough studio light to look gray. These use dark reflective materials fitted against a uniform-color app render; the studio lighting is unchanged.

Both hourglasses have broad rounded bars, revised column profiles, and separate fitted maps for brushed metal, glass, sand and background. Sprout has fewer, larger leaf/soil facets and revised emerald/gold/brown maps. Hidden regions are filled separately for each material to avoid painting another raised part into the background. Texture detail follows the owner's reference, setting aside the general preference for completely plain surfaces where needed.

The complete coins were edited and inspected through live Blender MCP. Editable scenes: [coins.blend](coins.blend). These use real raised geometry with fitted albedo/emission maps and reflective materials. The glass appearance is an opaque relief treatment.

| Preview | Model | Triangles | Bytes |
| --- | --- | ---: | ---: |
| Water | [USDZ](clean/mobile/clean_badge_mobile.usdz) | 56,694 | 4,515,480 |
| Teal hourglass | [USDZ](hourglass_teal/mobile/hourglass_teal_badge_mobile.usdz) | 87,800 | 4,867,442 |
| Gold hourglass | [USDZ](hourglass_gold/mobile/hourglass_gold_badge_mobile.usdz) | 87,800 | 4,901,992 |
| Sunrise | [USDZ](sunrise/mobile/sunrise_badge_mobile.usdz) | 62,864 | 4,434,224 |
| Sprout | [USDZ](sprout/mobile/sprout_badge_mobile.usdz) | 61,174 | 4,470,377 |

All five: `usdchecker --arkit: Success!`; frozen shell, identity transforms, Y-up/meters, frame/floor bounds, resolved textures and matching reverse geometry passed. All five preview builds: `ScreenTime-UIOnly: ** BUILD SUCCEEDED **`. Actual proof paths are in `build_results.json`. Front, side, back and other-side app captures were checked, including 4x crops. The original six-second loading deadline remained unchanged throughout this revision.

These are improved review previews. Remaining differences include the frozen rounded casing versus the mockups' flatter rim; tiny water defects and some thin relief-edge highlights remain visible at 4x. Phone performance and the full production build/test gate have not been measured. The triangle guideline is exceeded for smooth relief on both faces; all packages remain below 5 MB.

Sprout is left at rest in **Badge Coins Preview**, using its temporary Silver alias. The private test dataset was restored byte for byte after every build. The main app repo and other badges were untouched; no commits or branch changes.

Repack from the canonical `reliefs.npz`, `design.json` and `textures/` with `pack.py`. `fit_reference.py` requires a fresh uniform-material Home capture when fitting a changed shape. Do not rerun the initial `prepare.py` over these refined meshes.
