# Radiant Mountain Sunburst: rebuild plan

Status: CAPPED: owner decides (round 3 turned down revision 3; 8 blockers, all fixable inside this method)

## 1. What the owner will see

* **At rest on Home**: a gold sunburst medallion. A polished gold ring with a groove, five solid gold spikes with sharp facets, red wedges, pale lemon rays and flanks, a sun graded from pale lemon to orange, three faceted mountains with white snow, white clouds with chunky gold curls, a stepped gold border, and a blue faceted star gem in a ridged gold star frame. Gold lines are even, straight where the mockup is straight, and clean at the phone's real pixels.
* **While it turns**: the parts read as stacked pieces, each standing on darker gold side walls: the gem and frame in front, then border and curls, clouds, mountains, the sun, the spikes, and the ring and red plate at the back. The back is the front mirrored.
* **On the Badges screen** (about 40 points): sun, spikes, mountains and gem read as clear color blocks.
* **Floor reflection**: the border, the curls' feet, the frame's lower arm and the lower half of the gem.
* **Known app limits, accepted under the owner's "close, not exact" rule**: the yellows are pale lemon (owner's choice, November 8, 2026); whites (snow, clouds) show as a light grey of about 0.85 instead of the mockup's 0.95, because anything brighter glows; the sun carries its look by its gradient and a soft sheen, not the mockup's painted glare; the mountains' facets read mostly through their colors. Predicted colors: `rebuild/palette_predicted.png`.
* **Build order in one sentence**: measure every shape into `design.json` and check it over the mockup, compute every part as an exact solid in `geometry.py`, load them into the open Blender and check there, verify the stack with `validate.py`, then check once in the app at real pixels and 4x, then a fresh review.
* No open decisions remain.

## 2. Reference read

* Mockup: `mountain_sunburst_claude_20261108/reference/mockup.png` (1312 x 1199). Checklist: `mountain_sunburst_claude_20261108/review/checklist.md`.
* All pixel values are mockup pixels at 1x. Badge box x 81 to 1226, y 15 to 1176. Mirror axis x 653.5; it wins over any measured center.
* Units: S = 5.45 / 1161 = 0.0046942 units per pixel; X = (x minus 653.5) S; Y = 2.995 minus (y minus 15) S. Final bounds Y 2.995 to minus 2.455, X within plus or minus 2.69, Z centered on 0, with no rescaling anywhere.
* Measured: outer ring circle radius 473.7 px around (653.5, 557.9). Sun disc outer edge of the enamel 195 px around (653.5, 566.2); the rim adds 23 px outside it (outer radius 218, matching the checklist's 37% of W). Spike tips: top (653.5, 15); diagonals (248, 205) and mirror; sides (81, 567) and mirror; bottom point (653.5, 1176). Widest at y 840 (109 to 1197). Gem tips: top (653.5, 853), bottom (653.5, 1079), left (548, 958), right mirror.
* Materials as the mockup shows them: gold metal; glossy enamel (vermilion red, pale lemon, sun yellow to orange, white snow, pale lavender snow, teal, steel blue, navy, royal navy, warm off white cloud); a cyan to azure crystal. The mockup's white streaks, bright gold bands and dark wall edges are painted lighting: not copied.
* Intended differences recorded in `review.json`: back and sides finished; pale lemon yellows; whites as light grey; the flank gradient, the wedges' salmon edges and the lighter band inside each line are dropped (painted shading).

## 3. Prior art

* **The house side wall technique** (AGENTS.md section 4, used on Copper, Bronze and Platinum, October 13, 2026): side walls in plain dark metal, roughness 0.5 to 0.6, normals blended about 70% toward the face. This plan uses it for every step between parts.
* **Aurora Mountain** (`aurora_mountain_20261101/build_geometry.py`, built by Codex, available for owner review): separate closed parts stacked in depth, a gem in a ridged setting, mirrored rear with side walls. This plan follows that structure; its `ring` and `band` functions are not reused because they cannot make open bands, different seats or mirrored backs as needed here.
* **The gem**: clean02's builder (`enamel_badges_tools/blender_build_clean.py` lines 94 to 128): apex over the ridge crossing, girdle points lifted onto each facet plane so the facets stay flat.
* **Polygon work**: shapely 2.2 (installed November 8, 2026) for exact offsets with mitered joins, unions, differences, distances and constrained triangulation.
* **Checks**: `crimson_shield_20261019/validate.py` pattern, `enamel_badges_tools/app_try.py`, the review pack.

## 4. Construction

### Method

* `rebuild/design.json`: every shape in mockup pixels, as named points shared between neighbors. Curves are Catmull Rom through measured points with corner flags; straight edges are polygons.
* `rebuild/geometry.py` (Python 3.11, shapely, numpy): builds every part as a **closed solid**: a front relief, its exact mirror as the back (Z negated, winding reversed), and side walls joining front and back along the part's outline. Faces are triangulated with constrained Delaunay inside exact polygons, with every crease, profile breakpoint and color boundary as a constraint row (rows sampled at 2.5 px or less on curves, only at corners on straight runs). It writes `rebuild/candNN/parts.npz` (per part: vertices, faces, per corner normals, per face material).
* `rebuild/build_live.py` runs in the open Blender through `ruby_heart_claude_20261107/tools/blender_link.py`, updates the parts' meshes in place (never deletes objects), assigns materials, puts the mockup beside them, and saves `rebuild/mountain_sunburst_rebuild.blend`.
* **The stack rule**: parts are placed back to front: plate, spikes, sun, side mountains, central mountain, clouds, curls, border, star frame, gem. Each part's **base** (the height of its outline on the front) is computed by `geometry.py` as the highest front surface of all earlier parts inside its outline grown by 2 px, plus 0.006. Its relief is built on top of its base. Its side walls run from its front base down through to its back base (they pass inside the earlier parts, hidden). So no surface ever sits within 0.006 of another where they overlap, by construction, and `validate.py` proves it on the built mesh.
* **Steps**: the visible step at a part's edge is its side wall, in the side material with normals blended 70% toward the face. The edge where the front face meets the side wall gets a 1.5 px chamfer so it never forms a bright knife edge.
* **Line profile** (gold lines between enamel areas inside one part): the cells are inset by half the line width (mitered joins, miter limit 3); the gold between them rises from the enamel as a circular arc 0.0095 high over half the width, so its steepest slope is 39 degrees and its crest lies exactly on the design's shared boundary. Rows at 0, 1.5, 3 and 4.5 px from each cell edge plus the crest. A cell part narrower than 4 px is removed (opening by 2 px), so every ray and flank tip ends in solid gold.
* **Facets**: flat facets are planes; their normals are the face normals, split at every crease.

### Parts, back to front (heights in units above the part's computed base unless absolute)

1. **Plate** (absolute heights): the disc inside the ring's outer circle. Enamel cells (10 red wedges, 6 flanks, 4 rays, the top spike's lemon) flat at 0.100, gold lines between them per the line profile. The ring as part of the plate, profile from the outline inward: outline at 0.080, rising at 40 degrees to 0.118 at 10 px, rounded crest 0.124 at 16 px, a V groove 8 px wide and 0.007 deep, then down at 40 degrees to the enamel at about 29 px. The plate's lower half is hidden under clouds and border.
2. **Spikes** (5): each a measured convex kite: tip, two widest corners on the ring's outer circle (diagonals 69 px apart, sides 57 px), inner point 6 px inside the sun rim. The top spike: a solid point from the tip to the ring's inner foot, its width at the ring measured at checkpoint 1 (about 80 to 90 px); below it the lemon and its two edge lines belong to the plate. Relief: the lower envelope of four planes, each rising at 18 degrees from one kite edge, so each spike has four flat facets and creases along its straight skeleton, with a sharp center ridge running to the tip. Base computed (about 0.130). Ridge about base plus 0.05 (diagonals), 0.065 (top), 0.043 (sides).
3. **Sun**: disc of radius 195 px and rim to 218 px. Rim: rises at 40 degrees from the base to a rounded crest at base plus 0.020, inner lip 8 px, down at 40 degrees to the disc. Disc: a dome from base plus 0.005 at its edge to base plus 0.035 at the center (soft sheen; slopes under 6 degrees, accepted). The rim covers the spikes' inner points.
4. **Side mountains** (mirrored pair) and 5. **central mountain**: facets as planes through measured points with heights in `design.json` (peak, ridge points, base corners; the central peak at (653.5, 479) rising base plus 0.08, side peaks base plus 0.05). Each colored area (white and lavender snow facets, teal, steel blue, navy, royal navy, the chevron) is a face set clipped from its facet. Gold lines between colored areas follow the line profile on the facet planes. Which boundaries are gold lines and which are bare creases is decided at checkpoint 1 from 3x crops. The central mountain stacks over the side mountains where they overlap.
6. **Clouds** (mirrored pair): flat at base plus 0.004 to the wall foot (no rise at the edges); gold outline line 1.4% of W (16 px) per the line profile.
7. **Curls** (mirrored pair): a band along a measured spiral, width measured at checkpoint 1; profile a circular arc whose edges meet the cloud at 40 degrees (height 0.364 times half the width); a round end cap at least 8 px wide.
8. **Border**: a band along the lower outline from each notch at 61% down to the bottom V, 40 px wide: an outer rounded band 24 px (arc, 40 degree edges, about 0.020 high), a V groove 8 px (0.006 deep), an inner band 8 px (arc 0.007 high). Its outer edge is the silhouette with a side wall. At each notch the border ends against the ring with its side wall; its end is a rounded cap.
9. **Star frame**: between the gem outline and a measured mitered outer star (30% of W by 29% of H, 4 sharp tips). Profile: from the outer edge at the base rising at 30 degrees to a ridge, then down to the inner edge, whose height at every point is the gem's height there plus 0.008. Its lower arm is measured to its own tip (about y 1123); below it the border's V reaches the badge tip at y 1176.
10. **Gem**: the measured symmetric star (4 tips, 4 inner corners, curved sides as 6 points each), clean02's method: girdle points lifted onto their facet planes, apex at girdle plus 0.15 (facet tilt about 28 degrees), tucked 2 px under the frame's inner edge. Closed by its mirrored back and a girdle strip.

### Bottom tip and notches

At the bottom tip the frame arm ends at y 1123 on top of the border; the border's two bands meet in a mitered V at the tip; the cloud's white strip ends at least 8 px wide. At the notches the clouds and border stand on their side walls over the ring.

## 5. Materials

`rebuild/palette.json` and `rebuild/write_usdz.py` (from `write_clean_usdz.py`, changed to: one mesh per part, materials per face subset, per corner normals with face varying interpolation, no rescaling, output `candNN/model.usdz`, the gem's first UV set set to the foil axis (0, 0.5) front and (0.5, 0.5) back).
* **Gold** (`MountainSunburst_Gold`): metallic 1, roughness 0.24, base start linear (0.55, 0.22, 0.0). **Ring gold** (`MountainSunburst_GoldRing`): same base, roughness 0.30 (bloom on the upper left outline). Target: a 5 x 5 patch on the border's outer band crest at the bottom left (picked at checkpoint 2 from the mesh) shows (0.78, 0.55, 0.18) plus or minus 0.06 at rest; if off, scale the base once by the measured ratio.
* **Side** (`MountainSunburst_Side`): gold base times 0.6, roughness 0.55.
* **Enamel**: one material per color, flat; the sun gets a small gradient texture (512) from pale lemon at the top to orange at the lower left. Colors solved through `enamel_badges_tools/calibration.json` with the perceptual pale lemon match (`carve_badge_v7b.py` lines 131 to 156) limited to gain times albedo plus offset at most 1.4 linear per channel, and no glow. Predicted results are in `rebuild/palette_predicted.json` (for example red wedge shows 0.85, 0.31, 0.18; teal 0.18, 0.50, 0.67; navy 0.11, 0.20, 0.46; lemon 0.84, 0.73, 0.41; whites 0.85). Roughness 0.12; snow and clouds 0.28. After the first capture each color is re-solved once from its measured app color.
* **Gem** (`CrestGem_FoilSapphire`): the preview app's foil shader (style 17); production needs an integration patch, noted in the report.
* No coin names, no lights or cameras.

## 6. The app walkthrough

* **Rest front**: the side walls are edge on and invisible; the lines, facets, colors and the gem read.
* **Early turn**: the side walls appear as darker gold steps; spike ridges and gem facets catch the light.
* **Sides** (three quarters size): stacked parts on darker gold walls, the side wall around the silhouette.
* **Back** at half size: the mirrored front; compared with the front for contrast.
* **Badges screen**: color blocks and the gem.
* **Floor reflection**: border, curl feet, frame arm, the gem's lower half.

## 7. Risks

**Features**: measured from the picture; metal walls with enamel; bright saturated colors; separate stacked parts; mirror symmetry; a gem. Not applicable: glass, fine marks, coin shell.

**Layer 1, every badge**

1. Fuzz: every crease, breakpoint and color boundary is a constraint row. Check: triangles over 4x crops of the five checkpoint areas.
2. Wobbly lines: measured shapes, exact offsets. Check: an orthographic material render of the built mesh from Blender at 1x mockup scale: each line type's width at 10 places varies under 20%, and no line's centerline changes curvature sign more than the design does.
3. Proportions: checkpoint 1 overlay. Check: every edge within 3 px of the mockup's edge; width table within 2%.
4. Thin: cells under 4 px removed; caps at least 8 px; lines 11.5 px. Check: phone size picture.
5. Normals: flat facets, smooth arcs. Check: 4x crops in the app.
6. Grain and copied light: flat colors. Check: 4x of enamel areas.
7. Clay look: polished gold, spike facets at 18 degrees, real stacking. Check: rest capture beside the mockup.
8. Color: predicted table, one re-solve. Check: 5 x 5 patches at the red wedge (463, 271), the flank (463, 373), the sun (653, 420), the right cloud (996, 885), the left side mountain body (330, 700) and the gold patch: each within 0.06 of its predicted value.
9. Halo and glowing whites: enamel capped at 1.4 linear, no glow. Check: rest and early turn crops of sun, snow, clouds, flanks and the reflection show no glow ring.
10. Back: mirrored. Check: back pose contrast at least half the front's.
11. Side walls: side material, blended normals. Check: both sides and the early turn at 4x: steps read darker gold, never black, no streaks.
12. Missing faces or inside out parts: `validate.py`: each part merged by distance 1e-6 has 0 open edges, a positive signed volume, and a back equal to its front with Z negated.
13. Outline dots: chamfered front edges, side material on walls, ring roughness 0.30. Check: 4x of every tip and long edge, front and turned.
14. Floor reflection: Check: rest capture of the lowest fifth.
15. Contract: `validate.py`: exact bounds without rescaling, X inside 3.35, Z centered within 0.002, identity transforms, no coin names, UsdPreviewSurface with `st`, the gem's foil UVs. Check: it fails on a copy shifted by 0.01 and on a copy with one part's base lowered by 0.01.
16. Load: about 50,000 triangles (up to 60,000 with the reason), under 5 MB. Check: the writer's counts.
17. Grooves and lips: 8 px minimum. Check: 4x of the ring arcs at the early turn.
18. Bloom beside the outline: ring roughness 0.30; spike facets 18 degrees. Check: upper left outline at rest and early turn.
19. Wide flat gold: arcs and ridges on the border, curls and frame. Check: rest crops.
20. Process: open Blender, meshes updated in place, objects never deleted, finish gate before any reviewer or the owner, stop rule.

**Measured from the picture**: regions come from `design.json`; checkpoint 1's numbered map over the mockup catches wrong parts; the line inventory (ring and groove, sun rim, 5 spikes, 6 flanks, 4 rays, 10 wedge lines, snowlines and facet lines, chevron, 2 cloud outlines, 2 curls, border, frame) is ticked off there.

**Metal walls with enamel**: dark fringe and white streaks: 39 degree arcs, enamel flat to the wall foot. Puffy enamel: impossible, enamel below crests. Gold against yellow: deeper gold base, pale lemon. Slivers: removed below 4 px. Check: 4x of red and navy cells next to lines and of every tip.

**Bright saturated colors**: pale lemon, predicted. Check: the flank and sun patches.

**Separate stacked parts**: the stack rule. Check: `validate.py` renders every part's front height on a 1x pixel grid: the top part at each pixel matches the numbered map, and the gap to the next surface is at least 0.006; side poses at 4x.

**Mirror symmetric**: `validate.py` compares each mirrored part's vertices with their mirror images (under 0.5 px); a flipped capture difference, the central mountain masked out, shows no shape difference beyond lighting.

**Gem**: Check: the attach line in the console; the gem keeps its blue at the early turn, sides and back; no slit at its edge at 4x.

**This badge's own risks**

1. **Steps read as black lines.** Prevent: side material with blended normals, chamfered edges. Check: 4x at cloud, mountain and spike edges at the early turn.
2. **Ring and spike crossings look like blobs.** Prevent: spikes stand 0.006 or more above the ring with their own walls. Check: 4x of all crossings.
3. **Spike tips flash as dots while turning.** Prevent: chamfer, side material. Check: all tips at 4x, rest and early turn.
4. **The sun becomes a white disc.** Prevent: capped color, gentle dome. Check: sun crop, no pixel over 0.98 with a ring.
5. **Curl tips break into dashes.** Prevent: 8 px caps. Check: 4x of both curl tips.
6. **Small red triangles below the side spikes read as holes.** Prevent: red enamel there. Check: 4x.
7. **The badge reads as a thick puck from the side**: total front height reaches about 0.40 at the gem (0.80 thick), border about 0.30. Prevent: cap the computed bases (if the front height of any part except the gem exceeds 0.36, lower the increments). Check: side pose beside Aurora Mountain's side capture.
8. **The ring groove reads as a dark scratch.** Prevent: 8 px wide, 20 degree walls. Check: 4x at rest.
9. **Facets carried mostly by color look painted.** Accepted (close, not exact). Check: the fresh review's judgment.
10. **What is new compared with Aurora Mountain**: a many celled enamel plate, the computed stack, pale lemon. Checkpoint 4 crops these first.

## 8. Build steps and checkpoints

Work in the open Blender, file `rebuild/mountain_sunburst_rebuild.blend`, scene "Mountain Sunburst Rebuild". First create `rebuild/runtime_backup/` and copy `mountain_sunburst_claude_20261108/runtime_backup/preview_none.usdz` into it (`app_try.py` backs up beside the candidate folder). Shared tools are copied into `rebuild/`, never edited in place.

1. **Measure** (`rebuild/design_measure.py`): fit circles, read tips, propose corner points from traced edges at a 3 px tolerance, correct by hand, mirror. Write `design.json`.
   * **Checkpoint 1**: `rebuild/review/design_overlay.png` and 3x crops of: the top spike and ring, a side spike crossing, the central mountain, a cloud curl, the bottom tip. Pass: every edge within 3 px; the line inventory complete; no region under 6 px except designed tips; gold line or crease decided per mountain boundary; curl and top spike widths measured.
2. **Geometry** (`rebuild/geometry.py`) and **Blender** (`rebuild/build_live.py`).
   * **Checkpoint 2**: triangles over 4x crops of the five areas; the triangle count; the gold patch location.
   * **Checkpoint 3**: Blender viewport front, three quarter, side and back; `validate.py` passing.
3. **Colors** (`rebuild/palette.json`) per section 5.
4. **Write** (`rebuild/write_usdz.py` to `rebuild/cand01/model.usdz`) and `validate.py` on the file.
5. **App**: update `review.json` to `rebuild/cand01`; run `enamel_badges_tools/app_try.py rebuild/cand01 Badge3DPreviewMountainSunburst mountainSunburst`.
   * **Checkpoint 4**: the finish gate (`review_pack.py`: real pixels and 4x), every pose at 4x, the crops named in section 7, the color patches. Then one color re-solve and rebuild if needed.
6. **Fresh review** (badge-fresh-review): shippable and at least 90.

**Stop rule**: a checkpoint that fails because of the method stops the build: revise this plan's affected part and run one badge-plan-review round. Small fixes inside the plan (a point, a color, a height) need no review.

## 9. Budget

About 50,000 triangles (up to 60,000 with the reason stated), under 5 MB, one 512 sun texture. Expected app builds: two.

## 10. Final acceptance and delivery

Finish gate at real pixels and 4x; every pose at 4x; fresh review shippable and at least 90; `validate.py` passing; the model left in the simulator on Radiant Mountain Sunburst; `mountain_sunburst_rebuild.blend` saved. Delivery: `rebuild/mobile/` with the final USDZ, earlier candidates in `rebuild/previous/`, `rebuild/REPORT.md` (side by side, review, uncertainties, the gem shader's production patch need, about 14 parts, no reduction pass needed).

## Review log

### Round 1: TURNED DOWN
* Accepted and fixed in revision 2: creases as vertex rows; split facet normals; facets as measured planes; spike widths at the ring; shared points; profiles under 40 degrees; side walls; glow cap; measured frame and gem; junction table; units; writer materials; checks that could fail; the owner's decision recorded. Risks, nits and new risks folded in; new failure types added to the catalog.

### Round 2: TURNED DOWN
* Accepted and fixed in revision 3:
  * 1 overlapping enamel at one height: the plate is one part with color face sets; every other part stands on a computed base 0.006 above everything under it.
  * 2 junction contradictions: replaced by the stack rule, computed and proven by `validate.py` on the built mesh.
  * 3 top spike: its own definition (solid point above the ring, lemon and edge lines in the plate).
  * 4 spike facets: four planes at 18 degrees, creases on the straight skeleton.
  * 5 gem and frame: clean02 girdle lift, frame inner edge at gem height plus 0.008.
  * 6 Aurora functions: no longer reused; every part is built by `geometry.py` as a closed solid.
  * 7 edge flattening: removed; side walls use the house technique, edges get a 1.5 px chamfer.
  * 8 curls: arc edges at 40 degrees.
  * 9 checks: built mesh mirror check, back equals mirrored front and positive volume, widths from a material render, predicted color table, a per pixel stack check.
  * 10 pale lemon: named procedure with the cap; predicted swatches in `rebuild/palette_predicted.png`.
  * 11 cloud edges: flat to the wall foot.
* Risks folded in: sun rim rows; the sun radius meaning; blended side normals; spike walls as side material; a stable gold patch; flat enamel accepted; the triangle budget; the gem's azure; the busy reflection; in place updates.
* Nits folded in: ring material name; writer output name and face varying normals; backup copy; `review.json` update; lipfix dropped; red field definition; widths per line type; spikes' level in section 1; intended differences recorded.
* New risks folded in: ring outer rounding at 40 degrees over 10 px with roughness 0.30; joins built from one inset network per part; the gem's foil UVs in the writer and `validate.py`; navy in the color table (predicted reachable); the sun's soft sheen accepted; mountain facets accepted as carried by color; no rescaling.
* Owner visible changes since revision 2 (told to the owner): whites at about 0.85 light grey; the sun's sheen instead of glare.

### Round 3: TURNED DOWN (cap reached)
* Blockers (accepted, edits ready, waiting on the owner):
  1. Mountains need their gold outline band (missing from the inventory).
  2. Mountain edge heights must follow the facet planes; target heights for every named point; coplanar facets.
  3. Gem and frame bases computed over parts 1 to 8 only; frame ridge on the band's centre line, at least the inner edge plus 0.010.
  4. Drop the 1.5 px chamfer (sub pixel facet makes outline dots); use the lipfix method on the side walls' top row.
  5. Triangle budget: sample curves by chord error, skip rows on hidden surfaces, a per part estimate.
  6. Snow facets and teal against steel blue must keep their contrast (lavender at the mockup's ratio); a contrast check.
  7. A lemon against gold contrast check that can fail.
  8. Extra turn poses at 45, 135, 225 and 315 degrees.
* Strongest concern: pale lemon predicts as sand next to the gold. Shown to the owner in context: `rebuild/colors_in_context.png`.
* Risks, nits and new risks: accepted (junction heights rule, curl taper, curl and border as one part, gem color constants, gem apex at y 958, side spike tip height, height cap order, spike facet blobs, gold ratio in linear light, paths, interpreter, console string, patch distances, reflection gap, thin parts note, file naming, roughness match, two profiles, side wall flicker, wedge silhouette, coplanar field flash, mirrored pair bases, gem girdle UVs). New failure types added to the catalog.
