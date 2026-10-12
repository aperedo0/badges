# Diamond badge, 2026-10-09

A closed blue crystal with individually flat geometric cuts. Each of the 73 front faces has its own padded texture area, preserving independent material correction at the boundaries. The main outline and visible facet junctions follow the reference. Selected candidate 04; its changes are recorded in [candidates/04/NOTES.md](candidates/04/NOTES.md).

![Reference beside the actual Home render](proof/reference_vs_app.png)

The actual model was built, installed and viewed on the iPhone 17 Simulator using `ScreenTime-UIOnly`. The full native screenshot is [proof/app.png](proof/app.png). Because Diamond has no 3D app data set yet, the temporary preview used the **Silver** slot and the full screenshot retains that tier label. Beveled surfaces, facet lighting, and the matching floor reflection confirm the 3D model is showing. Screenshot pixels are unretouched; panels only crop screenshots, resize the reference and add labels.

ScreenTime-UIOnly: ** BUILD SUCCEEDED **. This was an asset preview, with no app source changes or code tests.

| Property | Final |
| --- | --- |
| Triangles | 172 |
| USDZ size | 0.88 MB |
| Width / height / thickness | 6.421 / 4.804 / 0.915 units |
| Lowest / highest Y | -2.455 / 2.349 |
| Floor gap | 0.440 units |
| Textures | Two 1024 by 1024 PNG maps |

Independent ARKit compliance, closed-mesh checks, explicit normals, face-varying BadgeUV coordinates, package texture hashes, fresh Blender import and packed editable-master checks passed. The one USDZ is Y up, meters per unit 1, front +Z, centered on the spin axis, and has no transforms, reserved coin names, lights, cameras, floor or reflection objects.

Materials were solved from measured app lighting using the unchanged Silver 2 AgX function. Facets were given separate texture areas after the first app check exposed thin dark lines from shared texture sampling. The final optical-surface pass then removed colored reflection artifacts from the dark facets. [proof/material_options.png](proof/material_options.png) compares the reference, candidate 03 with stronger studio response and selected candidate 04 with smoother optical color. Smooth maps, plain reverse materials and real geometry avoid normal-map grain.

The PreviewSurface crystal is opaque. Its apparent refraction, blue optical bands and spectral highlights come from reference-matched color and emission, rather than transmission through an optically simulated gemstone. The selected front surface uses the solved optical color predominantly as emission, with only 1% of its calibrated reflected component: this removes the colored dots visible in candidates 02 and 03. The front optical pattern stays attached to the faces during a turn; the blue back and edge surfaces respond to the real environment. Facet normals and shape are real geometry. Thin luminous facet lines and the bright lower tip are intentional reference-driven exceptions to the general preferences against inner glints and bright reflection detail. The 172 triangles are sufficient for flat cuts; extra tessellation would not improve them. Candidate 04 follows three material attempts because the final app measurement isolated reflected-light artifacts; this controlled material change replaces that unreliable component rather than guessing another metal color.

The app still draws its existing coin contact line below floating shapes. Permanent Diamond integration needs its own data set, model-table entry and still-art wiring by the app owner. The transparent fixed-Home-frame PNG is supplied without changing app art. All original temporary-slot assets and all 641 tracked app files were restored and verified byte for byte; branch, commit and Git status remain unchanged. Existing approved badges and Downloads folders were preserved.

Final model: [mobile/diamond_crystal_mobile.usdz](mobile/diamond_crystal_mobile.usdz). Editable model: [master/diamond_badge_master.blend](master/diamond_badge_master.blend). SHA-256: `06bf88af01dd4e3858325c7e0856071c0517d55a056a76bcf53b576769c24afe`.
