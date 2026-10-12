Steel candidate 03, 2026-10-10

Both chevrons have matching rear relief and brushing; lower-chevron fine detail is restored.

Upper-chevron texture and geometry are unchanged. Lower broad shading and the protected outline band are retained.

The blur came from the model texture pipeline, not the app. The original solve blends a 0.8-pixel detail field into a 6-pixel smoothed field between 19% and 44% of total height, weakening the lower chevron. Matching upper-chevron fine detail was restored in the lower interior in both color and emission maps. The bottom texture-fade guidance was set aside for fine brushing so the twins remain equally sharp.

App comparison: [front, right, back and left](candidates/03/review/fullsize_comparison.png). Top row is installed/current; bottom row is updated. The side and back screenshots use independent rotated inspection copies held at full size under unchanged app lighting. The delivered model has no transforms and faces +Z. [Actual Home scroll poses](candidates/03/review/scroll_comparison.png) and [slow full turn](candidates/03/full_turn.mp4) are separate.

Four full-size poses inspected at 4x, with dense intermediate turn samples retained at 4x. No isolated white outline dots or broken bright edge segments were observed in the reviewed app views. Existing front surface grain is retained where the owner requested an unchanged front, taking precedence over the smooth-surface guidance.

Package: 600 triangles; 0.74 MB; ARKit compliance checks passed. Frame, spin-axis bounds and material UV readers checked against the app contract. The package and all texture dependencies were independently unpacked and verified.

Final model: [mobile/steel_badge_mobile.usdz](mobile/steel_badge_mobile.usdz). Original installed model: [previous/installed.usdz](previous/installed.usdz). Approved parent-folder finals were not modified. The app repo was restored byte for byte after temporary tests; no app code, branch or commit changed.
