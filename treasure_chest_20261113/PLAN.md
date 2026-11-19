# First chest: complete form checkpoint

Status: APPROVED (full form round 2), phase 1 revision 2. The owner clarified that phase 1 must establish the whole chest shape, not only a box and lid. The old minimal checkpoint is preserved in phase01/candidate02. Build only rough solid forms and stop before surface detail.

## What is being built

One coherent, full volume chest with a rounded barrel lid, thick structural hoops, perimeter rails, corner uprights, substantial boot feet, projecting lock and hasp, a ring handle at each end, and rear hinges. Every side is built as an actual object. The image guides proportions and character; it is not a flat traced depth card. This remains a neutral material construction checkpoint with no plank grain, corrosion, gold finish, engraved ornament or fine rivets.

Reference: /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png. This is the first of the two chests. Existing model and dimension source: phase01/design.json and phase01/candidate02/chest.blend. Keep the closed body and barrel lid already built. Their actual local dimensions are width 5.20, depth 3.30, body Y negative 2.205 through 0.495, lid base 0.530, lid rise 2.050. Local X is length, Y up, positive Z front. Bake the 32 degree rest yaw into points and retain identity object transforms. Build in the open Blender, save treasure_chest.blend and candidate03. No object deletions and no app code changes.

## Whole form inventory and dimensions

1. Body and lid: preserve the existing closed beveled construction volumes. Wood panels are still continuous plain masses; later planks replace their surface construction without changing the approved whole form.
2. Four lid hoops: centers X negative 2.40, negative 0.90, positive 0.90 and positive 2.40; width 0.48. Each hoop follows the complete front to rear elliptical arch, not only its visible front. Inner profile is slightly inside the wooden lid; outer profile is 0.12 outside it along the ellipse normal. Solid side and end caps, edge bevel about 0.025. The hoops stop at the lid base and meet its perimeter rim. Their curves have 96 segments and smooth normals; cap planes remain flat.
3. Upper lid rim: a complete rectangular belt around the chest perimeter, Y 0.530 to 0.900. Inner half extents X 2.59, Z 1.64; outer half extents X 2.73, Z 1.78; small 0.06 corner chamfers and 0.03 edge bevels. The body top rail is a separate belt at Y 0.080 to 0.490 with the same extents. Preserve the 0.040 seam between moving lid and fixed body. The lower perimeter rail is Y negative 2.205 to negative 1.840. All three belts have the front, back and both ends, not only front strips. The core seam is 0.035; the exterior rail seam is 0.040.
4. Four corner uprights: solid L sections wrapping each local body corner at X plus or minus 2.60, Z plus or minus 1.65. Leg coverage about 0.36 along each adjacent face and thickness about 0.12, with a small overlap into the body. Span Y negative 2.16 through 0.49. Closed L profile caps and 0.03 bevels. The rails sit slightly outside the post faces, with corner armor covering the joins, so intersections do not share coplanar exterior faces.
4b. Central front body strap: a substantial closed vertical strip centered X 0, width 0.50, spanning Y negative 2.17 through 0.49, local Z 1.645 through 1.800. It continues behind the lock and meets a separate bottom cuff centered X 0, spanning Y negative 2.205 through negative 1.675, width 0.74, Z 1.780 through 2.000. Both are real beveled solids, with the cuff sitting in front of the lower rail and the strap buried just inside the wooden body.

5. Four proper boot masses: replace the four small foot guides in the current view. Foot bases remain at Y negative 2.455. Centers stay X plus or minus 2.36, Z plus or minus 1.43. A broad lower footprint about 0.80 square rises to a shoulder near Y negative 2.08 and tapers to a 0.58 square top near Y negative 1.56. Bevel the edges about 0.05. These are chunky angular boot forms, not little square pegs. Guide objects are retained hidden, not deleted.
6. Four lid corner armor masses: centers at local X plus or minus 2.36, Z plus or minus 1.43 and Y 0.75, dimensions 0.70 by 0.44 by 0.64 in X Y Z, around the hoop ends and upper rim corners. Simple beveled solids establish their thickness and outline. Add only the four major top bolt head masses at the hoop crowns, low domes of radius about 0.10 and height about 0.07. Fine rivet placement remains deferred.
6b. Broad lid end frames: both flat wooden end caps receive a full arched frame in their Y Z plane. Outer ellipse offset is 0.12 outward from the lid profile and inner ellipse offset is 0.24 inward, producing a visible 0.36 wide arch rather than a thin hoop edge. Extrude it 0.12 along X, centered at X plus or minus 2.64. Cap every edge and smooth the curved surfaces. The outer faces are at X plus or minus 2.70, outside the hoop end cap at 2.64, so their overlapping faces are not coplanar. Its lower ends meet the perimeter rim.

7. Front lock assembly: one broad mounting shoulder on the upper body; a closed shield plate about 1.68 wide and 1.75 tall, spanning Y 0.15 through negative 1.60, in front of the wood at local Z about 1.96 to 2.12. The plate is an actual solid with a real keyhole opening. The keyhole has a round upper lobe radius about 0.15 and a tapered stem to about Y negative 1.08, centered X 0. Use constrained planar triangulation only for this flat solid cap, with explicit outer and hole boundary edges, then build front, back, outside wall and hole wall. No image or relief field. Keep cap triangle edges coplanar and bevel only actual boundary or design creases, not interior triangulation edges.
8. Hasp: a simple projecting barrel hinge across X, radius about 0.14 and length about 0.78 near Y 0.64, Z 2.00; its support plate attaches to the lid rim. A 0.44 wide and 0.11 thick curved tongue descends from the hinge toward the upper lock plate. Sweep a closed rectangular profile along a smooth Y Z curve and close its ends. Keep a small real projection in front of the plate so its bend can be seen from the side. This is a solid hardware form, not a painted stripe.
9. Two side ring handles: one on each end, centered around Y negative 0.68, Z 0.00, local X plus or minus 2.84. The rings lie in the Y Z plane, major radius about 0.40 and tube radius 0.085. Use 64 around and 12 across tube segments, with real holes and smooth normals. Each gets a mounting plate on the side and a short barrel across Z near its upper attachment. Both ends have matching hardware. These handles sit inside the existing corner envelope in the reference view and must also pass full rotation bounds.
10. Two rear hinges: at local X plus or minus 1.55 on the rear face, with simple lid and body plates and short horizontal barrels. The back is the real back of a chest, not a pasted front latch. Their hardware stays within the structural frame envelope.

## Materials, scene and reference use

Use plain neutral construction materials with restrained lightness differences: lighter core, darker frame and medium hardware. Metallic finish, wood grain and small weathering are not judged now. No image projection, fixed highlights, normal map, emission, glass or gem shader is involved. Use actual solid volume, real bevels and smooth curves.

Keep the reference beside the complete model in Blender. The development lighting is fixed across views, with actual renders, AgX Medium High Contrast and a common camera. The mild perspective camera from phase01/camera_refinement.json can be reframed once for the enlarged full form. No independent width fitting. Include a top view to prove the real chest depth, plus a reference angle, straight front, both ends and back. A development floor or backdrop is never part of the shape data or any later USDZ.

Prior art: safe live connection and mesh updates from /Users/antonioperedo/Desktop/badges/camp_owl_mountain_sapphire_20261111/blender_link.py and the current phase01/tools/build_live.py. Closed sweeps and caps follow /Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools/meshkit.py construction principles; its unapproved visual crown is not a quality baseline. Every sweep has welded shared ring vertices and explicit solid end caps. Do not assume meshkit.sweep closes or welds them. Generate new pieces in local app coordinates, bake the yaw once and convert to Blender once. The existing core is already converted and is not transformed again. All prototype geometry is built live in Blender. The chest is a genuinely volumetric object, so the 2.5D enamel plate builder does not apply.

## Contract, joins and risks

All visible components must be individually closed and have positive volume. Front and rear caps, ring and keyhole walls must exist. Object transforms remain identity in the model. X and Z remain centered around the spin axis. Nothing may exceed Y 3.015 or fall below negative 2.895. The lowest feet remain at negative 2.455. Maximum projected width through an entire turn must remain below 6.70, checked by the largest radial envelope, not just the reference pose. Core plus frame is expected to be about 6.65 across. If any hardware exceeds it, move or resize that hardware locally instead of shrinking the entire chest without telling the owner.

The floor and reference are excluded from shape checks. No coin names. No runtime asset is shipped in this phase, and no app build or code edit is authorized for this unfinished chest. Both Ruby version apps remain intact in the simulator.

Specific checks and failures:
* Hoops and rails must wrap all the way around actual geometry. A front only relief fails the top, end and rear renders.
* The lid and body rails remain separate across the joint, so a fused cross seam belt does not imply an impossible opening mechanism. Check both end views.
* Boots must overlap the posts and body, without floating pieces or merely tiny guide feet. Check all corners from the underside and reference angle.
* Handle rings have actual central openings and correct end attachment. A solid disk or a ring passing through the wooden side fails the end view and closure checks.
* The keyhole has an open bore through the shield plate, with a dark cavity behind it, not a black painted mark. Check side lighting and a close view. Its hole walls must be closed in the manifold check.
* Triangulation follows outer and inner plate boundaries. Coplanar cap edges must not be beveled, and curved segments must not receive alternating hard normals. Inspect every important edge at 2x and 4x.
* Mounts, hasp, ring handles and rear hinges must meet the wooden core or structural frame with small controlled overlap. Exterior surfaces have no coplanar depth ties. Check the side and back views.
* Only four large top bolt masses are included now; they establish the highest outline. Fine fasteners, ornament and finish remain later work. Check upper Y bound after the domes.
* Empty band or torus ends, inside out caps and unfinished backs fail positive volume and edge incidence checks.
* Broad neutral clay must remain clean, with no grain, speckle, pinching or noisy traced outlines. The review is of the complete shape, not of absent wood and metal finish.

Full badge material and native motion acceptance remain deferred until those phases are requested. This is an expanded shape checkpoint, not a finished chest. No model bitmap is sampled in any material.

## Execution and acceptance

Approve this revised scope before changing the model. Build and save the expanded forms in the open Blender, preserving candidate02. Validate every solid, aggregate bounds, rotational envelope, transforms and counts. Target under 35000 triangles for this full form checkpoint, with no premature piece cap; the eventual final mobile target remains about 45000 triangles and 5 MB unless a justified exception is reviewed.

Render all six views and compare the reference pose at the same overall height with the first chest picture. Inspect the whole neutral model and important joins at 2x or 4x. A fresh reviewer judges phase 1 complete form and any missing major geometry. Do not ask that reviewer to excuse missing structural forms as a later phase again. Only surface detail and fine fasteners are deferred. Save the source, numbered checkpoint, validation, comparison and report. Stop for owner review before detailed wooden construction.


## Full form review log

Round 1: TURNED DOWN for missing central body strap and lower cuff. Added both explicitly. Accepted risks: specify corner armor centers, build broad end arches, cap and weld every sweep, convert axes exactly once, distinguish core and rail seams, and update the obsolete builder approval guard.


Round 2: APPROVED, no blockers. Build checks own actual boot rotation bounds, broad end arch overlaps and the lock mount/hasp connection.

APPROVED (full form round 2)

Construction inspection refinement: corner armor was hidden by the perimeter rim in the first full form render. Bring each lid cap to X center plus or minus 2.38 and Z center plus or minus 1.48, width and depth 0.76, Y 0.53 through 1.04. Add a matching body corner collar at Y 0.05 through 0.49, preserving the 0.04 opening seam. The same closed beveled solid method and aggregate bounds checks apply.

Join inspection refinement: the broad end arch outer offset is 0.08, underneath the outer hoop at 0.12. This removes overlapping coplanar curved exterior faces while preserving the visible broad end frame and the same closed sweep construction.

Fresh visual review of candidate03: construction clean and major forms complete, shape 88. Correct both ring handle outer diameters from 0.97 to 1.26, keeping their mounts engaged; clip all upper armor cube edges by 0.12 with a small real bevel; shorten feet to a top at Y negative 1.68 and broaden that top to 0.74; widen the lock plate silhouette by 10 percent without widening its bore. Same closed solid methods and bounds tests. Save as candidate04 and review again.

Owner requested further detail corrections after candidate04. Retain the body and lid volumes and band placement. Refine the same closed solid construction: three aligned shield layers with a shared real key bore, a stepped concave upper profile and rounded cheek transitions; larger bore and rolled hasp return with layered pivot collars; broadened handle mounts and pivots, slightly larger thick rings and lower sleeves; flare foot bases inward while retaining the outside envelope and shift upper sections onto the corner posts; peaked upper armor; tighter 0.018 lid seam; actual large domed construction rivets and upright diamond studs. Wood construction, grain, final material finish and mobile export remain later phases. Existing capped profile extrusions, welded closed sweeps and bevel methods remain unchanged. Preserve candidate04. Save as candidate05. The intermediate detailed source may exceed 45000 triangles; retain actual visible structure, record its cost and perform final mobile consolidation only when the whole chest is finished.

Lock inspection correction: the broad border is an explicitly lofted closed ring between correctly offset shield outlines. It has a real wide bevel rather than relying on a clamped edge bevel on many short outline edges. The aligned backing and raised face retain actual key bores. The same closed loop loft method already used for the boots and rails is retained. Intermediate source: 156 solids, 69572 triangles; final mobile reduction remains deferred until the completed model.

Candidate05 fresh review rejected sharp ring sleeves, excessive lock projection and faceted rivet shoulders. Cause checks use the untextured clay render and source topology: the artifacts remain without textures, separate angular collars create the wedges, and the original rivet outline has only 16 segments. Candidate06 changes those constructions: a single closed smooth ring with broad lower grip sections and shallow grooves; a thinner lock with the fastening ears on the backing, a separate pointed shield and a deep receiving U, with a true 0.095 broad bevel; smooth closed 32 segment rivet calottes with buried flat backs; wider mounts, exposed fastening heads, nested collars with smaller domed pivot ends, actual hasp edge rails, angled lower foot corners, end arch crown tabs and missing cuff/end bolts. Reduce vertical proportions 5 percent about the foot height instead of widening beyond the hard 6.7 turn limit. Preserve a baseline core and normals to prevent repeated scaling; transform corner normals by the inverse transpose. These remain closed profile, loft and lathed construction methods. The detailed source is intentionally above the final mobile geometry guideline and is not exported. Review actual Blender renders before returning it.

Candidate06 review: 86, not ready. The center grip groove creates the apparent pinch and the eight point boot section creates the unwanted narrow strip. Candidate07 removes the center groove, makes one broad continuous lower collar with two shallow border grooves, and uses four corner boot sections with real rounded edge bevels and a much shallower bottom transition. Shorten the hanging latch 23 percent and raise all aligned lock layers and fasteners 0.205, so the shortened rolled end sits captured in the receiving U; reduce its end projection. Increase barrel diameter 20 percent, add paired collars, make mount upper clips one sixth of its width, add shallow handle sleeve divisions, enlarge principal corner heads and seat them in real shallow circular bases, and raise small head projections by 25 percent. Preserve candidate06 as rejected evidence. Same closed geometry methods and actual rendered checks.

Corrective construction approach approved after two independent method reviews. See phase01/REFINEMENT08.md. Candidate07 is retained as rejected evidence. Candidate08 implements the approved contour preserving face grooves, reduced lock projection with unchanged domes and aligned bores, distinct hinge collars, localized lower foot corner clips and fine fastener seats.

Candidate08 clean finish passed; hardware fidelity 87. Candidate09 preserves the now clean construction and adjusts design details: shorten the upper hinge plate down to its lid base at Y 0.53, restoring a 0.155 gap above the receiver without lengthening the hasp; narrow the hasp 10 percent with its rails and rolled return; reduce end pin projection one third; enlarge main hoop heads 25 percent while keeping their dome proportions; make principal seats wider but very shallow; double the face groove widths and depths without changing the ring contours; expose the localized bottom foot clips with a narrower edge bevel; halve the lower apron bevel height. No new construction method, app or export changes. Preserve candidate08.

Candidate09 clean construction passed, hardware fidelity 88. Candidate10 addresses the three remaining findings: reduce both handle tube radii 20 percent and increase outer diameter about 8 percent, lowering their centers 0.08 so they remain engaged with the hinge; shorten each foot's upper slope from 0.30 to 0.20 while retaining its overall height; replace the clasp's separate lower cylinder with a genuine 180 degree center line curl, using an explicitly beveled eight point cross section. The curl radius 0.080 remains larger than the half thickness 0.055, so the inside never collapses. Caps and rails follow the same curve. Source remains detailed and no mobile export or app changes occur. Preserve candidate09.

Candidate10 review scored 89 and found two localized artifacts. Candidate11 excludes the outside folded bottom boot corner from the localized vertex clips, so that fold reaches the ground continuously. The curled strap tail turns about 157 degrees and pulls back 0.035 smoothly into the backing, burying the terminal cap and rail ends. Grip cuts become narrower and more defined with rounded roots, preserving contours. Shield bevel inset increases to 0.090 and its face to 0.084, retaining the required 0.006 overlap. Preserve candidate10 and save before rendering.


Owner detail correction pass, November 13
Owner detail corrections, November 13

The owner identified the upper corner armor, feet, hanging latch, end crown tab and ring handle hood as incorrect, and requested all rivet placements corrected.

Reference diagnostic and measured landmarks are saved in this candidate. Front and end fasteners use four corner dome centers as independent plane landmarks. The known visible counts are one upper end rail dome, one lower end rail dome, three upper front rail domes with the outer one smaller, and two lower front rail domes separated by the center strap. The outside hoops have sparse studding and the end arch has two slope domes plus its separate crown tab. The two middle hoops retain their denser four visible studs including the crown. Hidden sides use coherent matching construction rather than claiming the reference shows them.

The five hardware shapes are rebuilt with curved shoulders, flared tall feet with real inward lower side notches, a flat middle latch with a concentrated bottom curl, a true folded crown tab and deeper rolled handle hood cheeks. Both handle plate fasteners are exposed. The ring assembly is shifted toward the front on the end face from measured reference plate landmarks. The lower grip sleeve is broader with wrapped divisions. Lock backing and upper points address the previous independent findings.

Retain the detailed, neutral construction stage. Do not add wood, grain or final material finish in this pass. Save the canonical Blender file and numbered checkpoint after meaningful changes and before rendering. Inspect six rendered directions and the marked hardware, then obtain a fresh scoped review.


Hardware attachment and profile corrections
Correction pass after owner hardware review

Raise the bottom center rivet inside its plate. Lower and inset both handle mount heads on a rounded flat plate. Raise the foot heads. Keep the reference count and measured rail layouts.

Preserve a narrow continuous lid opening by keeping the mating seam edges on one plane rather than rounding them away separately. Add a real perimeter bevel to the folded upper armor. Reduce foot shoulder height and give that height to its main wall.

The lower grip now has a constant sleeve diameter with short shallow end divisions, not a swollen gradual thickening. Its oval centerline is shorter while the tube remains round, with explicit differential normals. Widen the hanging latch. Replace stacked washers with two rounded collar groups. Fit and widen the folded crown tab against the end arch. Round the fitted handle end cheeks. Narrow the shield bevel, retaining the 0.006 face overlap.

Source and numbered Blender copy must be saved before each render. Wood, wear, final materials and mobile optimization remain later phases.


Measured hardware method, approved round 2
The affected part of this plan is superseded by phase01/measured_hardware/PLAN.md, approved after an independent review corrected the upper mounting depths and hidden rivet seating. Follow that measured construction method for the five owner marked parts. The other phases remain unchanged.
