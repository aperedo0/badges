# Emerald Archer

The complete badge is modeled in Blender through the live MCP connection. The design follows the owner's supplied reference: a gold recurve bow, emerald settings, a horizontal feathered arrow, four laurel sprays with 37 individual leaves, and a recessed green metal field. The back repeats the full sculpture through a genuine Y half turn. The coin has the approved complete circular shell and floating placement.

The initial physical finish was inspected in the app. Its field was too pale and the stones too dark. A Home lighting measurement guided the final uniform darker green and warmer gold. Spatial color fitting produced cloudy patches, so those maps were replaced with uniform metal colors and subtle intrinsic fine grain. The emeralds retain distinct modeled facets with a small color fill. The rim is excluded from all color fitting.

The final USDZ is `mobile/emerald_archer_badge_mobile.usdz`. The editable complete scene is `emerald_archer.blend`. The initial finish is retained in `previous/` and candidate01. The final material pass is candidate02.

Validation passes for Y up, meter units, identity transforms, model bounds, a closed circular shell, finite normals, zero degenerate triangles, zero missing normals, and a matching sculpted back. The approved shell geometry, normals, both UV sets, material graphs, finish maps, and compact inner glint maps are preserved exactly. Apple's ARKit USD checker returns Success. `validation.json` contains checks and the final hash.

The model is 4,413,347 bytes and 62,784 triangles in 16 relief meshes plus the casing. The triangle guidance is exceeded because both faces include modeled leaf veins, swept bow relief, shaft collars, feather plates, and jewel settings. Physical device load performance has not been measured. Textures are 512 or 1024 pixels.

The fixed standard rim is wider than the reference's rim. The bow's feather ornament and leaf carving are simplified for the phone's small badge size. These remain visible differences from the reference; the model is not an exact reproduction.

Production code and assets were not written by this task. All preview changes are in the preexisting separate project under `/tmp/achievement_coin_app_20261014`. The saved patch adds the Emerald Archer picker entry and a longer initial frame wait for this entry only in that private debug preview. Lights, floor, reflection, glow processing, glint shield, gem shader, and other badge materials retain their rendering. No commits or branch changes were made.

Current app verification status: the initial finish and the spatial fitting experiment both rendered as live 3D badges on Home. The final uniform finish is built and installed in the older private preview. Its final front, both side poses, back, full turn recording, and 4x outline inspection are pending. The shared simulator service stopped answering install and boot requests, including on a fresh Badge Studio Preview simulator. Restart approval has been requested because another simulator is running a separate task. No successful final app check is claimed yet.

The candidate01 comparison contains the real initial Home render beside the reference at equal visible diameters. Blender views are working evidence only. Final app comparisons will be added after the simulator service recovers.
