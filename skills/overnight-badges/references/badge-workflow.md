# Reference matching in this badge workspace

Read this when building or refining a badge. The workspace guide remains authoritative for the app contract. Check which source version and finish the owner actually approved before reusing a builder.

## Local starting points

The workspace is `/Users/antonioperedo/Desktop/badges`. Production is `/Users/antonioperedo/Desktop/screen_time`; keep it untouched for preview work. The private preview has been at `emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. Verify current context using XcodeBuildMCP session defaults rather than assuming these stay current.

The Blender add on has been on local port 9876. `water_match_20261014/blender_live.py` edits the open application and captures its viewport. Verify it first. Background Blender is a disclosed fallback.

`three_crests_20261027/` contains the moon, mountain and sword workflows and native light fitting. `bronze_phoenix_20261028/` includes the phoenix, closed gems, planar bezels and later metal adjustment. Inspect these examples, but do not edit their approved finals or apply their parameters indiscriminately.

## Small details that matter

1. **Actual forms.** Compare silhouette, negative spaces, spacing, thickness and proportions before polishing. Preserve bright reference tips; a color threshold can accidentally cut them away. A flat picture on a thick outline is not the sculpted design.
2. **Distinct parts.** Match leaf taper and veins, feather count and overlap, flame curls, ribbon folds, eyes, beaks, gem seats and small points. Include only features present in that reference. Do not replace complex forms with generic primitives because they look similar at first glance.
3. **Real planes.** Closed gems and straight planar bezels hold their edges during a turn. A raster height drop around a gem creates stair shaped cuts. Keep support geometry below the visible facets, preserve correct UVs, and use plain matching metal on side walls instead of stretching a front picture onto them.
4. **Coherent surfaces.** A sudden height threshold across an arc can look like a paper crease. Replace it with a continuous transition. Forcing front facing normals onto a steep bevel can make narrow triangles correct themselves differently, causing striped reflections. Keep gentle feather reflections separate from the normal treatment a steep body edge actually needs.
5. **Requested finishes.** For the exact background of an approved badge, transfer its actual material, color and texture data rather than approximating by eye. Preserve deliberate fractured bronze or cracked stone when shown in the reference; the owner's reference outranks general smooth finish guidance.

## Metal through a turn

The owner likes moving reflections and glints, but rejected a sword changing abruptly from a soft resting face into strong chrome. Start from the approved finish and compare rest against early turning poses. Keep the fixed studio lighting.

Reference fill may preserve small marks and front color, but it must not supply the only shine. Retain actual physical reflection. Fit it against native app light when needed, and record which details stay fixed in reference maps. Increasing a metallic scalar already at 1 does nothing.

For a percentage adjustment, record a real parameter change and baseline, such as multiplying bronze reflectance colors in linear light while preserving roughness and geometry. The visible highlight change varies with angle, Fresnel response and the app view transform; do not claim an identical visible percentage everywhere.

## Native evidence

Use XcodeBuildMCP to build and run the private preview. Native full resolution PNGs may be needed for fitting and 4x inspection. Wait for Home and the badge to load, then look at the capture. Launch logos and flat fallback pictures are invalid calibration data. Check every side, the reflection and a slow full turn. Approximate old scroll poses were 94, 133 and 171 points; verify the actual view instead of trusting a number.

Each numbered candidate keeps the USDZ, complete packed `.blend`, screenshots, comparison and two lines explaining the change. Save UV bindings, material maps and rebuild instructions. Deliver the final in `mobile`, retain the previous final in `previous`, and leave the new separate preview entry open. Do not replace production tiers to add a preview entry.
