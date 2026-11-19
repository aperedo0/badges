# Plain wood board joints

Status: APPROVED (round2), construction phase2, board joint revision41.

## 1. What the owner will see

The current accepted complete3D chest keeps its shape and hardware. Its plain wooden surfaces gain clean shallow board joints: horizontal planks on the body and lid end faces, and lengthwise staves around the barrel roof. No grain, wood color, wear, metal finish, texture or final lighting is introduced. The owner explicitly withheld wood grain and metal finish and authorized everything else. The full reviewed rig and hollow cavities stay intact.

Build the shallow joints in the two existing wooden solids, inspect closed and open views, then save the accepted construction. These grooves represent fitted joints in an assembled wooden shell, not independently removable planks. Continuous uncut inner surfaces serve as a plain interior lining. No open decisions. Final appearance and mobile review remain deferred until the owner supplies finish instructions.

## 2. Reference and accepted source

Mockup: /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/reference.png. Read actual image and cropped wood regions. The body shows broad horizontal boards, not vertical slats. The barrel roof has multiple lengthwise boards following its curve. End cap wood has horizontal lines. Fine irregular scratches and grain in the image are material detail and are explicitly excluded. Hidden faces repeat coherent horizontal construction rather than fake perspective offsets.

Source: canonical treasure_chest.blend, identical to phase01/candidate40/chest.blend at closed frame0. Current construction40 is independently accepted, including the two cavities and real rear hinge. Static155 meshes and177892 triangles. Closed turn width6.675822, minimumY negative2.455, maximumY2.56575. The current object points already contain the32degree rest turn and height correction. Work only on Chest Body Envelope and Chest Barrel Lid Envelope, retaining their objects, materials, parents and rig. All153 other visible static objects, controllers, drivers, action and removable key remain unchanged.

LocalX is length, Y up, Z toward the front lock. Existing world38/local38 in phase01/tools/hinge38_geometry.py convert this convention. design.json beside this plan holds exact profiles and row positions.

Body: outer halfX2.55, halfZ1.60, inner halfX2.33, halfZ1.38, floorY negative2.0175, exterior bottomY negative2.2175, topY.3475. Three horizontal joints atY negative.35, negative.95 and negative1.55 form four visible rows between the metal rails. They continue across all four outside walls, hidden underneath the corner uprights. Looks right when the closed front, back and both end views show straight horizontal joints on wood only, without seams in the metal, open air holes or displaced hardware.

Roof: accepted ellipseY=.38075+1.9475*sin(a),Z=1.65*cos(a),0<=a<=pi. Eleven evenly spaced angle joints a=j*pi/12 form12 lengthwise staves around the actual roof. Each joint runsX negative2.36 topositive2.36, terminating underneath the outer hoop at centerX2.4275 and width.48. These longitudinal ends do not reach the exposed end cap facesX plus/minus2.60. Looks right when closed front, crown and rear roof views show regular narrow stave joints following the curve, never a faceted roof, radial end cap cuts or wavy lines.

End faces: three horizontal joints atY.90,1.40,1.90 on both external lid end facesX plus/minus2.60. Their ends meet the current curved outline, where the broad end arch covers them. Looks right when end views show horizontal planks within the arch and no cut floating past the actual wood contour.

Interior lining: unchanged body floor and walls, curved roof inside and closed end walls. Looks right when an open top view still shows continuous clean walls and floor with no roof cutter intrusion, holes, tiny strips or hardware inside the cavity. No seam is painted on any surface.

All wood remains below the existing metal bands and mounts. The metal outlines own their existing external silhouette, untouched. Geometry widths are symmetric aboutX andZ. Board positions do not attempt to reproduce the perspective image's asymmetric spacing.

## 3. Prior art and method

No finished approved wood V joint implementation was found in the required read only prior art search. Reuse the actual closed Exact difference and exterior corner normal preservation from phase01/tools/trim_interior35_live.py, and the newer double precision source_field36/transfer36/topology36 from phase01/tools/frame36_geometry.py. The accepted hinge cutting path in phase01/tools/hinge38_geometry.py and hinge38_live.py already includes negative38(cutter) in the surface field, which preserves source shading and gives new recess faces their proper normals. phase01/candidate40/REPORT.md records current acceptance; phase01/hollow35/PLAN.md describes the accepted cavity construction. No full chest regeneration or generic weighted normal modifier is allowed.

## 4. Actual joint geometry

Each joint is a closed triangular prism subtracted from the existing solid with Blender Exact Boolean. The triangle uses the actual local outward normalN and joint transverse tangentT at surface pointP. Apex isP minus.020N. The two exterior cutter corners areP plus.035N plus/minus.061875T. Thus the nominal intersection with the original surface is.045 wide and.020 deep, with sloping flanks about42degrees. This is a true V recess with explicit boundary rows, not a height field, texture, open line or thin raised strip. The width differs from general.04 bevel guidance only because these are deliberately narrow wood joints, not major metal edges; flank width exceeds.03. Visual checks own whether they read cleanly.

Body front/back: P=(0,level,plus/minus1.60), T=(0,1,0), N=(0,0,plus/minus1), prism alongX betweenplus/minus2.70. Body ends: P=(plus/minus2.55,level,0), T=(0,1,0), N=(plus/minus1,0,0), prism alongZ betweenplus/minus1.75. Cut each prism separately; their concealed corner intersections must remain closed and behind the uprights.

Roof atanglea: P=(0,.38075+1.9475*sin(a),1.65*cos(a)); N=normalize(0,sin(a)/1.9475,cos(a)/1.65); T=normalize(0,1.9475*cos(a),negative1.65*sin(a)). Prism alongX plus/minus2.36. Endface joints useP=(plus/minus2.60,level,0), N=(plus/minus1,0,0), T=(0,1,0), alongZ plus/minus1.80. Their depth.020 remains far inside the.220 endwall and.180 roof thickness. Minimum residual roof thickness.160; body and endwall thickness.200. Floors and mating faces do not change.

Capture original triangles, face attributes and per triangle corner normals before editing. Apply existing exact Boolean and bounded clean36 only. Source field contains the original mesh plus reversed cutter triangle normal fields. transfer36 retains the original.0008 distance and.75degree normal encoding limits, with new recess faces matched against actual cutter planes. No tolerance widening. Snapshot original geometry before changes. New helpers are development_only, hidden and never exported; no objects are deleted. Existing objects receive only mesh updates. All selection and development visibility restore in finally. Do not alter rig transforms while cutting at frame0.

## 5. Materials and app walkthrough

Every original material reference, graph, color, roughness, texture and UV set is retained. The source two wood cores have no UV textures. No coin names, lights, cameras, floor or reflections are added to export. Existing development lights are used only for inspection. Final metal and wood materials remain owner blocked, so this checkpoint is neutral geometry, not an attempted match to the mockup's lighting.

At rest, early turn, both ends and back, wood joints must remain recesses below the metal, without changing silhouette or exposing air. At half size the main chest and hardware silhouette stays readable; small joint lines may reduce naturally. At40points they need not resolve individually. No fine grain or emissive outline may create glitter. The lowest wood geometry remains the accepted plain surface, with no new bottom carving for the reflection. Final all angle phone checks, color acceptance and piece reduction remain required after finishes, with no current simulator rebuild.

## 6. Risks and checks

Every badge catalog items0 to29: existing stacked hardware and shape are preserved; grooves have designed vertices rather than raster grids; measured profiles replace tracing noise; rest dimensions and turn bounds remain unchanged; major forms remain readable; smooth source shading is transferred with hard V flanks; no textures, glow or colors change; hidden sides have matching construction; surfaces remain closed with outward normals; silhouette and floor surfaces do not change; no coin naming; all current driver and source files preserved. Check actual closed, both end, back, roof close and open cavity renders, plus geometry source and contract checks. Render full construction before a fresh scoped review. The plan does not claim unchanged material appearance in the app or final shippability.

Opened features: separate stacked parts keep their existing seating; no new overlapping external face is introduced. Symmetry uses exact paired normal directions and row levels. Fine marks concern the board recess width; no random roughness or grain is introduced. Skip traced enamel, colored enamel, bright colors, gems, glass and coin shell features because none changes here. This is an existing volumetric object, not a stacked badge recipe, so PIECES.json validation does not describe it; actual topology and shell checks own it.

Specific risks: cuts pass through the roof and open holes, prevented by depth.020 versus wall.180 and checked by residual wall witnesses plus unchanged inner surfaces. Roof cutters reach flat end faces and create radial lines, prevented byXextent2.36 and verified by source triangle comparisons on exposed endcaps. Roof profile angular sampling produces saw teeth, prevented by straight designed cutters and preserved ellipse normals, checked in the crown closeup. Adjacent cuts create Boolean slivers, bounded clean36 may repair only its existing tiny limits and the actual depth/width probes must still pass. A source normal field misses V flanks, prevented by negative cutter fields and fail on unmatched loops. Removing wood can uncover a hardware root, checked with mounts and bands visible in end and close views. Intersecting cuts carve away the inner corner, checked with exact cavity surface retention and closed positive volume. A stale generator changes metal or drivers, caught by hash equality on153 unaffected static meshes and the removable key, parent and driver snapshots.

## 7. Build checkpoints

1. Require the clean canonical40 file, frame0, active nonpaused run, no unexpected unsaved edits and matching source geometry. Save frozen40 hashes. Read the plan APPROVED status before modeling.
2. Build only the body joints, then topology and actual groove probes. Each affected solid must remain one closed connected positive volume mesh, Euler2, nondegenerate. Removed volume must be positive and below3percent of the original per core. A giant cutter or empty source must fail.
3. Build roof and endface joints. Recheck closed topology, residual roof and wall material witnesses and actual cavity absence. Preserve all original inner triangles as the same surface within.0008, plus correct normals. A through cut or altered inner wall fails. Exterior test points away from intended cutter volumes retain source geometry and normals. Named script board41_live.py owns these actual checks, including opposite wall and groove apex probes.
4. For every intended joint, a ray from outside alongN measures the recess depth within.0015 of its actual polygon source location, and transverse probes show an opening near.045 width within.004. At depth.010, center is outside current solid; at depth.030 center is inside material. Deliberately test the uncut source as a failure control for the missing groove. Do not infer whole solid containment from vertices. Rerun the existing phase01/tools/motion40_live.py against the saved41 geometry, retargeting only its candidate path. It must again pass all56 opening angles and99 action frames with zero unclassified collisions and all three meaningful failure controls. Actual cavity surface and material witnesses remain mandatory to catch a hollow wall bridged by a triangle. A source vertex can lie in material while its triangle crosses the empty cavity, so a vertex only shortcut cannot replace these tests.
5. Save isolated candidate41 only after checks. Render closed, both ends, back, roof close, an early turn and opened floor and lid views, inspect every capture, then fresh independent construction review. Also reduce whole chest images to416pixels tall and view4x crops of the joints to judge thin stripes, crawling or a scored rather than fitted board appearance. No promotion while a gate fails. Keep accepted40. If the method fails, return to the plan and review the method rather than accumulate candidates.

## 8. Budget and delivery

The construction already has177892 triangles; the two wood cores should add fewer than4000. Hard construction gate185000, no new textures or visible part count. This exceeds general mobile guidance because mechanical detail is still editable and the final appearance preserving reduction waits for approved finishes. Current155 static meshes retained. Save the complete scene beside the mockup periodically, not a partial object. No app code, production source, simulator install, global script security change or final animation.

Final geometry acceptance is the actual checks and fresh scoped construction review. Overall completion still requires the owner's materials, all angle phone finish review, a full review score of90andshippable and the final appearance preserving reduction. Do not mark this badge done at this stage.

## Review log

Round1 TURNED DOWN. Accepted blocker: a vertex only subset claim cannot establish triangle or solid containment in a hollow source. Removed that shortcut and required the actual existing full motion40 screen retargeted to41, all56 opening angles and99 frames plus its three failure controls. Cavity and source surface tests still apply independently. Accepted risk: inspect actual416pixel chest captures and enlarged joint crops, including an early turn, before accepting the board joints. New standalone numerical gates are not used to bypass a review round.
Round2 APPROVED, no blockers. Existing full motion screen and416pixel enlarged render review own the remaining checks.

Build diagnostic: the first width probe measured at0.001 below the opening and used a0.001 transverse grid. Actual double precision ray scans show the groove center depth0.020 and opening width0.044, versus0.0415 at depth0.001. The opening requirement remains0.045 within0.004. The checker now measures the opening at depth0.00001 with transverse samples0.00025 apart; no geometry or tolerance changed. candidate41/width_probe_diagnosis.json records this distinction.
