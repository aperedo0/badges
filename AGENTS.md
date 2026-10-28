# BestSpent 3D badges: guide for every agent

Read this before working on a badge. It applies to every agent (Codex, Claude, anyone); `CLAUDE.md` points here. The `archive/` folder holds older versions of this file as history only. They are not rules.

## 0. How to use this file

- **The job:** make the badge look the way the owner wants, in the app. When the owner gives a reference image, the badge on Home should look like that reference. Everything else in this file serves that.
- **Only section 2 is hard.** It is the contract with the app: break it and the badge breaks in the app. Sections 3 and 4 are guidance: the owner's taste and lessons from past badges. If a guideline stands between you and the reference, set it aside, say so in the report, and show the result.
- **The owner's word beats this file.** If you are unsure what the owner wants, ask with a picture early instead of guessing through many candidates.
- **Judge with your eyes, in the app, next to the reference.** Numbers help find a problem; they never prove a badge looks right. Past badges passed every number and still looked wrong.

**How a badge gets made:**
1. **Reference.** Start from the owner's reference image or request, and the tier's place in the ladder.
2. **Model in Blender.** Import a working copy of the complete existing badge, including its shell and rim, then build and inspect the new design there. Follow section 2 and the Blender workflow in section 4.
3. **Final test in the app.** Once the model looks ready in Blender, put it in the app and inspect every side (section 5). Do not repeatedly build the app to inspect unfinished geometry. Blender renders are only for working.
4. **Measure and match.** Compare with the reference at the same size. If it is not getting closer, measure the app's light and solve for the colors (section 4) instead of guessing again.
5. **Deliver.** Show the owner side by sides, with options when the look is a judgment call (section 6).

## 1. How the app shows a badge

- One RealityKit USDZ per tier (Iron, Copper, Bronze, Steel, Silver, Gold, Platinum, Diamond), drawn on Home on a lit stage: a backdrop, a glossy floor, the badge's blurred mirror image in the floor, and (for coins) a thin contact shadow. Stage, lights, floor, reflection and shadow are app code, the same for every badge.
- The light is the original studio light: one environment map plus 8 point lights, key light from the upper left. It is fixed; a badge cannot change it.
- The camera is fixed. As Home scrolls up, the badge makes one full turn about the Y axis while it shrinks and sinks toward the floor (angle and size follow the scroll: a quarter turn at three quarters size, the back facing the camera at half size, and so on). At rest it shows its front, but **the owner sees every side**, so the back, sides and top are part of the badge.
- After rendering, the app applies Blender's AgX view transform (Medium High Contrast) and adds a glow to anything brighter than 1.5 in linear light. That glow is why a pure white face grows a halo.
- At load the app retains the model's shape. On the Diamond it replaces the material named `DiamondGem` with its own gem shader (section 2, rule 10). On a coin it gives the brushed ring back its anisotropy, found by name (section 2). The Crimson Shield preview also restores its named field's brushed reflections, as described below.
- **Known app limits:** under a floating shape the app still draws the coin's contact shadow line (a fix is planned, section 7); the first launch after an install shows the flat fallback picture while shaders compile.

### Crimson Shield brushed field (owner approved, 2026-10-20)

The owner approved a shield specific app material addition so its center has real directional brushed reflections. The USDZ field material is named exactly `CrimsonShield_BrushedField`. The preview app restores anisotropy 0.55 and straight diagonal tangents on that material only, before cloning the floor reflection. The front brush direction is `(0.840, 0.543, 0)`; the back reverses X because it is a Y half turn of the front. `ShieldUV` follows the same direction. Other shield materials, coins and Diamond keep their existing rendering.

This exception is currently in the separate preview app, with the production integration patch and instructions at `crimson_shield_20261019/app_material.patch` and `app_material_README.txt`. Production integration must carry that patch: the USDZ alone cannot carry the runtime anisotropy. Never give this shape the coin casing or brushed ring names to trigger their code. The owner authorized this material addition; it is a scoped exception to the app editing restriction, not permission to change lighting, the gem shader or other badges.

### Coin glint shield (owner approved, 2026-10-15)

The owner calls this the **glint shield**. It contains highlight bloom outside a coin's silhouette, removing the occasional puff of light beside the edge while retaining the bright reflections and glints on the metal. It is app image processing, not geometry, a texture, or a material setting.

- **Implementation:** `/Users/antonioperedo/Desktop/screen_time/ScreenTime/Sources/App/Features/Badges/BadgeHeroCard.swift`. Search for `confinesHighlightGlow` and `reflectionGlowLevels`.
- **Automatic coin detection:** the model contains `Casing___smooth_rounded_outer_edge_mobile_geometry`. This covers Water Drop, Teal Sands, Golden Sands, Sunrise Path and Emerald Sprout, and future coins with that casing name. Floating shapes and Diamond keep their previous rendering path.
- **What stays:** original highlight bloom inside the coin; antialiased coverage at its outline; separate reflection bloom outside it. The stage halo, background, floor reflection, lights and model finish are preserved. Never mask the combined bloom alone: that would also remove reflection bloom.
- **Preserve the approved look:** do not dull the metal, remove the inner rim flashes, paint an outline, or change glint frequency to recreate this shield. It does not repair actual model gaps, white edge specks or texture seams; those still need the normal outline checks.
- **Verification:** the initial shield change was checked on Teal Sands at the offending side pose. During the later matching-finish and round-bottom pass, all five coins were checked through full turns and four poses at 4x, with no new external bloom puffs observed. Future renderer edits must preserve the shield and check both side poses alongside the front, back and reflection.

## 2. The app contract (hard rules)

Both kinds of badge:
1. **One USDZ**, USD Y up, 1 meter per unit, front faces +Z, no transforms, same scale as the shipped silver.
2. **Materials** are UsdPreviewSurface. Every texture reads the UV set named by its material's `UsdPrimvarReader` (`varname`); coins carry two UV sets, and editing through the wrong one changes nothing visible.
3. **No lights, cameras, floors or reflections inside the file.** Glowing (emissive) surfaces are allowed: they are part of a material, not a light. The app shows emissive color 1:1.
4. **Fits the frame:** nothing above Y = 3.015 (the Home slot cuts it off) and no wider than about 6.7 units (X from -3.35 to 3.35: Home shows more, but the Badges screen picture frame holds 6.7 at the coins' scale). Centered on X = 0 with the thickness centered near Z = 0 (the spin axis), or it swings sideways while turning. The coins are 6.03 wide; Silver 2 is 6.39 (6% bigger, owner's call).

Coins (round, stand in the floor):
5. **Frozen shell** copied exactly from the shipped silver (`badge_realitykit_silver/mobile/silver_badge_mobile.usdz`, never edit it): casing, rim, lips, channel, inset, same radius 3.015, same names. The app finds `Casing___smooth_rounded_outer_edge_mobile_geometry` and `Silver___circumferential_brushed_steel` by name.
   **Owner-authorized new coin standard, 2026-10-14:** new coins use a wider flat metal band with short bevels, still protruding above a recessed emblem background. Canonical working geometry: `water_match_20261014/shell_template.usdz`, `shell_geometry.npz`, and `shell_design.json`. Outer radius 3.015, inner radius 2.420, band width 0.595, total casing depth 0.930, centered at Z -0.165. The front rim is at Z 0.300; a plain background is at Z 0.044, giving a real 0.256 recess. Keep the floor cut, identity transforms and the app's casing/material names. The five mockup coins use this geometry, with individual material finishes. Their rims use `coin_rim.py`: a uniform metal hue with subtle fine reflectance grain, no emission or painted lighting, and the app's runtime anisotropy. Never solve rim lighting or glow against the reference; highlights and dark sectors must come from actual light. Preserve the shipped silver source and existing installed badges. The owner can refine the new standard after reviewing the app results.
   **Owner's brushed metal reference, 2026-10-15:** use the fine directional grain saved in `coin_brush_grain.npz`, derived from the owner's photo with its broad light bands removed. This refines the earlier constant-color restriction to allow neutral microtexture, never baked highlights. Face, outer bevel and wall share the recognized brushed material, so runtime anisotropy reaches the outer wall too. The inner bevel stays separate with a softer satin finish, targeting the repeated inner rim flicker the owner identified on all five. `RimBrushUV` packs the material charts; it may change with the finish, while points, topology, normals and the original UVs retain the authorized shell geometry.
   The owner likes the compact inner rim flashes, confirmed in the October 15 picture. Both the 0.39 and later 0.32 inner-only experiments failed to preserve that effect. The current confirmed baseline restores BOTH border shader graphs from `coin_glint_reference.usdz`, including their original roughness image and UV sampling; `coin_rim.py` applies this after the broad brushed face and outer wall finish. Preserve these glints. Roughness changes reflection strength and width, not an independently controlled frequency; never claim a measured frequency reduction without observing it. The owner prefers the current flashes over losing them, so no frequency suppression is currently applied.
   **Approved finish transfer, 2026-10-15:** Teal Sands is the finish reference: front band roughness about 0.24, outer wall about 0.198, fine neutral brushing, and the outer bevel using the inner bevel's softer roughness mapping. `match_coin_finish.py NAME SOURCE.usdz OUTPUT.usdz` transfers that finish to `clean`, `hourglass_gold`, `sunrise` and `sprout`, retaining each metal hue and all emblem data. Run it after the older packers; `coin_rim.py` and the original Blender sources alone still produce the preceding finish. Keep the inner rim flashes and the app's glint shield.
6. **Floor cut** at Y = -2.895, no cap, for the older floor standing coins (the coin sinks 0.12 units into the floor).
   **Owner-authorized hovering coins, 2026-10-15:** Water Drop, Teal Sands, Golden Sands, Sunrise Path and Emerald Sprout now have a complete circular shell, with no floor cut. Raising the old shell exposed its flat missing bottom, which the owner rejected. `round_coin_bottom.py SOURCE.usdz OUTPUT.usdz`, run with Blender's bundled Python after the finish step, restores the original eight-point rim profile around all 256 segments and checks that the shell is closed. This exception permits their raw model minimum Y = -3.015, retaining maximum Y = 3.015 and width 6.03. They require app placement: size 0.96 and lift 0.56, which keeps the lowest point at the shared floating height Y = -2.455. Never install them with the old floor standing placement. This placement is currently in the separate simulator preview only; production integration must carry it too. The legacy shell templates and floor-cut validators remain for the older standing models; use the round builder's closed-shell validation for these five instead.
   **New mockup coins, 2026-10-16:** Star Ascent and Island Sunset in `star_island_20261016/` copy that same complete round shell and require the same size 0.96 and lift 0.56. Their fronts have matching sculpted backs. They are separate preview entries, not replacements for existing tiers. Their `README.md` documents rebuilding and `validation.json` checks shell and finish preservation. Never floor-cut these two or install them at the legacy standing placement.

Shapes (custom outline, float above the floor):
7. **Nothing below the floor** (Y = -2.895). How high a shape floats is the owner's design choice (section 3).
8. **Never use the coin names** above: the app would apply the coin's ring shading and glint shield to the shape.

Files:
9. **Work on copies.** Never modify an approved final, the shipped silver, the folders in `~/Downloads/badge_realitykit_*`, or the app repo, except the temporary test in section 5, which must leave the repo exactly as found.

Diamond (drawn by the app's gem shader, 2026-10-11):
10. **One closed, convex mesh with flat facets**, one material named `DiamondGem` (plain UsdPreviewSurface, no textures), at most 256 facet planes, identity transforms. The app traces the studio light through the gem every frame (`BadgeGemSurface.metal`), so every color, flash and rainbow on the Diamond comes from the light at runtime: paint nothing into the model. A dent, a second material name or more than 256 planes makes the app silently keep the plain material, which looks flat. The installed gem is a round brilliant (89 facets, girdle radius 3.12, table at Y 2.349, culet at Y -2.455), turned 22.5 degrees about Y so the seam between two bezel facets faces the camera (a bezel facing it showed a keyhole shaped white flash). Its builder is `gold_diamond_20261009/diamond/gem_shader_20261011/model/build_gem.py`; a plain re-run rebuilds the installed file byte for byte. The Diamond's look (blue, sparkle, rainbow) is tuned in the app's shader, so changing it is an app change (section 7).

## 3. The owner's taste (what good looks like)

1. **Real polished metal.** Strong light and dark, bright highlights, warm and cool tones. Contrast is welcome; a badge that is all soft mid grey reads as plastic or clay.
2. **Smooth.** No grain, mottling, speckle, sparkle, banding, seams, folds or crumpled looking planes anywhere. Check zoomed crops of the app screenshot.
3. **Clean inner edges.** No wide glint lines along the ridges inside an emblem or shape (the owner rejected them). A thin bright border along a shape's outer outline is fine when the reference has one.
4. **Separate from its reflection.** A clear dark line (coin) or gap (shape) between the badge and its floor reflection. Keep plain whatever the reflection shows sharpest: the lowest fifth of the badge and every face that points down.
5. **Readable small.** On the Badges screen a badge is about 40 points wide: each tier needs a distinct silhouette, and no part thinner than about 0.6 units.
6. **Coin rims** keep the shipped silver's original glossy look.
7. **Shapes float at one shared height:** today the lowest point sits at Y = -2.455 (0.44 above the floor), the gap the flat Steel badge shows on Home. This is the owner's design choice, not an app limit; it changes only when the owner asks, and then for every shape.
8. **Light enough to load fast.** Home's launch waits for the badge to load, so stay near the shipped badges: about 35,000 to 45,000 triangles, under about 5 MB, textures 512 or 1024 pixels. Go over only with a reason, and say so in the report.
9. **Clean outline.** No white or bright lines, dots or broken specks along a badge's outer outline (or along a front face's edge where a side wall shows beyond it) at Home size, and no dark notches either. A reference's bright rim highlight is not copied onto the outermost strip of the badge: on the phone that strip is thinner than a pixel and breaks into white dots (found on Copper, Bronze, Steel, Silver 2, Platinum and Diamond, 2026-10-10). Highlights inside the outline stay.
10. **Finished from every angle.** The badge turns all the way around on Home (section 1), so a plain flat colored back reads as unfinished. The back looks like the front (or like the real object's back, for example a shield's), and side walls look like the same metal. Rules 2 and 9 apply at every angle: no white specks, dots or flashing edges while it turns (2026-10-10).

## 4. Techniques

**Blender first, app at the end (owner's workflow, 2026-10-14):**
- Bring the complete current badge into Blender, rather than working on an isolated emblem. For a new coin, include the new coin standard in section 2 so the actual rim, inset, size and depth guide the design.
- Keep the source untouched. Existing approved badges retain their frozen shells; new coins use the owner-authorized replacement in section 2. Preserve the chosen shell data and names when packaging the final USDZ, rather than changing it through a Blender round trip.
- Build and inspect the raised shapes, bevels and materials in Blender, with the reference visible. Check front, both sides, back and the full rotation before exporting. Scripts may create or repeat parts, but inspect the complete result in Blender.
- Prefer the live Blender MCP connection when available: edit the open working scene through Blender's API, then inspect viewport captures after major changes. Verify the connection and viewport capture first. Background Blender is a fallback; say which method is actually being used. Computer Use is optional when the live add-on already supplies editing and visual inspection.
- Use the app for final validation once the design is ready. Its lighting and rendering remain authoritative, so Blender alone cannot prove the final appearance. If that final check reveals a problem, fix that problem and recheck; avoid repeated app builds for routine shape development.
- Keep owner-facing comparisons short. Do not create large review folders or packs in Downloads unless the owner explicitly asks for them.

What works:
- **Match a reference by measuring, not guessing.** Render the badge once in the app with an even color to measure the light on every point of every face, then compute each texture pixel's color as target divided by light, and add emissive for what the light cannot reach. Silver 2's star went from clay to the reference's look in one pass this way, after 34 guessed candidates. Scripts and README: `silver2_metal_claude/` (`try.sh` tests in the app, `solve2.py` solves, `agx.py` inverts the app's view transform). They are built around Silver 2's star (its ten flat faces, each with its own texture area): reuse the method and `agx.py` as they are, and adapt the face and texture mapping for any other badge.
- **Shape in geometry.** Facets are real flat planes (every triangle of one plane shares one normal), dents and bevels are real faces.
- **Texture in the color and roughness maps,** with marks at least 3 to 4 screen pixels wide (about 0.05 units) and intentional patterns (brushing, machining) rather than random speckle.
- **Fade texture out toward the bottom:** fully plain below about 19% of the height, blended back by about 44% (`badge_realitykit_iron/reflection_fix/fade_textures.py`). A fade must never make one part look blurred or plainer than its twin (Steel's lower chevron looked blurred next to the upper one, 2026-10-10): keep it to the parts the reflection really shows and judge the reflection in the app.
- **Solve with the outline excluded.** When solving color and glow maps against the app's light, leave out every texel whose surface point projects within about 3 screenshot pixels of the badge's silhouette, and of a front face's edge where a side wall shows beyond it, from BOTH the light fit (those calibration pixels mix with the background) and the target (the reference's bright rim). Then give those outline texels their tone this way (what fixed all six badges on 2026-10-10, `edge_fix_20261010/tools/solve_band3.py`):
  - **Target from just inside, on screen:** the brightness the surface shows 4 or more pixels inside the outline, measured on screen and spread outward smoothly, separately for front faces and side walls.
  - **Only darker, same hue:** each outline texel keeps its own color and is only scaled down by a brightness ratio (target / its own brightness, at most 1). Never paint a new color into the strip.
  - **Smooth ratio:** blur the ratio along the strip so neighbouring texels never alternate (that made dashes), but never let the blur weaken a texel's own darkening: a one texel white line next to normal texels must still reach the target (ratio = the stronger of its own and the blurred one).
  - **Floor:** never darker than 0.6 x the wider average nearby, so thin tips and points never turn black.
  - **Include the partly covered pixels** at the silhouette and at the front edge (the staircase steps): their texels left untouched show as dots.
  - **Mind the neighbours in the map:** texture filtering blends texels that sit next to each other in the UV map, even across a face edge. Steel's side wall texels beside the front edge were painted white and kept a white line on the front edge after the front was fixed; cap such neighbours (within about 3 texels) to the fixed front texel's brightness.
  Keep side walls a moderate, slightly rough version of the metal so they never flash white at grazing angles.
- **Thin untextured edge parts** (rolled lips, edge strips thinner than a screen pixel) break into dotted lines at Home size. Give them a dark, rough version of the metal (Copper's rolled edge: base color 0.14, 0.055, 0.025, roughness 0.55) or leave them out.

What does not:
- **Baked normal maps on shiny metal:** blotchy facets and a mottled ring.
- **Soft linear ramps on each face to fake metal:** reads as clay (Silver 2 candidates 25 to 34).
- **A mirror polished plane aimed at the key light:** a pure white blob with a glow halo.
- **Judging in Blender only:** different light, and the app shows fine grain about 2.5 times stronger.
- **Chasing number targets** (face brightness gaps, white pixel counts, shine caps): they produced badges that passed and still looked wrong.
- **Patching the outline after the solve** (replacing the outermost strip of a finished map with the nearest inner texel): it removed some white rims but left dark notches on thin tips, black bands where a side wall shows, or no change where the rim sits a few pixels inside (2026-10-10). Fix the outline in the solve instead.
- **Painting an inside color into the outline strip:** light patches on thin flames and a changed dome ring. **Darkening without a smooth ratio and a floor:** dashed edges and black leaf tips (2026-10-10).
- **Checking only a couple of zoomed spots:** missed edges came back in review. Check every tip, point and long edge at 4x zoom against the previous version.

What fixed the outlines for good (Copper, Bronze, Platinum, 2026-10-13, `rim_fix_20261012/`, REPORT.md and tools there):
- **The darken-only outline strip itself became a dark or orange stroke** (the owner still saw "weird outlines"). Repaint the outermost 3 screen pixels of the texture as the smooth (harmonic) continuation of the texels just inside, narrower on thin tips, and refill everything outside the shape by pull push so mipmaps never bleed a rim (`tools/bandfill.py`).
- **A thin edge lip with its own dark material draws a 1 px line around everything.** Give the lip the normals and texture coordinates of the face it borders and a dimmed (about half) copy of that face's material (`tools/lipfix.py`). A lip at full brightness draws a light line instead.
- **Rounded edges mirror a different part of the studio than the face** (dark or white rim). Blend the normals within about 0.07 units of the edge toward the normal just inside (`tools/edgeflat.py`).
- **Side walls:** plain metal (no texture: a wall sampling the face texture zips and streaks from behind), dark but not black, roughness 0.5 to 0.6, normals blended about 70% toward the nearest face.
- **Look for real gaps:** Bronze's dashed ring was a 0.015 unit see-through gap and a hairline between two beads.
- Blender's USD writes the file about twice as big: re-save with `/usr/bin/usdcat`.

## 5. Testing in the app (required before showing the owner)

The app repo is `/Users/antonioperedo/Desktop/screen_time`. All eight tiers have a 3D model in `ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModel<Tier>.dataset/<tier>_badge_mobile.usdz` and a Badges screen picture in `BadgeArt<Tier>.imageset/BadgeArt<Tier>.png` (600 x 600, cut at the fixed Home frame: `stills/make_still_fixed.py`, or `edge_fix_20261010/tools/still_cut.py` from a Home screenshot). **The installed files are the newest versions**: Copper, Bronze, Steel, Silver and Platinum carry the 2026-10-10 outline fix that the finals in the older working folders lack, and the Diamond is the 2026-10-11 gem (section 2, rule 10), so start any change from a copy of the installed file. Whatever file is in a data set, back it up and put it back byte for byte after a test.

```sh
/Users/antonioperedo/Desktop/screen_time/tools/sim/badge-try <tier> <candidate.usdz> --out <candidate folder>
```

It swaps the model only while it builds, restores it byte for byte even after a failure, and shoots the front plus the 94, 133 and 171 point turns on its own BestSpent Badge Lab simulator. It takes several minutes: allow at least 15, and if it is killed, copy the backup named on its first line (`backup: ...`) back over the model, delete the backup, then run `/Users/antonioperedo/Desktop/screen_time/tools/sim/app build`.

Prove the 3D badge is showing by looking (beveled edges catching light, a matching reflection; the fallback is flat art), or with a slow upward drag of 80 to 180 points, after which the badge is turned and smaller (the flat still never turns). Then check the outline (section 3, rule 9): a 4x nearest neighbor zoom of every tip, point and long edge, next to the previous version. Never edit app code, never commit, never switch branches.

**Every side (section 3, rule 10):** the turn starts after about 56 points of scroll and takes about 153 more. Slow drags of about 94, 133 and 171 points show the badge from the side, from the back (half size) and from the other side. `badge-try` shoots the 94, 133 and 171 point turns by default; adjust with `--poses a,b,c` until each pose shows. Check every pose like the front, outline included.

## 6. Working and delivering

- **Each candidate** gets a numbered folder: the usdz, the app screenshot, a side by side with the reference (or the previous final) at the same size, and two lines on what changed and why.
- **Check in early.** If two or three candidates do not move clearly toward the reference, stop and report with pictures and what you think blocks you, instead of spending ten candidates.
- **Offer options when the look is a judgment call** (how bright, how warm, border or no border): show two or three candidates side by side from the app and let the owner pick, instead of delivering one final and defending it.
- **Deliver:** the final usdz in the tier's `mobile/` folder (previous final kept in `previous/`), a short `REPORT.md` (what changed, the side by side, anything uncertain, any guideline you set aside and why), and the app repo left exactly as found.

## 7. Planned app changes (the owner asks Claude; badge agents never make them)

1. A per model setting telling the app a badge floats, which turns off the coin contact shadow under it (and maybe adds a soft shadow).
2. Each new 3D tier's data set and its line in the app's model table.
3. Each tier's Badges screen picture (`stills/`), rendered at the coin stills' scale (6.03 units = 108 of 120 width units) with the badge where it sits on Home.
4. A tilt of the spin axis toward the viewer, for a badge that should lean the same way all the way around (Gold's full crown may ask for it). A tilt built into the model turns with the badge, so it leans toward the viewer at the front and away at the back.
5. The Diamond's look: its blue, brightness, sparkle and rainbow are named constants in the app's gem shader (`BadgeGemSurface.metal`), not in the model.
