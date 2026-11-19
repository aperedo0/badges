Body metal thickness correction

Status: APPROVED (review round 1).

Scope and reference
Owner requested visibly thicker lower rails and corner uprights, preserving the reviewed continuous arches, crown tabs, corner joints and alignment. Reference /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png and owner_examples_20261114/thin_upright.png, thin_lower_rail.png, reference_body_strip.png. Current complete scene candidate23, neutral construction only. No material or app changes. This step is separate from unfinished lock mechanics and opening rig.

Method
Keep every exterior metal face and the closed chest silhouette fixed. The current widest armor already uses almost the full 6.7 rotational width. Instead make real thicker metal backs, and recess the wooden body by 0.050 on each side so the increased depth is visible next to the wood. Body half width goes from 2.600 to 2.550, half depth 1.650 to 1.600, about two percent. Heights, outer metal silhouettes, lid wood, corners, feet and every rivet remain unchanged. This is the body inset under its existing armor, not a smaller chest. The owner already requested greater physical projection; no new decision or phase scope.

Body implementation
Always restore immutable core_baseline first. In local chest coordinates apply body X scale 2.550/2.600 and Z scale 1.600/1.650 only to Chest Body Envelope. Preserve Y and inverse transpose its split normals. Lid envelope remains untouched. Then continue the normal builder and common height adjustment exactly once. Store actual new half extents in the candidate design metadata for future hollowing. Do not alter core_baseline.npz.

Metal implementation
For Chest Body Upper Rim and Chest Lower Rim only, change inner chamfer rectangle half extents from 2.590 and 1.640 to 2.540 and 1.590. Upper Lid Rim retains original inner dimensions. Outer dimensions and rail heights and bevel .028 are unchanged. Inner body rail surfaces overlap new wood by .010 on flat walls. The rail front depth becomes .190 rather than .140 and lower end depth .190 rather than .140; upper end depth .140 rather than .090. Preserve chamfer .060 and closed ring topology.
Corner upright outline remains the same at exterior X 2.720 and Z 1.770. The local L shaped six vertex cross section changes only its interior flat edges from X 2.590 to 2.540 and Z 1.640 to 1.590. Broad legs still extend to X 2.240 and Z 1.290, with outside faces fixed. This retains .010 overlap into wood, grows actual front and end depth .180 rather than .130, and preserves original bevel .030.
Central Lock Strap keeps front Z 1.800 and back moves from 1.645 to 1.595, overlapping body .005. Side handle mounting plates keep face X magnitude 2.810, bounds Y and Z, head locations and bevel, but back moves from 2.595 to 2.545, overlapping new wood .005. Ring and cover are unchanged. Corner collars and feet already overlap this wood envelope and remain unchanged. Rear hinge leaves remain seated on unchanged bands. Do not move exterior fasteners. The functional shield case will be built as its own later step.

Proof
Before render, strict all solids, area, volume, identity, top height and full turning bounds stay in force. Verify every unaffected active mesh is exactly unchanged, with geometric surface comparison for rebuilt Boolean covers if needed. Allowed changes are body envelope, two body rail rings, four corner uprights, central body strap and two handle mounting plates. Actual ray tests at several flat wall locations must show wood half planes at 2.550 and 1.600, rail inward planes at 2.540 and 1.590, upright inward planes likewise, central strap back 1.595 and plate back 2.545. Measure metal projection from actual outer faces to adjacent actual wood at front and both ends. Require closed contacts and no exposed see through gaps. The lower rail top and center cuff top remain aligned, and upper band stays in front of lower band. Compare reviewed joint surfaces unchanged.

Appearance
Save complete source and candidate24. Render reference view, both ends and rear using guarded live renderer, inspect all views and 2x tiles against original reference. Metal must visibly read thicker at its exposed edges; no new floating plate, missing wood, bright sliver, outline change or seam at feet is acceptable. Fresh scoped review judges only this construction improvement and its side effects. All final materials, lock motion and phone checks remain pending. No claim of completed chest.

Pacing
Read schedule before operations, save before render, defer when insufficient time remains and do no badge work in the twenty minute break.

Review log
APPROVED round 1, no blockers. Accepted visual risk: extra depth must visibly read at exposed rail and upright edges in equal size renders; numeric change alone is not acceptance.
