# Silver reference badge — 2026-10-09

Two separate downward silver chevrons with closed backs, real broad bevels, flat core faces and directional brushing. Candidate 02 selected: the second measured solve refined highlight and bevel contrast without changing the geometry.

![Reference and actual Home render](proof/reference_vs_app.png)

The actual RealityKit model was built and installed with the `ScreenTime-UIOnly` scheme on iPhone 17 Simulator. Preview slot: **Silver**. The full screenshot is [proof/app.png](proof/app.png); the shape's lighting and matching floor reflection show that the 3D model loaded. The screenshot is unretouched; comparison panels only crop, resize the reference, and add labels. The Bronze full screenshot consequently says “Copper.”

One Y-up, meter-scale USDZ with front +Z and no transforms, lights, camera, floor or reflection objects. All meshes are closed and use PreviewSurface materials, matching face-varying BadgeUV coordinates and explicit normals. Independent ARKit compliance, packaged texture hashes, fresh Blender import, and packed master checks passed.

| Property | Final |
| --- | --- |
| Candidate | 02 |
| Triangles | 440 |
| USDZ size | 0.63 MB |
| Width / height / thickness | 5.627 / 5.285 / 0.600 units |
| Lowest / highest Y | -2.455 / 2.830 |
| Floor gap | 0.440 units |
| Textures | Two 1024 × 1024 maps |

Fine color texture fades out toward the lowest fifth; backs and downward edge surfaces use plain materials. No normal maps. Colors and supplemental emission were solved against measured app lighting with the unchanged AgX function. Broad highlight placement is reference matched and partly fixed in the maps; physical lighting still changes during the turn. The small texture details soften at Home size, and the fixed coin contact-shadow line remains under the floating shape.

Kept fine directional brush marks to match the reference, setting aside the suggested minimum texture-mark width. The 440 triangles are intentional: the silhouette and broad facets are flat and need no dense tessellation.

The two temporarily used app data sets were restored byte for byte after every build. All 641 tracked app files, the original branch, commit and Git status were verified unchanged. No app code or approved final was edited. Bronze still needs its own model data set and table entry for permanent integration; that work belongs to the app owner. The transparent still is supplied as an additional asset, not installed into the app.

Final model: [mobile/silver_chevrons_mobile.usdz](mobile/silver_chevrons_mobile.usdz). Editable source: [master/silver_badge_master.blend](master/silver_badge_master.blend). Final SHA-256: `fa647f99b2aabdbe0d39a799017ee06d726cbb402050454d23c1e4060abe7122`.
