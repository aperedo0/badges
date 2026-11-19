Ruby Heart: improve the actual ruby cut

Rebuilt the stone as one closed faceted ruby with 92 front crown planes and a matching back. Replaced the two broad central panels with a continuous crown of smaller angled facets. The lobe cut includes an actual plane angled to catch the existing studio softbox. Highlights move with the changing optical paths and facet reflections. No reference picture, appearance texture or new sparkle effect is used.

The approved gold frame, smooth upper shoulders, UVs, roughness image and material graphs are identical to the previous asset. Only the gem points, normals, triangle data and extent changed. All app Swift and Metal source files are unchanged, including light, exposure and the existing ruby optical shader. Sapphire is unchanged. Approved original models are preserved.

Development used the live Blender connection with the complete badge and reference visible. The saved editable file is source/ruby_heart.blend. The development ruby material mirrors the existing native optical equations. Explicit camera ray, facet normal and numeric studio map checks were performed; parity measurements and remaining renderer differences are in source/parity.json. Actual Blender front, early turn, both sides and back renders were reviewed before exporting.

The private preview build succeeded. Native front, three early angles, both sides, back and an 11.18 second complete turn were checked. Runtime logs confirm the heart shader on both the badge and its reflection at the unchanged exposure of 1.7. The loaded model hash matches source/validation.json. The simulator is left on Ruby Heart at rest. Production code was not edited.

Independent visual review passed this requested gem improvement at 92/100, including the full motion addendum. It confirms one continuous ruby, retained red body color and no new gem surface or outline defects. It notes a minor square ended dark patch near the lower center during early turns. The reference has brighter internal light and finer apparent detail; this interpretation is darker and more geometric. The score is not an overall exact mockup match. See source/comparison.png and source/review.md.

Final optimization retains the minimum useful separation of one gold mesh and one optical ruby mesh. Meshes and material sections stay at 2. Triangles increased from 26680 to 27524. File size increased from 1523329 to 1589146 bytes. Further merging would mix the optical ruby with the metal, so no appearance changing reduction was applied. No device speed claim is made. Final asset: mobile/ruby_heart.usdz.


Owner version labels: the ruby before this gem work is Version 1, preserved as mobile/ruby_heart_v1.usdz. This newer cut is Version 2, preserved as mobile/ruby_heart_v2.usdz. The current model alias and simulator remain on Version 2. See VERSIONS.md and versions.json.
