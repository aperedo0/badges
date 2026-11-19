# Badge failure catalog

What has gone wrong in this app, or plainly can. Three layers:

1. **Every badge**: always applies. The plan answers each item with a prevention and a check.
2. **Only if the badge has it**: sections opened by the badge's features. The plan lists the badge's features, answers every item in the matching sections, and skips the other sections with one line each ("No gems"). No item by item "not applicable".
3. **This badge's own risks**: found fresh for every badge (method below). The catalog only holds what happened before; the next failure is usually something new.

Format: **what the owner sees**: cause. Prevent. Check. (Where it happened, when known.)

The app (AGENTS.md section 1): fixed camera and studio light (key from the upper left), a glossy floor with a blurred reflection, AgX color finish (Medium High Contrast), glow on anything brighter than 1.5 in linear light, one full turn about Y while scrolling (side at three quarters size, back at half size). A badge is about 416 pixels tall at rest in a simulator capture and about 40 points wide on the Badges screen.

## 1. Every badge

0. **Flat, fuzzy look: the badge built as one plate with painted areas and tiny bumps for lines.** Relief of a few hundredths of a unit smears into blur at phone size. Prevent: stacked pieces with real thickness and bevels at least about 0.04 units wide (badge-plan, "Build it like the real object"). Check: side and 45 degree poses show distinct stacked pieces; 2x tiles show crisp edges between pieces. (Mountain Sunburst rebuild, Nov 8, 2026.)
1. **Fuzz or glitter along lines**: triangles that cross the design's lines instead of following them. Prevent: vertices along every outline, bevel and crease; build from curves, never a grid over a picture. Check: triangles drawn over a 4x crop before materials. A raster height field sampled at vertices cannot hold a crease either: ridges, grooves and profile breakpoints each need their own vertex row. (Enamel badges, Nov 8, 2026; Mountain Sunburst plan review, Nov 8, 2026.)
2. **Wobbly, lumpy or melted lines and blobby junctions**: noisy outlines, uneven widths, heights that bulge where lines meet. Prevent: clean curves, straight runs straight, tips sharp, one width per line, designed junctions. Check: 4x crops of junctions and long lines. (Enamel badges, Nov 8, 2026.)
2b. **A part built from a misread description**: a written summary of the mockup called gold edged lemon spikes solid gold and the badge flat enamel. Prevent: inventory from the image; sample pixels across any unclear part. Check: the overlay of the design on the mockup, part by part. (Mountain Sunburst, Nov 8, 2026.)
3. **Wrong proportions or placement**: guessed sizes. Prevent: measure from the mockup's badge box in units. Check: the review pack's outline overlay and width table.
4. **Too thin to read**: parts under about 0.6 units vanish at 40 points. Check: the phone size picture.
5. **Faceted patches on curves, mushy facets, rounded ridges**: wrong normals; one blurred normal per vertex rounds every ridge and facet. Prevent: smooth within curved parts, split at intended hard edges, facets as real flat planes. Check: 4x crops under the app light.
6. **Grain, speckle, mottling, blotches, copied highlights**: detail under 3 to 4 screen pixels, normal maps on shiny metal, the mockup's painted light copied into colors. Prevent: intrinsic colors only; marks at least 0.05 units. Check: 4x crops of flat areas.
7. **Clay or plastic look**: no strong light and dark. Prevent: real relief, polished metal, judged in the app. Check: rest capture beside the mockup.
8. **A color or metal that looks wrong in the app, or two areas meant to differ that come out the same** (two snow facets both capped to one grey): AgX desaturates bright colors and pale metals; some colors cannot be shown at all (layer 2, bright saturated colors). Prevent: check every mockup color against what the app can show; measure the app light and solve colors (AGENTS.md section 4) instead of guessing. Check: captured colors at named spots against the mockup.
9. **White blob with a halo, whites that glow, or a haze around all the gold**: a mirror plane facing the key light, or any surface over 1.5 linear; bright enamel reaches it easily. Prevent: enamel through `enamel_fill.py`, whose emission stays at or under 1.4 linear on every color, whites and yellows included (item 24b); flat painted colors through `palette.py`, which caps them the same way. Bright polished gold passes the glow level too and wraps every line in haze: keep metal bases and roughness so flat gold stays under it. Check: rest and early turn crops of every white, yellow and gold area at 2x, and of the reflection. (Mountain Sunburst plan review and rebuild, Nov 8, 2026.)
10. **Unfinished or washed out back**: a plain back, or only fill light reaching it. Prevent: a back that mirrors the front or matches the real object; judge it in the app. Check: the back pose beside the front.
11. **Mottled, streaked or banded side wall; edges that flash while turning**: the side samples the face texture, coarse steps, sharp rims at grazing angles. Prevent: plain side metal, dark but not black, roughness 0.5 to 0.6, normals blended toward the faces. Check: early turn and both sides at 4x. (Enamel badges, Nov 8, 2026.)
12. **Missing faces or inside out patches**: one sided faces, flipped normals. Check: back and side poses.
13. **White dots or a broken bright line along the outline; dark notches**: a bright strip thinner than a pixel. A chamfer or bevel narrower than a screen pixel does the same. Prevent: AGENTS.md section 4 outline fixes; the top row of a side wall takes its face's normal and material (`rim_fix_20261012/tools/lipfix.py`). Check: 4x of every tip and long edge, front and turned. (Six badges, Oct 10, 2026; Mountain Sunburst plan review, Nov 8, 2026.)
14. **Badge merges with its floor reflection**: a busy or bright lowest fifth. Prevent: keep the lowest fifth and downward faces plain. Check: rest capture.
15. **Clipped, swinging, misplaced, or treated as a coin**: over Y 3.015 or 6.7 wide, off the spin axis, below the floor, coin names used. Check: `skills/badge-build/scripts/validate.py` (bounds, coin names, Z centering) and the bounds the writer prints.
16. **Slow Home launch, or no texture**: over about 45,000 triangles or 5 MB, textures over 1024, a UV set name the material does not read. Uniform fine sampling of long curves blows the budget: sample by chord error (about 0.1 px) and skip rows on hidden surfaces; estimate triangles per part in the plan. Check: the writer's counts and the app capture.
17. **Grooves and lips that crawl**: profile details under about 8 px (0.04 units) break into dashes on curves and shimmer while turning. Check: 4x at the early turn. (Mountain Sunburst plan review, Nov 8, 2026.)
18. **Bloom puffing beside the outline**: bright gold facing the key light near the silhouette; only coins have the app's glint shield. Prevent: rougher metal near the outline, limited tilt toward the key. Check: upper left outline at rest and early turn.
19. **Wide flat gold blowing out**: a broad flat band reads flat or white. Prevent: a rounded or ridged profile with numbers. Check: rest crops.
20. **A glossy flat field flashing as one sheet** at some turn angle. Prevent: a slight dome per cell or roughness of at least about 0.18. Check: turn poses at about 45 and 135 degrees.
21. **Turn checked at too few angles**: problems that show only between the standard poses. Prevent: capture extra poses at about 45, 135, 225 and 315 degrees, or a slow full turn. (Mountain Sunburst plan review, Nov 8, 2026.)
22. **A defect missed because only part of the badge was looked at, or it was compared with the last version instead of with clean**: Prevent: the finish check covers the whole badge at 2x in tiles, a fresh agent repeats it, and several turn frames are viewed in a row for crawling edges. (Mountain Sunburst rebuild, Nov 8, 2026.)
23. **Process**: built outside the open Blender; Blender closing after objects are deleted; a broken method tuned round after round; a build shown before passing the finish gate. Prevent: badge-quality's Blender rules, the plan's stop rule, badge-fresh-review step 0.
24. **A colored face washed pale by a mirrored studio light**: enamel faces that tilt left and down, worst in the badge's lower left, mirror the studio's low left reflector (teal read pale grey, navy read lavender). Tilting the faces up instead still washed navy to 9 times its paint (cand03). Flat but rough still washes near the reflector's mirror spot (about badge minus 1.5, minus 1.5): at roughness 0.30 its glow spread a unit (cand04). Prevent: colored faces flat, as real enamel, domes about 0.03 or less, colored fields in the lower half at roughness about 0.18; metal may tilt any way. Check: `badge-build/scripts/app_colors.py`, the app's lightness of every material against the mockup's. (Mountain Sunburst cand02 and cand03, Nov 9, 2026.)
24b. **Enamel washed pale or glaring white in the app** even when flat: a non metal enamel adds the studio's pale reflection on top of its color. Prevent: the approved enamel method (`badge-build/scripts/enamel_fill.py`: metallic, near black color, the mockup's color in emission through the inverse AgX). Check: `app_colors.py`. (Mountain Sunburst cand02 to cand06; method from Tidal Compass and Emerald Trophy, found Nov 9, 2026.)
25. **Stripes in a painted gradient**: each step solved on its own snaps to its own paint and neighbors jump back and forth. Prevent: solve the two ends and blend smoothly (`palette.py`). Check: 4x of every gradient. (Mountain Sunburst cand02, Nov 9, 2026.)
26. **Straight streaks across a dome**: long thin triangles spanning the middle between the outer rings. Prevent: rings all the way to the center (`badge3d.py`). Check: 4x of every domed area. (Mountain Sunburst cand02, Nov 9, 2026.)
27. **A whole badge score hiding a missing part**: gold scored 84% overall while both curls were thorns and the border half as wide. Prevent: `material_map.py` lists every local miss with its place; fix each or say why it is not one (metal highlights read as white). Check: its misses picture. (Mountain Sunburst cand02, Nov 9, 2026.)
28. **A dark speck on a smooth glowing surface at rest**: the app draws a dark pixel wherever one of its eight lights reflects straight into the camera (surface direction half way between light and camera). Glow only enamel shows it as a speck in pale or bright color. Prevent: every enamel material in `glow_only` in PIECES.json, so badge3d gives it one fixed shading direction clear of every light (enamel_fill.py and write_usdz.py refuse otherwise). Check: `light_centers.py CAND` prints `centers: 0`. On real metal it cannot be avoided; a faint dark pixel in a highlight is an app side fix for the owner. (Golden Storm, Nov 9, 2026.)

29. **False geometry drift from thin triangle distance queries**: Blender BVH nearest points reported0.0043 away on chest bevels that double precision tests placed within0.00000001, and one ray falsely classified a slider point0.225 outside its backing as inside. Prevent: preserve the shape gate and verify long thin triangles with double precision bounds, closest points, parity rays and cross product barycentrics. Containment uses verified solid interior witnesses, not boundary vertices. Check known surface/outside points, real displacement and a fully enclosed solid without crossing surfaces. (Treasure chest, Nov15,2026.)

## 2. Only if the badge has it

### Traced from the mockup picture
* **Lumpy traced line work**: spirals and outline rings traced from color wobble with the shading beside them and come out lumpy and twice as wide; a highlight on the gold read as enamel and dropped an inner curl. Prevent: gold with its highlights, then `badge-build/scripts/linework.py` (even strokes from the centerline). Check: the strokes drawn over the mockup. (Golden Storm plan, Nov 9, 2026.)
* **Thin gold eaten by subtraction**: gold curls built as a gold area minus grown enamel lose every part thinner than the growth (the C curls came out as thorns). Prevent: trace the enamel fills by color, smoothed (blur, contour, simplify), and set them into one gold plate; the gold between them stays as the mockup has it. Check: the misses picture. (Mountain Sunburst cand02, Nov 9, 2026.)
* **Wrong parts** (gold where enamel belongs, white highlights taken as white enamel, painted shading taken as walls). Prevent: a numbered part map checked by eye against the mockup and corrected by hand. Check: the map over the mockup. (Enamel badges, Nov 8, 2026.)
* **Missing lines** (a snowline, a rim) where tracing found only fragments. Prevent: list every line of the mockup and its source. Check: the line inventory against the built map.

### Raised metal walls with enamel or inlay between them
* **Dark fringe around every wall**: wall sides steeper than about 45 degrees mirror the studio's dark parts. Check: 4x of walls.
* **Puffy enamel** standing above the wall tops instead of sitting just below them. Check: side pose.
* **White streak along walls**: enamel that rises at the wall foot catches the light. Prevent: enamel flat to the wall foot. Check: 4x of dark cells next to walls. (Mountain Sunburst clean02, Nov 8, 2026.)
* **Enamel slivers that shimmer**: a cell tapering between two lines to under a pixel. Prevent: end the enamel at about 0.02 units with a gold cap. Check: 4x of every tip.
* **Yellow enamel and gold metal look the same**, or gold reads pale. The app's strongest yellow has only about 70% of a mockup lemon's color, so the lemon cannot move away from the gold: move the gold instead (deeper, more orange), solved per region because the studio lights each region differently (upper gold read dull, lower gold pale). Check: `app_colors.py`, gold and yellow apart in hue and lightness. (Enamel badges, Nov 8, 2026; Mountain Sunburst cand02, Nov 9, 2026.)

### Bright saturated colors (lemon, yellow, bright orange)
* **Turns khaki or pale**: AgX shows strong yellow only up to about (0.76, 0.57, 0.04) in display terms, and glossy enamel adds the studio's reflection on top. Prevent: default to pale lemon (the owner's choice; enamel_fill.py's pale lemon rule) and list it in the review settings as an intended difference; offer darker golden or an app change. Check: predicted against captured color. (Enamel badges, Nov 8, 2026.)

### Separate stacked or layered parts
* **Layering misread: a part cut in two by one it should cross over.** The long blades lay under the ring, so each read as a kite plus a cone; a top view check passes because both are gold. Prevent: for every crossing, read from the mockup which part's edges run unbroken through it; that part comes later in the stack. List the crossings in the plan. Check: 2x tiles at every crossing. (Mountain Sunburst cand02, Nov 9, 2026.)
* **Gaps or see through slits** when turned. Prevent: shared edges or overlaps with closed backs. Check: side poses at 4x.
* **Flicker where two surfaces share a depth** (z fighting). Prevent: offsets of at least about 0.004 units. Check: early turn. (Blue Hourglass plates, Nov 8, 2026.)
* **Parts that look stuck on, floating or flat from the side**. Check: side poses.
* **Steps that read as black outlines**: a vertical or steep step mirrors the dark studio all around a part. Prevent: steps as gold ramps no steeper than about 40 degrees, or steps of 0.03 units or less. Check: 4x at part edges. (Mountain Sunburst plan review, Nov 8, 2026.)
* **Blobs or poke through where parts meet**: undefined heights at junctions. Prevent: a junction table: which part is on top, heights on both sides.
* **Side walls in the same place flicker**: a covered part's edge running along its cover's edge. Prevent: covered parts end at least 4 px inside their cover. Check: outlines of different parts never run within 2 px of each other. (Mountain Sunburst plan review, Nov 8, 2026.)
* **A base under an edge forming piece**: a full silhouette base plate leaves its wall beside every piece that forms the outline (star points, clouds), or a sub-pixel ledge of bevel outside it. Prevent: that piece reaches the silhouette exactly and the base ends 6 px inside it along the outline. Check: `validate.py` fails on outlines running together over 30 px. (Golden Storm plan review, Nov 9, 2026.)
* **A recess cancelled by a rising profile**: a fill set into a plate whose profile is still rising at the fill's edge ends up flush, with a tilted floor. Prevent: profiles reach full height before any cell begins. Check: print crest minus floor for every plate (at least 0.015). (Golden Storm plan review, Nov 9, 2026.)
* **A part's outline missing**: the line inventory forgot the gold band that outlines a whole part (the mountains). Prevent: list every part's outline band in the inventory.

* **A working sleeve still passes through the frame**: reliefs cut only into hinge leaves leave the actual body or lid rail inside the other moving knuckles. Prevent: cut the complete opposite sleeve swept envelope from every affected assembly, with real rooted supports retained. Check the actual frame throughout opening and prove a missing frame relief fails. (Treasure chest rear hinge plan, Nov15,2026.)

### Mirror symmetric design
* **Lopsided** from traced noise. Prevent: build one half and mirror. Check: flipped capture compared with itself.
* **Mockup halves that differ** (an AI picture is rarely symmetric): mirroring one half leaves the other off by the full difference. Prevent: average both sides by signed distance to the shape's edge; the badge stays symmetric, halfway between both. (Mountain Sunburst cand03, Nov 9, 2026.)

### Gems
* **Odd colors on a foil gem's girdle**: the girdle strip blends the front and back foil UVs. Prevent: split the strip into front and back rows with their own UVs.
* **Drained of color, shards, a keyhole flash while turning**, or the gem shader silently not attached. Prevent: badge-quality's gem section and the renderer's conditions (closed convex mesh, flat facets, material names). Check: several turn angles and the attach line in the console.

### Glass or transparent parts
* **Invisible, grey, or showing the studio's light panels as grey squares**; a bright bar from the overhead light. Prevent: the preview app's glass shader path and its normal limits. Check: rest and turn. (Blue Hourglass, Nov 8, 2026.)

### Fine marks: brushing, engraving, veins, glitter
* **Speckle or a shimmering line** from marks under 0.05 units or glitter dots catching the key light. Check: 4x crops at rest and early turn. (Blue Hourglass stream, Nov 8, 2026.)

### Coins (the round shell)
* **Broken rim or glint shield**: the frozen shell, names, placement and finishes in AGENTS.md section 2. Check: AGENTS.md section 5.

## 3. This badge's own risks

Before the plan is done, find the risks no catalog lists. Write at least five, specific to this badge, each with a prevention and a check:

* **Pre mortem**: it is a week later and the owner hates this badge. Write the most likely reasons.
* **Part by pose**: picture each part at rest, at the early turn, from the side, from the back at half size and at 40 points. What does it look like there?
* **Material by light**: each material facing the key light and at a grazing angle.
* **Joins**: each place two parts meet, from the front and from the side.
* **What is new**: everything this badge does that the closest approved badge did not. New things are where new failures hide.

## Growing the catalog

When something goes wrong that this catalog does not name (an owner complaint, a reviewer finding, a failed checkpoint), add it with the badge and the date: under Every badge when it could happen to any badge, otherwise under the feature that causes it, adding a feature section if needed. Keep each item to one or two lines; merge with an existing item rather than repeating it.
