# Copper flame, 2026-10-09

Recommended delivery: [finish 03 USDZ](mobile/copper_flame_mobile.usdz). [Softer option 02](mobile/options/copper_flame_soft.usdz) is also included. Both are new proposals, with no approved Copper final replaced.

![Reference and two actual Home finishes](proof/reference_02_03.png)

Three closed, smoothly cambered ribbons follow the supplied flame silhouette. Their crests, thickness and edges are real geometry. The front uses reference-derived copper color and emission textures, solved from actual app lighting with a full RGB inverse of the app's AgX transform. Two measured correction passes reduced the pale initial appearance. The back and narrow edge material are plain physical copper. No normal maps or random texture were added.

Finish 03 retains finer curved brushing and brighter narrow crests; 02 has softer highlights. Broad bands and reference color are close at Home size, but the very fine brushing and crest lines remain softer than the original. A couple of small lighting marks remain visible in the enlarged native crop; an exact photographic match is not claimed. See [native surface zoom](candidates/03/surface_zoom.png), [floor gap](candidates/03/floor_gap.png), and [40 pt proof](proof/40pt_proof.png).

40,812 triangles; 1,281,488 bytes; two 1024 px textures. Bounds X [-1.574832, 1.574832], Y [-2.455, 2.845], Z [-0.325, 0.325]. Height 5.30 units preserves the reference's tall silhouette; width is about 3.15. Floor gap is the shared 0.44 units. USD Y up, meters/unit 1, front +Z, no transform operations, no coin-reserved names, and no cameras, lights, floor or reflections in the model. All three meshes are closed. All textures read `FlameUV`, matching their material reader.

[Independent validation](candidates/03/independent_validation.json): ARKit compliance PASS, 40,812 triangles after Blender reimport, both textures present and byte-identical to their packaged members, and both images packed into the editable [Blender master](scenes/copper_flame_master.blend). The editable USD and textures accompany the final USDZ in `mobile/`; numbered candidates retain their screenshots, build logs, settings and changes.

All three finishes were built and viewed in the actual iPhone 17 simulator Home stage, with three launches and shader-settling waits. Rounded illuminated edges and their matching floor reflection confirm actual 3D, rather than fallback art. `ScreenTime-UIOnly: ** BUILD SUCCEEDED **` for each candidate; see each `build.log`. No app code changed and no code tests were needed for this asset-only visual check.

Copper has no 3D dataset or model-table entry. Testing temporarily substituted the Silver asset; the Silver label in the full screenshot belongs to that test slot. The repository was restored after every build/install: [verification](proof/app_restore_verification.json) confirms the original Silver bytes, all 637 tracked file hashes, git status, HEAD and branch. The simulator preview can still show the candidate. Production Copper integration is pending the owner's app work; no permanent tier installation was performed.

Guidance exceptions: preserve the reference's narrow tips and finer-than-3-pixel brushing, with intentional smoothing at native size. Fine brushing fades out in the bottom 19% and returns by 44%; broad reference color bands continue there to preserve the copper look. Front bands are partly encoded in color/emission, so they do not all travel physically during rotation. The app's existing coin contact-shadow line remains beneath this floating shape.

Prepared [600 px still artwork](mobile/BadgeArt_copper_flame.png) at the fixed Home frame, extracted from the actual app render with a supersampled geometry mask. It is a handoff asset only and was not installed in the app.
