# Badge RealityKit handoff

All requested assets and reports are in this folder. The original Blender file is unchanged, verified by SHA-256 before and after. Work was performed in background Blender using copies. No app source code was changed.

Source: `/Users/antonioperedo/Desktop/badges/medallion/silver_medallion_stage_refined.blend`

## Environment maps

- [2048 x 1024 EXR](environment/badge_studio_2048.exr)
- [1024 x 512 EXR](environment/badge_studio_1024.exr)
- [Display-only preview](environment/badge_studio_preview.png)
- [Reproducible bake scene](scenes/environment_bake.blend)

Both maps were rendered in Cycles with a 360 x 180 degree panoramic equirectangular camera at (0, 0, 0). They contain 32-bit float scene-linear Rec.709 RGB, ZIP compression, with no AgX, display transform, glare or denoising. The badge, floor and haze are hidden.

Temporary one-sided emissive rectangles reproduce the original five area-light shapes, transforms, colors and radiance. A finite-radius emissive sphere with the original spotlight angular falloff reproduces the spot. Native lights are hidden in the bake to avoid double counting. The reflection ambient is uniform linear RGB (0.00875, 0.00875, 0.00875); keep the app background black separately.

| Map direction | Axis |
|---|---|
| Center | +Z, badge front |
| Horizontal seam | -Z |
| Top / bottom | +Y / -Y |
| u = 0.25 / 0.75 | +X / -X |

Use an EXR as the lighting source, not the PNG preview. All six emitters were sampled at their expected image coordinates and checked against their radiance. The map peaks at about 2490 in linear RGB, so the HDR highlights have not been clipped to 1.

This is an origin capture: an infinite IBL cannot preserve the nearby lights' parallax and distance falloff over the entire badge. It also cannot reproduce Blender's per-light specular/diffuse/volume controls independently. Match environment orientation and exposure against the supplied references before fine-tuning the app.

Normalized rectangle radiance is power / (pi * width * height). The normalized spotlight sphere uses power / (4 * pi^2 * radius^2), with the original cone attenuation. The formulas were checked against the [Cycles area-light implementation](https://raw.githubusercontent.com/blender/blender/main/intern/cycles/kernel/light/area.h), [light setup](https://raw.githubusercontent.com/blender/blender/main/intern/cycles/scene/light.cpp), and [spotlight implementation](https://raw.githubusercontent.com/blender/blender/main/intern/cycles/kernel/light/spot.h). Exact source light rotations and all factors are in [scene_settings.json](reports/scene_settings.json).

| Light | Position XYZ | Power | Shape |
|---|---|---:|---|
| Key \| tall left softbox | (-5.4000001, 3.5, 2.8) | 450 W | 2.2 x 4 rectangle |
| Rim \| right strip | (4.8000002, 1.8, 4.1999998) | 260 W | 1 x 3 rectangle |
| Top \| silver crown | (-0.30000001, 5.0999999, 3.5) | 430 W | 2.1 x 1 rectangle |
| Bottom \| narrow reflection | (-1.8, -2.0999999, 4.5999999) | 230 W | 0.8 x 1.8 rectangle |
| Fill \| large frontal card | (0, 0.60000002, 7.5) | 40 W | 3 x 3 rectangle |
| Overhead \| soft visible shaft | (0, 10.293409, -1.8) | 6144.4043 W | radius 0.25, cone 41.58909 degrees, blend 0.75 |

## Animation

[Exact animation explanation](reports/ANIMATION.md), [all keys and handles as JSON](reports/animation.json), and [every frame as CSV](reports/animation_samples.csv).

The badge parent rotates once around +Y while scale grows linearly from 0 to 1. Its center also rises linearly from floor Y = -2.895000219 to 0. Frames 1 to 360 at 30 fps. The camera and all six lights are static and unparented.

## Mobile badge

[Mobile USDZ](mobile/silver_badge_mobile.usdz), [editable reduced Blender copy](scenes/silver_badge_mobile.blend), and [mesh report](reports/mobile_model.json).

Exactly **40,000 triangles**, reduced from 213,730. File size: **4,730,909 bytes**, 4.73 MB (4.51 MiB). The six meshes remain separate. Full original names are preserved as USD displayName and sourceObjectName metadata; USD prim identifiers replace unsupported spaces and pipes with underscores. The exact mapping is in the mesh report.

| Mesh | Source triangles | Mobile triangles |
|---|---:|---:|
| Casing \| smooth rounded outer edge | 163,840 | 28,000 |
| Emblem \| faceted compass spear | 230 | 230 |
| Inner channel \| shadowed bevel | 18,432 | 3,500 |
| Inner edge \| fine silver reveal | 12,288 | 2,200 |
| Inset \| charcoal textured disk | 8,188 | 3,570 |
| Rim inner lip \| narrow highlight | 10,752 | 2,500 |

The emblem remains 230 triangles with its geometry intact. Planar interior faces were dissolved where possible, then the other meshes were decimated to their budgets. Source corner normals were transferred to preserve the rounded rim and bevel shading. The USDZ contains face-varying normals on all six meshes.

Existing baked UV maps were reused after checking that their source geometry matches the supplied Blender scene within 0.000001 scene units. The largest sampled surface deviation on the decimated casing is about 0.001 scene units on a badge 6.03 units across. These are sampled checks, not a formal error bound.

Casing color, roughness and normal maps are 512 x 512. Inset base color is 512 x 512. Emblem and inset normal maps remain 1024 x 1024. All six images are embedded in the USDZ and supplied separately under `mobile/textures/`. Normal maps are OpenGL tangent space, green = +Y, with no green flip.

USD up-axis is Y and metersPerUnit is 1. The model is 6.03 native units wide, so normalize it to the desired physical size in the app. It contains only the six static badge meshes, with no floor, lights, camera or animation. Its face points toward +Z.

Apple `usdchecker --arkit` completed with `Success!`. It printed duplicate GeomSubset registration diagnostics, recorded in [the log](logs/usdchecker.log). This is asset validation, not an iPhone RealityKit render test.

## Materials

[Full readable material report](reports/MATERIALS.md) and [every source node and input](reports/materials_full.json).

The source has eight materials. The circumferential brushing combines a UV-directed anisotropic reflection with procedural color, roughness and bump grain. The texture appearance is baked, but anisotropy and its tangent direction are absent from the exported UsdPreviewSurface shaders. All eight source coat and sheen weights are zero. The report distinguishes rendered linked inputs from ignored socket defaults and describes every lost node effect.

## Reference renders

All six requested images are 16-bit RGB PNG, 1080 x 1440, Cycles, 96 samples with denoising. The beam remains hidden using the source haze visibility setting; its light is retained.

| Reference | Frame | Rotation | Scale | File |
|---|---:|---:|---:|---|
| final_face_on_agx | 360 | 360.00001 deg | 1.000000 | [PNG](references/final_face_on_agx_f0360.png) |
| spin_45_degrees_agx | 46 | 45.12535 deg | 0.125348 | [PNG](references/spin_45_degrees_agx_f0046.png) |
| nearly_edge_on_agx | 91 | 90.25070 deg | 0.250696 | [PNG](references/nearly_edge_on_agx_f0091.png) |
| half_size_agx | 181 | 180.50140 deg | 0.501393 | [PNG](references/half_size_agx_f0181.png) |
| final_face_on_standard | 360 | 360.00001 deg | 1.000000 | [PNG](references/final_face_on_standard_f0360.png) |
| final_face_on_no_glare | 360 | 360.00001 deg | 1.000000 | [PNG](references/final_face_on_no_glare_f0360.png) |

The 45-degree frame is only 12.5% size because spin and growth happen together. The half-size frame shows the back at about 180 degrees. These are exact animation frames, not altered full-size poses.

AgX references use the source Medium High Contrast look, exposure 0, gamma 1. Standard uses look None because the AgX-specific look is unavailable with Standard. The no-glare reference keeps the source AgX settings and mutes only Glare.

An additional [mobile mesh/material preview](references/mobile_meshes_preview_in_blender.png) uses the reduced badge in the source studio with anisotropy disabled to show that export limitation. It is a Blender preview, not a RealityKit screenshot.

## Reflection, contact shadow and glow

The reflection is traced from the actual floor, not a flattened or shortened duplicate badge. The floor is nearly black dielectric material, base RGB (0.0005, 0.0007, 0.001), metalness 0, IOR 1.5, specular IOR level 0.5, coat 0, alpha 1. It is mixed with a black Diffuse shader to fade its reflection.

The floor is at Y = -2.895000219. The full-size casing bottom reaches Y = -3.015, intentionally intersecting the floor by about 0.12 scene units to remove a visible gap.

Its blur and fade are screen-space gradients. With Blender window Y measured from the image bottom:

```text
t = clamp((0.3439477086 - windowY) / (0.3439477086 - 0.1842258275), 0, 1)
roughness = sqrt((1 - t) * 0.0252^2 + t * 0.145^2)
frontReflectionWeight = 0.6 * (1 - t)^2 * (1 + t)
rearBlackWeight = 1 - smoothstep(-5, -1, worldZ)
blackMixWeight = max(1 - frontReflectionWeight, rearBlackWeight)
result = mix(reflectivePrincipled, blackDiffuse, blackMixWeight)
```

This spans about 230 pixels at 1440 image height. It increases roughness continuously while the reflection fades to black. There is no Gaussian blur node or transparent floor. The old node name mentions 90 percent opacity, but the actual current front reflection weight starts at 0.6. Match the numbers, not that stale label. Coat Roughness is also linked to the gradient, but Coat Weight is zero.

[Transparent 512 x 512 contact-shadow PNG](references/contact_shadow_512.png) and [placement/bake metadata](reports/contact_shadow.json). Physical cast shadows exist below the badge, but are subtle on the almost-black floor. There is no separate source AO node or shadow decal.

The bake isolates shadow attenuation using the ratio of two diffuse-receiver renders under the source lights, with and without the badge casting shadows. RGB is black; alpha is clamp(1 - occluded luminance / unoccluded luminance, 0, 1). Reflection and badge color are excluded.

Place the decal on the XZ floor at Y = -2.895000219. Crop: X from -4 to 4, Z from -2 to 6. Image left/right corresponds to X -4/+4; top/bottom corresponds to Z -2/+6. Use unlit black with alpha blending, slightly offset from the floor to avoid z-fighting. This is the final-pose shadow only. Some cast shadow extends beyond the crop; soften the decal boundary or use a larger receiver if that boundary becomes visible. A moving or growing badge needs a corresponding animated or real-time shadow.

The only compositor effect is Glare: Fog Glow, Medium quality, threshold 1.5, smoothness 0.1, clamp off, strength 0.45, saturation 1, white tint, size 0.6. The chain is Render Layers -> Glare -> Output. Cycles denoising and the AgX view transform also affect the image, so Glare is not the only image-processing step if those are counted.

## Tiers and verification

[Per-tier/shared material proposal](reports/TIERS.md). Only silver is authored in the source. Five visible metal slots should vary by tier; gunmetal backing, smoked-nickel recess and charcoal inset can remain shared.

[Image format checks](reports/image_validation.json), [USDZ contents and shaders](reports/usdz_validation.json), [source matching checks](reports/mobile_source_verification.json), and [original-file integrity](reports/final_integrity.json).

Every written file, including scripts, logs, working copies and intermediate renders, is listed by absolute path in [FILE_MANIFEST.txt](FILE_MANIFEST.txt). Nothing in this handoff modifies the original Blender project.
