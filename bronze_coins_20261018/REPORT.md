# Bronze coin previews

Zen Balance was off for two reasons: compressed oval geometry gave the stones a floating appearance, and the full reference lighting fit put muddy gray and green patches into their color maps. The refinement uses the reference silhouettes with flatter undersides, a broad foundation behind the rim, and intrinsic warm bronze with neutral texture and roughness grain. Highlights now come from the app. One prior Zen USDZ is retained in `zen_balance/previous/`.

Torch Sunburst has two genuinely curved flame reliefs, 24 shallow faceted rays, a beveled bowl lip and a turned stem. Its matching back is sculpted too. The first app render exposed dark ray faces and isolated bright roots. Shallower, wider blades and roots trimmed around the flame gap corrected that issue in the second render. Lightning Compass remains byte identical to the earlier version, already selectable under its existing name.

All three retain the exact approved Sunrise shell geometry, rim shader graphs and rim texture bytes, including the brushing and compact glints. No studio, camera, shader or glint shield changes were made. The standard wider rim differs from the references' narrower rims; fixed studio highlights also differ from the illustrations.

| Model | USDZ size | Triangles |
| --- | ---: | ---: |
| Lightning Compass | 1.80 MB | 8,696 |
| Zen Balance | 3.26 MB | 39,616 |
| Torch Sunburst | 3.24 MB | 41,888 |

Apple USD validation and `validate.py` passed: preserved closed shell, identity transforms, Y up, no embedded lights or cameras, zero degenerate triangles and no invalid normals. Complete circular coins require size `0.96`, lift `0.56`; never floor-cut these models.

[One compact comparison](comparison.jpg) shows Zen before and after plus the torch reference and actual Home render. All working captures and videos stay in `/tmp`, with no Downloads review folder.

Preview work is confined to `/tmp/achievement_coin_app_20261014`. The production app and other badges are untouched by this task. No commit or branch change was made. These are simulator previews, not production tier integration.

Zen and Torch were checked at native Home rest and through full scroll turns, including the front, back and both sides at 4x. Outer contours are clean, with no exterior glow puffs observed. Torch ray tips naturally become subpixel while shrinking. All 42 preexisting preview dataset files remain byte identical; all three installed preview models match the source files. Torch Sunburst is left selected at rest, with all three names in Choose Badge.

ScreenTime-UIOnly: ** BUILD SUCCEEDED **

tests skipped: private visual prototype, per dispatch

The production build and test gate was not run because the production app was not changed. Physical device performance was not measured. The private source change is three Torch picker lines following the existing DEBUG preview pattern, plus its dataset metadata.
