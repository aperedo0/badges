Bronze candidate 02, 2026-10-10

Rear dome, rays, channel and rolled lips now match the front relief and texture.

The original front geometry, normals, UVs and materials are unchanged. Grazing edge pixels can differ because the rear relief is now present.

46,176 triangles slightly exceed the guideline to preserve the installed front tessellation and matching rear lips.

App comparison: [front, right, back and left](candidates/02/review/fullsize_comparison.png). Top row is installed/current; bottom row is updated. The side and back screenshots use independent rotated inspection copies held at full size under unchanged app lighting. The delivered model has no transforms and faces +Z. [Actual Home scroll poses](candidates/02/review/scroll_comparison.png) and [slow full turn](candidates/02/full_turn.mp4) are separate.

Four full-size poses inspected at 4x, with dense intermediate turn samples retained at 4x. No isolated white outline dots or broken bright edge segments were observed in the reviewed app views. Existing front surface grain is retained where the owner requested an unchanged front, taking precedence over the smooth-surface guidance.

Package: 46,176 triangles; 3.72 MB; ARKit compliance checks passed. Frame, spin-axis bounds and material UV readers checked against the app contract. The package and all texture dependencies were independently unpacked and verified.

Final model: [mobile/bronze_badge_mobile.usdz](mobile/bronze_badge_mobile.usdz). Original installed model: [previous/installed.usdz](previous/installed.usdz). Approved parent-folder finals were not modified. The app repo was restored byte for byte after temporary tests; no app code, branch or commit changed.
