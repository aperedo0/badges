# Targeted iron surface character

Owner review pending. Scope remains the existing lower reinforcement and the two small knobs already assigned iron. Approved wood, other components and original scene lighting are preserved. Git fe8e703 and the complete packed baseline.blend recover the starting artwork.

## Diagnosis and retained changes

Identical warm and neutral Cycles comparisons were used. The broad hammer field was useful and was not strengthened or regenerated. The remaining appearance differences included sparse fine scale character, a prominent older exposed stroke mask, quiet dark face reflections and smooth edge deterioration.

The existing conductor and dielectric scale material was extended with independently adjustable weathering, pigmentation, roughness and shallow surface marking layers. Separate cached scalar channels supply the weather masks. Source rust colors are not used. Interior reference feature shapes guide a new marking mask, with the rivets and bright border excluded. Reference RGB is never copied into base color. The shallow scale interpretation is an artistic hypothesis; a single image cannot establish the physical cause of every line.

Only selected portions of the marking mask affect exposed conductor coverage. Other marks contribute shallow normal relief and roughness variation. A final high resolution check exposed broad pale marking shapes. Nonmaximum suppression narrowed only their profiles, with broad weathering and geometry fixed.

The older broad exposed stroke mask was reduced to prevent bright outlines from dominating the finer marks. Large hammer impressions remain unchanged.

Existing chip positions receive localized edge deterioration. Small upper bevel facets provide real reflective slopes, with a mesh attribute controlling exposed wear. A lower facet trial made the notches too prominent and was reverted. All broad face vertices outside localized edge edits are restored exactly to the starting mesh, including protected hardware contacts. Original UVs and topology remain unchanged.

Neutral versus warm renders distinguish material variation from illumination. The retained warm review world uses the existing studio HDRI and fixed warm source lights, with a restrained neutral to warm environment tint and stronger environmental reflections. These conditions are applied identically to the baseline and selected candidate. Only the isolated review world changes in the saved scene; Test plank master retains its original world and lights. Edge hue comes from reflections, not gold paint or emission.

## Regressions rejected

The first marking height was too raised and cratered. It was reduced and bracketed to a shallow 0.00055 scene unit bump distance. This is an artistic setting, not a measurement inferred from the image. Excessive legacy exposed strokes and broad lower bevel facets were also rejected. The final reference derived marking layer has limited source resolution; 16 bit processing avoids additional quantization but cannot invent captured detail.

## Verified Shader AOV diagnosis

A temporary material copy and view layer AOVs exported seventeen actual signals: three base colors, three roughness inputs, iron and oxide metallic constants, final oxide coverage and exposed blend, facet wear, marking and fine height, pigment source, final and geometric normals, and existing surface alpha. Raw 32 bit OpenEXR passes were verified against the shader sockets. Correct clean iron scene linear color and metallic one were checked numerically. Oxide metallic zero was verified with a tiny control render using the existing iron metallic one on that AOV output only; neither production BSDF was altered.

The passes showed working roughness, wear, oxidation and relief, but a uniformly zero pigmentation source. Its native 16 bit image had been clipped through an 8 bit conversion before normalization. Correct native precision loading restored the pigment variation. All other authored fields are exactly unchanged. Before and after AOV comparison verifies that only the two affected layered base colors and their pigment source changed; all fourteen other passes match. Matching beauty crops were opened and compared directly. The retained result restores subtle brown and charcoal mottling without changing hammering, roughness, wear or normal strength.

The diagnostics are reusable socket driven helpers, run in background scene copies. No Shader AOV nodes or diagnostic view layer passes are saved in production materials. Detailed EXRs, raw arrays, sheets, source signal records, verification and statistics remain locally in aov/before and aov/after. No additional software was installed.

## Limits

The reference still has stronger, sharper broken highlights and more irregular overlapping scale formations. Some existing pits remain softer and rounder. The new surface is deliberately quieter than the rejected raised marking trial. No exact reference match or owner approval is claimed. All full resolution outputs remain beside the selected master. Contextual surrounding finishes are temporary render substitutions only.

No download, installation, paid resource, new software, app change, subagent or AI reviewer was used. Existing free resource provenance and source hashes are in SOURCES.json. Rendering, material branches and validation reuse the established infrastructure.

## Resumed edge reflection and scale cleanup

The exact resumed baseline is 11_restored_pigment/master.blend. Controlled reflections showed that stronger broad sources reveal the bevel but also brighten too much of the face. Narrow warm sources retain more localized highlights. A lower reflection reveals existing lower chips that previously reflected a black environment. Extending the source span along the front construction axis addresses both bays. Environmental fill 0.35 preserves darker face contrast without changing base colors. The original scene environment remains exact. New lights are isolated to the review scene and linked to the authorized iron only.

A separate material comparison changes only the existing new scale boundary bump direction. Shallow recesses read less embossed than the previous raised markings. The quantity, placement and strength of detail remain fixed, as do geometry, large hammering, pits, pigmentation, metallic response, roughness and coverage fields. A local damaged facet exposure remap made negligible difference and was rejected. No new texture generator, damage, source asset or software was introduced.

The earlier seventeen verified AOV signals established functioning material inputs and guided the reflection diagnosis. They were reused as evidence rather than recreated. Current neutral and warm Cycles comparisons distinguish intrinsic relief direction from warm reflection color. Diagnostic nodes and passes remain absent from production.

The owner comparisons are resume_reference.jpg, resume_close_views.jpg and resume_context.jpg. The reference sheet intentionally compares the resumed saved appearance with the new material and lighting together. mark_direction_comparison.jpg holds lighting fixed to isolate the scale correction. The original reference still has sharper, more irregular overlapping scale and stronger edge shapes. Existing broad pits remain rounder, and some fine marks still read etched. Surrounding finishes in the chest image are temporary placeholders. No exact match or approval is claimed.

### AOV driven reflection correction

A final closeup exposed a sharply terminated lower highlight. Six existing signals were exported with the same temporary helper: exposed blend, oxide coverage, bare roughness, geometric normal, final normal and surface alpha. Variable fields, finite normalized normals and the legitimate constant alpha one were verified. Enlarged beauty and pass crops showed no matching material or normal break at the highlight end.

The extended lower light was tilted along its long axis. Its corners spanned the floor and chest height range. Making that axis horizontal keeps the emitter entirely between the floor and rim. The actual corrected render removes the sharp bright wedge without changing the material or geometry. Increasing its power after correcting the orientation retains a warm lower highlight across both bays. Widening the previously tilted emitter made the wedge larger and was rejected. Detailed passes, source records, boundary crops and verification are in aov/edge_cut. No diagnostic nodes or passes are saved in production.

The final render mode is edge_floor. All final views use the same fixed sources and exposure. The native review scene stores their exact settings, with original source lighting preserved separately.
