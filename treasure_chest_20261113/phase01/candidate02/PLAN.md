# First chest: phase 1

Status: APPROVED (review round 1). Only phase 1 is authorized in this turn. This is a shape checkpoint, not a completed badge.

## 1. What the owner will see

A plain solid chest with the reference's broad rectangular lower body, separate rounded barrel lid, visible left end and four simple corner foot guides. The owner asked for the first, less decorated reference. Neutral clay materials make the proportions readable. Individual planks, grain, metal straps, latch, handles, rivets and final finishes belong to later phases and are not part of this checkpoint.

Build order: body and lid dimensions first, foot position guides second, then actual Blender renders from the reference angle, straight front, ends and back. Stop after this phase. Do not install this unfinished chest into the simulator. The simulator remains on the Home Screen with the two Ruby Heart version icons visible.

No owner decisions remain open for this limited phase. Dimensions are a measured starting point for the owner to inspect, not a claim that the entire chest is reference matched.

## 2. Reference and proportions

Reference: /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png. Original: /Users/antonioperedo/Downloads/3914ffb2-f5d0-44c7-8280-263a55f60668.png.

Measured approximate full object bounds in the 1254 square picture: X 74 to 1184, Y 176 to 1084. Width to height is about 1.22. The lid to body join passes near Y 540 to 580, and the visible left end occupies about 29 to 31 percent of the overall width. The curved lid is a barrel extending along the long width axis, not a hemisphere or dome of revolution.

Model axes: X long width, Y height, Z depth with the front toward positive Z. The complete chest is symmetric in its own construction axes. Bake a 32 degree positive Y yaw into vertex positions for the visible left end at rest. No pitched geometry or off center spin axis. Blender display uses the same coordinate conversion as the Ruby Heart loader: (X, negative Z, Y).

Initial local dimensions, in app units:
* body width 5.20, depth 3.30, bottom Y negative 2.205, top Y 0.495, height 2.70;
* lid width 5.20, depth 3.30, bottom Y 0.530, crown rise 2.05, top Y 2.580;
* lid cross section: Z = 1.65 cos(theta), Y = 0.530 + 2.05 sin(theta), theta 0 through pi, with a flat bottom closure; 96 segments;
* a real 0.035 separation around the lid to body join;
* four guide feet centered at local X plus or minus 2.36, local Z plus or minus 1.43, width and depth 0.80, bottom Y negative 2.455, height 0.65. These overlap the lower body as location masses, and do not represent finished metal feet;
* at the 32 degree rest yaw the widest unrounded foot envelope is about 6.62, body envelope about 6.16, both centered on X and Z. The construction leaves the future lid band and rivet top below Y 3.015.

The complete image inventory for later phases is wooden body and curved lid, four arched lid straps, perimeter rails, vertical corner straps and boot brackets, the central hinged hasp and lock plate with an actual keyhole, side ring handles, rear hinges, round rivets and two small front strap diamonds. These details explain the reference outline, but they are deliberately deferred.

## 3. Prior art

Read only research found no approved chest or barrel lid. The closed sweep and cap methods in /Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools/meshkit.py are useful construction primitives, but that crown was not owner approved and its visual design is not a quality baseline. The phase 1 lid uses the same explicit closed profile principle, implemented directly in the live Blender API so its end cap and edge bevels are editable.

The successful live connection and safe scene construction approach come from /Users/antonioperedo/Desktop/badges/camp_owl_mountain_sapphire_20261111/blender_link.py and /Users/antonioperedo/Desktop/badges/ruby_heart_smooth_20261112/tools/load_live.py. Build a new scene and keep old scenes untouched. Do not delete objects. Repeated changes update a mesh in place or use a new version collection.

## 4. Construction in the open Blender

1. Create a dedicated Chest Phase 1 scene in the newly opened Blender. Units are meters with scale 1. Keep the mockup as a packed reference image beside the model.
2. Body: one closed box with six faces, dimensions above. Apply actual 0.06 bevels with three to four segments. Broad planes keep flat normals; bevels are smooth. This is a temporary construction volume that establishes the later plank envelope.
3. Lid: extrude the closed elliptical D profile across the long X dimension. Both end caps and the flat bottom are closed. Use actual 0.05 bevels around the two end rims and the front and back bottom ridges, not every narrow curved segment. Smooth only the curved surface and bevels, preserving flat end caps and the bottom. No rectangular mesh sampled from a picture, displacement map or painted depth.
4. Feet: four closed 0.80 square guide boxes with simple 0.06 bevels. They are separate objects with Guide in their names. They locate the final boots without building their metal finish or bracket shape.
5. Bake the rest yaw and coordinate conversion into all six meshes. Keep every object at identity transform. The lowest guide points stay at Y negative 2.455 in app space. Do not add coin casing or material names.

Save one editable working file at /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/treasure_chest.blend, and a numbered phase checkpoint. Previous Ruby sources and the new reference original are never overwritten.

## 5. Development materials and staging

The body and lid share neutral clay, base color about 0.32, metallic zero and roughness about 0.45. Foot guides are a slightly darker neutral. No emission, wood texture, image projection, brushed normal maps or weathering in phase 1.

Use fixed neutral studio lighting with a large upper left key, soft fill and back light. The reference camera is a mild perspective from the positive model Z side, about 8 degrees above the center, with the chest's yaw supplying the visible left end. Seed camera distance 20, sensor width 36 and lens about 103 for a field width near 7 units. Render 1100 square with Cycles and AgX Medium High Contrast. The development floor is at the app floor height of negative 2.895 so the standard 0.44 model gap stays apparent. Camera and floor remain Blender development objects only.

A second straight front and direct end view remove the reference angle's foreshortening from the proportion check. Camera matching may refine the seed lens and framing, but not silently stretch the model independently per view.

## 6. Contract and every angle

Today there is no USDZ or app build: an unfinished chest is not ready for final simulator judgment. Precheck all closed shape meshes in model coordinates, positive signed volume, identity transforms, no coin names, width no greater than 6.7, top no greater than 3.015, bottom no lower than negative 2.895, X and Z bounds centered. Six meshes must stay inside the declared envelope. The floor, cameras, lighting and reference image are excluded from those measurements.

Render the reference pose, straight front, both ends and back with the same light and camera distance. A missing cap fails an end view; an incorrect barrel direction fails the front and end views; a squat or tall body fails the side by side and the unforeshortened front; an off center yaw fails bounds and a turn. A 40 point silhouette check tests whether the lid and body division remain readable, not whether absent hardware is finished.

## 7. Risks and checks

Every badge checks, scoped to phase 1:
* Flat relief, noise crossing design lines, wobbly contours and wrong proportions: explicit box and swept D profile, measured dimensions and silhouette comparison. The broken result is a flat card, rounded blob or hemisphere.
* Thin unreadable features and profile crawling: actual bevel widths 0.05 or 0.06; the lid division is the only small seam in this phase. Check the complete form at real size and 2x or 4x. The failed result is a broken highlight or dotted rim.
* Curved surface facets, missing faces and inside out patches: smooth curve normals, flat caps, closed solids and positive volume. Check end renders and outline crops.
* Speckle, plastic finish, color mismatch, bright halos, painted gradient banding, white blobs, washed out colored cells, brushed side streaks and flat field flashes: this phase uses plain neutral clay and no final appearance claim. Final wood and metal checks are explicitly reserved for phase 5; the current neutral shader must itself remain free of noise and clipping.
* Unfinished back, floor merging and dangerous lower detail: full volume closed back and ends, plain lower construction, standard gap and all side renders. The failed result is an open box or an intersecting floor.
* Misplacement, slow load and wrong UV sets: coordinate and bounds checks now; texture and native load checks are deferred because no texture or app asset exists yet. Keep phase 1 below 6500 triangles, final target below 45000 triangles and 5 MB unless the owner accepts a reason.
* Missed transition defects and partial review: rotate through the development views, inspect the whole outline, get a fresh scoped shape review. Do not call this phase a shippable finished badge or claim an overall mockup closeness score.
* Process: use the live bridge, actual Blender renders, saved checkpoints, and no object deletion. A failed construction method returns to this plan rather than repeated app builds.

Opened feature sections: separate solids, symmetric construction and smooth curves. Closed overlaps at feet are intentional guides. Keep seam surfaces separated by 0.035 to avoid coplanar flicker. Geometry follows continuous profile curves; no thin lips or random trace noise. Do not use a mirrored screenshot to demand the asymmetric reference perspective itself be symmetric.

No gems, glass, enamel inlays, saturated color finish, fine marks, traced gold curls or coin shell are built in phase 1. Their catalogs do not apply to this limited shape checkpoint.

Chest specific risks:
1. Wrong barrel direction: use the Y Z D profile extruded along X; both end renders must show one arch over a horizontal base.
2. Lid too flat or circular like a pipe: compare the crown rise and join fraction, retaining separate 1.65 depth radius and 2.05 rise parameters.
3. Wrong left side exposure: seed yaw 32 degrees from the reference's side to front ratio; compare the actual rendered joint locations, not only its outside box.
4. Model grows beyond the frame when boots or handles arrive: foot guides establish the approximately 6.62 maximum envelope now; future phases may not grow outside it without an explicit new bound check.
5. Feet mistaken for finished boots: label them as guides in the file and phase report, keep them plain, and do not model rivets or plating in this phase.
6. Neutral blockout mistaken for finished wood or metal: every presentation is labeled Phase 1 shape only; future appearance and hardware remain pending.
7. Reference cap shape is obscured by the end band: infer the underlying continuous arch from the visible wood and compare a matching angle plus a direct end view. Never copy the metal thickness into the wood profile twice.

## 8. Checkpoints and scope stop

Checkpoint A: prove the Blender bridge and viewport capture before building.
Checkpoint B: build six closed masses, save the complete scene and run geometry bounds and closure checks. The check must reject an intentionally removed cap or an out of bounds point when exercised on a temporary in memory copy.
Checkpoint C: render all five views, compare reference pose at one common scale with the mockup, inspect outline at 4x, and obtain a fresh review scoped to body, lid, depth and foot locations. A low material or hardware score is not a phase 1 failure because those are absent by instruction.
Checkpoint D: save the phase source, render comparison, validation and a short report. Stop before phase 2 and present the shape to the owner.

No repeated app builds or additional phases are authorized by this plan. A construction failure changes the affected plan section and gets a fresh plan review; numerical adjustments within the approved shape method belong to the checks.

## 9. Budget

Six simple shape meshes; target below 6500 triangles. A packed reference and a compressed Blender file, no runtime textures. Zero chest app builds during this phase. The later completed chest gets its final USDZ, optimization and full native finish review after all five phases are authorized and complete.

## 10. Phase acceptance

Accept this phase when the complete shape is closed, clean, framed correctly, shown in five actual Blender renders, compared with the reference, independently reviewed for its phase scope and saved. This does not mark the chest complete or approved for the app. Ruby Heart V1 and V2 remain accessible in the existing simulator throughout.


## Review log

Round 1: APPROVED, no blockers. The reviewer confirmed the closed body, capped barrel lid and guide feet are sufficient for phase 1. Build checks own the seam appearance after bevels, perspective side exposure and the maximum rotational width of about 6.623. Later hardware must stay inside the reserved envelope and receives its own bound check. Top clearance is 0.285 and the intended floor gap is 0.440.

APPROVED (round 1)


Phase 1 numerical refinement after the first render: lower body height 2.70 and lid bottom 0.530 retain the same 0.035 seam and all construction methods. The reference camera is refined to about 4 degrees elevation and distance 45, with lens and vertical aim calibrated once to the common silhouette height. These are the dimensional and camera refinements explicitly assigned to the build checks; there is no method or scope change.
