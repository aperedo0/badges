# Radiant Mountain Sunburst: stacked pieces plan

Status: BUILDING (owner chose to build after round 2, November 9, 2026; round 2's fixes applied; numeric risks owned by the build checks)

## 1. What the owner will see

* **At rest**: a medallion built from stacked pieces, the way the mockup is layered. A red back plate; a rounded gold ring on it; nine raised lemon rays and spikes, each with its own beveled gold rim, standing clearly above the red; five faceted gold spike points over the ring; a sun with a gold rim on top of the rays; three faceted mountains with gold outlines and snowlines in front of the sun; white clouds with gold rims and gold curls in front of the mountains; a gold border along the bottom; a ridged gold star frame with a faceted blue gem in front of everything. Every edge between pieces is a real bevel, so it stays crisp at phone size.
* **While it turns**: each piece shows as its own raised layer on darker gold side walls. The back is the front mirrored.
* **Known app limits (owner accepted, close not exact)**: pale lemon yellows, light grey whites (about 0.85), the sun's look from its gradient and a soft sheen.
* **Build order in one sentence**: turn the checkpoint 1 measurements into a pieces file, build and prove the stacked solids with the badge-build tools in the open Blender, then check once in the app at real pixels, 2x and 4x and turning, then a fresh review.
* No open decisions.

## 2. Reference read

* Mockup: `mountain_sunburst_claude_20261108/reference/mockup.png`. Shapes: `mountain_sunburst_claude_20261108/rebuild/design.json` (measured, checked at checkpoint 1 on November 8, 2026: overlay `rebuild/review/design_overlay.png`). Inventory from the image: the spikes and their kites were sampled with a pixel profile: inside the ring each spike is a lemon kite with thick gold edges; beyond the ring a solid gold point.
* Units: S = 5.45 / 1161 units per pixel; mirror axis x 653.5; Y 2.995 at row 15; bounds Y 2.995 to minus 2.455.
* Pieces, back to front, as the owner described them (November 8, 2026: "the background should be one shape, then the star and its rays are another shape that sit on top of the background, and the mountain sits on top of the sun"). Built by `make_pieces.py` into `pieces.json`; bases by the stack rule from earlier surfaces within 8 px of each outline (interiors under a piece are hidden), gap 0.008:
  0. **core**: the silhouette shrunk 6 px, side material, base 0.03: nothing can be seen through the badge.
  1. **background**: red disc of radius 459 px (inside the ring's outer edge, no shared wall), base 0.06.
  2. **star**: the gold sunburst: the disc to radius 451 px minus the red openings (the red areas shrunk to the gold line centers, opened by 2 px so no sliver is under 4 px). Its outline drops into every red opening over a 9 px bevel (0.03, about 35 degrees). The nine lemon areas (shrunk the same way) are set 0.012 into it over a 6 px bevel, so every gold divider, kite edge, wedge frame and V stands above the lemon and the red as real gold.
  3. **ring**: band 445 to 473.7 px, rounded profile 0.038 high (slopes about 35 degrees), roughness 0.32, over the star's outer edge.
  4. **spike points** (5, twins share bases): each a triangle from the tip along its two measured flank lines to 22 px inside the ring; two flat facets meeting on one center ridge (tip 0.010, inner end 0.055), no hip at the ring; roughness 0.32.
  5. **sun**: 218 px disc; 9 px bevel (0.03) then a 14 px rim (cosine, 0.015) make its 23 px gold edge; gradient disc inside with a dome of 0.04.
  6. **side mountains** (twins) and **central mountain**: faceted bodies (two planes through the peak, the far base corners and the bottom of the ridge at 0.4 of the rise; side peaks 0.06, central 0.09), 7 px bevel (0.025) and 8 px rim (0.01): a 15 px gold outline; their faces (royal; teal, navy, steel) as color areas meeting at creases.
  7. **snow caps** (3) and the **chevron**: their own pieces on the mountain facets (same planes), 6 px bevel (0.02) and 8 px rim (0.01): the snowlines and the chevron's V are real raised gold edges; snow white on the left facet, lavender on the right; chevron navy.
  8. **clouds** (4, the small lobes beside the gem included): grown 6 px, 7 px bevel (0.025), 8 px rim (0.01), white inside with a 0.02 dome.
  9. **curls** (3): the gold between the cloud lobes, running into the border; 7 px bevel, dome 0.02; roughness 0.34.
  10. **border**: band 28 px inside the lower outline below y 690; ridge 0.034; roughness 0.34.
  11. **gem**: the measured star, 8 facets, apex 0.12 above its base.
  12. **frame**: stacked over the gem's 2 px tucked rim; ridge rising to 0.06 at its middle; check frame base minus gem base between 0.008 and 0.04.
* Every bevel, rim and recess stays at or under about 40 degrees (rims start where bevels end, cosine profile), checked from the front normals at checkpoint 2.

## 3. Prior art

* The badge-build tools (`skills/badge-build/scripts`): `badge3d.py` (pieces engine), `validate.py`, `palette.py`, `build_live.py`, `write_usdz.py`, `app_try.py`; they come from this badge's first rebuild, which proved closed solids, exact walls and per pixel stacking (validate passing, broken copies failing).
* Aurora Mountain (`aurora_mountain_20261101/build_geometry.py`): separate stacked parts with profiles, mirrored rear, side walls.

## 4. Construction

Each piece is built by `badge3d.py` from `rebuild2/pieces.json` (written by `rebuild2/make_pieces.py` from the measured shapes): exact outlines, every bevel, rim, line, cell border and facet crease an edge of the mesh, heights from exact distances, a closed solid (front, mirrored back, side walls from the front's boundary with the face's normal on the lip and 70% blended normals on the wall), stacked on a computed base, hidden areas not meshed. Lines and rims are real raised bevels at most about 45 degrees, never paint.

## 5. Materials

`palette.py` with targets: red (0.85, 0.31, 0.17), lemon (1.0, 0.77, 0.06), snow white and lavender at the mockup's ratio, cloud white, teal, steel, navy, royal; the sun gradient from lemon at the top to orange (0.94, 0.49, 0.06) at the lower left. Gold base linear (0.80, 0.37, 0.015), roughness 0.26; ring and spike points 0.32; curls and border 0.34; side walls 0.6 of the gold at roughness 0.55. Red, lemon and the sun at roughness 0.18 (a glossy flat field flashing as one sheet). The chevron uses the navy color. The sun gradient: center (653.5, 566.2), radius 195, from the top (angle 270) to the lower left, texture over the 1312 by 1199 mockup space. Gem: `CrestGem_FoilSapphire` (preview app shader; production needs its patch). Material prefix `MountainSunburst2`.

## 6. The app walkthrough

Rest, early turn, 45, sides, 135, back, 225, 315 degrees: stacked pieces with crisp bevels, darker gold walls, the mirrored back; Badges screen: color blocks; reflection: border, curls, gem lower half.

## 7. Risks

**Every badge** (catalog numbering): 0 too flat (stacked pieces, bevels 9 px or more, rims 16 px); 1 fuzz (rows on every edge); 2 wobble (measured shapes); 3 proportions (checkpoint 1 passed); 4 thin (nothing under 9 px except tips); 5 normals (facets flat, bevels smooth); 6 grain (flat colors); 7 clay (polished gold, depth); 8 color (solved, one re-solve); 9 halo and gold haze (cap 1.4, rougher wide gold); 10 back; 11 side walls; 12 closed solids; 13 outline dots; 14 reflection; 15 contract; 16 load (about 60,000 triangles); 17 grooves (none under 9 px); 18 bloom beside the outline (rough ring and border); 19 wide flat gold (profiles); 20 glossy flat field (roughness 0.18, the 45 and 135 degree poses); 21 turn angles (nine poses); 22 partial checks (whole badge at 2x, a fresh agent); 23 process (open Blender, in place updates, the job file named per badge and printed). Missing lines: the star piece holds every gold line of the sunburst; snowlines and the chevron V are piece edges; check the material map. Yellow against gold: the lemon is set in below raised gold; check lemon against the nearest gold crest at least 0.10 apart in Oklab on the rest capture. Enamel slivers: openings and lemon areas opened by 2 px (no part under 4 px). Side walls in the same place: background radius 459 against the ring's 473.7; the border ends at the ring zone. Steps as black outlines: bevels under 40 degrees with the house side walls; check the 45 degree pose at 2x. Checks: `validate.py` (must fail on broken copies), the finish pictures, the fresh review.

**Feature sections**: measured from the picture (checkpoint 1 passed); metal rims and lines with enamel (bevels at most 45 degrees); bright colors (pale lemon); stacked parts (stack rule, validate); symmetry (twins share bases); gem (attach line, color while turning).

**This badge's own risks**: rays touching each other near the sun (stack rule, the sun covers their inner ends); the ring visible through gaps between ray pieces (red plate between them, ring only at the outer edge); rim bevels turning dark at the bottom edges of pieces (house side walls, check 2x); the many raised lemon pieces looking busy at 40 points (check the phone size picture); the stack growing too thick (cap: front height under 0.6 except the gem apex).

## 8. Build steps and checkpoints

1. `make_pieces.py` writes `pieces.json` and prints every dropped shape (must be none visible); **checkpoint 1b**: `overlay.py` over the mockup with crops of the top spike, a side spike crossing, the central mountain, a cloud curl and the bottom tip: every piece edge within 3 px of the mockup's edge.
2. `badge3d.py pieces.json cand01`; `validate.py cand01` passes and fails on broken copies; **checkpoint 2**: `material_map.py` (top material per pixel beside the mockup): at least 85% of each gold, red, white and blue area shows that material and no holes; the steepest front slope of every bevel, rim and recess under 45 degrees; all bases printed (twins equal).
3. `palette.py`; `build_live.py` in the open Blender, saved as `rebuild2/mountain_sunburst_stacked.blend`; **checkpoint 3**: front, 45 degree and side views in Blender show distinct stacked pieces.
4. `write_usdz.py`; `app_try.py`; **checkpoint 4**: finish check over the whole badge at 2x by me and by a fresh agent; turn frames.
5. Fresh review: shippable and at least 90.

**Stop rule**: a method failure returns here for one light review round.

## 9. Budget

About 60,000 triangles, under 5 MB, two app builds.

## 10. Final acceptance

As badge-plan: finish check clean by a fresh agent, fresh review shippable and at least 90, validate passing, the model in the simulator, the .blend saved.

## Review log

### Round 1: TURNED DOWN
* Accepted and fixed: 1 the gold star was missing (now its own piece); 2 spike points rebuilt from tip and flank lines with one ridge; 3 gem before frame; 4 slopes (rims after bevels, cosine profiles, at most about 40 degrees); 5 snow caps and chevron as raised pieces; 6 small cloud lobes kept, dropped shapes logged; 7 roughness 0.18 on flat fields, dome scale fixed; 8 every opened catalog item answered; 9 a material map check that fails on missing gold or holes, plus named color checks.
* Risks taken in: bases from an 8 px edge band (steps stay small), a hidden core against holes, the curl running into the border, the border at 28 px, twins sharing bases, the frame's continuous ridge, rough spike points, the job file chosen by time and printed, the gem's console line ("stone prepared").
* Tools changed for every badge (skills/badge-build): rim after bevel, recessed cells, true domes, edge band bases, material_map.py, writer error on a missing color, newest job file.

### Round 2: TURNED DOWN (light round)
* Accepted and fixed: 1 sloped pieces floating (stack rule now subtracts the piece's own height at each band point); 2 spike points end over the ring band with a 7 px bevel, ridge highest over the ring and low at both ends; 3 enamel roughness: whites 0.28, blues 0.22, red, lemon and sun 0.18 (`targets.json`).
* Risks taken in: ring, border and frame profiles start under 40 degrees; the gem's base set 0.012 under the frame's, the frame ignoring the gem when it stacks; lemon and sun kept out of the gold class in the material map; clouds and curls as twins; snow clipped at the body's bevel top; the central mountain's foot at y 905; mountain rises 0.20 and 0.14.
* Owner (November 9): build now; the build's checks own the remaining numbers.

## Build log

### cand02, fresh review: 66, not shippable (November 9, 2026)
* Accepted and fixed in cand03:
  * Blades were under the ring, so each read as a kite plus a cone. Now five blade pieces over the ring, from under the sun to the tip, yellow set in, a 3.5 degree ridge.
  * Lower body rebuilt as one gold plate with the clouds set in. Clouds are traced from the mockup's white, smoothed, and averaged with the mirrored other side. The C curls and the wide border come out as the mockup's gold. Small lobes no longer knot beside the gem. The gem frame is 40 px, from the mockup's 40 to 46.
  * Washed teal and lavender navy came from faces tilting left and down, which mirror the studio's low left reflector (measured per face). Mountain faces now rise toward the ridge and toward the bottom.
  * The sun's streaks came from two causes, both fixed in the tools for every badge:
    * the gradient texture's per step solve made stripes (now two solved ends blended smoothly);
    * long dome triangles (now rings to the center).
  * Colors are set from the app measurements (`cand02/review/app_colors.json`):
    * gold solved per region (upper brighter, ring more orange, lower deeper amber);
    * lemon at the app's strongest yellow;
    * the sun more saturated;
    * blues from the mockup's medians.
* Rejected with data:
  * The ring is not 6% too large, and the peak is not low (landmarks at the same scale land on the mockup).
  * The lower body is not too full (silhouette within 1 to 10 px of the mockup at every height).
  * Needles stay thin (the mockup's are about 20 px).
  * The gem's upper facets come from the preview app's foil shader, an app setting.
* Known: the stack is deeper (front 0.66 against 0.46). About 92,000 triangles and 6.3 MB, over the guideline. Trim after the look is approved.

### cand03 to cand06 (November 9, 2026)
* cand03:
  * The cloud averaging erased the C curls. Back to tracing the left cloud and mirroring it, which keeps the curls exact.
  * Teal still washed with faces tilted up. Colored faces are now flat.
* cand04:
  * Flat but rough (0.30), teal and royal still washed: the low reflector's mirror spot, near badge (minus 1.5, minus 1.5), spread its glow. Blues now at roughness 0.18.
  * Blade yellow patchy from the ridge; blades now flat.
  * A gold spur at the plate edge; the plate outline is now smoothed.
  * Gold paints solved per region from the app measurements: lower plate (0.30, 0.12, 0.004), ring (0.82, 0.31, 0), upper gold (1.0, 0.47, 0).
* cand05:
  * Blues on the mockup. A white spot on the teal face's lower left corner.
* cand06:
  * Central mountain tilted (normal slopes 0.03, 0.02) so the spot falls on the cloud and gold.
  * Teal now 0.48 against the mockup's 0.47. Validate passing.
  * 100,264 triangles, 6.87 MB. Front height 0.59 at the gem.

### cand06, fresh review: 68, not shippable (November 9, 2026)
* Stop rule: two reviews (66, 68) with the same top items (yellow reads khaki next to the gold, the reviewer's width table counting glow). Stopped for the owner.
* Confirmed new defects:
  * white dashes on the sunken edges of the yellow fills (colored slopes; fix: the sunken edge in the piece's gold);
  * gold lines between clouds and mountains in several strands;
  * curls read as beaks;
  * the lower frame dark;
  * glare on the red beside the upper right blade.
