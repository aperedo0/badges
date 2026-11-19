# Wood experiment record

A: exact existing normal mapped material. Warm and neutral renders show dark painted channels and a hollow looking knot. No physical shadow relief.

B: existing numerical height as real geometry, residual fine normals. Stronger occlusion and better ridge shading. Existing heavy cavity pigment and flowing ridge shape remain.

C: CC0 Poly Haven Rough Wood, one board crop rotated along X, chestnut pigment, 0.045 unit relief range. Natural fine fibers, but too quiet and without the reference knot. The cabinet material is finer and more polished; TextureCan wood0034 is more cartoon styled. Download previews and moderate maps were inspected locally.

D: existing anatomy at 70 percent depth, scanned fine fibers, flatter cavity pigment, filled knot core, four independent checks. Actual warm and grazing renders show over rounded ridges and an overly smooth knot core.

E: power curve flattens ridge tops, authored chips and sharper cuts. Reduced rounded mass, but the synthetic knot rings look too even and some surface detail is still missing.

F: perspective rectified owner reference used to interpret height. Reference intensity was discarded from pigment. Rejected after actual warm renders: occlusion fill seams, false pits and wax like plate boundaries. This is not a measured scan and is not the chosen system.

G: authored growth channels, branch flow and clustered damage with scanned fine fibers. Rejected after actual warm renders: too regular, smooth and procedural. It is a diagnostic experiment, not the chosen direction.

H: retains the more irregular sculpted source, removes the synthetic core rings, corrects the gap between geometry and normal detail, and uses independently controlled chestnut pigment, stains and roughness. The final mesh uses a 0.0055 unit smoothing split with the full complementary high band in the tangent normal map. The scanned grain supplies restrained fine fibers. This is the current best technical and visual candidate, pending owner judgment. It still has more flowing rounded grain and a more prominent knot than the reference.

Master: H is sampled on a 1537 by 417 grid. The original front is replaced in an isolated body copy. A five sided boundary bridge stitches the relief to the original bevel perimeter. 641121 vertices, 1282238 triangles. Every edge has two incident faces. Positive fine peaks are capped at the original front datum to preserve hardware clearance. Retained source face normals are preserved; displaced face normals use actual geometry.

Lighting: draft comparisons share neutral and warm camera settings. Cinema lighting is an approximate reference inspired studio, not a calibrated reconstruction. Neutral, opposed key and gray clay grazing views diagnose relief. Temporary iron, brass and plain wood color context exists only during background renders and is never saved over the source chest.

Files: comparisons.blend preserves every draft. wood_master.blend preserves the entire original editable scene plus the isolated plank master. baseline_live.blend is the initial live save. No original candidate or root chest file was overwritten. The current source scene contains original rig and guides; the master scene is a static look development copy. Change the original scene for rig work.
