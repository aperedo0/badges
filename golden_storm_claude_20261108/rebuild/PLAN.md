# Golden Storm: stacked pieces plan

Status: DRAFT (round 3 review pending), revised after review rounds 1 and 2 (TURNED DOWN; the round 1 text is in `PLAN_round1.md`). Every blocker's fix is in the scripts named below and proven on a plan check build (`rebuild/planchk`, engine output only, not a candidate).

## 1. What the owner will see

* **At rest**: a gold storm medallion built from stacked pieces, layered the way the mockup is.
  * A gold base plate whose rim is the beveled frame band, with its small crown point.
  * Four gold star points with a center ridge (top, bottom, left, right).
  * A navy to purple enamel field set into the base.
  * Light blue wind ribbons with beveled gold edges lying on the field, and the slim gold crescent at the upper left.
  * The lower left pearl cloud with its gold outline, two gold spiral curls and its sharp tail.
  * The yellow bolt in its 26 px gold rim, lying over the lower cloud.
  * The upper right cloud with its big spiral and two sharp hooks, lying over the bolt's top end.
* **While it turns**: each piece shows as its own layer on darker gold side walls. The back is the front mirrored.
* **Known app limits (owner accepted, close not exact)**: the bolt's yellow is the app's strongest. BoltLight is pale lemon, BoltDeep golden, about 70% of the mockup's color strength. Whites at about 0.85. A linear field gradient (navy at the top to purple at the bottom) stands in for the mockup's painted patches.
* **Build order in one sentence**: `measure.py` writes `design.json`, `make_pieces.py` writes `pieces.json`, then the badge-build tools build, prove, color and load it in the open Blender, then the app capture, `app_colors.py`, the finish check and a fresh review.
* No open decisions.

## 2. Reference read

* Mockup: `golden_storm_claude_20261108/reference/mockup.png` (1254 by 1254, light grey background with a soft drop shadow that is not part of the badge).
* Inventory from the image by color class (`rebuild/review/classes.png`):
  * field (0.157, 0.145, 0.357);
  * ribbons (0.44, 0.62, 0.84), hue about 214, saturation 0.42 to 0.57 (the field's painted highlights are 0.67 to 0.71, so they are told apart by saturation);
  * cloud pearl (0.88, 0.82, 0.82);
  * bolt yellow (0.99, 0.81, 0.04), with the deeper golden half reading as gold by color;
  * gold (0.73, 0.50, 0.17).
* **Profiles measured across the parts** (pixel samples along normals):
  * bolt rim 24 to 28 px: a bright outer bevel of about 14 px, then a darker inner step of about 10 px, then yellow;
  * frame band 40 px: outer bevel 0 to 8, flat 10 to 24, bead 26 to 28, inner slope 30 to 38, field from 40.
* **Units** (`design.json`, from the traced silhouette): S = 5.45 / silhouette height, top row 45 is Y 2.995, bottom is Y minus 2.455, width 5.39 units. `validate.py` checks the bounds exactly.
* **Pieces, back to front.** All heights are in `make_pieces.py`, which prints them.
  0. **core**: the silhouette shrunk 1 px, Side, base 0.03, hidden.
  1. **base** (GoldFrame):
     * The silhouette, minus a 6 px strip inside every piece that forms the outline (clouds and star points), along the outer outline only.
     * Profile measured from the silhouette (badge3d `profile` with `from`): [[0, 0], [5, 0.02], [9, 0.032], [18, 0.036], [21, 0.041], [24, 0.043]], full height by 24 px.
     * Field cell (gradient): the traced field grown by its 7 px slope, set in 0.025. The slope is GoldFrame and the navy floor is the traced field, at Y 0.078. Base 0.06.
  2. **star points** (GoldPoint):
     * From the tip along the silhouette's flanks (150 px run for top and bottom, 130 for left and right) to the field's edge. The hull is pushed 15 px past the flanks so the point's edge is the silhouette itself. It ends 6 px inside a cloud.
     * Top: badge3d `planes` with two facets split on the line from the tip to the center of the inner end: tip 0.012, ridge end 0.06, flank ends 0.
     * Bevel 8 px, 0.03.
  3. **ribbons** (GoldRibbon):
     * Each piece is the traced light blue fill plus the gold within 18 px of it inside the field: its own edge lines, and the bolt's or a cloud's outline gold where its end runs under them, so the end lands hidden under the cover.
     * Ribbons that touch are one piece.
     * Bevel 8 px, 0.025 on the gold sides only (`edge_skip` = the fill grown 1.5 px). The Ribbon cell is the fill grown 4 px, set in 0.012 over a 4 px gold slope; on the plain sides the slope falls outside the piece, so no gold appears there.
     * Fill holes (highlight streaks) filled. Explicit base 0.111, so its lowest edge clears the field floor by 0.008.
  4. **line pieces** (GoldRibbon): gold lines lying on the field alone, the crescent at (486, 301) and one at (985, 562). Bevel 4 px, 0.015, base 0.101.
  5. **lower cloud** (GoldCloud):
     * Line work: the cloud's gold is taken from the mockup, including the highlights on the metal (warm, green above blue; the pink pearl stays out), specks under 80 px dropped. `skills/badge-build/scripts/linework.py` thins it to its centerline, prunes spurs under 8 px, smooths the width over 10 px of line (radius at least 3.5 px) and redraws even strokes. Traced edges had wobbled with the pearl's shading and the spirals came out lumpy and twice as wide; the clean strokes follow all three spirals, inner curls and tips, within a few px (`rebuild/review/top_*.png`).
     * Plate = the clean strokes plus the pearl, filled. Plus the measured tail tip (942, 972), joined as a spike to the plate points 18 px either side. Every gap under 28 px between it and the badge outline is filled, so it owns the outline there.
     * Profile [[0, 0], [4, 0.02], [8, 0.035], [12, 0.042]], full by 12 px.
     * Pearl cells: the pearl (plate minus strokes) grown by its 4 px slope, but never into a stroke's core (the stroke shrunk 2 px). Every stroke keeps its full width as gold: flat core plus its two slopes. Set in 0.02.
  6. **bolt** (GoldBolt):
     * Plate = the measured polygon. Each edge is a line fitted to the outer edge of the gold outline, between 20 and 36 samples per edge. Vertices L (348, 642), P2 (579, 601), B (419, 977), R (944, 447), P1 (645, 499); the upper right edge runs parallel to the upper left edge, offset fitted.
     * Its top keeps only what lies on the mockup's gold, yellow or cloud above row 310, so it follows the curve into the upper cloud's outline.
     * Profile [[0, 0], [6, 0.02], [12, 0.034], [16, 0.038]], full by 16 px.
     * Floor = the polygon inset 26 px (mitred). One BoltLight cell = the floor grown 5 px, set in 0.018. One BoltDeep cell, not set in, painted on the floor (no ridge between the tones).
     * Segments split by the lines L to P1 and P2 to R. Deep side: upper segment right of the spine TC to M1, bar below M1 to M2, lower segment left of M2 to B. Here TC is the midpoint of the top corners, M1 = (L + P1) / 2 and M2 = (P2 + R) / 2.
  7. **upper cloud**: as the lower cloud, with tips (783, 445) and (917, 598) and its large spiral.
* **Bases on the plan check build**: points 0.13 to 0.14, ribbons 0.111, lower cloud 0.18, bolt 0.23, upper cloud 0.28. The front is at most 0.32.
* **Crossings** (the piece whose edges run unbroken through a crossing is on top; each covered end runs at least 6 px under its cover):
  * star points over the base band;
  * ribbons and lines over the field, clipped 4 px inside it;
  * the lower cloud over the frame, field, bottom point's inner end and the lower ribbons' ends;
  * the bolt over the lower cloud (its bottom tip) and the upper left ribbons' ends;
  * the upper cloud over the bolt's top, the frame, the top point's right base and the lower right ribbons' starts;
  * the bolt's right tip (944, 447) meets the upper cloud's lower lobe edge to edge, with the cloud on top.
* **Colored faces**: all flat. Every sunken slope is gold. Profiles reach full height before any cell begins, so fills are truly set in.
* **Symmetry**: none; every piece is measured as it is.
* **Painted light not copied**: highlight streaks on clouds, bolt and field. Only the two bolt tones and the field gradient are paint.
* **Dropped on purpose**:
  * the frame band's 2 px groove before its bead (under 8 px: it would crawl, catalog 17);
  * the bead is kept as the profile's rise at 18 to 21 px.

## 3. Prior art

Mountain Sunburst rebuild2 cand06 (`mountain_sunburst_claude_20261108/rebuild2/`) uses the same tools. Its review (`cand06/review/review.md`, 68) found:

* curls that read as beaks;
* multi strand cloud top lines;
* white dashes on colored slopes;
* a dark lower frame.

This plan answers each:

* gold thinner than two slopes is kept, and tips are measured;
* profiles are full height before the cells begin;
* slopes are gold;
* gold is solved per region from `app_colors.py`.

Reused from it: flat colored fields with glossy lower fields, gold plates with traced fills, whole pieces at crossings.

## 4. Construction

* `measure.py`:
  * color classes;
  * silhouette, closed and filled from the badge's colors plus the warm highlights on the gold;
  * field = everything inside the frame's gold band (gold within 70 px of the outer edge and connected to it), every part over 300 px kept;
  * ribbons;
  * clouds: large white areas per cloud locate them; their gold is rebuilt as clean strokes (`linework.py`), the pearl is the rest;
  * bolt edges fitted;
  * gold lines on the field joined to the ribbon or cloud they touch, the rest kept as line pieces;
  * star point flanks;
  * tips.
  Traces are blurred 2 px, contoured at 0.5 and simplified 0.6 px.
* `make_pieces.py` writes `pieces.json`. `topview.py` draws it flat from above beside the mockup.
* `badge3d.py` builds:
  * closed solids;
  * profiles from a given outline;
  * a sunken fill's slope in the piece's metal;
  * rows at 0.5 px chord error.

## 5. Materials

`palette.py`, gold measured per region after the first capture:

| Material | Paint | Roughness |
|---|---|---|
| Field | gradient (0.16, 0.18, 0.47) at the top to (0.22, 0.13, 0.38) at the bottom, 1024 px texture over the 1254 px mockup | 0.18 |
| Ribbon | (0.44, 0.62, 0.84) | 0.18 |
| Pearl | (0.88, 0.82, 0.82) | 0.30 (catalog 24: at 0.18 the low reflector's spot becomes a hot white spot on white; at 0.30 it spreads; checked at 2x of the lower left) |
| BoltLight | (0.95, 0.88, 0.40) | 0.22 |
| BoltDeep | (0.92, 0.66, 0.10) | 0.22 |
| GoldFrame | (1.0, 0.47, 0.0) | 0.34 (rougher at the outline, catalog 18) |
| GoldPoint | (0.82, 0.31, 0.0) | 0.32 |
| GoldCloud | (1.0, 0.47, 0.0) | 0.26 |
| GoldBolt | (0.95, 0.42, 0.0), deeper and more orange than BoltDeep | 0.26 |
| GoldRibbon | (1.0, 0.47, 0.0) | 0.26 |
| Side | (0.48, 0.222, 0.009) | 0.55 |

* Prefix `GoldenStorm2`.
* `palette.py` prints what each paint shows before building. If BoltDeep's shown color lies within 0.06 lightness and 8 degrees of hue of the gold's measured mid tone, the fallback is one tone (BoltLight only), shown to the owner beside the two tone version.

## 6. The app walkthrough

* **Rest**: crisp gold bevels on every piece.
* **Early turn and 45 degrees**: the darker gold walls; the field (0.18) must not flash as one sheet.
* **Sides**: the stack about 0.32 at most, the clouds and bolt highest; the navy pocket inside the upper cloud shows the cloud's walls about 0.2 tall (accepted: it is the layering).
* **Back at half size**: the mirrored front.
* **Badges screen at 40 points**: bolt, clouds and points read as blocks.
* **Floor reflection**: the bottom point and the lower cloud's lower edge.

## 7. Risks

**Features**: traced from the picture, metal walls with enamel, bright colors, stacked parts. No symmetry, gems, glass, fine marks or coin shell.

**Every badge** (catalog numbering, prevention, then the check):
* 0: stacked layers 0.06 to 0.32; Blender checkpoint views at front, 45 degrees and side.
* 1: rows on every edge; 2x tiles.
* 2: smoothed traces and fitted bolt lines; 4x of spirals, tips and bolt edges.
* 3: measured; `topview.py` beside the mockup and landmarks.
* 4: no part under 4 px; phone size.
* 5: flat fields, analytic normals; 4x.
* 6: flat colors, one smooth gradient; 4x.
* 7: polished gold, depth; rest capture.
* 8: solved, then `app_colors.py`.
* 9: paints capped, gold roughness; 2x of whites and gold.
* 10: mirrored; back pose.
* 11: house side walls; turn frames.
* 12: `validate.py`.
* 13: pieces own the outline; 4x of tips.
* 14: plain bottom; rest.
* 15: `validate.py` bounds.
* 16: about 46,000 triangles on the plan check, said in the report.
* 17: no groove under 8 px.
* 18: GoldFrame at 0.34; upper left at rest.
* 19: profiles on every gold band.
* 20: field roughness 0.18; 45 and 135 degree frames.
* 21: nine poses.
* 22: the whole badge at 2x, a fresh agent.
* 23: open Blender, one .blend, job file per badge.
* 24: colored faces flat, glossy fields in the lower half; `app_colors.py`.
* 25: two ends blended; 4x of the field.
* 26: no domes.
* 27: `material_map.py` misses picture.

**Feature sections**:
* **Traced**: wrong parts (class map checked by eye); missing lines (every gold line listed in section 2 and found in `topview.py` crops); thin gold eaten (kept, see the clouds).
* **Metal walls with enamel**: dark fringe (slopes at most about 40 degrees), puffy (set in), white streak (flat to the slope foot), slivers (no part under 4 px), yellow against gold (separate GoldBolt paint, measured).
* **Bright colors**: accepted limit, the strongest paint.
* **Stacked parts**:
  * layering per the crossings list;
  * gaps (covered ends tucked 6 px or more under);
  * z fighting (gap 0.008, `validate.py`);
  * stuck on (side poses);
  * black outline steps (gold slopes);
  * blobs at joins (stack rule, printed bases);
  * coincident walls (`validate.py` now fails on any shared outline run over 30 px and names the pieces and spot);
  * missing outline (every fill has its gold).

**This badge's own risks**:
1. Spiral tails and eyes lost or beaked. Prevent: clean strokes from the centerline, fills never into a stroke's core. Check: the strokes drawn over the mockup (`review/top_*.png`), and 4x in the app.
2. BoltDeep merging with GoldBolt. Prevent: separate paints, the fallback above. Check: `app_colors.py`.
3. The low reflector's glow on the lower cloud. Check: 2x of the lower left.
4. Ribbon tips shimmering. Prevent: no part under 4 px. Check: 4x at the early turn.
5. The two bolt tones meeting in a seam. Prevent: paint only, one floor. Check: 2x of the bolt.
6. Thick stack. Prevent: printed bases, front under 0.4. Check: the build printout.
7. The bolt top's curve into the upper cloud. Check: crop at the top.
8. Multi strand lines where a cloud's rim lies over the frame bevel. Prevent: the cloud owns the outline there (gaps under 28 px filled), so only one bevel shows. Check: 2x at the cloud and frame joins.

## 8. Build steps and checkpoints

1. `measure.py`, `make_pieces.py`, `topview.py`, then **checkpoint 1**: crops of each spiral, each tip, each bolt corner, the ribbons, the crescent and each star point beside the mockup. Every gold line in the mockup present, tips sharp, edges within 3 px.
2. `badge3d.py`, `validate.py` (no failures; fails on `--break-shift` and `--break-base`), `material_map.py` (gold, white, blue and light blue at least 85%, no holes, every local miss over 1200 px explained), then **checkpoint 2**.
3. `palette.py` (its printout checked against the BoltDeep rule), `build_live.py` in the open Blender, saved as `rebuild/golden_storm_stacked.blend`, then **checkpoint 3**: front, 45 degree and side views.
4. `write_usdz.py`, `app_try.py` (dataset `Badge3DPreviewGoldenStorm`, key `goldenStorm`; `rebuild/runtime_backup/` created first), `app_colors.py` (with `review.json` mockup box set to rows 45 to 1201), then **checkpoint 4**: the finish check over the whole badge at 2x and 4x and the turn frames.
5. Fresh review: shippable and at least 90.

**Stop rule**: a method failure returns here for one light review round.

## 9. Budget

About 46,000 triangles on the plan check. Under 5 MB expected. One 1024 px gradient texture. Two to four app builds.

## 10. Final acceptance

* The finish check is clean, also by a fresh agent.
* The fresh review is shippable and at least 90.
* `validate.py` passes.
* The model is in the simulator and the .blend is saved.

## Revision for round 3 (November 9, 2026)

**Method change from approved prior art** (owner: "have you tried looking at those badges, seeing how they got it done?"). A search of the approved Codex badges found:
* Their enamel is a metal with a near black color, so the studio adds no pale reflection, with the mockup's own colors in emission, solved through the inverse of the app's AgX. The paths are `forge_tide_compass_20261103/prepare_finish.py` lines 46 to 52 and `pack.py` (emission scale 8).
* Emerald Trophy: "A fully metallic emerald field removes the pale dielectric reflection and increases green saturation."
* The geometry gives relief; the picture gives the fine color and shading.
* Gold stays physical metal. No approved badge got lemon next to gold either ("Bright yellow highlights are paler than the reference"), so pale lemon stays the accepted limit.

**What changes in this plan:**
* **Enamel materials**, all metallic 1, near black color, emission from the mockup (`skills/badge-build/scripts/enamel_fill.py`):
  * `Enamel` = the field and every ribbon top, one material, roughness 0.4;
  * `Pearl`, roughness 0.3;
  * `Bolt`, roughness 0.3, with its two tones and highlights taken from the mockup.
* **How the picture is sampled.** Only mockup pixels where the build shows that material are sampled: 3 px inside its edges, never the mockup's gold, and blurred 1.2 px against grain. Every other texel takes the nearest sampled one, so no gold bleeds in. Colors the app cannot show go to the nearest it can (Oklab, lightness 0.35), and nothing exceeds 1.4 linear.
* **Measured on the plan check:**
  * Enamel shows (0.189, 0.179, 0.427) against the mockup's (0.189, 0.18, 0.429);
  * Pearl shows (0.857, 0.804, 0.807) against (0.883, 0.806, 0.808);
  * Bolt shows pale lemon (0.833, 0.763, 0.347).
* **Tools:**
  * `write_usdz.py` writes color and emission textures with scale 8 and metallic 1;
  * `build_live.py` shows the same in Blender;
  * `topview.py` paints picture enamel as the mockup's pixels.
* **Gold materials unchanged.** The section 5 rows for Field, Ribbon, Pearl, BoltLight and BoltDeep are replaced by the above.

**Round 2 blockers, fixed:**
1. **Ribbon divider.** Each ribbon's gold wires are clean strokes (`linework.py` on the gold within 18 px of the ribbon). The enamel cell is the whole piece minus the wires' core (the stroke shrunk 2 px), grown 3 px past the plain sides. The divider and every wire keep their width. Ribbons that touch are one piece.
2. **Ribbon gold sides.** A 3 px, 0.01 bevel on wire sides only (`edge_skip` = the piece minus the wires grown 4 px). The enamel is set in 0.012 over 3 px. Base 0.11, so even the tips clear the field floor by 0.006 or more (`validate.py`). Clipped 4 px inside the field.
3. **Strand beside the bolt.** The cloud line work masks out the visible bolt (below row 310) grown 10 px, the frame band and the four star point triangles. The lower cloud's pearl runs 20 px under the bolt, so it meets the bolt's rim directly. The cloud's navy pocket is kept open (only holes under 300 px are filled).
4. **Needle.** One clean stroke from its gold in a box (440 to 525, 232 to 345), at least 3.5 px radius, run 8 px into the frame's inner slope. Its base comes from the stack rule.
5. **Checkpoint 1.** `skills/badge-build/scripts/overlay.py` at 3x (`review/cp1/overlay_*.png`, each piece in its own color) and `topview.py` from the final `pieces.json`, with picture enamel (`review/cp1/top_*.png`).

**Other changes:**
* **Points.** Points run under a cloud past the field's edge, so the two never stop at the same line. Ridge 0.09. GoldPoint as before.
* **Cloud slope.** 0.016 over 4 px (40 degrees). Frame crown profile [[0,0],[4,.016],[8,.028],[13,.036],[18,.040],[21,.042],[24,.043]].

**Plan check now** (`rebuild/planchk`):
* `validate.py` passes with no failures and fails on `--break-shift` and `--break-base`.
* `material_map.py`: gold 0.86, yellow 0.92, white 0.87, blue 0.99, light blue 1.0, no holes, no outline difference.
* Remaining white misses: the mockup's painted highlights on the bolt, at (762, 553) and (516, 466); and pearl at (980, 345), (895, 239), (381, 946) and (138, 576), where each cloud's outer gold band is a few px wider than the mockup's (a 2.5 to 3.5 px stroke radius, judged acceptable).
* 61,000 triangles: over the guideline; trimmed after the look is approved.

## Review log

### Round 1: TURNED DOWN

**Blockers, all accepted and fixed** (in the scripts and checked on the plan check build):
1. Point walls on base walls: points own the outline (hull pushed past the flanks), and the base ends 6 px inside along the outline. `validate.py` now fails on shared outline runs over 30 px.
2. Base ledge outside the clouds: clouds fill every gap under 28 px to the outline and own it.
3. Grown fills eating thin gold: cloud gold rebuilt as clean strokes (`linework.py`), and pearl grows by its 4 px slope only up to each stroke's core, so no stroke loses width.
4. Recess cancelled by rising profiles: every profile is full before its cells begin, with a crest minus floor of 0.018 to 0.025 printed.
5. Blunt tips: three tips measured and joined as spikes.
6. Flat painted ribbon lines: ribbons have beveled gold edges, a set in blue and an explicit base.
7. Undefined bolt tones: spines given, one sunken floor with the deep tone painted on it.
8. Hip shaped points: two facet planes ending at the field, 8 px bevel, GoldPoint.
9. Inventory gaps: the crescent and a second free line as line pieces, the crown point's navy triangle kept in the field (parts over 300 px), the spiral eyes kept, the frame groove dropped on purpose (sub-pixel).
10. Checks that could not fail: the gem guard in `validate.py`; `material_map.py` now classes purple fields as blue and light blue as cyan and fails on both; thin lines are checked in `topview.py` crops.

**Risks taken in**:
* bases printed (cap stated);
* BoltDeep fallback;
* the bolt rim measured at 26 px (not 14);
* the bolt tip and upper cloud crossing;
* ribbon holes filled;
* the frame rougher;
* gold materials per region named;
* the triangle estimate from the plan check;
* the junction checks.

**Rejected**: none.

**Plan check build** (`rebuild/planchk`): `validate.py` passes with no failures, and fails on `--break-shift` (bounds) and `--break-base` (520 px cloud over bolt). `material_map.py`: gold 0.88, yellow 0.92, white 0.93, blue 0.99, light blue 0.99, no outline difference, no holes; the remaining white misses are the mockup's painted highlights on the bolt.

**Nits fixed**: units 1254, the review box, the backup folder, checkpoint order, 45 degree views. The gradient accepted as linear.

### Round 2: TURNED DOWN

**Blockers, all accepted**:
1. The ribbon divider is painted blue (grown fills merge across a 6 to 8 px line). Fix: ribbon cells grow only up to the gold lines' core, as the clouds do.
2. Ribbon gold sides are puffy. An 8 px bevel on 6 to 8 px lines puts the blue highest, with a tilted blue strip. Fix: line widths measured, a short bevel, a cell without growth past the core; a sampled z check across edges (crest minus floor at least 0.008, floors under 2 degrees).
3. A jagged gold strand beside the bolt over the lower cloud: the cloud's line work took the bolt's rim and its warm reflection. My "painted highlights" note was wrong. Fix: the bolt and frame gold masked out before line work; clouds and pearl run under the bolt; every miss of 150 px or more named.
4. The crescent needle is broken and floating. Fix: one measured piece from under the frame band to the tip, at least 8 px wide over its first half, or dropped and said so.
5. Checkpoint 1 could not fail and its pictures were stale. Fix: per piece outlines over the mockup at 3x, plus a top view regenerated from the final pieces.

**Risks taken in**: cloud slope at most 40 degrees; frame crown profile; a fallback for splitting frame gold; GoldFrame glow; GoldPoint hue; the point ridge; the lower segment's deep side settled by pixel profile; the bolt tip yellow length; the rim width reconciled; wall heights; opening of tips; the last profile row; hidden walls.

**Owner, November 9**: "have you tried looking at those badges, seeing how they got it done?" A search of the approved badges for spirals, line work, yellow, clouds, enamel and edges is running; its methods go into this plan before the fixes.
