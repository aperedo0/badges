# Crimson Shield brushed metal

The center's previous fine grain disappeared at phone size, and its matte finish lacked directional brushed reflections. The updated field uses the owner's metal photo with broad lighting removed, aligned diagonally through its UVs. Its lower roughness and live anisotropy give it a clearer metal reflection. The first app check showed excessive striping; color and roughness grain were reduced before the final check.

The silver frame's broad face is about 23% wider, with its bevel angle retained and a deeper inner recess. The outer silhouette, top, bottom, hover height, spin axis, rubies and ornaments retain their previous shape. The back has the same brushing and sculpture.

The owner authorized the shield specific app material exception. The private preview restores anisotropy 0.55 only on CrimsonShield_BrushedField, with diagonal tangents that follow both faces and the floor mirror. app_material.patch and app_material_README.txt carry this addition for production integration. The production repo is untouched. Other badge materials, lights, glint shield and gem shader are unchanged.

A missing studio EXR in the private preview initially caused fallback art. That one required file was restored from production, matching the previous validated studio hash exactly. Unrelated missing preview resources were left alone.

The USDZ is 4.02 MB with 512 pixel maps and 47,376 triangles. The count is slightly above the suggested 45,000 because both faces carry the full layered sculpture. Model contract and ARKit validation pass. Physical iPhone performance has not been measured. Previous models remain in previous/.

Model SHA256: 4f24cdfc041fcbd8d474eda1865c537fa8c20401a01dea45a308cafcacc4ada1.
No commits or branch changes were made.

The final native app check passed at rest, from both sides and the back, and through the slow full turn. Each outline was inspected at 4x. No detached bright edge dots, broken outlines or new grain shimmer were observed. The moving directional reflection also returns on the matching back. comparison.jpg contains only the previous and updated Home views. The updated shield is selected at rest in the separate Badge Coins Preview simulator.

The two required generic device builds and native simulator build passed. No logic tests were added for this visual material change.

```text
ScreenTime: ** BUILD SUCCEEDED **
ScreenTime-UIOnly: ** BUILD SUCCEEDED **
tests skipped: presentation lane, no logic changed
```
