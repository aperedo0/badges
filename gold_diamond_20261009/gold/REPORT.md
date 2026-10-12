# Gold badge, 2026-10-09

Five rounded finials above a curved scalloped front shell, broad rolled valley borders, fine lips and a closed annular band with a real open center. The rear band is lower to preserve the reference view into the cavity. Selected candidate 03; its changes are recorded in [candidates/03/NOTES.md](candidates/03/NOTES.md).

![Reference beside the actual Home render](proof/reference_vs_app.png)

The actual model was built, installed and viewed on the iPhone 17 Simulator using `ScreenTime-UIOnly`. The full native screenshot is [proof/app.png](proof/app.png). Because Gold has no 3D app data set yet, the temporary preview used the **Copper** slot and the full screenshot retains that tier label. Beveled surfaces, facet lighting, and the matching floor reflection confirm the 3D model is showing. Screenshot pixels are unretouched; panels only crop screenshots, resize the reference and add labels.

ScreenTime-UIOnly: ** BUILD SUCCEEDED **. This was an asset preview, with no app source changes or code tests.

| Property | Final |
| --- | --- |
| Triangles | 42,580 |
| USDZ size | 3.48 MB |
| Width / height / thickness | 6.378 / 4.451 / 1.442 units |
| Lowest / highest Y | -2.455 / 1.996 |
| Floor gap | 0.440 units |
| Textures | Two 1024 by 1024 PNG maps |

Independent ARKit compliance, closed-mesh checks, explicit normals, face-varying BadgeUV coordinates, package texture hashes, fresh Blender import and packed editable-master checks passed. The one USDZ is Y up, meters per unit 1, front +Z, centered on the spin axis, and has no transforms, reserved coin names, lights, cameras, floor or reflection objects.

Materials were solved from measured app lighting using the unchanged Silver 2 AgX function. The opening was narrowed after the first app check. The lower wall curve was then made independent of the peak heights and given smooth analytical normals, eliminating the pinched fold visible in the earlier app renders. The new wall was measured again in the app. Broad highlight placement is partly fixed in the maps; physical lighting still responds during the entrance turn. Smooth maps, plain reverse materials and real geometry avoid normal-map grain.

The five pointed stems occupy the front half of the hollow band, and the reverse uses plain gold materials. The small outer finials and narrow lips deliberately remain smaller than the general 0.6-unit guideline to match the reference. The lower band retains smooth broad gold reflection bands; it carries no fine grain. Bright yellow highlights are paler than the reference under the fixed studio light and AgX transform; this is visible in the comparison.

The app still draws its existing coin contact line below floating shapes. Permanent Gold integration needs its own data set, model-table entry and still-art wiring by the app owner. The transparent fixed-Home-frame PNG is supplied without changing app art. All original temporary-slot assets and all 641 tracked app files were restored and verified byte for byte; branch, commit and Git status remain unchanged. Existing approved badges and Downloads folders were preserved.

Final model: [mobile/gold_crown_mobile.usdz](mobile/gold_crown_mobile.usdz). Editable model: [master/gold_badge_master.blend](master/gold_badge_master.blend). SHA-256: `2306ce19a8d9fabb804775350c6d7677901a29283fe5fa80914a790ca6b638a2`.
