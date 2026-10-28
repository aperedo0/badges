# Emerald Trophy

The owner's reference is modeled as a complete coin in Blender through the live MCP connection. The cup has a curved bowl, layered mouth bands, two curled handles, a turned stem and pedestal, and raised acanthus ornament. Two fluted torches have twelve flowing metal flame tongues. The laurel sprays contain 28 primary leaves with modeled veins, joining stems, and berries. The emerald ribbon has curved front folds and shaped loose tails. Both emeralds have real crown facets and beveled gold settings. The back carries the complete matching sculpture.

The selected model is `mobile/emerald_trophy_badge_mobile.usdz`. The complete editable scene is `emerald_trophy.blend`. Earlier models remain in `previous/` and the numbered candidate folders. Candidate01 is the first app pass. Candidate02 improves ribbon folds and emerald readability. Candidate03 gives the field a deeper metallic green, removing the pale dielectric reflection seen under the Home light. `comparison.jpg` places the final native Home render next to the reference at equal visible coin diameters. `field_options.jpg` compares the softer and deeper green finishes; the deeper finish is selected.

The approved complete gold coin shell, its points, topology, normals, original UVs, brushing UVs, rim material graphs, and rim texture bytes are preserved exactly from Emerald Sprout. No rim highlights are painted or fitted. The app retains its original anisotropy, compact inner flashes, glint shield, studio environment, point lights, camera, floor, and reflection. The emeralds use ordinary physical materials with a small facet color fill, separate from the app's Diamond shader. The field maps contain only subdued intrinsic mineral variation.

The model passes the app contract checks and Apple's ARKit USD checker. Bounds are X and Y from minus 3.015 to 3.015, Z from minus 0.780 to 0.450. The spin axis stays centered at the approved casing center. All transforms are identity, units are meters, and Y is up. The round shell is closed. There are no lights or cameras in the USDZ, no degenerate triangles, and no zero normals. The matching back is an exact Y half turn of the front geometry and normals. `validation.json` contains the checks and final hash.

The file is 4,713,148 bytes with 76,172 triangles, using 18 combined relief meshes plus the casing. The triangle guideline is exceeded because the complete sculpture, fine veins, scrollwork, and folded ribbon are present on both faces. Resolution was reduced on small round details and hidden sheet undersides were omitted after Blender inspection. Physical device performance has not been measured. Maps are 512 pixels. The approved floating placement is size 0.96 and lift 0.56, putting the lowest world point at minus 2.455.

Native simulator validation passed at the front, from both sides, on the back, and through a complete recorded turn. The outlines were inspected at 4x using nearest neighbor crops. No detached bright dots, broken outer outline, or external bloom puffs were observed in these checks. The matching back, sides, ribbon folds, and reflection remain finished as the badge turns. `candidate03/full_turn.mp4` preserves the final turn. The geometry before and after the final field color change is identical.

The established coin rim is wider than the reference, and its highlights follow the fixed app studio. The fine cup ornament, leaf carving, and emerald facet arrangement are interpretations of the image at phone size. These are remaining visual differences rather than an exact reproduction. The reference's very fine surface marks were kept subdued to preserve a smooth appearance in the app.

The old temporary preview project was incomplete, so a separate private copy was restored under `preview/`. It uses the original renderer and Metal shader files. `setup_preview.py` restores all 13 custom entries, the approved shield brushing extension, and floating coin placement. The private app is named Badge Studio, with bundle identifier `com.antonioperedo.badgestudio.preview`. Its simulator is Badge Studio Preview. This separate identity prevents normal app builds from replacing it. The original app repository, its models, and its badge art were not written by this task. No commits or branch changes were made.

The private simulator build succeeded. Its existing FocusSessionManager unreachable code warning remains. No logic tests were added for this presentation task. A capture briefly failed when the disk filled. Automatic approval review rejected the broad cleanup script before execution because its chat moving and simulator deletion were outside the badge task. Space became available again and the captures completed. The owner then explicitly approved clearing only this trophy's generated build files. That scoped cleanup removed 507,334,656 allocated bytes from this task's temporary Xcode intermediates, indexes, module cache, SDK statistics cache, and compilation cache. The finished app, model files, Blender scenes, and captures were preserved. No chats moved and no simulators were deleted. `build_cache_cleanup.json` records the exact scope and free space readings.

```text
ScreenTime-UIOnly: BUILD SUCCEEDED
USD ARKit validation: Success
App contract validation: passed
```

Optional owner cleanup commands, if needed later:

```sh
/Users/antonioperedo/Desktop/screen_time/tools/sim/make-space
/Users/antonioperedo/Desktop/screen_time/tools/sim/make-space --restore "<archived chat file>"
```
