Fitted crown tab correction

Status: APPROVED (review round 1).

Scope and references
Preserve the continuous arches, lid bands, reviewed corner and rail joins, feet and all other candidate19 geometry. Correct only the two crown straps and their hanging head origins. Original reference is /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png. See owner_examples_20261114/reference_crown_tab.png and candidate19/arch19_crown_tab.png, finish_2x_1.png and slit_pixel_diagnosis.json, all relative to the chest root or phase01 as appropriate. Candidate19 still fails its scoped visual review. The complete source stays open in Blender, neutral clay. No wood, final materials, lock, handle, rig or app work is included here.

Cause proved
The source ray test of the dark image pixels 860,162 through 880,166 first hits the tab at its exposed return end plane X 2.500, before any arch behind it. The apparent slit is the shadowed vertical cut end, not proof that the sampled underside is detached. The existing 0.070 thick plate makes that plane broad and dark. The tab bottom also uses radial offset negative 0.400, while the visible arch front inner boundary is negative 0.375 because the back bevel occupies the last 0.025. These are geometric causes. Preserve the new single surface arch, its analytic normals and its curved inner edge.

Construction
Use the approved draped closed x and radial offset profile method, with 17 samples across its width, both sides mirrored in X. Source is phase01/tools/arch19_live.py, crown_strap. The same ellipse normal offset function supplies every Y at the actual Z. Do not flatten a return, change lighting, paint shadows or add a hidden patch to cover an opening.

The inner top remains radial 0.178, the inside bend radius 0.083 about (X 2.670, radial 0.095), and hanging inside X 2.753. These retain the 0.002 seat into the actual arch. Reduce the normal strap thickness from 0.070 to 0.040. Outer top is radial 0.218, outer bend radius 0.123, outer hanging face X 2.793. Keep the complete fold and its physical thickness.

At the free return end X 2.500, taper the OUTSIDE top down to radial 0.179, just inside the arch top 0.180. Leave the inside top at 0.178. From X 2.500 to 2.560 use 12 intervals of the smooth profile r = 0.179 + (0.218 minus 0.179) times smoothstep((X minus 2.500)/0.060). At X 2.560 continue flat radial 0.218 to the bend at 2.670. This buries the tiny cut face in the arch, replacing its exposed black plane with a real forged taper. The thin terminal geometry stays hidden, so it cannot create a bright outline. It is one connected closed strap, not an added lip. Contact faces and their edges stay unbeveled; exposed external edges retain 0.010 bevels where the shape allows.

The hanging outer face bottom is radial negative 0.375, matching the visible arch front inner curve. Its back edge is negative 0.377 at X 2.753, following that actual inner bevel. Across the 0.040 thickness interpolate this bottom contour. For each x define bottom_r = negative 0.377 plus 0.002 times clamp((x minus 2.753)/0.040,0,1). Use this same local bottom_r to calculate the width taper progress. Top Z limits remain negative 0.142 and positive 0.322. Bottom Z limits remain negative 0.033 and positive 0.255. The entire bottom stays curved by the same offset ellipse, not a constant Y cut. Give its cap a real closed wall and inspect whether the outside bevel leaves a short or drooping edge.

Move each crown face head nominal origin X magnitude to 2.795, seating its buried back in the new face 2.793. Keep radius 0.083 and Z 0.051. Center Y at the matching curve for radial negative 0.140, halfway down the visible straight face. Preserve head counts and actual contact. Other roof and arch heads retain candidate19 positions.

Checks and risks
1. The former dark pixels must no longer see the broad X 2.500 cap. Recast those camera rays against the new source and inspect the far tab render. A changed material or merely smaller shadow without correcting the exposed cap does not pass.
2. Actual return end points are buried below the arch top, including outer width edges. Test actual beveled geometry across 17 width samples. Retain the existing top, fold and face tests, adjusting only head and bottom dimensions. A mid span contact pass cannot excuse the return end.
3. The lower front curve must align to the visible arch edge after bevel. Compare actual minimum radial coordinates at the visible front and inspect a matched close render from the reference angle and both ends. A tab that reaches the back minimum but makes a notch on the front fails.
4. The slim buried end can collapse: preserve positive minimum thickness 0.001, no duplicated points, connected closed topology, nonzero triangle areas and positive volume. Cap triangulation uses the clean x and radial outline. Thin geometry is buried, never an exposed glitter edge.
5. Bevels can pull a contact away: exclude all mating surfaces from edge bevels, sample the actual final mesh and inspect the far return with side lighting.
6. The new taper can produce a crease: sampled smooth profile, analytic drape, smooth along the curve and split intended boundaries. Inspect whole 2x images and 4x crown crops.
7. A later rebuild can change the arch: compare every unaffected active vertex array and triangle array with candidate19. Keep the single height conversion and old archives.
8. The narrower plate can leave floating heads: verify buried bases and a real mounting face, then view both ends.

Execution and acceptance
Build in owner open Blender after approval. Save candidate20 and root source after geometry and before render. Validate all active parts and hard bounds. Render six complete views with the fixed development scene. First inspect surfaces, then get a new fresh scoped review. Do not declare the chest finished; only this crown correction is being reviewed. If the draped construction itself fails, return to this affected plan. Stay inside the 30 minute block and save the exact next action before the break. All final materials, app and mobile catalog risks remain deferred to their later phases, per the previously approved neutral construction plan.

Review log
APPROVED round 1, no blockers, risks or nits. Source ray diagnosis and the visible inner bevel boundary were independently checked.
