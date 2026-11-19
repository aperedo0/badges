# Final badge optimization

Use this after the badge already matches the owner's intended appearance. The objective is the same exact look with fewer rendering pieces, not a simpler design. Keep the detailed original and work on a copy.

## Combine compatible surfaces

Inventory the exact current asset: mesh count, effective material sections, geometry attributes, texture assets and runtime lookups. Meshes and material sections are different costs. Joining different materials into one object with many subsets may reduce objects without reducing drawing sections. Do not claim a frame rate improvement from counts alone.

Batch surfaces that share the same effective material and compatible rendering properties. Preserve each oriented triangle corner's position, normal, every relevant named UV set and other attributes, and its effective material. Preserve winding, transforms, visibility, culling, subdivision behavior and any relevant hierarchy. Welding is appropriate only where all required render attributes agree; preserve normal and texture seams. Keep the original material graphs and texture bytes when possible.

Identify geometry that must remain separate before merging. In BestSpent, preserve the recognized coin casing and inset, their names, topology, UVs and material bindings. Preserve the brushed field material used by Crimson Shield. Each optical stone remains its own closed convex mesh with the names and facet limits required by its shader. Do not combine disconnected stones into one optical mesh. Read the workspace app contract and the gem reference for the actual current rules rather than guessing from object color.

For USDZ, verify relative asset references and named primvar readers survive packaging. Export a fresh USD crate after deleting old mesh payloads, rather than retaining dead arrays through incremental saves. Repack without changing image data. Preserve source metadata and runtime names. Use the available USD and ARKit validation tools, plus a comparison of material assignments and rendered triangle attributes before and after packaging.

The local examples `astral_compact_20261104/` and `badge_family_compact_20261106/` in the badge workspace demonstrate this method. Their compactors have asset assumptions and review exclusions. Inspect and adapt them to a new badge; never blindly rerun an old installer or modify its approved finals.

## Prove the appearance survived

Use the complete optimized model in Blender for working inspection. The final native preview remains authoritative. Hold the studio, camera, size, placement and actual turn angle fixed when comparing original and optimized versions. Do not compensate for a changed finish by altering lights or repainting highlights.

Verify the displayed badge title and silhouette before capturing. A matching cached file hash alone does not prove that file is the badge on screen. Confirm actual 3D rotation and reflection rather than accepting fallback art. Measure or visually match the actual scroll pose; a requested gesture can be partly dropped or leave a menu row outside the visible area.

Review front, early turn, both sides, back and a slow full turn. Inspect fine edges and local differences at four times size. Check metal contrast, highlight width, glints, gem optics, depth, outlines, back details and reflection. For optical gems, confirm shader attachment to every intended stone and its reflection where used. A lower count and equal attribute hashes never override a visible mismatch.

If a reduction changes appearance, reject that batch or keep the approved original. The Steel trial in the local family pass preserved triangle attributes but changed native highlights; keeping its already compact two mesh original was the correct result. This is an example of the acceptance rule, not a blanket exclusion of future Steel designs.

Finish with the reviewed final model, a complete editable checkpoint of that model, the preserved detailed original and a short comparison. Check that packed checkpoint images match the intended asset and required names survive. Report before and after mesh counts, material sections and bytes, accepted reductions and any retained parts. Keep runtime, production integration and permission boundaries unchanged.
