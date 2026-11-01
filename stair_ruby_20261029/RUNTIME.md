# Dynamic crest gems

The separate Badge Studio preview now supports `CrestGem_Ice`, `CrestGem_Sapphire` and `CrestGem_Ruby`. Every stone is one independently closed convex mesh. The plain USD material is a fallback; the moving optical effect requires the preview renderer and Metal function in this folder.

The renderer traces the existing studio environment through each stone's real facets, with Fresnel reflection, refraction, internal reflection, wavelength dependent color absorption and intrinsic density variation sampled along the ray. Ice includes bounded internal reflective planes. These are runtime optical approximations against the studio environment, not a photograph, a fixed emission image, animated UV coordinates or a full scene caustics renderer.

The custom material writes the computed optical result to its emission output because the light is already included. That output changes every frame. The gemstone USD materials have no appearance textures. The runtime base color texture slot carries numeric facet planes, and the custom slot carries the existing studio HDR environment.

RealityKit exposes texture reads at half precision. Crest plane coefficients use two rows: the rounded coefficient and its residual multiplied by 1024. The shader reconstructs both rows. This preserves thin tips while retaining the approved Diamond's original single row upload and shader.

The source edits are confined to the separate preview. `runtime_integration.patch` records its Swift binder, new Metal function and project registration relative to the starting preview. Complete edited sources are in `runtime/`. The original `BadgeGemSurface.metal`, studio light, stage, floor and production repository were not changed.

For another app, port the recursive crest material binding and register `BadgeCrestGemSurface.metal` in its target. Preserve its existing Diamond path, including its original constants. Each mesh requesting a crest profile must contain exactly one whole convex stone. Do not combine several gems or a concave star into one traced mesh. The current plane limit is 256. The private preview menu hunks are preview specific and should not be applied blindly to production.

Runtime logs report successful attachment or failure for each stone and its floor reflection. The reviewed preview attaches 3 Frostwing stones, 8 stairway stones and 7 ruby stones, with the same counts for their reflections. `check_runtime_gems.py` checks the exported meshes using the renderer's actual Swift convexity routine. The individual candidate folders contain the validation and attachment evidence.

The final files keep the shared floating height and identity transforms. The custom projecting frames follow their references and do not use the frozen coin shell or its reserved names.
