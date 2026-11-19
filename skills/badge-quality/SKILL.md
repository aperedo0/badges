---
name: badge-quality
description: Standing quality rules for 3D badge work, used alongside the badge-plan, badge-build and badge-fresh-review workflow rather than in place of it. Covers working in the owner's open Blender, judging in Blender before the simulator, small sculpted details, real metal and gem behavior while turning, clean outlines, finished backs, and the final pass that reduces rendering pieces without changing the look. Use when refining a badge's look, when a gem or metal looks wrong while turning, and before delivering any badge.
---

# Badge quality

Make the badge match the owner's reference in the actual preview, including when it turns. Read the workspace AGENTS.md for the app contract. Work on copies of approved files. This skill adds quality checks; it does not set a schedule, grant renderer permissions or replace the owner's instructions.

## Reference detail

Compare the complete silhouette and the small features at the same size. Count and place feather layers, leaves, flames, ribbon folds, settings, facets and ornament marks from the actual reference. Generic substitutes accumulate into a visibly different badge. Model the forms and overlaps in Blender, with the complete frame or shell present. Inspect back and side geometry too.

Use intrinsic surface maps for material color, inclusions and intentional fine brushing. A photograph of a polished object contains lighting as well as material: copying its highlights into a texture does not create reflective metal or a real gem. If reference appearance fitting is used elsewhere, identify it honestly and keep it off gemstones that must respond physically to motion.

## Close, not exact

Owner rule, November 8, 2026: the badge does not have to match the mockup exactly. A real 3D object under the app's light will differ in highlights, reflections, depth and colors the app cannot show, and that is fine. Match the design: shapes, proportions, parts, line work and colors as close as the app allows. Never spend rounds chasing exact pixels or a painted look.

## Build it like the real object: stacked pieces

A badge is made of several pieces, and that is the right way to build it. Each visible element is its own solid with real thickness and beveled edges, and pieces sit on top of each other the way the mockup shows: a back plate, the rays on it, the sun on the rays, the mountains in front of the sun, the clouds and border in front of them, a gem in its frame on top. Pieces may overlap and stack; nothing needs cutting.

* Never build the badge as one flat plate with painted color areas and small bumps for lines. On November 8, 2026 the Mountain Sunburst's rays and wedges were built that way: its gold lines rose about 2 phone pixels, light smeared across them, and the owner saw fuzz at once and asked why a 3D badge was flat.
* Make every edge big enough to see: steps between pieces about 0.03 to 0.08 units, bevels at least about 0.04 units wide (3 screen pixels at rest) at about 45 degrees. Smaller relief does not read as an edge; it reads as blur.
* Each piece carries its own gold rim when the mockup outlines it, so lines come from real bevels, not from paint.
* Use the house side wall technique for the visible sides of each piece (AGENTS.md section 4).

## Start from an approved plan

A new badge or a rebuild starts with a written plan (the badge-plan skill) that fresh reviewers approve (the badge-plan-review skill). Build exactly the approved plan. When a checkpoint fails because of the method, return to the plan instead of tuning the build round after round (owner rule, November 8, 2026).

## Build it in the owner's open Blender

Every badge is built in Blender, in the open window the owner can see, never only in files or scripts. The owner wants to open Blender at any time and find the badge being worked on, the way they watched Codex work (owner rule, November 8, 2026).

* One saved Blender file per badge, in its working folder, named after the badge. It always holds the current version: the model, its materials and the mockup as a reference image beside it.
* Build and change the badge in the live Blender through the connection (the Blender MCP bridge), so each step appears in the window as it happens. Scripts may create the parts, but they run inside that open scene.
* A background Blender is only for heavy steps that would freeze the window. Load their result into the open scene right away and save.
* Working on several badges: open the file of the badge being worked on now. Save it before switching to the next badge's file, so every badge's file stays complete and openable.
* Save after every meaningful change. Update a version by replacing the geometry inside the same objects (`mesh.clear_geometry()`, then rebuild); never delete objects (on November 8, 2026 the open Blender closed twice right after a loader deleted objects; a strong pattern, not a proven cause).
* If Blender closes, reopen the saved file with the connection on (`Blender <file.blend> --python <bridge start script>`), wait for ports 9876 and 9877, tell the owner, and carry on. Do not rebuild from scratch.
* Tell the owner which file is open and where the others are.
* **Never overwrite the owner's unsaved changes** (owner rule, November 14, 2026). Before loading anything into the open Blender or switching its file, check `bpy.data.is_dirty`. Since every step of ours ends with a save, unsaved changes mean someone worked in the window by hand: stop and ask the owner whether to save or drop them. `badge-build/scripts/build_live.py` refuses on its own; one off scripts must check first.
* **Two connections run in the open Blender.** The community bridge on port 9876 (`blender_link.py`) builds and loads, as before. Blender's official MCP plugin (Blender Lab, v1.0.3) runs on port 9877 as the Claude Code server `blender-official`. Use it to look up the Blender 5.2 Python API and user manual offline (`search_api_docs`, `get_python_api_docs`, `search_manual_docs`) before writing any call you are unsure of, instead of guessing from older Blender versions; and for scene summaries and window or area screenshots. Both start from `tools/start_official_mcp.py`, which the start scripts run; if 9877 is not listening in an open Blender, send that file through the 9876 bridge.

## Judge in Blender during development

Owner rule, November 12, 2026: develop and judge the badge from actual renders inside Blender. Keep the complete current badge and its reference together in the open Blender, render the front, both sides and back, and compare the design, depth, materials and small details there before exporting a candidate for final app review. A viewport capture or a valid mesh does not replace inspecting a finished render.

Reserve the simulator for final judgments once the complete badge looks ready in Blender. Do not use repeated app builds and simulator captures as the routine design loop. If a final app check exposes a specific lighting, material or motion problem, fix it in Blender and repeat the relevant final check. The app remains authoritative for its own runtime optics and lighting, but this does not move ordinary design work out of Blender.

For gems that use a custom app shader, give the Blender development material the same optical model and parameters before judging the cut or body color. Verify camera ray direction, light map orientation and sample colors against that shader's equations. Record remaining renderer differences for the final app check.

## Geometry follows the design

Build every part from its outline. Put vertices along the outline, each bevel and each ridge, so the triangle edges follow the lines, and make lines and bevels smooth curves with even widths rather than traced pixel edges. Tracing a mockup is a good way to find the outlines: turn the traced outlines into clean curves, then model from the curves.

Never lay a fixed grid of triangles over a traced picture or height image. Every line crossing the grid becomes a tiny zigzag that catches the light as fuzz or glitter. On November 8, 2026 three enamel badges built that way reached the owner with fuzz along every gold line; the owner called them atrocious and far from shippable. Check new geometry by drawing its triangles over a 4x crop of the reference before building materials on it.

## Gems during rotation

A gem's outline and cut move with the badge. Its reflections, internal light paths, bright facets and glints respond to the badge's new angle under the fixed studio light. A UV map following the object is necessary for intrinsic marks but does not prove the optics work.

For a colored gemstone, review the body color from the front through the complete turn. Small changes in saturation and brief bright facets are natural, but turning must not drain most of the stone's color or make it broadly colorless. Compare several nearby angles, both side views and the back. Diagnose the actual cut, optical path lengths, absorption, surface reflections and incomplete ray paths. Keep the optics responsive to light; do not preserve color with a reference picture or fixed emission.

Use actual gemstone shading for the owner's realistic gems: light reflection, refraction, internal reflection and color absorption through real faceted geometry, or another renderer that produces equivalent moving optics. Do not use a reference photo, painted highlight, fixed emission image, scrolling picture or unrelated sparkle animation as the gem's appearance. Emission computed by a runtime optical shader is different from a fixed emission texture.

For the local convex gem renderer, export each stone as a separate closed convex mesh with flat facet normals and identity transforms. A disconnected collection of stones or a concave outline cannot be traced as one convex gem. Split a concave design into genuinely convex stones with joins hidden by its setting, or use a renderer that supports that shape. Check the actual facet plane limit and material names in the current renderer; preserve the approved Diamond contract.

Check the renderer precision at thin tips. Valid geometry can still develop chipped facets when plane coefficients lose precision during upload. Preserve sufficient coefficient precision and verify the outline in motion.

Confirm the runtime shader actually attaches to every intended stone. A material name or a successful file check alone is not proof: a failed convexity check can silently retain a plain fallback material. Record attachment evidence and inspect motion. Keep ordinary materials available as honest file fallbacks. Document any runtime integration required by a custom shader; a USDZ alone does not carry RealityKit shader code.

For gemstone work in the owner's Badge Studio, read [the local gem renderer reference](references/badge-studio-gems.md) for the existing optical path and its precision requirements.

## Metal and surface finish

Check polished metal at rest and through the first small turn. It should have believable light and dark reflections before spinning and change continuously rather than jumping from dull clay to chrome. Glints must come from the real surface and light. Do not change the shared studio to compensate for one badge. A metallic value already at one cannot be increased another percentage; adjust the actual finish and judge the result.

Check for paper creases, mottled normals, harsh internal glint lines, seams and texture filtering at narrow tips. Keep real folds or weathering only where the owner or reference calls for them. Inspect every long edge, tip and cutout at four times size, next to the previous version to catch regressions, but judged against clean. Finish the back and side walls in the same material language as the front.

## Build for appearance, then reduce pieces

Use as many separate modeling pieces as needed to make the badge match the reference, including its smallest details. Do not simplify the design early to meet a piece count. Real app and shader limits still apply.

Once the complete badge looks right in the native preview, save that detailed version as an immutable comparison baseline. Before delivery, perform a final optimization pass that seeks the same exact appearance with fewer meshes and material sections. Start by combining compatible surfaces that already share a material and rendering behavior. There is no default piece cap. If the owner supplies a target, seek it without altering the appearance; report a conflict rather than silently sacrificing detail or claiming the target was met.

Preserve the geometry, silhouette, relief, bevels, explicit normals, UV sets, textures, material graphs, finish, placement and animated material behavior. Keep independent optical stones and runtime recognized geometry separate wherever their renderer requires it. Do not flatten the badge into a picture, remove small features, reduce texture quality or bake moving reflections to obtain a smaller piece count.

Compare the optimized copy against the detailed baseline in the actual app, with the same lighting, size and poses. Check rest, early turning, both sides, back, reflection, outlines and a slow complete turn. Confirm the intended badge is visibly selected and the intended model loaded. File checks alone cannot prove the same appearance: changing batches can change native highlights or shadows even when triangle attributes match.

Accept only reductions that preserve the finished appearance. Reject or undo a batch that changes it, while keeping any independent reductions that pass. If a badge is already compact or no further reduction preserves its look, retain its detailed version and state the count and reason. Do not force a number or promise that every badge can be reduced. Report meshes, material sections and file size before and after; claim a measured speed improvement only after measuring it.

The finish pass is part of completion for new badges and visual revisions. On an overnight run that uses breaks, it stays inside the work blocks. Deliver the reviewed compact asset and an editable checkpoint of that same asset, and preserve the detailed baseline. Read [the final optimization procedure](references/finish-optimization.md) when performing this pass.

## Acceptance in the preview

Verify the actual 3D model loaded by observing a turn and its reflection. Compare the resting front with the reference at equal size. Review an early small turn, a quarter turn, both sides, the back and a slow complete rotation. Inspect gemstone highlights relative to their facets over several nearby angles with the studio held fixed. They must respond to angle, not remain glued to a reference image.

Closeness is gated by badge-fresh-review (shippable and 90 from a fresh reviewer); your own comparison here never replaces it. Judge beauty and reference fidelity separately from technical validity. Before delivery, put every final badge beside its mockup at the same size and look for obvious differences in silhouette, proportions, cut, cloth, metalwork and small details. Actual 3D can naturally change lighting and perspective, but a generic substitute for the reference is unfinished. The badge must look deliberately finished and attractive from every angle, with coherent color, volume, materials and detail on its front, sides, top and back. A convincing front alone, valid meshes or successful shader attachment cannot satisfy this review. Preserve the owner's rejected versions as evidence and address the stated visual problem before calling the badge complete.

Capture enough real frames to judge the transition. If a recorder repeats frames or a gesture skips the early turn, fix the capture before declaring success. Use native simulator captures when tool resizing hides detail. Record uncertainties plainly; image measurements and mesh validators cannot replace looking at the result.

Deliver the reviewed model, editable Blender checkpoint, a short comparison and any required private preview integration patch. Preserve production code and approved sources unless the owner authorized changing them. Do not declare a badge complete while its motion, required sides or final optimization review remain unchecked.
