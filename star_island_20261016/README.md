# Star Ascent and Island Sunset

Two new coin prototypes made from the owner's October 16 mockups. Existing badges and the production app are not replaced.

* Star Ascent: faceted silver star, seven rays, five raised steps and overlapping silver clouds on charcoal.
* Island Sunset: two raised green and gold palms, sunset enamel, gold island, sculpted teal water and raised gold wave borders.

Each `mobile/` directory contains its USDZ. Each `.blend` contains the complete round coin, front, matching back, packed textures and reference image. The complete circular shell and approved brushed/glint finish come from Water Drop and Emerald Sprout respectively, without geometry or material changes.

Both require the preview's floating placement: size `0.96`, lift `0.56`, lowest world Y `-2.455`. The raw round shell spans Y `-3.015` to `3.015`; do not use the legacy floor-cut placement. The recognized casing name enables runtime anisotropy and the existing coin glint shield.

## Rebuild

From the badges repository, with the Blender MCP add-on connected:

```sh
python3 star_island_20261016/prepare.py
python3 water_match_20261014/blender_live.py code star_island_20261016/build_live.py
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I star_island_20261016/pack.py star_ascent island_sunset
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I star_island_20261016/validate.py
```

`prepare.py` rebuilds the hand-traced outlines and intrinsic starting maps. `build_live.py` edits and saves complete scenes in the running Blender, then exports intermediate geometry to `/tmp/star_island_20261016`. `pack.py` preserves the approved shell data and rim maps while combining disconnected relief parts by material for lighter RealityKit loading. It runs Apple's USD checker and writes `model.json` with sizes, triangle counts and checksums.

The fitted per-badge `textures/` maps take priority over the starting maps. They were measured against the app's real Home lighting using `fit_materials.py`, following the established relief fitting method. The casing is excluded from that fitting entirely. Metal reliefs remain reflective with zero emission. The colored enamel may fill colors the studio light cannot supply; this is separate from the Diamond's pure runtime gem shader.

Keep Island Sunset's `texture_scales.json` with its maps: the sky emission image is normalized per channel, and that metadata restores the correct linear values in Blender and USD. This prevents low blue values from collapsing into a few texture codes.

For a new lighting measurement, pack with `--calibration`, capture verified live neutral rest renders at native resolution, and place them at `/tmp/star_island_20261016/NAME_calibration.png`. Never use the flat Steel fallback as a measurement. Then run `python3 star_island_20261016/fit_materials.py NAME` and rebuild the live scene and USDZ. Calibration captures and review scratch files remain in `/tmp`.

## Simulator preview

Private project: `/tmp/achievement_coin_app_20261014/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.screentime.uidev`.

Dedicated simulator: `Badge Coins Preview`, ID `85DF6D3B-6622-491A-8996-3ED0725DB273`. Choose either new name under Home's **Choose Badge** menu. Their temporary asset names are `Badge3DPreviewStarAscent` and `Badge3DPreviewIslandSunset`. No permanent tier assignment or Badges-screen artwork is included.
