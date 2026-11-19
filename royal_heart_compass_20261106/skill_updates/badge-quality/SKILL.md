---
name: badge-quality
description: Build, refine or review 3D badges against owner references, with particular attention to small sculpted details, genuine metal and gem behavior during rotation, clean outlines, finished backs and a final reduction of rendering pieces without changing the finished appearance. Applies to badge work in Blender and the simulator preview, including daytime and overnight builds.
---

# Badge quality

Make the badge match the owner's reference in the actual preview, including when it turns. Read the workspace AGENTS.md for the app contract. Work on copies of approved files. This skill adds quality checks; it does not set a schedule, grant renderer permissions or replace the owner's instructions.

## Reference detail

Compare the complete silhouette and the small features at the same size. Count and place feather layers, leaves, flames, ribbon folds, settings, facets and ornament marks from the actual reference. Generic substitutes accumulate into a visibly different badge. Model the forms and overlaps in Blender, with the complete frame or shell present. Inspect back and side geometry too.

Use intrinsic surface maps for material color, inclusions and intentional fine brushing. A photograph of a polished object contains lighting as well as material: copying its highlights into a texture does not create reflective metal or a real gem. If reference appearance fitting is used elsewhere, identify it honestly and keep it off gemstones that must respond physically to motion.

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

Check for paper creases, mottled normals, harsh internal glint lines, seams and texture filtering at narrow tips. Keep real folds or weathering only where the owner or reference calls for them. Inspect every long edge, tip and cutout at four times size, together with the previous version. Finish the back and side walls in the same material language as the front.

## Build for appearance, then reduce pieces

Use as many separate modeling pieces as needed to make the badge match the reference, including its smallest details. Do not simplify the design early to meet a piece count. Real app and shader limits still apply.

Once the complete badge looks right in the native preview, save that detailed version as an immutable comparison baseline. Before delivery, perform a final optimization pass that seeks the same exact appearance with fewer meshes and material sections. Start by combining compatible surfaces that already share a material and rendering behavior. There is no default piece cap. If the owner supplies a target, seek it without altering the appearance; report a conflict rather than silently sacrificing detail or claiming the target was met.

Preserve the geometry, silhouette, relief, bevels, explicit normals, UV sets, textures, material graphs, finish, placement and animated material behavior. Keep independent optical stones and runtime recognized geometry separate wherever their renderer requires it. Do not flatten the badge into a picture, remove small features, reduce texture quality or bake moving reflections to obtain a smaller piece count.

Compare the optimized copy against the detailed baseline in the actual app, with the same lighting, size and poses. Check rest, early turning, both sides, back, reflection, outlines and a slow complete turn. Confirm the intended badge is visibly selected and the intended model loaded. File checks alone cannot prove the same appearance: changing batches can change native highlights or shadows even when triangle attributes match.

Accept only reductions that preserve the finished appearance. Reject or undo a batch that changes it, while keeping any independent reductions that pass. If a badge is already compact or no further reduction preserves its look, retain its detailed version and state the count and reason. Do not force a number or promise that every badge can be reduced. Report meshes, material sections and file size before and after; claim a measured speed improvement only after measuring it.

The finish pass is part of completion for new badges and visual revisions. On an overnight run, it remains inside the existing work blocks and breaks. Deliver the reviewed compact asset and an editable checkpoint of that same asset, and preserve the detailed baseline. Read [the final optimization procedure](references/finish-optimization.md) when performing this pass.

## Acceptance in the preview

Verify the actual 3D model loaded by observing a turn and its reflection. Compare the resting front with the reference at equal size. Review an early small turn, a quarter turn, both sides, the back and a slow complete rotation. Inspect gemstone highlights relative to their facets over several nearby angles with the studio held fixed. They must respond to angle, not remain glued to a reference image.

Judge beauty and reference fidelity separately from technical validity. Before delivery, put every final badge beside its mockup at the same size and look for obvious differences in silhouette, proportions, cut, cloth, metalwork and small details. Actual 3D can naturally change lighting and perspective, but a generic substitute for the reference is unfinished. The badge must look deliberately finished and attractive from every angle, with coherent color, volume, materials and detail on its front, sides, top and back. A convincing front alone, valid meshes or successful shader attachment cannot satisfy this review. Preserve the owner's rejected versions as evidence and address the stated visual problem before calling the badge complete.

Capture enough real frames to judge the transition. If a recorder repeats frames or a gesture skips the early turn, fix the capture before declaring success. Use native simulator captures when tool resizing hides detail. Record uncertainties plainly; image measurements and mesh validators cannot replace looking at the result.

Deliver the reviewed model, editable Blender checkpoint, a short comparison and any required private preview integration patch. Preserve production code and approved sources unless the owner authorized changing them. Do not declare a badge complete while its motion, required sides or final optimization review remain unchecked.
