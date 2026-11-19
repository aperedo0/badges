Handle finish parameter correction

Status: APPROVED (review round 1).

Scope
Refine only the lower handle grip and mounting plate edge. Preserve candidate22 continuous supported cover, actual root aperture, plate bounds, ring axis, fixing heads and all other chest geometry. Reference: /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png and owner_examples_20261114/reference_handle_plate.png. Current evidence phase01/candidate22/close_handle.png, left_end.png, right_end.png and review.md.

Diagnosis
The continuous tube has intrinsic sleeve rise 0.020 over a 0.040 radian smoothstep fade. At the oval lower shoulders the surface tangent rapidly changes and gives the raised crescent in the actual render. Narrow central recess depth 0.0045 reads faintly. This is parameter tuning of the existing exact analytic tube and Boolean cover methods, not a new geometry method.

Exact correction
Keep the oval center, axis, radii, base tube radius 0.1109 and sleeve angular coverage 2.15 through 4.13. Lower the sleeve addition to 0.018 and broaden its endpoint smoothstep fade to 0.060 radians. This reduces the physical step ten percent and the maximum tangent slope forty percent. Add exact rows at both fade endpoints and quarter intervals. Use exact piecewise smoothstep derivatives for collar and groove depth, including zero derivatives at endpoints, then correct surface normals, including common height inverse transpose, and add no normal map.
Keep groove centers 2.40, pi and 3.88 and flat groove floor distance at most 0.008 radians. Double depth to 0.009 and broaden smoothstep side ramps to end at 0.024 radians, with exact rows at center, plus or minus 0.008 and 0.024. This makes the central divisions legible while keeping smooth ramps instead of sharp Gaussian waists. The minimum grip radius stays above the ungripped tube radius. Keep the existing angular modulation and derivative normal method.
Reduce mounting plate bevel from 0.050 to 0.025 with unchanged bounds. Head locations and support are unchanged. Do not rebuild the already reviewed cover against the new narrow grip surface because its aperture is at the unmodified ring root, but recompute its actual cutter with existing safe method as part of a reproducible complete rebuild.

Checks and review
Retain every strict manifold, triangle area, signed volume, bounds, ring plate and ring cover separation check. Compare unchanged active vertex positions against candidate22, allowing only the two ring objects and two mounting plates. Verify plate heads are still seated. Save source and candidate23 before four guarded Blender renders. Inspect full views and close handle picture against reference at 2x and 4x. Reject visible raised shoulder crescents, pinched bands or waviness independently of contact validation. Fresh scoped review judges finish and reference form; final material and mobile work remain later. No app editing and no changes to lock or other metal in this candidate.

Pacing
Current block ends at the saved schedule deadline. Check before substantial operations. Renderer itself defers poses if too little time remains. Save before rendering and end work for the required break.

Review log
APPROVED round 1, no blockers. Accepted risk: compare both lower shoulders under identical camera, light and exposure and reject a sharper raised crescent. Accepted derivative correction: implement exact smoothstep derivatives rather than the former finite difference approximation. Rebuilt covers compare geometric surfaces within numerical tolerance rather than vertex index order. Final materials and phone appearance remain outside approval.
