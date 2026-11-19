# Continue the existing bottom iron

Read ../../PROJECT_STATE.md and REPORT.md first. Selected editable scene: P_iron_knobs/master.blend. Owner review is pending. Do not apply this material elsewhere. Original Test plank master lighting is preserved; Bottom iron reflection review isolates the alternative reflection environment. Existing secondary image window shows the selected Cycles closeup.

Checkpoint 546d617 stores the complete starting scene. baseline.blend is its packed live snapshot. Do not rerun guarded initial promotion on an already promoted result.

## Reproduction

Use Blender 5.2.2 and existing /private/tmp/chest_wood_env/bin/python for NumPy, SciPy and Pillow. Existing helper ../lower_iron/render.py and ../../phase04/wood_lab/render_batch.py supply the original rig. No paid tool or install is required.

Authoring order is material_masks.py, build_layers.py, prepare_relief.py, planish.py, build_relief.py with G_planished_hires_displaced, reference_laps.py, and build_response.py with K_reference_laps, then darken_scale.py. The selected oxide base color is scene linear (0.012, 0.009, 0.006); conductive values stay unchanged. Each Blender build script takes its key after --. Final candidate generation starts from the cached earlier scenes; regenerate those only if required, using the names in these scripts. Existing baseline data is authoritative. Rebuilds must be reviewed before any promotion.

Rendering: IRON_FINAL=1 /private/tmp/chest_wood_env/bin/python run_candidates.py P_iron_knobs:iron:studio3. Other views are right, context and full. current preserves the source lighting, neutral uses the diagnostic HDRI, studio3neutral removes warm light tint. context uses temporary surrounding material substitutions; full preserves actual assignments. Results are cached by name. Render locks serialize GPU work. Do not overwrite a cached result with changed settings and assume it was rerendered.

Run validate.py in a fresh background Blender with -- P_iron_knobs after saving. present.py P_iron_knobs creates the four owner comparison sheets. The complete master contains packed required images, physical geometry and editable shader controls. Authoring float fields and before and after displacement data are retained separately.

## Retained parameters

The selected coating mixes from 0.60 to 0.92 coverage, preserving sparse intermittent exposed wear. Blackened iron is conductive, exposed iron is conductive, opaque scale is dielectric. Coarse field encoding spans 0.010 scene units with midlevel 0.8, fine encoding spans 0.004 with midlevel 0.5. Physical displacement samples the original float coarse values directly, with protected contacts. Coarse bump strength is zero in the physically displaced candidate. Fine bump distance is 0.004, shallow scale 0.00035, reference lap bump 0.003. These are artist calibrated settings in existing scene units, not measurements inferred from the reference.

Neutral studio reflections plus a small warm key and raised warm fill are isolated from the original scene. No golden edge paint. See environment.py for exact reproducible settings and resources/SOURCES.json for licenses.

## Avoid repeating failed work

Do not repeat professional cloudy height replacement, low density displacement, full range patchy oxide coverage, broad warm wash lights, repeated global strength tuning, closed polygon stamps, or global noise detail. Tests and full resolution outputs remain locally; rejected scene caches are excluded from new Git staging. Further meaningful improvements concern deliberately sculpted angular formations, not more fine detail.

The owner additionally authorized the two small front knobs on the textured lower strip to use the same iron. apply_iron_knobs.py makes local mesh copies, retains their shape and transforms, adds matching physical scale UVs and assigns the existing shared iron material. N_charcoal_scale/master.blend remains the complete checkpoint before that request. P_iron_knobs/master.blend is the current checkpoint. Do not transfer the finish to other knobs or components.
