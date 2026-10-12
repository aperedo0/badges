Gold candidate 22, 2026-10-10

A true circular crown band with a continuous curved crown wall, eight round finials and the reference five-point front silhouette.

The installed gold texture and original peak design are retained, with the front shell projected along the original camera rays onto the round wall. The band and wall geometry changed; the front is judged against the original app picture. The lowest wall row is seated in the band with reference shading normals retained, and the band texture is continuous through both side joins.

The circular band is tilted 17.179 degrees about X, baked into the vertices. Its radius after the 0.995 uniform fit is 2.6318 units. This physical tilt turns with the badge, exposing the inside from a different angle at the back. A constant tilt toward the viewer would need Claude to tilt the app spin axis, as described in AGENTS.md section 7. The rear intermediate finials are slightly shorter so their caps remain hidden behind the front valleys at rest. The circular band reaches Y = -2.7878 at its far edge, below the shared floating-height guideline but above the hard floor; the reference projection takes precedence over that guideline. 74,272 triangles preserve the source finials and smooth rolled details around the entire crown, exceeding the triangle guideline while remaining below 5 MB.

App comparison: [front, right, back and left](candidates/22/review/fullsize_comparison.png). Top row is installed/current; bottom row is updated. The side and back screenshots use independent rotated inspection copies held at full size under unchanged app lighting. The delivered model has no transforms and faces +Z. [Actual Home scroll poses](candidates/22/review/scroll_comparison.png) and [slow full turn](candidates/22/full_turn.mp4) are separate.

Four full-size poses inspected at 4x, with dense intermediate turn samples retained at 4x. No isolated white outline dots or broken bright edge segments were observed in the reviewed app views. Existing front surface grain is retained where the owner requested an unchanged front, taking precedence over the smooth-surface guidance.

Package: 74,272 triangles; 4.79 MB; ARKit compliance checks passed. Frame, spin-axis bounds and material UV readers checked against the app contract. The package and all texture dependencies were independently unpacked and verified.

Final model: [mobile/gold_badge_mobile.usdz](mobile/gold_badge_mobile.usdz). Original installed model: [previous/installed.usdz](previous/installed.usdz). Approved parent-folder finals were not modified. The app repo was restored byte for byte after temporary tests; no app code, branch or commit changed.
