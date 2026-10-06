# Mobile badge export rules (RealityKit)

These rules apply to every badge exported for the app. The app lights the coin with small point lights and draws it without Blender's softboxes, pixel filter or denoiser, so detail that looks calm in Cycles can turn into blotches, grain and sparkling dots on the phone. Each rule removes one of those failure modes at the source, so the app needs no load-time patches.

`scripts/badge_mobile_rules.py` applies rules 1 to 6 automatically. `scripts/export_mobile.py` is the v1 reduction pipeline with that rules step at the end.

## The rules

1. **Sub-pixel bevel strips shade exactly like the facet they belong to.** Every bevel face narrower than `max_strip_width` (0.02 units, about 2 master pixels) gets its owner facet's own shading normals, continued across the strip. The owner is the nearest broad facet. Broad facet normals are never touched.
   *Why:* a strip under a pixel wide cannot be drawn as a line. With its own rounded normals (they were up to 173 degrees off at the spear tips), a point light catches it in isolated pixels, which reads as a dotted, sparkling line along the edge.

2. **Those strips use exactly their owner facet's material.** The separate bevel material is dropped from that mesh.
   *Why:* the brighter, glossier bevel material outshone its facet and crossed the app's glow threshold, so edges glittered.

3. **No baked normal maps on polished metal** (the emblem, and the casing with its ring). Facet shape lives in geometry and custom normals, and brushed texture lives in the color and roughness maps.
   *Why:* near-mirror metal reflects a tilt of a fraction of a degree as a shift of a whole light. Bakes carry exactly such tilts: UV-border seams (up to 51 degrees on the emblem map) and grain inside islands, which appeared as blotchy facets and a mottled ring.

4. **A normal map that stays is baked at the strength it should show in the app.** USD has no normal-strength input, so any strength is baked into the pixels using Blender's own Normal Map formula (`normalize(flat + k * (n - flat))`), and the Normal Map node goes back to 1.
   *Why:* an exporter silently drops a Normal Map node's Strength. For the silver inset the bake already matched Blender, but the app shows fine grain about 2.5 times stronger than Blender's final (denoised) render, so the mobile file bakes 0.4. Pass `--inset-strength 1.0` for a Blender-exact file.

5. **Floor cut: nothing below the stage floor ships.** Every mesh is cut at the floor height in the exported model space (USD, Y up; the silver badge uses Y = -2.895). Triangles that cross it are split, with neighbours sharing the new corner so there are no cracks; everything below is deleted. The opening is not capped. Faces above the floor keep their data exactly (26,245 of the silver casing's triangles are bit-identical to v2); new corners on a cut edge take normals and UVs interpolated along that edge. Meshes that stay above the floor are not touched at all.
   *Why:* the coin stands sunk 0.12 units into the floor, as on the Blender stage, and RealityKit cannot hide geometry under a floor. The app used to cut the model at load; now the file arrives cut, and its mirrored reflection inherits the cut. A cap would only add triangles nobody sees, because the cut sits exactly on the floor.
   *Which height:* the stage floor's world height with the badge at its final resting pose (turntable at rest, scale 1, frame 360), measured along the axis that becomes USD +Y. The exporter writes Blender world coordinates unchanged (`convert_orientation=False`) and these scenes are authored Y up, so it is simply the floor object's Blender world Y (here Y = -2.8950002, rounded to the app's -2.895; the difference is one float32 step). The app's own floor value must match the file's.

6. **Everything else is carried over untouched,** with the v1 exporter settings: object names and hierarchy (sibling order is fixed after export, because Blender's USD exporter shuffles it on every run), Y up, 1 meter per unit, front toward +Z, no transforms, same meshes, UVs, colors, roughness maps and texture sizes.
   *Why:* the app frames and finds parts by name and by the model's native size.

## Material names

Names are stable: `<source material>_Mobile_<mesh>` with spaces and `|` turned into `_` (for example `Emblem___satin_silver_facets_Mobile_Emblem`). The app finds parts by these names and prefixes, so never rename a source material or mesh without updating the app. A material a rule makes unused disappears from the file.

Silver badge, v3 file (counts after the floor cut; only the casing changed):

| USD material | Used by (triangles) | Values |
|---|---|---|
| `Inset___finely_textured_charcoal_Mobile_Inset` | Inset disk (3,570) | color map, metallic 0.05, roughness 0.83, normal map at strength 0.4 |
| `Silver___polished_cut_edges_Mobile_Inner_edge` | Inner edge reveal (2,200) | (0.64, 0.62, 0.58), metallic 1, roughness 0.19 |
| `Silver___circumferential_brushed_steel_Mobile_Casing` | Casing: brushed ring face (4,950) | color and roughness maps, metallic 1 |
| `Outer_edge___smooth_satin_silver_Mobile_Casing` | Casing: rounded outer edge (20,384) | color and roughness maps, metallic 1 |
| `Back_and_edge___gunmetal_Mobile_Casing` | Casing: back and edge (1,232) | color and roughness maps, metallic 0.95 |
| `Emblem___satin_silver_facets_Mobile_Emblem` | Emblem: raised center facets, side walls, back (18) and their bevel strips (162) | (0.56, 0.54, 0.5), metallic 1, roughness 0.29 |
| `Emblem___shaded_outer_facets_Mobile_Emblem` | Emblem: four lower outer facets (4) and their bevel strips (46) | (0.21, 0.2, 0.185), metallic 1, roughness 0.29 |
| `Recess___smoked_nickel_Mobile_Inner_channel` | Inner channel (3,500) | (0.07, 0.067, 0.06), metallic 1, roughness 0.27 |
| `Silver___polished_cut_edges_Mobile_Rim_inner_lip` | Rim inner lip (2,500) | (0.64, 0.62, 0.58), metallic 1, roughness 0.19 |

Removed in v2: `Silver___polished_cut_edges_Mobile_Emblem` (rule 2), and the textures `USDZ_Emblem_normal.png` and `USDZ_Casing_normal.png` (rule 3). Anisotropy never survives USD export; the app restores it on the brushed ring.

## How to export a new badge

1. Author the master with each Bevel modifier's own bevel material set (`bevel.material`), so rule 1 can find the strips. Keep mobile-visible glints at least about 2 px wide at the largest on-screen size; anything thinner is folded into its facet.
2. Set `floor_cut.usd_up_height` in the badge's config to its stage floor (rule 5). Run `export_mobile.py` once on a **copy** of the master. It decimates, reuses the baked UVs and maps, applies the rules and writes the USDZ plus `scenes/silver_badge_mobile_reduced.blend` (before rules) and `scenes/silver_badge_mobile.blend` (after rules).
3. Keep the reduced .blend. Decimation is not bit-reproducible (a second run changes vertex order and tiny positions), so later rule or strength changes re-export from it with `badge_mobile_rules.py --input <reduced .blend>`. A scene that already carries rules 1 to 4 (such as v2's saved `scenes/silver_badge_mobile.blend`) takes `--skip-v2-rules`, so only the floor cut runs; re-applying rule 4 would bake the inset strength twice. Scenes saved by this script record what was applied and refuse a second pass of rules 1 to 4.
4. Check the file: `compare_usd.py` against the previous export (only the intended prims may change, bounds must match except the cut minimum), `verify_floor_cut.py` (kept triangles bit-identical, new corners interpolated), `usdchecker --arkit`, `reimport_check.py`, then the proof renders (`render_proof.py`, `measure_smoothness.py`, `make_proof_sheets.py`, `compare_renders.py`).

The rules script refuses to continue when a face with the bevel material is wider than `max_strip_width`: a bevel that wide is visible geometry and needs a deliberate decision, not a silent fold.
