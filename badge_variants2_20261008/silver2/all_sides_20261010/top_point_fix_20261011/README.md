# Silver top point fix, 2026-10-11

The owner saw flickering near the top of the Silver badge while it turns. Cause: in the 2026-10-10 all-sides model, the star's front face ends at the top point's front tip and its back face at a separate back tip, so the two edges cross half way along each top side wall. Each wall then folds (one half faces out, one in) and the halves swap in and out of view as the badge turns.

Fix (`fix_silver_top_point.py`, run on the extracted `compacted.usdc` of `../mobile/silver_badge_mobile.usdz`, then packaged with `UsdUtils.CreateNewUsdzPackage`): the back tip moves onto the front tip, the two triangles that collapse are deleted, and the touched faces get flat normals. Only `Silver2_Star_Satin` changes (38 faces instead of 40); the front view renders pixel-identical; ARKit compliance check passes.

Not fixed here (smaller, also new on 2026-10-10): flat ledges on the leaf backs seen side-on, and about 640 stem triangles less than 1 mm over other stem triangles.

## Second fix, same day: the back faces crossed the front

The owner still saw flicker on the star's surface while it turned. Cause: the star's front faces run from the front apex to the star's BACK outline, and the mirrored back faces ran to a FRONT outline, so the two sets crossed and, past about 68 degrees of turn, slivers of the back faces showed through the front. `fix_silver_star_back.py` (run after `fix_silver_top_point.py`) makes the back faces end on the front faces' outline and deletes the 18 side walls left with nothing to join. Front renders pixel-identical; the back is flatter (relief about 0.2 deep against the front's 0.48). `silver_badge_mobile.usdz` in this folder now holds both fixes; the owner chose this over flattening the front or deepening the star.

## Third fix, same day: leaf and stem backs crossed their fronts

The leaves and stems were built like the star: each front runs down to a back outline and the mirrored back runs up to a front outline, so the backs poked through the fronts while turning (about 4,900 crossing triangle pairs against about 1,400 in the 2026-10-09 model, whose crossings are stems running through leaf bases by design). `fix_silver_backs_behind_fronts.py` (run after the star fixes) pushes only the back points that sit in front of their own leaf's or stem's front to 0.004 behind it; fronts, textures, UVs and normals are untouched, and the leaf side walls shrink to 0.004 as a result. Crossings left: 172, all present in the 2026-10-09 model too. Front renders pixel-identical. `silver_badge_mobile.usdz` here now holds all three fixes.
