Measured mounting plate and seated ring handle

Status: APPROVED (review round 1).

Owner view and scope
A larger substantial mounting plate sits fully below the body horizontal strip, with a ring resting in front instead of entering it. The curved rolled cover remains attached to the plate and supports the ring root, with two narrow surface divisions. The lower grip has clearer three divisions. Both ends mirror in X. Preserve all reviewed frame, arch and crown geometry from candidate20. Build plate and ring, join the cover to the plate seat, cut real root clearance, then render. There are no owner decisions needed for this correction. This remains neutral construction; other metal thickness, lock and opening rig remain later tasks, not approved here.

Reference and measured source
Original: /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png. Owner examples in owner_examples_20261114: ring_into_plate.png, reference_handle_plate.png, overlapping_body_strip.png and reference_body_strip.png. Current complete source and render are phase01/candidate20/chest.blend and reference.png. Read phase01/handle21/plate_measurement.json and DESIGN_NOTES.md. The four plate corners and both heads were measured in the original reference and projected onto their X mounting plane. The global fit has about 6.5 pixel residual; clean geometry is then judged by actual rendered comparison, not calibration numbers alone.

Coordinate and source contract
Numbers use original local X length, Y up, Z front, before 32 degree yaw, Blender axis conversion and the single common height correction. The existing live builder restores core_baseline.npz, builds measured hardware, continuous arches and corrected crown tabs, then this handle revision runs before the height conversion. Rebuild only these handle objects. Never delete old objects. Save canonical and candidate21. Closed source stays inside the 6.700 turning width and existing Y limits. Materials and app code stay unchanged. No production or simulator changes.

Plate
Use the existing closed beveled box method. Outer magnitude X 2.595 to 2.810, Y negative 0.635 to positive 0.105, Z negative 0.320 to positive 1.120, edge bevel 0.035. Width 1.440 and height 0.740 are about 20 percent above the current 1.200 and 0.610. Back overlaps current body end X 2.600 by 0.005. The top sits 0.045 below body strip bottom 0.150, so it cannot form another raised rectangle over the strip. Preserve plain back and actual wall thickness. Mirroring reverses X and winding as usual.

Heads
Use two domed heads per end, radius 0.070, common center Y negative 0.040, Z negative 0.202 and positive 0.916 from the measured reference. Nominal normal origin X magnitude 2.815 puts the buried base at 2.803 inside plate face 2.810. Inspect both mounting faces and test their actual contact. Do not add more heads.

Ring and lower grip
Regenerate the exact existing oval ring construction from full_form_live.py, retaining center Y negative 0.74714387, Z 0.260, oval radii 0.525 and 0.640 and base tube radius 0.1109. Move only its X axis magnitude from 2.7429 to 2.930. Its main back is 2.8191, leaving 0.0091 in front of the plate. The thick lower grip radius 0.1309 occurs below the plate. Measure actual ring vertices against the whole plate volume, including bevels, and require at least 0.004 clearance where their Y and Z overlap. Test mesh intersections too. The ring cannot pass through the plate, even if its center is in front.
Widen the lower sleeve angular coverage by about 20 percent, from 2.32 to 3.96 to 2.15 to 4.13, keeping the smooth endpoint fades. Keep three groove centers 2.40, pi and 3.88, increase actual depth from 0.004 to 0.008 and Gaussian half width from 0.025 to 0.035. Preserve the existing normal derivative formula with the revised profile, so the oval has no seams or geometric ridges. The widened lower sleeve reaches approximately Y negative 0.965; verify its completed bounds, remaining well below the plate, well clear of plate bottom negative 0.635. This is actual geometry, not a material stripe.

Cover and attachment
Reuse the measured C cross section in measured_hardware/profiles.json, 80 points in handle_section_outer and matching inset handle_section_inner, from measured_hardware18_live.py. Translate X magnitude by 0.1871 with the ring, retaining Y and overall height around 0.490. Extrude across Z from center 0.260 minus 0.310 to plus 0.310. Use the existing inset profiles at the two end planes and full profiles 0.012 inside, preserving its real axial bevels. All caps tessellate from the clean C outline. No generic spool or solid rectangular replacement.
The translated C shell needs two actual mounting necks to reach the plate. Join closed top and bottom neck solids into that SAME cover object before the ring cut. Top neck spans X magnitude 2.795 to 2.930, Y negative 0.030 to positive 0.018. Bottom neck spans 2.795 to 2.960, Y negative 0.472 to negative 0.414. Both span the cover width. Their backs overlap plate face by 0.015. Their forward ends must overlap the actual translated C material, not just its bounding box, by at least 0.010. Validate connected union, clean faces and no separate outlined block at either neck. Only hidden overlap into the plate is allowed. Refine the neck face to the existing curve if a straight end shows as an extra ledge; do not hide it with material.

Cover divisions
Create two true narrow grooves at Z 0.125 and 0.395. Each total width 0.030, maximum depth 0.010, with a flat 0.018 bottom and 0.006 ramps at either side, sampled at the shoulder and ramp midpoints. Offset only the outer curved profile points inward along the fitted outer arc normal; the inner receiving wall remains unchanged. The measured outer arc is indices 0 through 47, circle center X 2.681084921 plus the 0.1871 translation and Y negative 0.228049008. This gives real surface divisions without separate collars or changing the outside silhouette. Grooves may end under the plate attachment. Inspect smooth normals and the actual recess after union and cleanup.

Actual root opening
Build the new ring first, then make a hidden copy expanded 0.012 along its exact vertex normals. Use that closed torus as the Boolean difference cutter on the assembled cover only. It is the existing measured_hardware18 method, with the actual relocated ring. Never carve the plate. Keep at least 0.010 clearance at the root and a substantial continuous cover wall. Closed cover topology may be Euler zero or two depending on the actual cut; it must be one connected solid with no floating chips or zero area triangles. Recompute stable smooth curve normals and flat cap normals after Boolean cleanup; do not retain a stale pre Boolean normal list. The curve is sampled along its actual outline and groove rows, never a raster grid.

Prior art and materials
Reuse the existing proven ring profile derivatives, measured C cover, exact closed union and root cut, and closed box from the current chest. Their source scripts are in phase01/tools/full_form_live.py and measured_hardware18_live.py. No unrelated badge is a useful visual baseline for this attachment. Current neutral frame and hardware materials, fixed Blender lights and AgX remain. Final polished metal, wood textures, glow, app optics and mobile mesh consolidation remain deferred. No gems, glass, enamel, coin shell, bright saturated color or fine texture marks apply.

Checks and risks
1. A ring in front by center alone still clips: actual triangle intersections with the plate, actual vertex separation in its Y Z region, and end renders must reject it.
2. A plate floats off wood: buried back face and actual body contact samples at the flat plate interior; edges beveled away cannot be counted as contact.
3. A larger plate overlaps the body strip: the complete top bound must stay below 0.150, and the reference angle must show no raised outlined overlap.
4. Mounting necks float or look patched: actual connected Boolean union and multiple ray samples through each neck plus a close end render; no separate block seam accepted.
5. The cover breaks when cut: manifold edge counts, positive connected volume, no zero area triangles or loose components. A finished outer shape with hidden disconnected fragments fails.
6. Grooves create stripes or jagged lines: true profile rows along each division, smooth curve normals and complete 2x finish crops. A dark painted stripe does not pass.
7. Lower sleeve becomes a pinched torus: exact derivatives after changing the groove profile, all cross sections circular around their intended varying radius, and a close ring view.
8. Heads float or clip the cover: actual plane seating and both end views; match measured counts and positions.
9. The new projection breaks frame limits: exact closed full turn width at most 6.700, and the original feet and floor gap unchanged. Never shrink the full chest to compensate.
10. Approved parts regress: compare every unaffected active vertex array against candidate20, and inspect the full front, both ends and rear. No changed crown, arch, band seam or diamonds.
11. Construction passes numbers but looks off: actual original image beside the complete rendered chest at the same overall scale, matching cover and plate close crops, then fresh scoped visual review. Numeric geometry cannot overrule a visible ring penetration.
12. Work crosses the break: save source and next action before long operations, check schedule before modeling and render, declare finite busy time. Do not start a render expected to finish after the work deadline.

Acceptance and scope
After approval, build in open Blender, save source and candidate21, validate all active solids and actual attachment checks, render the six directions, inspect all changed surfaces and ask one fresh reviewer. The plan returns to review if the attachment method fails. Two or three rounds without clear gain require diagnosis rather than another guessed size. This checkpoint does not approve the complete chest, all metal thickness, functional lock or opening rig. Those owner tasks stay in OWNER_FIXES.md. The detailed intermediate source may stay above the final mobile triangle guideline; report its actual cost and keep final optimization deferred until finished appearance.

Review log
APPROVED round 1, no blockers. Accepted numeric nit: widened grip reaches about Y negative 0.965, safely below the plate. Neck caps may stop 0.010 inside the cover axial end planes to avoid coplanar Boolean caps; the seating and visible shell remain as planned.

Numeric cleanup evidence
The first root cut creates nearly collinear microscopic Boolean faces. A test on a copy shows 0.000020 vertex and degenerate cleanup followed by triangulation retains closed manifold topology and positive volume, with minimum triangle area above 0.000000003. The volume changes by about 0.0000000014 in model units, below a visible feature. Restrict this cleanup to handle unions and cuts; restore the original helper afterward. This corrects numerical slivers, not the visible construction method. The actual render and fresh review still own the appearance. Evidence: candidate21/cleanup_probe.json.

Mirroring implementation
Build and validate the left cover once, then mirror its actual completed geometry and split normals for the right. Reverse reflected winding and prove that solid again. This follows the planned X symmetry and prevents independent Boolean roundoff from generating different slivers on the second end. The actual ring and plate clearance checks still run on both ends.

Reflection precision check
The reflected micro faces need 0.000040 cleanup before final normal generation. A copy test retains closed topology and increases the minimum triangle area to about 0.000000020 without changing the visible cover shape. Recompute the reflected stable curve normals after that cleanup. Evidence is candidate21/mirror_cleanup_probe.json. Do not weaken the area or closure validator.
