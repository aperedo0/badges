# Golden Storm: stacked pieces plan

Status: DRAFT

## 1. What the owner will see

* **At rest**: a gold storm medallion built from stacked pieces, layered the way the mockup is.
  * A gold base plate whose rim is the frame, with its small crown point.
  * Four ridged gold star points (top, bottom, left, right).
  * A navy to purple enamel field set into the base.
  * Light blue wind ribbons with gold edges lying on the field.
  * The lower left pearl cloud, with its gold outline and two gold spiral curls.
  * The yellow bolt in its thick gold outline, lying over the lower cloud.
  * The upper right cloud with its big spiral, lying over the bolt's top end.
  * Every edge between pieces is a real gold bevel or step.
* **While it turns**: each piece shows as its own layer on darker gold side walls. The back is the front mirrored.
* **Known app limits (owner accepted, close not exact)**: the bolt's yellow is the app's strongest (a pale lemon and a golden yellow, about 70% of the mockup's color strength); whites at about 0.85.
* **Build order in one sentence**: measure the shapes into `design.json`, write the pieces file, build and prove the solids with the badge-build tools in the open Blender, capture in the app, measure colors there, then the finish check and a fresh review.
* No open decisions.

## 2. Reference read

* Mockup: `golden_storm_claude_20261108/reference/mockup.png` (1254 by 1254, light grey background with a soft drop shadow to the lower right that is not part of the badge).
* Inventory from the image, by color class (`rebuild/review/classes.png`, medians from about 750,000 classified pixels):
  * field: navy to purple (0.157, 0.145, 0.357), navy at the top and sides, purple in the middle;
  * ribbons: light blue (0.44, 0.62, 0.84);
  * cloud fills: pearl white with a pink cast (0.88, 0.82, 0.82);
  * bolt: yellow (0.99, 0.81, 0.04), light on the upper left half of each segment and deeper golden on the lower right half (the deeper half reads as gold by color);
  * gold metal (0.73, 0.50, 0.17).
* **Units**:
  * silhouette from the gold rim inward, without the shadow: x 54 to 1198, y 45 to 1201;
  * S = 5.45 / 1156 units per pixel; center column 626; row 45 is Y 2.995, row 1201 is Y minus 2.455;
  * width 5.39 units.
* **Pieces, back to front** (heights in units; bases by the badge-build stack rule, gap 0.008):
  0. **core**: the silhouette shrunk 1 px, side material, base 0.03. Hidden; nothing can be seen through the badge.
  1. **base**: one gold plate = the silhouette (frame, crown point, star point bases).
     * Frame profile from the outline: [[0, 0], [5, 0.018], [10, 0.032], [18, 0.045], [28, 0.05], [40, 0.052]]. That is a beveled band about 30 px wide like the mockup's.
     * The field cell (navy to purple gradient) is set in 0.025, with a 7 px slope in gold. The field cell is the mockup's field, ribbons and everything under the bolt and clouds, traced and smoothed. Base 0.06.
  2. **star points** (4): each a gold triangle from its tip along its two measured flanks to the frame band's middle, with a roof top (center ridge, 20 degrees) and a 6 px bevel. Metal may tilt. On the base band.
  3. **ribbons** (5, two upper left and three lower right):
     * Each piece is a light blue fill (traced, smoothed) joined to its gold edge line: gold class within 12 px of the fill and inside the field.
     * Flat top: the fill flat light blue, the gold line flat gold.
     * Clipped to the field cell shrunk 4 px; tips opened so nothing is under 4 px.
  4. **lower left cloud**:
     * A gold plate = its traced pearl fills grown 16 px (its gold outline), clipped to the silhouette shrunk 3 px.
     * Profile [[0, 0], [5, 0.02], [10, 0.035], [16, 0.045]].
     * The pearl fills set in 0.02 with a 7 px gold slope. The gold left between the fills is the outline and the two spiral curls, exactly where the mockup has them.
  5. **bolt**:
     * A gold plate on a measured polygon. Each edge is a line fitted to the outer edge of the mockup's gold outline: left tip about (360, 630), inner corners about (595, 508) and (600, 575), right tip about (935, 452), bottom tip about (440, 965). The top end is extended under the upper cloud.
     * Profile [[0, 0], [5, 0.02], [10, 0.035], [18, 0.05]].
     * Fill: the polygon offset 18 px inward (mitred), split along each segment's spine into BoltLight (upper left half) and BoltDeep (lower right half). Both flat, set in 0.015 with a 6 px gold slope.
  6. **upper right cloud**: as the lower cloud, with its large spiral.
* **Crossings** (the piece whose edges run unbroken through a crossing is on top):
  * star points over the base band;
  * ribbons over the field, under the frame band (clipped inside it);
  * the lower cloud over the frame, field and the lower ribbons' ends;
  * the bolt over the lower cloud (its bottom tip), over the upper left ribbons (they end at its left edge) and over the field;
  * the upper cloud over the bolt's top end (its spiral covers it), over the frame, over the top point's right base and over the lower right ribbons' starts.
* **Colored faces**: all flat (field, ribbons, cloud fills, bolt fills). Every sunken slope around a colored fill is gold, never the fill's color: a colored slope caught the light as white dashes on the Mountain Sunburst (cand06).
* **Fill widths**: each traced fill is grown by its slope width before it is set in, so its colored floor is exactly the traced fill and the gold around it keeps the mockup's line width (`badge3d.py` puts the color only on the flat floor).
* **Symmetry**: none. The design is not mirror symmetric, and every piece is measured as it is.
* **Painted light not copied**: the mockup's highlight streaks on the clouds, bolt and field are lighting. Only the two bolt tones and the field's navy to purple shift are paint.
* **Owner's intended differences**: none beyond the yellow limit.

## 3. Prior art

* Mountain Sunburst rebuild2 (`mountain_sunburst_claude_20261108/rebuild2/make_pieces.py`, cand06). Same tools (`skills/badge-build/scripts`). Reused from it:
  * gold plates with traced fills set in (its lower plate: the curls and border came out right);
  * blades as whole pieces at crossings;
  * flat colored fields with roughness about 0.18 in the lower half;
  * gold solved per region from `app_colors.py`;
  * smooth gradients;
  * domes with rings to the center.
* Changes for this badge:
  * no mirroring;
  * one more cloud plate;
  * the bolt polygon with two flat tones;
  * ribbons as raised flat pieces;
  * a badge-build engine change for every badge: a sunken fill's slope takes the piece's metal, and the color covers only the flat floor (fixes cand06's white dashes).

## 4. Construction

* `rebuild/measure.py` writes `rebuild/design.json` from the mockup:
  * silhouette, field cell, ribbon fills and gold edges, cloud fills per cloud, star point flanks;
  * bolt edges fitted to the gold outline's outer edge, where it meets field, ribbon or cloud, sampled along each edge's normal;
  * fills traced by color, smoothed (Gaussian blur 2 px, contour at 0.5, simplify 0.4), small bits under 1500 px dropped and logged.
* `rebuild/make_pieces.py` writes `pieces.json`. `skills/badge-build/scripts/badge3d.py` builds closed solids:
  * the front;
  * the mirrored back;
  * side walls from the front's exact boundary, a lip row with the face's normal and material, then the side material with normals blended 70% toward the face;
  * heights from exact distances, every outline, slope, fill border and crease an edge of the mesh, hidden areas not meshed.

## 5. Materials

`palette.py` solves paints through the app's measured light. Colored fields have no emission and are capped at 1.4 linear.

| Material | Target | Roughness |
|---|---|---|
| Field | gradient, navy (0.16, 0.18, 0.47) at the top to purple (0.22, 0.13, 0.38) at the lower middle, 1024 px texture | 0.18 |
| Ribbon | (0.44, 0.62, 0.84) | 0.18 |
| Pearl | (0.88, 0.82, 0.82), capped at about 0.85 | 0.30 |
| BoltLight | pale lemon (0.95, 0.88, 0.40) | 0.22 |
| BoltDeep | golden (0.92, 0.66, 0.10) | 0.22 |
| Gold | albedo (1.0, 0.47, 0.0) | 0.26 |
| GoldPoint | albedo (0.82, 0.31, 0.0) | 0.32 |
| Side | albedo (0.48, 0.222, 0.009) | 0.55 |

* After the first app capture, `app_colors.py` measures each material against the mockup, and gold is re-solved per region.
* Prefix `GoldenStorm2`.

## 6. The app walkthrough

* **Rest**: the layered pieces with crisp gold bevels.
* **Early turn and 45 degrees**: the darker gold walls of each layer; the field must not flash as one sheet.
* **Sides**: a thin stack, the clouds and bolt standing highest.
* **Back at half size**: the mirrored front.
* **Badges screen at 40 points**: bolt, two clouds and frame points read as blocks.
* **Floor reflection**: the bottom point and the lower cloud's lower edge; nothing busy.

## 7. Risks

**Features**: traced from the picture, metal walls with enamel, bright colors (yellow), stacked parts. No symmetry, gems, glass, fine marks or coin shell.

**Every badge** (catalog numbering, prevention, then the check):
* 0 too flat: six stacked layers, steps of 0.03 to 0.06; Blender checkpoint 3 views.
* 1 fuzz: rows on every edge; 2x tiles.
* 2 wobble: smoothed traces and fitted bolt lines; 4x of spirals and bolt edges.
* 3 proportions: measured; overlay and landmarks.
* 4 thin: ribbon tips opened to 4 px; phone size picture.
* 5 normals: flat fields, analytic normals on profiles; 4x.
* 6 grain: flat colors and one smooth gradient; 4x.
* 7 clay: polished gold, depth; rest capture.
* 8 color: solved, then measured with `app_colors.py`.
* 9 halo: paints capped, gold roughness; 2x of whites and gold.
* 10 back: mirrored; back pose.
* 11 walls: house side walls; turn frames at 4x.
* 12 closed solids: `validate.py`.
* 13 outline dots: lip rows; 4x of tips.
* 14 reflection: plain bottom; rest capture.
* 15 contract: `validate.py` bounds.
* 16 load: about 60,000 triangles, said in the report.
* 17 grooves: none under 8 px.
* 18 bloom beside the outline: rough points; upper left at rest.
* 19 wide flat gold: profiles on every gold band.
* 20 glossy flat field: roughness 0.18 on the field; 45 and 135 degree frames.
* 21 turn angles: nine poses.
* 22 partial checks: the whole badge at 2x, a fresh agent.
* 23 process: open Blender, one .blend, job file named per badge.
* 24 colored face mirroring a light: all colored faces flat, glossy fields in the lower half; `app_colors.py`.
* 25 gradient stripes: two solved ends blended; 4x of the field.
* 26 dome streaks: no domes.
* 27 hidden local misses: `material_map.py` misses picture.

**Feature sections**:
* **Traced**:
  * Wrong parts: the class map is checked by eye (`rebuild/review/classes.png`).
  * Missing lines: every gold line is either a plate's outline, the gold between fills, or a ribbon's edge line; the misses picture.
  * Thin gold eaten: spirals come from the gold left between traced fills, never from subtraction of grown fills; overlay crops of all three spirals.
* **Metal walls with enamel**: dark fringe (slopes at most about 40 degrees), puffy enamel (fills set in), white streak (fills flat to the slope foot), slivers (opening by 4 px), yellow against gold (BoltDeep is golden, so the bolt outline uses the deeper gold, kept apart in hue and lightness by `app_colors.py`).
* **Bright colors**: the yellow limit is accepted; the solved paint is at the app's strongest yellow.
* **Stacked parts**:
  * layering per the crossings list;
  * gaps (pieces overlap, closed solids);
  * z fighting (gap 0.008);
  * stuck on (side poses);
  * steps as black outlines (gold slopes, no steep colored steps);
  * blobs at joins (the stack rule);
  * coincident walls (cloud plates end 3 px inside the silhouette);
  * missing outline (every fill has its gold).

**This badge's own risks**:
1. The cloud spirals traced too thin or cut into dots, read as beaks. Prevent: blur 2 px, keep any gold line over 8 px; compare against the gold class. Check: overlay of each spiral and the misses picture.
2. The bolt's golden half merging with its gold outline, so the bolt loses its edge. Prevent: BoltDeep warmer and lighter than the gold's mid tone. Check: `app_colors.py`, BoltDeep and Gold at least 0.06 apart in lightness or 8 degrees in hue.
3. The low reflector's mirror spot (near badge minus 1.5, minus 1.5) on the lower cloud and the field beside it as a white glow. Prevent: pearl at 0.30, field at 0.18. Check: 2x of the lower left.
4. The ribbons' thin tapered tips shimmering. Prevent: opened to 4 px, ending in gold. Check: 4x at the early turn.
5. The two bolt tones meeting in a visible seam. Prevent: one flat floor, only paint changes. Check: 2x of the bolt.
6. The stack growing thick. Prevent: front height under 0.55. Check: the build's printout.
7. The upper cloud covering too much of the bolt's top. Prevent: the bolt's top extension stays under the cloud's outline, and the visible bolt matches the mockup's. Check: overlay at the top.

## 8. Build steps and checkpoints

1. `measure.py`, then **checkpoint 1**: overlay of every piece over the mockup, with crops of the three spirals, each bolt corner, the ribbon tips and each star point. Every edge within 3 px.
2. `make_pieces.py`, `badge3d.py`, `validate.py` (passes; fails on `--break-shift` and `--break-base`), `material_map.py`, then **checkpoint 2**: no unexplained local miss over 1200 px, no holes.
3. `palette.py`, `build_live.py` in the open Blender, saved as `rebuild/golden_storm_stacked.blend`, then **checkpoint 3**: front, 35 degree and side views show distinct stacked pieces.
4. `write_usdz.py`, `app_try.py` (dataset `Badge3DPreviewGoldenStorm`, key `goldenStorm`), `app_colors.py`, then **checkpoint 4**: the finish check over the whole badge at 2x and 4x and the turn frames.
5. Fresh review: shippable and at least 90.

**Stop rule**: a method failure returns here for one light review round.

## 9. Budget

About 60,000 triangles and under 5 MB. Over the house guideline of about 45,000; the reason, and the trim after the look is approved, go in the report. One 1024 px gradient texture. Two to four app builds.

## 10. Final acceptance

* The finish check is clean, also by a fresh agent.
* The fresh review is shippable and at least 90.
* `validate.py` passes.
* The model is in the simulator and the .blend is saved.
