# Lightning Compass, Zen Balance and Torch Sunburst

New bronze coin prototypes from the owner's October 18 references. Each has the current complete circular casing, raised flat brushed rim, recessed dark face and a matching sculpted back.

* Lightning Compass: a solid beveled bolt over four raised compass needles and four slim ring arcs.
* Zen Balance: three rounded, slightly asymmetric bronze stones over a broad resting plinth.
* Torch Sunburst: two curved bronze flames, 24 faceted rays, a beveled bowl lip and a turned handle.

See [comparison.jpg](comparison.jpg) for one compact reference and Home comparison, and [REPORT.md](REPORT.md) for validation and remaining visual differences. Each `mobile/` folder contains its final USDZ. The `.blend` files contain the complete front, back, casing, packed materials and reference. The source casing is the approved Sunrise Path model; its geometry, UVs, material graphs and rim texture files are preserved exactly in the packaged USDZ.

## Rebuild through live Blender MCP

Open Blender with its MCP add-on connected on port9876, then run from the badges repository:

```sh
python3 water_match_20261014/blender_live.py get_scene_info
python3 bronze_coins_20261018/prepare_zen.py
python3 bronze_coins_20261018/prepare_torch.py
python3 water_match_20261014/blender_live.py code bronze_coins_20261018/build_live.py
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I bronze_coins_20261018/pack.py lightning_compass zen_balance torch_sunburst
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I bronze_coins_20261018/validate.py
```

The builder edits scenes in the running Blender and reuses the earlier native Blender helpers from `star_island_20261016/build_live.py`. The packer and material fitter reuse the established packaging and projection helpers from that folder. Existing projects are imported for their helpers only and are never edited or rebuilt.

Material maps apply only to the new emblem and inset. The entire coin rim stays physical brushed metal with the approved glints, never fitted reference highlights. All new materials are reflective with zero emission.

Zen and Torch use intrinsic bronze color and neutral fine grain, with texture variation in roughness. Their highlights come from the studio at runtime. Zen's earlier full reference fit produced muddy and green patches and has been replaced. Do not run the light fitter on Zen or Torch. Zen's silhouettes come from `stone_outlines.json`, rebuilt by `prepare_zen.py`; its broad foundation extends behind the rim so it supports the stack.

Lightning retains its existing fitted emblem maps. To repeat that measurement only, package with `--calibration`, capture verified native Home rest into `/tmp/bronze_coins_20261018/lightning_compass_calibration.png`, run `python3 bronze_coins_20261018/fit_materials.py lightning_compass`, then rebuild that model. Never fit from the flat fallback artwork. To build only one scene through MCP, prepend `BADGE_NAMES=['zen_balance']` or the desired badge name to the builder code sent to Blender.

## Preview placement

The models require size `0.96` and lift `0.56`, keeping the lowest point at world Y `-2.455`. Their raw complete circular shells reach Y `-3.015`: never floor-cut them or use the legacy standing placement.

Private project: `/tmp/achievement_coin_app_20261014/ScreenTime.xcodeproj`. Dedicated simulator: **Badge Coins Preview**, ID `1B2918D9-6C08-4593-9652-C6C1E40B81B9`. Choose the three names under Home's **Choose Badge** menu. Preview datasets are `Badge3DPreviewLightningCompass`, `Badge3DPreviewZenBalance` and `Badge3DPreviewTorchSunburst`; no existing tier is replaced and no production app integration is included.
