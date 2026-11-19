# Astral Navigator with fewer mesh objects

Completed and left open in Badge Studio Preview. The badge now has 23 mesh objects instead of 352, below the requested target of about 50. Every original triangle, shading normal, texture coordinate and material assignment is preserved. Textures and gemstone mesh definitions are unchanged.

[Final model](mobile/astral_navigator_badge_mobile.usdz) | [Editable Blender scene](source/astral_navigator_compact.blend) | [Front comparison](candidate01/review/comparison_front.png) | [All side comparisons](candidate01/review/all_sides_comparison.png) | [Slow turn](candidate01/review/full_turn.mp4)

| Item | Before | After |
| :--- | ---: | ---: |
| Mesh objects | 352 | 23 |
| Authored material sections | 564 | 23 |
| Triangles | 88,556 | 88,556 |
| Independent optical stone meshes | 18 | 18 |
| Package size in MB | 4.82 | 5.09 |

The five ordinary meshes group existing surfaces by material and flat or smooth shading. Eighteen gemstone meshes remain independent because the existing optical shader requires each stone to be closed and convex. The new grouping preserves the front, back, bevels, fine scale marks, scrollwork and live metal and sapphire reflections. There is no geometry reduction or texture resizing. Only identical render vertices are shared.

The USD validation compares every oriented triangle corner and its normal, UV and effective material before and after batching. It also checks the complete material graphs, exact gemstone prim definitions and texture bytes. All comparisons pass, as does ARKit USD validation. Identity transforms and bounds are preserved. The original approved final remains unchanged in its original folder and is copied in baseline for reproducibility.

The complete working copy was inspected through live Blender. Native simulator front, early turn, both sides, back and full turn were compared with a fresh capture of the approved original. Four times outline views and a slow rotation were visually reviewed. All eighteen optical stones and their eighteen reflection copies attach successfully. See candidate01/validation.json, candidate01/runtime_attachment_final.txt and candidate01/review/native_pixel_comparison.json. The rendered images are visually equivalent; they are not asserted to be bit identical because batching can change small GPU rounding and edge coverage results.

This change targets scene and material submission overhead. It does not reduce triangle shading or gemstone ray tracing work. No physical iPhone frame rate or memory measurement was collected, so a device speed improvement is not quantified. The package is slightly larger because regrouping changes USD array storage while preserving the full normal data. The main reduction is the number of scene objects and material sections.

Only the Astral Navigator asset in the separate private preview was replaced. The other preview models and the approved original are byte unchanged. No app code, studio light or shader was changed. The existing Astral sapphire runtime integration remains required for the optical finish.
