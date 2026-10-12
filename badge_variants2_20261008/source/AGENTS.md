# BestSpent 3D badges: rules for every agent

Read this whole file before touching any badge. It applies to every agent (Codex, Claude, anyone). `CLAUDE.md` in this folder points here.

The owner's words that drive everything below: "I always want all of the badges to look super smooth," and every tier's rim must be "uniform, the same across the board." When the owner asks for something these rules forbid, do what the owner asked for that badge, write down the exception in that badge's REPORT.md, and still follow every rule that the request does not touch.

## 1. What a badge is

- One RealityKit USDZ per tier (Iron, Copper, Bronze, Steel, Silver, Gold, Platinum, Diamond). The app draws it on Home on a lit stage: a backdrop with a light from above, a glossy floor, the badge's mirrored reflection in that floor, and a thin contact shadow where a coin touches the floor. The stage, lights, reflection and contact shadow are app code and are the same for every badge. A badge never brings its own floor, lights or reflection.
- A badge is one of two kinds. The owner decides which kind each tier is. Today Iron and Silver are coins, and Steel is planned as the first shape.
  - **Coin**: round. A frozen **shell** shared by every coin tier + a per-tier **emblem** (the raised center shape) + per-tier **colors**. It stands sunk into the floor. Sections 2 and 3.
  - **Shape**: a custom solid silhouette (chevrons, a shield, a crown, a gem) with no coin around it. It floats slightly above the floor, like the flat Steel badge on Home today. Section 2B. Every other section applies to both kinds unless it says "coins only" or "shapes only".
- Approved coin reference: `badge_realitykit_silver/mobile/silver_badge_mobile.usdz` (the shipped silver). Never edit it. Its source pipeline and rules live in `~/Downloads/badge_realitykit_v3/` (`EXPORT_RULES.md`, `scripts/`); the master scene is `~/Downloads/badge_realitykit_handoff/scenes/silver_medallion_working_copy.blend`.
- Work on copies only. Never modify the silver files, the folders in `~/Downloads/badge_realitykit_*`, or the app repo (except the temporary in-app test in section 7).

## 2. Coins only: never change (the frozen shell)

1. **Shell geometry**, copied exactly from silver: casing and rim, rim inner lip, inner edge, inner channel, inset disk. Same radius (3.015), same front and back (Z -0.345 back), same profile and bevels, same triangles. Every tier's rim has the same size and shape.
2. **Names**: every object, mesh and material name stays identical to silver's. The app finds parts by name, for example the entity `Casing___smooth_rounded_outer_edge_mobile_geometry` and the material prefix `Silver___circumferential_brushed_steel` (the app restores that ring's brushed anisotropy at load, because USD cannot carry it). Names are IDs; only the look changes. The app's `prepareRimMaterials` silently skips the brushed anisotropy and the rim roughness (section 4, rule 8) when a model's casing entity or that material name differs (no error, the ring just loses its brushed highlight and its even look), so the names must stay identical on every tier. It also reads the casing's outer-edge material by the name prefix `Outer_edge___smooth_satin`.
3. **Coordinates**: USD Y up, 1 meter per unit, front faces +Z, no transforms, same origin and scale as silver. The app's camera frames every badge identically.
4. **Floor cut**: every mesh is cut at Y = -2.895 (EXPORT_RULES rule 5), no cap. The coin stands sunk 0.12 units into the floor; nothing below the floor may ship.
5. **The coin-to-reflection separation**: at the bottom of the coin, where it meets the floor, a thin dark line must separate the coin from its reflection, exactly as silver shows. Anything bright, busy or textured in that band makes the coin look pasted onto its own reflection (see section 9, mistake 5).

## 2B. Shapes only: never change (the frozen frame)

Every shape tier follows all of these, so the shapes read as one family and land where the app expects them.

1. **Coordinates**: the same as coins: USD Y up, 1 meter per unit, front faces +Z, no transforms, same scale. The app's camera and pose are the coin's, unchanged.
2. **Centered on the spin axis**: the badge enters with one full turn about the Y axis through X = 0, Z = 0. Center the shape on X = 0 and its thickness on about Z = 0, or it swings sideways while it turns.
3. **Size box**: at most 6.03 units wide (X from -3.015 to 3.015, the coin's width) and 4.6 to 5.4 units tall. The flat Steel art is about 5.1 wide and 4.9 tall in these units. Nothing above Y = 3.015: the Home slot shows only a sliver above the coin's top, so anything higher is cut off.
4. **Float height**: the lowest point sits at Y = -2.455, which is 0.44 units above the floor (Y = -2.895). That is the gap the flat Steel badge shows on Home today. Every shape tier uses the same gap; if the owner wants a different height, it changes for every shape tier at once. Nothing may reach below the floor, so shapes need no floor cut.
5. **Same build on every shape**: front to back 0.5 to 0.8 units thick (the coin is about 0.6), with the same thickness, the same bevel width and profile on the outline, and the same outline finish on every shape tier. The first shape the owner approves becomes the shape reference; later shapes copy those three exactly.
6. **No thin parts**: no arm, point or bar narrower than 0.6 units (the flat Steel chevron arms are about 1.1). The Badges screen draws badges about 40 points wide, where 0.6 units is about 4 points; thinner parts break up or vanish.
7. **Distinct silhouette**: fill the outline solid black and shrink it to 40 points wide. It must be recognizable and unlike every other tier's. Today's flat art is the starting point unless the owner picks new outlines: Iron hexagon, Copper ring, Bronze shield, Steel double chevron, Silver star, Gold sunburst, Platinum crown, Diamond gem. Higher tiers may get more detailed and richer, never plainer than a lower tier.
8. **Names**: name objects and materials `<Tier>_<part>_<finish>`. Never use the coin names (`Casing___smooth_rounded_outer_edge_mobile_geometry`, `Silver___circumferential_brushed_steel`, `Outer_edge___smooth_satin`): the app reshapes those parts' shading at load to fit a round ring, which would distort a shape.
9. **Finish lives in the file**: the app's rim roughness override (section 4, rule 8) touches only coin rims, so a shape ships exactly the roughness in its file. Outline bevels are satin, roughness about 0.40, never mirror polished: a mirror edge reflects the gaps between the studio lights and goes dark and bright in patches, which is what made the coin rims look uneven. USD cannot carry anisotropy, so a brushed look must come from the color and roughness maps (section 5).
10. **The gap separates it from its reflection**: in the app, a clear dark band must show between the shape's lowest edge and the top of its reflection. Keep the lowest fifth of the shape and every face that points down plain and even, because the reflection shows them sharpest (section 5, rule 7).

## 3. Coins only: may change per tier (within limits)

Shapes may change anything section 2B does not fix: the outline, inner details, colors and textures (section 5).

- **Emblem shape**: any shape, centered on the inset, about the same height, width and depth as the silver emblem so it sits the same way in the frame.
- **Emblem colors**: a lit tone and a shaded tone (two materials, names unchanged).
- **Rim tint**: the rim may be tinted to the tier's metal, but its brightness in the app stays in the same family as the approved rims (`rim_top` from the measure script between 130 and 175; silver 167, iron 147). The rim's finish stays the same family on every tier.
- **Textures**: allowed when the owner asks for them, following section 5.

## 4. Look rules (the owner's standing taste)

1. **Smooth.** No grain, mottling, blotches, streaks, banding, seams or sparkling dots on any facet, the rim or the inset. Check zoomed crops of every surface before calling anything done. Fix at the source (model or material), never by hiding it.
2. **Clean gem edges.** No widened bevel glints along facet edges. The owner rejected them; never propose them again.
3. **Every plane truly flat.** All triangles of one visible plane share one normal (report the max difference; it must be 0). A plane split into slightly different triangles reads as crumpled foil.
4. **Clear structure.** One clear ridge; lit side and shaded side; each plane a visibly different tone from its neighbors (at least 10 display levels apart in the app-lighting render). No horizontal band or "roof" across the top. No tiny slivers visible from the front.
5. **No blown highlights.** No plane renders pure white, and nothing glows past the emblem's edge. The app adds a glow to anything very bright, so a plane that mirrors a light straight at the camera turns into a white blob with a halo. In the app test, a coin's `emblem_clip` must not exceed silver's (796). A shape has no emblem box: count the pure white pixels (max channel at least 254) over the whole badge box of the app screenshot (x 360 to 845, y 340 to 812 on the iPhone 17 shot); at most 1249, silver's count in that same box.
6. **No dead black.** No large plane goes nearly black (plane mean at least 15).
7. **Shine at most silver's.** Lower tiers may be a little duller than silver, never shinier.
8. **Even rim, judged in the app (coins; shapes see the end of this rule).** The app's studio environment includes a soft ring of light (about 20 to 60 degrees from the view axis) so the polished rim reads evenly all the way round instead of going dark between the light panels. At load the app also sets the roughness of the rim's brushed face (`Silver___circumferential_brushed_steel`) and of the casing's outer edge (`Outer_edge___smooth_satin`) to 0.40 for every tier, so a badge file's own roughness on those two materials is overridden and a Blender render of the rim does not predict the app. Judge rim evenness only in the app: `/usr/local/bin/python3 lighting/rim_even.py <app_rest.png>` prints the worst dark share of the rim band (about 0.08 on a good silver or iron) and the band's brightness spread (about 61 to 71). Shapes: the outline bevel must read evenly all the way round in the app, with no stretch of edge going nearly black next to a blown white one. `rim_even.py` measures only round coins, so judge a shape's outline by eye on zoomed crops of the app screenshot.

## 5. Textures (allowed, done the right way)

Textures can look great. Silver's rim already has a brushed texture and looks smooth. Textures go wrong in three specific ways, so every texture must follow all of these:

1. **Color and roughness first, not bumps.** Put the texture in the color and roughness maps (glossier and duller patches, gentle color variation). These cannot sparkle, because the surface stays flat to the light.
2. **Bumps (normal maps) only when the owner explicitly asks** for that badge. Then: bake the strength into the map (USD drops the Normal Map node's Strength; EXPORT_RULES rule 4), keep it restrained, and prove it with the sparkle checks in section 7. On the matte inset a subtle baked normal map is fine.
3. **Marks big enough.** Every texture mark (dimple, scratch, grain, line) is at least 3 to 4 screen pixels wide at the coin's size on Home (the coin is about 459 pixels wide on a 3x iPhone, so about 0.04 to 0.05 model units). Finer detail cannot be drawn cleanly and turns into shimmering grain.
4. **Low contrast.** Subtle variation reads as premium; strong variation reads as dirt.
5. **Intentional patterns.** Directional or structured patterns (brushed lines running around the ring, concentric machining, large hammer dimples) look crafted. Random fine speckle looks like a rendering error.
6. **Big shapes in geometry.** A hammered or forged look made of large dents should be real faces on the model, not painted-on bumps.
7. **Keep everything the floor reflection shows clean, not just the contact.** The reflection is a mirror image of the coin seen from below the floor, so it shows a much taller strip of the rim than the part that touches the floor, and it is sharpest right under the contact. Any texture in that strip appears crisp at the top of the reflection, directly under the coin, and reads as a second object overlapping the coin. What worked on iron (2026-10-07): fully even below 1.1 model units above the floor (about the lowest 19% of the coin), blending back (smoothstep) to the full texture by 2.6 units (about 44%); see `badge_realitykit_iron/reflection_fix/fade_textures.py`. Then judge in the app's floor-contact zoom: the top arc of the reflection must look as smooth as silver's. Cleaning only the lowest 5% is not enough (section 9, mistake 8). On a shape, the reflection mirrors its lowest part and every face that points down: keep the lowest fifth of the shape plain and blend the texture back in above it the same way.

## 6. Export rules

Follow every rule in `~/Downloads/badge_realitykit_v3/EXPORT_RULES.md`. In short: sub-pixel bevel strips shade exactly like their facet and use its material (set each Bevel modifier's own bevel material so the rules script can fold them); no baked normal maps on polished metal unless section 5.2 applies; any normal map that stays is baked at the strength it should show; floor cut at -2.895 (coins only; a shape floats, so nothing of it reaches the floor); everything else (names, hierarchy, Y up, units, textures sizes) carried over. Keep the triangle count, texture sizes and file size in the same range as silver (about 38,500 triangles, about 2.5 to 4.5 MB).

## 7. Checks before a badge is "done"

All of these, every time, in one candidate:

1. **Export checks**: `usdchecker --arkit` and `reimport_check.py` for both kinds. Coins also: `verify_floor_cut.py`, and `compare_usd.py` against silver (the shell prims must match exactly; only emblem geometry and material values may differ; report every difference). Shapes also: print the bounding box and prove every number in section 2B: width at most 6.03, height 4.6 to 5.4, lowest point at Y = -2.455 (within 0.005), top at most 3.015, X centered on 0 (within 0.01), thickness 0.5 to 0.8, and no coin names.
2. **Smoothness**: `measure_smoothness.py` facet mean and edge excess no worse than silver's (stage 0.92 / 61.5, harsh 1.00 / 64.6), unless the owner asked for texture, in which case report the numbers and judge by eye in the app. For a shape, pass its own facets as the emblem file; the ring and inset numbers exist only on coins.
3. **In the app** (the ground truth; Blender renders alone are not enough). Repo: `/Users/antonioperedo/Desktop/screen_time`. Each tier's model lives in its own data set, `ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModel<Tier>.dataset/<file>.usdz` (`Badge3DModelIron.dataset/iron_badge_mobile.usdz`, `Badge3DModelSilver.dataset/silver_badge_mobile.usdz`). A candidate replaces its own tier's file, keeping the filename. A tier with no data set yet shows its flat art on the stage in the app, so it cannot be tested there until the owner adds its data set and one line in the app's model table (`Badge3DModels` in `BadgeHeroCard.swift`). You may temporarily replace ONE file and must always restore it:

   ```sh
   cd /Users/antonioperedo/Desktop/screen_time
   SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
   TIER=iron                           # the candidate's tier, lowercase: iron, silver, ...
   F=ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelIron.dataset/iron_badge_mobile.usdz   # that tier's file
   git status --porcelain -- "$F"      # prints nothing (tracked) or `??` (not committed yet, see below); anything else: STOP and ask the owner
   cp "$F" /tmp/${TIER}_model_backup.usdz
   cp <candidate.usdz> "$F"            # same filename on purpose
   tools/sim/app build
   APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1)
   xcrun simctl install $SIM "$APP"
   # `tools/sim/app launch` drops launch arguments, so launch with simctl, all three times, with the tier argument.
   # The first launch after install always shows the flat fallback badge (shader compile). Launch three times:
   for i in 1 2 3; do xcrun simctl terminate $SIM $BID; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $TIER; sleep 15; done
   tools/sim/shot <your_folder>/app_rest.png
   cp /tmp/${TIER}_model_backup.usdz "$F"   # ALWAYS restore, also after any failure
   ```

   `-BadgeHeroTier <tier>` makes the simulator's Home show that tier (without it the mock shows Steel). Which restore: if `git status --porcelain -- "$F"` printed nothing, the file is tracked and `git checkout -- "$F"` restores it too (then it must print nothing again). A data set the owner has not committed yet (iron, until then) is untracked: `git status --porcelain` prints `??` for it, that is expected, and the backup copy above is the restore (`cmp "$F" /tmp/${TIER}_model_backup.usdz` must say nothing). Never edit any other repo file, never commit, never switch branches. Then measure:
   `/usr/local/bin/python3 badge_realitykit_iron/app_reference/measure_app_shot.py <app_rest.png>`
   - `loaded_3d` no longer proves the coin loaded: when the 3D model fails or is slow, the app now shows the tier's flat art on the same lit stage, and the script reads that flat badge as True too (it measures the same pixels). Prove the coin is showing by looking at the shot (metal rim ring, dark inset, the emblem, the reflection with the same ring in it; a flat fallback is the tier's flat art with a faint, uniform reflection) and by comparing against the tier's previous app screenshot (`app_silver_rest.png` for silver, `reflection_fix/app_fix_c.png` for iron): outside what the candidate changed the pixels must match. If it shows the flat art, relaunch once more and wait 20 s; if it still does, the file is broken.
   - `emblem_clip` at most 796 (silver's).
   - `rim_top` between 130 and 175.
   - Shapes: `measure_app_shot.py` reads fixed coin regions and means nothing on a shape. Use the whole badge white count from section 4, rule 5, and prove the 3D shape is showing by eye (beveled edges catching light, a reflection that matches it; the flat fallback is the tier's flat art). A new shape tier has no previous app screenshot; compare its shine with silver's.
   - Shapes, until the app change in section 10 lands: the app still draws the coin's contact shadow, a dark line about a coin wide on the floor where a coin would touch it. Under a floating shape that line is app code, not the badge's fault: note it in the report and judge everything else.
4. **By eye in the app**, next to silver's app screenshot (`badge_realitykit_iron/app_reference/app_silver_rest.png`): the whole badge, a zoom of the emblem (coins) or the outline all the way round (shapes), and a zoom of the floor (a coin's bottom plus the top of its reflection, or a shape's gap plus the top of its reflection). Check every look rule in section 4, plus the separation line in section 2.5 for coins or the gap in section 2B.10 for shapes.
5. **Write it down**: put each candidate in its own numbered folder with the usdz, the app screenshot, the measurements and 2 to 3 lines on what changed and why. Change one or two things per candidate so you know what helped.

## 8. Delivering

- The final usdz in the tier's `mobile/` folder (keep the previous final in `previous/<name>/`).
- `REPORT.md`: what changed, every check's output, the material table (name, color, metallic, roughness), triangle count and file size vs silver, any rule exception the owner asked for, and anything uncertain.
- A side-by-side of silver and the new badge from the app, plus a floor zoom of both (for a shape: its gap and the top of its reflection).
- End by confirming `git status --porcelain` in the app repo prints nothing from you.

## 9. Past mistakes (do not repeat; the reason matters)

1. **Baked normal maps on shiny metal** (silver, first version): tiny tilts in the bake caught single lights, giving blotchy facets and a mottled ring. Fixed by putting facet shape in geometry.
2. **Dark rim outer edge** (iron v1): the outer edge material was nearly black, so the coin looked outlined and the rim looked thin.
3. **Planes split into tilted triangles** (iron v2): each triangle caught light on its own, and the crystal read as crumpled foil.
4. **A plane mirroring the key light** (iron v3): it rendered pure white and the app's glow put a halo past the crystal's edge (4,934 white pixels vs silver's 796).
5. **Texture at the floor contact** (iron forged revision): a bright, speckled rim bottom ran straight into its bright reflection, so the coin looked pasted onto the reflection. Silver avoids this: its smooth rim bottom stays separated from the reflection by the thin dark contact line.
6. **Judging from Blender only**: Blender's denoised renders hide grain that the app shows (the app draws fine grain about 2.5 times stronger). Always test in the app.
7. **Testing too early**: the first launch after installing a new build shows the flat fallback badge. Wait and relaunch before judging (section 7.3).
8. **Cleaning only the lowest 5% of the rim** (iron contact fix, 2026-10-07): the coin's own bottom edge was smooth, but the reflection mirrors a much taller strip of the rim, so the forged texture still showed crisp at the top of the reflection and the coin still looked overlapped. Judge the reflection's top arc, not only the coin's bottom edge.
9. **Editing textures through the wrong UV set** (2026-10-07): the casing carries two UV sets, `Machining_UV` (the brushed direction) and `USDZ_UV` (what every texture reads). Mapping texture pixels through `Machining_UV` changed the wrong pixels and nothing visible moved. Always use the primvar named by the material's `UsdPrimvarReader` (`varname`), and prove a texture edit lands where intended (paint the edited region a test color once and look in the app).

## 10. Planned (not built yet)

A template kit is planned: a frozen `kit/` (coin shell, shape frame, rules, references), one small recipe file per tier under `tiers/<name>/` (coins: emblem outline and ridge, emblem tones, rim tint; shapes: outline, inner details, tones; both: optional texture settings), one build command (recipe + kit = badge, refusing anything outside these rules) and one check command (every check in section 7, with a pass/fail sheet). Until it exists, follow sections 1 to 9 by hand.

App changes needed before the first shape ships. The owner asks Claude for these in the app repo; a badge agent never makes them:

1. A per-model setting telling the app a badge floats, which turns off the coin's contact shadow for it (and, if the owner wants, puts a soft shadow under the shape instead).
2. The tier's data set (`Badge3DModel<Tier>.dataset`) and its line in the app's model table.
3. Its Badges screen picture (`stills/`), rendered at the coin stills' scale (6.03 units = 108 of the picture's 120 width units) with the shape where it floats, so Home's loading picture lines up with the 3D badge.
