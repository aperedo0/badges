Handle opening and lower grip finish correction

Status: APPROVED (review round 1).

Scope
Preserve candidate21 plate dimensions, ring position and the reviewed frame, arches and tabs. The scoped handle reconstruction passed for placement, but its cover has a black rectangular rear notch and the lower grip has soft pinches. Correct those two shapes and soften the mounting plate edge. Neutral clay only. No other metal, lock, rig or app work. There are no owner decisions needed.

Reference and evidence
Original /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png and owner_examples_20261114/reference_handle_plate.png. Current close evidence phase01/candidate21/close_handle.png, reference.png, left_end.png, right_end.png and its fresh review brief. Current source is phase01/tools/handle21_live.py. The rectangular notch is the space between two rectangular rear anchor necks and the curved C cover. The pinched seams come from the 0.008 Gaussian groove waists and the broad sleeve transitions. Actual ring plate separation already passes and must be preserved.

Continuous supported cover
Replace the C shell plus two rear neck unions with one closed profile having the SAME measured outside curved face and a full rear web. Its profile is (X magnitude 2.795, Y equal to the first measured outer arc Y), then measured outer arc indices 0 through 47 translated outward by 0.1871, then (X magnitude 2.795, Y equal to the last outer arc Y), closing vertically at the back. The outside arch is the actual measured profile, not a generic circle or rectangular block. The added web occupies only the old rear void and attaches continuously into the mounting plate, so there is no exposed rectangular notch or extra patch. The ring opening is then cut from the actual ring, making a smooth true root opening in the supported cover.

Loft and details
Use the existing convex polygon inward offset method to make a 0.012 inset end profile for the axial bevel. Extrude along Z center 0.260, width 0.620, with inset end loops and full loops 0.012 inside. The two cover grooves retain their exact positions, depth and width from the approved handle21 plan. Apply the radial recess only to measured outer arc vertices, now indices 1 through 48 in the new profile. Keep the rear web and contact edge uncut by those decorative grooves. Cap from the clean profile and prove a connected closed positive solid.

Use a copy of the actual moved ring expanded by 0.012 along its true normals for a Boolean root cut, using the already tested local adaptive cleanup. One root cut replaces the former pair of unions and a cut, reducing numerical slivers. Restrict cleanup to at most 0.000160 units and retain all original strict area, manifold, volume and connectedness checks. The root aperture must follow the ring, not a sharp rectangular subtraction. At the rear web it may open into the mounting plate contact, but no ring surface may intersect the plate. Cut the cover only. Keep a substantial continuous wall around the root and inspect both end caps.

Build one cover and mirror the completed geometry for the opposite end. Reverse winding and recompute the stable curve normals only after tiny reflected face cleanup, as in handle21. No independent slightly different end reconstruction. Compare both ends in the rendered views.

Lower grip
Keep the ring center, oval radii, main tube radius 0.1109 and maximum grip radius 0.1309. Sleeve coverage remains angles 2.15 through 4.13. Tighten the endpoint fade width from 0.070 to 0.040 radians, with the same smoothstep endpoints, producing a broader constant radius grip with firmer shoulders.
Keep groove centers 2.40, pi and 3.88. Replace the deep broad Gaussian recess with a flat 0.0045 deep seam for angular distance at most 0.008, then a smoothstep ramp to zero at 0.016. Add exact vertex rows at each center plus or minus 0.008 and 0.016, so the seams follow mesh edges. Reuse the existing exact derivative normal calculation with this profile; finite difference at 0.0001 retains the smooth endpoints. The three seams become narrower, shallower divisions without a radial waist or inflated bands. The outside oval is unchanged and the extra grip depth stays below the mounting plate.

Plate
Retain X bounds 2.595 through 2.810, Y negative 0.635 through positive 0.105, Z negative 0.320 through positive 1.120 and its existing actual head positions. Increase the real edge bevel from 0.035 to 0.050 to soften the blocky right edge. Validate head seating on the actual remaining flat face, rear wood overlap and the 0.045 gap below the body strip. Do not shrink the plate or move the ring back into it.

Checks
Preserve actual ring plate clearance at least 0.004 wherever Y and Z overlap, and zero triangle intersection pairs between plate and ring and cover and ring. Verify the rear web intersects the plate seat at multiple Y and Z samples and its main back is 2.795, below plate face 2.810. Verify each fixing head back is inside the actual plate face. All active solids stay closed, connected where intended, positive and free of triangles below the existing area threshold. Do not weaken validation to accept a Boolean failure. Full closed turning width remains at most 6.700 and all unaffected vertex positions match candidate21 exactly.

The appearance check can fail independently. Render actual reference view, both ends and rear in the unchanged development studio. Inspect the entire handle at 2x and 4x for wavy grooves, pinches, black notches or exposed web rectangles. Compare the original reference, not only the prior candidate. Then a fresh scoped reviewer judges clean surfaces first and reference fidelity. If a full web changes the curved cover into a visually blocky form or closes the needed root aperture, return to this affected plan instead of hiding it with material. All final materials and mobile checks remain deferred with the existing construction scope.

Execution and pacing
Build only after this affected method is approved. Reuse the current safe live solid, loft, actual ring cutter and exact ring normal methods. Save canonical source and candidate22 after geometry and before a render. Read schedule before any substantial operation. The renderer itself now checks the saved work deadline before every pose, leaves remaining views deferred and restores the scene in finally. Never continue orchestration after a failed guard command. Stop new badge work during breaks. This corrects the construction finish only, not the remaining thickness, lock or opening rig tasks.

Review log
APPROVED round 1, no blockers. Accepted visual risks: the new rear web must not appear as a squared patch or closed root opening, and narrowed seams must not retain pinched or swollen shading. Both actual end views and close crops own these checks.
