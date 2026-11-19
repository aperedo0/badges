Visible barrel and continuous latch edge correction

Status: APPROVED (review round 1).

Scope
Preserve candidate26 real pin, fixed knuckles, center sleeve, case, receiver and all surrounding chest. Correct visible strap attachment and stacked lower edge from fresh review. Reference /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png, candidate26/close_lock.png and finish_4x_hardware.png. Owner wants the large real horizontal barrel, strap below it and a hefty shield case. All geometry remains neutral clay. No materials, app or later wood work.

Cause and design
Current measured upper strap starts above the hinge axis and crosses the front of its center sleeve, hiding the barrel. Separate narrow raised edge rail solids also make doubled edges at the tight lower return. Replace only tongue and its two rails with one continuously lofted strap whose buried upper root attaches inside the lower sleeve quadrant. Keep moving sleeve and actual pin separate and unchanged. This reveals the horizontal center barrel rather than disguising it behind the broad strap. All fixed construction and release angle limit remain unchanged.

New post height centerline
Use chest local coordinates after the one time height adjustment, as mechanism25. X0. Actual hinge axis Y0.48525,Z2.000. New upper cubic centerline control points Y/Z (0.39525,2.050), (0.360,2.120), (0.300,2.170), (0.250,2.170), sampled20 points. Its first cross section is buried inside the sleeve. Keep only material outside the actual pin bore by the existing0.086 radius X cut. This is not an overlapping visible root cap. Straight centerline then runs Y0.250 through negative0.06575 at Z2.170,24 rows. Retain the measured lower bend: Y negative0.06575 minus0.08075 sin(a), Z2.085 plus0.085 cos(a), a0..pi/2,32rows. Returned tip stays Ynegative0.1465,Z2.085 through1.900,20rows. Cross bore remains radius0.032 atYnegative0.1465,Z1.970 alongX. Receiver and bolt dimensions stay exact.

One integral cross section
Width0.455, half thickness0.055, real corner bevel0.012. Make raised edge ridges integral to the front cross section rather than separate sheets. Cross section ordered around X and outward normal offset is: negative0.2155/negative0.055; positive0.2155/negative0.055; positive0.2275/negative0.043; positive0.2275/positive0.043; positive0.2215/positive0.057; positive0.2185/positive0.070; positive0.1985/positive0.070; positive0.1955/positive0.057; positive0.1905/positive0.055; negative0.1905/positive0.055; negative0.1955/positive0.057; negative0.1985/positive0.070; negative0.2185/positive0.070; negative0.2215/positive0.057; negative0.2275/positive0.043; negative0.2275/negative0.043. Every row follows the centerline tangent with X across and outward in the YZ plane. This is one closed swept piece with real raised borders.
Taper only ridge offsets above0.055 smoothly to0.055 over the last quarter of centerline arc length. Distinct X samples stay distinct at the end, preserving nonzero edges, even when the end cap contains collinear front points. Use the already tested collinear boundary triangulator and strict cleanup, not a fan that emits zero triangles. The final ridge ends flush in the main face, without separate exposed end caps or a second paper layer. Hide old edge rail objects, preserving their historical geometry. Record moving ownership as sleeve and tongue only.

Normals and solid proof
Preserve hard breaks across profile edges and smooth curvature along the centerline. Compute split normals by averaging adjacent longitudinal face normals for the same profile edge at each row, with separate flat end cap normals. Do not average normals across ridge edges. Cut the actual pin clearance at root and actual retaining bore at the tip with the proven safe Boolean helper. All final solids connected, closed and positive, no duplicate triangles, triangle areas above1e-10, intentional Euler topology only. The receiver minimum cross gap must be measured with the full0.070 ridge height and the new lower taper, not only the tongue base.

Checks and delivery within phase
Save candidate27 and complete root Blender source. Preserve every unaffected active mesh exactly against26 and full turning width at most6.700. Full0..60degree release must be collision screened against all fixed geometry and certified continuously with conservative bounds or remain explicitly unfinished. Existing certificate for26 cannot be reused for the new tongue; unchanged sleeve envelope may be reused only with source hashes proving all fixed and sleeve geometry unchanged. All case internal, hollow wood, rear hinge and full opening tasks remain pending.
Render reference, both ends and rear with guarded timer, inspect complete2x and4x lock. The center barrel must visibly read as a horizontal separate sleeve with the strap emerging below, no new root cap, black slit or doubled lower edge. Fresh scoped review before construction approval. Return to affected plan if this method fails. No simulator while construction is unfinished.

Pacing
Read schedule before major work. Save and defer when time is insufficient. No modeling or render during20minute break. No overall deadline.

Open decisions
None. This implements the reference barrel attachment and clean continuous latch requested by the owner.

Review log
APPROVED round1, no blockers. Accepted clarification: preserve returned centerline, terminal Z, bore center and radius, but replacement half thickness0.055 intentionally differs from the old compressed0.05225, so actual receiver gap must be measured. Outward normal is normalized cross product of centerline tangent with positive X. Restore final split normals after both Boolean cuts and cleanup, including distinct bore wall normals, because the helper rewrites triangles. Screen nonadjacent tongue triangles for self intersection at bends and tapered ridges; manifold and signed volume alone do not prove this. Candidate26 motion certificate remains incomplete and cannot be reused for the replacement tongue. Only unchanged sleeve envelope may be reused with fixed and sleeve geometry hashes.
