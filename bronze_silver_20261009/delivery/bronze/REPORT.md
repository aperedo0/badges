# Bronze reference badge — 2026-10-09

Eight alternating long/short bronze rays, a closed domed center, two rounded rim lips and a dark channel. Ray crests stay behind the rim. Candidate 03 selected after the measured correction brought the rays back to the reference bronze palette and reduced the upper-ray mismatch.

![Reference and actual Home render](proof/reference_vs_app.png)

The actual RealityKit model was built and installed with the `ScreenTime-UIOnly` scheme on iPhone 17 Simulator. Preview slot: **Copper (Bronze has no model data set yet)**. The full screenshot is [proof/app.png](proof/app.png); the shape's lighting and matching floor reflection show that the 3D model loaded. The screenshot is unretouched; comparison panels only crop, resize the reference, and add labels. The Bronze full screenshot consequently says “Copper.”

One Y-up, meter-scale USDZ with front +Z and no transforms, lights, camera, floor or reflection objects. All meshes are closed and use PreviewSurface materials, matching face-varying BadgeUV coordinates and explicit normals. Independent ARKit compliance, packaged texture hashes, fresh Blender import, and packed master checks passed.

| Property | Final |
| --- | --- |
| Candidate | 03 |
| Triangles | 39,440 |
| USDZ size | 3.21 MB |
| Width / height / thickness | 5.342 / 5.300 / 0.650 units |
| Lowest / highest Y | -2.455 / 2.845 |
| Floor gap | 0.440 units |
| Textures | Two 1024 × 1024 maps |

Fine color texture fades out toward the lowest fifth; backs and downward edge surfaces use plain materials. No normal maps. Colors and supplemental emission were solved against measured app lighting with the unchanged AgX function. Broad highlight placement is reference matched and partly fixed in the maps; physical lighting still changes during the turn. The small texture details soften at Home size, and the fixed coin contact-shadow line remains under the floating shape.

Kept subdued worked-metal color markings from the reference, setting aside the general preference against fine mottling. The pointed ray tips also intentionally taper below the general 0.6-unit small-part guideline.

The two temporarily used app data sets were restored byte for byte after every build. All 641 tracked app files, the original branch, commit and Git status were verified unchanged. No app code or approved final was edited. Bronze still needs its own model data set and table entry for permanent integration; that work belongs to the app owner. The transparent still is supplied as an additional asset, not installed into the app.

Final model: [mobile/bronze_sun_mobile.usdz](mobile/bronze_sun_mobile.usdz). Editable source: [master/bronze_badge_master.blend](master/bronze_badge_master.blend). Final SHA-256: `13e1be6a35822b1d4b2f654873d9e46bfe5af351e763187ec6cf3e3ea7b98c72`.
