# Targeted iron surface refinement

Current selection is recorded in selection.json. Only the existing lower rim and its two already treated knobs are involved. The approved wood, other hardware and original Test plank master lighting are preserved. The isolated Bottom iron reflection review scene holds the selected warm studio setup. The owner alone approves the result.

Starting checkpoint: complete packed baseline.blend, captured live from P_iron_knobs. Git fe8e703 also restores that starting artwork. Original reference setup is preserved. New resources were not downloaded; cached official free surface data and the owner reference supply independent masks.

The existing material graph is extended, not replaced. Independent weather, pigmentation and roughness masks reuse separate scalar channels from ambientCG Metal025 and Metal003. Their rust colors are not used. Shallow marking shapes are extracted from rectified interior reference regions, excluding hardware and borders. Source RGB is not copied. This is an appearance driven interpretation of scale features, not proof that every source line is a crack. New relief uses a 16 bit map with a calibrated small bump distance. Only some marks affect exposed conductor coverage.

Existing broad physical hammering remains exact outside narrowly localized edge edits. Existing chip positions receive limited extra deterioration. Flat upper bevel facets use a mesh attribute for local wear. Lower facet changes that exaggerated the notches were reverted. Large legacy exposed stroke masks were reduced because they created prominent outlines. No gold pigment or emission is used. The existing three conductor and dielectric scale branches remain independently editable.

Reproduce authoring in a working copy with existing Blender and /private/tmp/chest_wood_env/bin/python: prepare_layers.py, build_candidates.py -- 05_combined, refine_balance.py, refine_integration.py, refine_bevels.py, combine_strongest.py, refine_mark_width.py, restore_pigment.py. Build scripts run inside Blender. The complete selected master already packs all required maps and geometry, so regeneration is unnecessary for editing or restoration. Float fields and before and after edge arrays remain available.

Rendering reuses ../iron_fidelity/render_candidate.py and ../lower_iron/render.py through a small adapter. Run IRON_FINAL=1 /private/tmp/chest_wood_env/bin/python render_batch.py 11_restored_pigment:iron:reference_lift. Other views: right, context. neutral is the diagnostic HDRI. Final renders use 128 samples. Files are cached by key, view and environment. Use a new key or remove only the specific cached render if changing parameters. Context materials are temporary render substitutions only.

Run validate.py in a fresh Blender with -- 11_restored_pigment. It compares the saved result against baseline, including exact wood, original UVs, hardware, transforms, original worlds and source lights, protected contacts and closed rim integrity. Broad surface vertices outside edge edits are exact. Review world changes are explicitly allowed. present.py 11_restored_pigment reference_lift builds the compact comparisons. Do not rerun initial guarded promotion on an already promoted scene.

The final marking mask narrows bright ridges through nonmaximum suppression. This addresses broad pale marks exposed by the full resolution comparison. Only the fine marking height and related exposure masks changed in that final pass.

## Temporary Shader AOV checks

The reusable aov_tools.py accepts existing Blender input or output sockets, records their sources and exports raw Color or Value passes through native OpenEXR files. It uses Blender 5.2 AOV collections, aov_name, compositing_node_group and file output media_type IMAGE. No production shader nodes or view layer AOVs are saved.

The iron adapter aov_iron.py reads the actual three layered base colors and roughness signals, conductor and oxide metallic constants, final oxidation and exposed wear factors, facet wear, pigment and relief data, final shading normal, geometric normal and existing surface alpha. There is no invented composite albedo or metallic field. Registered channels, target alpha scope and a tiny control render distinguish a valid zero metallic pass from an empty pass. The control reads the existing iron metallic value without modifying either production BSDF.

Run Blender with render_aov.py -- 10_defined_scale aov reference_lift for the preserved pre correction state, or -- 11_restored_pigment aov_after reference_lift for the correction. The same established render rig supplies camera, light, exposure and framing. Raw passes, statistics, source socket records, verification and beauty crops remain in aov/before and aov/after. aov_sheet.py before or after creates a compact comparison beside the original reference.

The AOVs exposed the unexpectedly constant pigment mask. Its 16 bit source had been clipped by an 8 bit conversion. Native precision loading restores color variation while all other authored fields remain byte identical. Valid metallic constants and functioning roughness, wear and relief signals were retained.

## Resumed reflection and scale cleanup

The latest selected master is 14_edge_review/master.blend. The previous 11_restored_pigment/master.blend is preserved as the exact resumed baseline. Only the existing new marking Bump node invert property changes in the material. Source maps, geometry, hammering, fine pits, pigmentation, roughness and coverage inputs remain unchanged.

Narrow warm area sources aimed at existing bevel reflections reveal damaged edges in the isolated review scene. They are linked only to the authorized rim and two small knobs. HDRI strength 0.35 preserves darker charcoal face contrast. Wide stronger lights washed out the face and were rejected. The weak facet exposure remap was not retained. No gold pigment or emission is introduced.

Use render_batch.py 14_edge_review:iron:edge_floor, with IRON_FINAL=1 for final samples. right and context use the same fixed lighting setup. resume_reference.jpg compares the resumed saved look to the selected look; lighting differs intentionally. mark_direction_comparison.jpg isolates only marking direction under identical lighting. resume_context.jpg uses temporary surrounding finishes. No original scene lighting or surrounding material is changed.

The lower reflection source long axis must remain horizontal. Projecting the horizontal axis onto an oblique aim plane tilted the long emitter into the floor and prop height range, creating a sharp bright wedge. The level option in edge_reflection.py prevents that. Existing AOV helpers were reused for six targeted signals in aov/edge_cut; no material boundary matched the artifact. Source orientation correction removes it. Saved source dimensions and pose are in the selected design.json.
