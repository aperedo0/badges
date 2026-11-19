Owner directed joint correction

Status: APPROVED. One independent scoped review found no blockers.

The owner now explicitly rejects slanted lower bevel edges, the remaining gaps at upper corner and foot joints, the open space behind the end arch, and vertical stud misalignment. These instructions supersede the former deliberately clear corner seam. The screenshot pair shows the foot shoulder still reading as a separate cap after the solid union. Replace the entire foot assembly with one measured closed loft, rather than continue combining sheets and a wedge.

Foot construction
Use the already measured front and end outlines to recover the minimum X and Z at each height. The outside main planes remain X magnitude 2.775 and Z magnitude 1.865. Use one eight point chamfered rectangular cross section per height; the inner bounds follow the measured step and flare, and the outside bounds stay constant over the main riveted face. Use the same horizontal height for every vertex in each ring, with bottom Y negative 2.455 and shoulder break around negative 1.705. This makes horizontal edge rows level through the folded corner. The owner also rejects the second visible seam near the base. Remove that separate bottom bevel band; the main faces continue directly to the level closed base. Keep the vertical corner chamfers, which do not create a horizontal seam.

Build the full filled body from bottom to shoulder in one mesh. Include the upper shoulder in that same mesh. Its final two rings lead to the existing top footprint at Y negative 1.525, outer X 2.690 and Z 1.780, inner X 2.080 and Z 1.170. Around the shoulder break add two close profile rows over about 0.040 in Y, blending from a vertical main face to the sloping shoulder. This is a true physical curve, with no separate cap, coplanar patch or air space. Round the vertical cross section corners with chamfer about 0.040. Connect equal indexed rings, cap the bottom and top, recalculate outward winding, and prove closedness, positive volume and absence of zero area triangles.

Shading
Use exact surface normals on each longitudinal strip. At each row take the tangent along that cross section edge and the derivative of its vertex along height; their cross product is the strip normal. Split normals at intentional cross section chamfers, use a smooth height derivative through the shoulder bend, and keep both horizontal caps flat. This keeps the broad main faces planar and avoids a dark artificial stripe at the join. Check actual rendered near and far feet, both ends, bottom and oblique view. Do not infer success from watertightness alone.

Other owner corrections
The upper corner bottom and body collar mating edge are now level and unbeveled at their actual join; the collar extends to Y 0.465 against the plate bottom at 0.460. Its outside mounting planes meet the upper plate at X 2.775 and Z 1.875. No open joint is intended. Preserve the visible knobs and their real contact. The upper collar top edge must not be rounded away into a new gap.

The end arch retains its outer face at X magnitude 2.755 but its back extends to 2.590, overlapping the lid's end face at 2.600 by 0.010. The two end arch rivets use the actual radial midpoint, offset negative 0.160 between inner negative 0.400 and outer positive 0.080. Each upright diamond is centered between the upper collar bottom at 0.020 and the foot top at negative 1.525, hence center Y negative 0.7525, before the common height conversion.

Build checks
No other badge, app source or approved asset changes. Build in the open Blender and save after each geometry correction and before rendering. Restore the immutable core before the one common height adjustment. The foot remains within the current turn envelope; maximum X and Z do not increase. Validate its mirrored copies, identity transforms, minimum Y and maximum turn width at most 6.700. Match the owner screenshot angles and inspect the exact seam the owner flagged. The new solid must show no separate cap line, slanted bevel baseline or floating stud.

This corrects only the failed foot assembly and explicit owner join instructions within the measured hardware plan. Crown tab, latch, metal finish and later phases retain their existing scope. No final app or performance approval is claimed.

Review: APPROVED with no blockers. Checkpoints own the actual seam, upright contact, mirrored winding, closedness and bounds. The top footprint is extended slightly inside the existing main bounds to cover the actual upright rather than leaving its outer edge unsupported.
