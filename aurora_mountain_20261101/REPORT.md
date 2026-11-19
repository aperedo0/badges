# Aurora Mountain review

Created the owner's aurora mountain crest in live Blender, then checked it in the separate Badge Studio simulator. The final working copy is candidate03. It is available for owner review in **Choose Badge** as **Aurora Mountain**.

[Reference beside simulator](candidate03/review/comparison.png) | [All sides](candidate03/review/all_sides.png) | [Slow turn](candidate03/review/full_turn.mp4) | [Motion frames](candidate03/review/motion_review.png).

The mountain silhouette and gold road were traced from the supplied reference. The rock has real relief and matching rear geometry. Atmospheric aurora and mountain color use reference artwork mapped onto those surfaces. The gold road, two frame bands, gold trims, diamond setting and guiding star are real geometry with physical metallic materials. The illustrated aurora and star cores are emissive. The amethyst has no appearance image or fixed emission map: it uses runtime reflection, refraction, internal reflection and purple absorption through a closed convex cut.

The gold road and gemstone show different resting highlights from the painted still. Their highlights change with the fixed studio light during rotation. The comparison is the evidence of the current match; no claim of identical reference lighting is made.

The custom frame follows the reference's silver inward sweep and hanging diamond setting, rather than using the ordinary circular coin template. No recognized coin casing or brushed ring names are exported. This sets aside the generic template guidance to match the owner's explicit reference. The model stays inside the Home frame, with its lowest point at negative 2.455 and its depth centered at zero. The stage, camera and lighting are unchanged.

All 24 physical solids are closed with consistent winding and no degenerate triangles. ARKit USD validation passed. Normals and UVs are compacted without changing their meaning. The final model has 51,076 triangles and is about 3.9 MB. The extra triangles over the usual 45,000 target retain both complete shaped frames, continuous side walls and matching sculpted backs; the package stays below the usual 5 MB size guidance.

The actual preview's Swift convexity checker accepts the amethyst and its reflected mesh, including split coefficient precision. Native runtime logs confirm shader attachment to the gem and reflection. Front, early turn, both sides, rear and full turn were captured from the actual loaded model, whose bytes match the final USDZ. Four times outline views and the slow turn were visually reviewed. The road normals were smoothed after the first rotation revealed narrow ridges in its side reflections.

Earlier candidates remain for history. Candidate01 has the first simulator captures. Candidate02 was an intermediate material and star correction; it does not claim a complete native pose review. Candidate03 contains the final native captures and validation.

The isolated amethyst optical profile and preview entry are saved in `runtime_integration.patch`, with complete runtime files under `runtime/`. Existing badge assets were checked unchanged. Production app files were not edited. No commit or staging was performed.
