# Bottom iron test for owner review

The owner limited this transition to the bottom portion beneath the approved wood. Only the existing Lab Chest Lower Rim is developed. The approved BC wood, other wooden surfaces, feet, uprights, cuffs, rivets and brass retain their original geometry and materials. Context renders use explicitly temporary surrounding shaders.

Git checkpoint 2ae680c captures the complete live scene after the current render finished. Fresh Blender restoration verifies exact approved wood geometry and all artwork required images packed. The existing wood scripts and numerical heights remain in Git ancestry. baseline.blend and live_before_iron.blend preserve the source and immediate live state. The approved BC master is not overwritten.

## Retained surface

09_pitted_iron is the selected initial test. It combines a dark metallic body, restrained hammer impressions, fine pitting adapted from official CC0 ambientCG Metal055A, and sparse pits from Metal003. Base color, metallic response, roughness and 16 bit height are independently editable. Exposed edges use neutral warm iron, with no golden paint or emission. Source and license links are in resources/SOURCES.json.

The existing rim surface is adaptively tessellated with matching shared edge subdivisions. A few larger dents and chips use actual geometry; secondary forming and pitting use a separate bump layer. Identical relief is not applied to both. Original anchor coordinates, outside dimensions and rivet contact areas are protected. The editable master has 98672 vertices and 98736 faces on the target rim. Numerical rest positions and deformation data remain beside the master. This is an editable art master, not an optimized export.

## Controlled trials and diagnosis

The flat iron control, native professional materials and custom surface trials used the same camera, source lights, exposure and AgX look. The first forged texture was too granular. Closed angular stamps looked artificial. Broader eroded bands looked crumpled. A quiet alternative lost too much surface character. Dedicated TextureCan hammered maps were more natural close up but produced cloudy, stone like reflections at whole chest scale, so they were rejected. The retained finish returns to the earlier pitted iron with less fine grain and protected physical edge geometry.

White light, warmer key and low reflection strip diagnostics were also rendered. The strip demonstrated reflected color changes but made the entire band too bright and flat. It is not retained. Existing scene lighting remains unchanged. The reference's warm edge appearance cannot be attributed entirely to one material or light from a single image; no such claim is made.

## Review and remaining differences

reference_comparison.jpg compares corresponding lower iron crops at comparable apparent width without stretching. baseline_comparison.jpg holds lighting fixed against flat iron. close_views.jpg shows both bays and the approved wood. chest_comparison.jpg shows the complete reference alongside the isolated temporary context. Full resolution renders remain in the selected folder.

The reference has sharper irregular forge scars, more broken plate formations and richer golden edge reflections. The selected test is still rounder in several dents and has cooler exposed highlights under the preserved lights. It is an initial material candidate for owner review, not a claim of exact reference fidelity or finished iron. Repeated isolated changes produced regressions; the owner chooses the next refinement before this finish reaches any other component. Brass is not developed in this round.

No paid resource, installation, image generation, app change, subagent or AI reviewer was used. Failed trials remain locally cached. Git preserves the complete baseline, selected editable scene, required source maps, numeric authoring data, scripts and comparisons; rejected scene caches are excluded.

## Saved delivery verification

Final 1600 by 800 Cycles closeups at 64 samples, the 1400 square contextual render, the reference crop, both bays and the flat control comparison were opened and visually inspected. The selected master is saved and loaded in the owner's existing Blender, with the final closeup displayed in the existing secondary image window. The original reference editor and main camera framing remain. All scene lights, environment and color management remain unchanged. Validation passes on the final saved file. Its fingerprint is in 09_pitted_iron/validation.json. The approved BC master is byte identical to owner commit c7c3034, and the prework baseline is byte identical to Git checkpoint 2ae680c.

The new iron work is saved but uncommitted for the owner's normal review workflow. prepare_commit.sh stages only this round's scoped files. Unrelated badge work, existing camera notes and external cleanup deletions are excluded.
