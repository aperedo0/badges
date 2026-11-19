# Report: treasure chest badge reveal

## Version 7 (2026-11-18): side rings that really swing, landing dust

Owner's request: the left side ring looked like real physics but the right one did not, make both
real physics; rework the dust that comes up when the chest lands (the version 5 dust was fine but not
physical, and could look much better), with high quality settling; show only the rings and the dust.

### Rings
- **Cause:** each ring's top bar sat in a rolled cover whose outer ends droop to follow the ring's
  round top. Any swing past about 15 degrees ran the ring into the cover, so the swing simulation had
  a stop at 14 degrees and the rings spent the landing pressed against it. On the right side, where
  the hits throw the ring outward, it read as a ring glued on at an angle.
- **Fix** (`tools/v7_rings.py`, on copies of the two ring and two cover meshes): the cover keeps its
  straight middle with the beaded collars, the drooping ends are trimmed off and closed, and the bore
  is opened to a round hole; the ring's top is eased up at most 0.05 units onto the barrel's axis and
  the pivot moved onto that axis. The covers keep their smoky iron material.
- **Swing:** rebaked with `anim_rings.py` (`RING_OUTER_DEG=170, RING_START_STILL=True,
  RING_PIVOT_UP=0.026, RING_F_END=150`): the rings start still in the world and are moved only by
  gravity and the chest's real motion, with hinge friction. The left ring flips to about 170 degrees
  on the first hit and falls back; the right ring swings out to about 105 degrees; both rock and hang
  still by about frame 75.
- **Verified:** no ring touches its cover, plate or any other part from frame 1 to 99 (contact check
  against 188 objects); ring close ups in Downloads (`Chest rings close up.png`).

### Dust (`chest_reveal_v7_dust.blend`, separate from the core file)
- **First pass (tests 2 to 7, owner rejected as not physical):** dust released on all four sides at
  each impact, weighted toward the hitting end. The owner: when the left side hits the floor, dust must
  come up from that location and follow real dust physics; also wanted a video.
- **Plan:** written, then audited twice by an independent agent (approve with changes both times,
  13 then 6 findings, all applied). Main corrections: the air under the chest is inertial, not a thin
  viscous film (gap Reynolds number about 11,000); use the real landing parameters at high rate; open
  boundary only at the real perimeter; inflow at lifting sides; no dust clumps steered by the same air
  they feed; dust settles at its Stokes speed, not by heavy gas.
- **Built:** `tools/v7_squeeze.py` (air and dust solve, `physics/dust_sources.json`) and the openings
  in `tools/v7_dust.py` (see README Version 7).
- **Checks:**
  * Landing rerun at 2400 per second reproduces all five impacts exactly.
  * Air volume leaving equals the volume lost under the chest at every sub step.
  * Bake source list: only the 46 openings and the grit emitters are enabled.
  * Baked grid, chest frame: 100 percent of the dust on the left from the first hit until the right
    end lands (frame 21); the air at the left end blows outward along the chest's axis in world space.
  * Full size frames 15 to 34 looked at one by one; fixed on the way: dust before touchdown (thin
    layer limited to gaps under 6 cm), box shaped dust (round puff clusters), a crash when initial
    velocity was keyed on and off (kept on, idle openings parked).
- **Physics note for the owner:** the second left landing (frame 32) throws more dust than the first:
  the chest comes down nearly flat and squeezes the whole underside at once.
- **Videos** (Downloads, front camera): `Chest landing physics test 1.mp4` (quick bake),
  `Chest landing physics test 2.mp4` (full detail).

### The flash, proportionality and the ending light together (after test 3)
- Owner: the dust appears like a flash; is it proportional to how hard each side hits; show it with
  the ending light.
- Measured from the baked grid (per side, amount and the height below which 90 and 99 percent of the
  dust sits): the top of the left cloud climbed 2.2 to 3.3 units in one frame and hit the domain top.
- Cause: the openings are parked far above the domain when idle and keyed down to the floor on the
  frame they fire. Blender 5.2 ignored the "new keyframe interpolation" preference for keys added from
  Python, so the keys were smooth: during the frame an opening slid down through the whole domain
  while releasing dust, drawing a column of dust from top to floor in one frame. Fixed by setting
  every key of every opening to constant (`set_interp` in `v7_dust.py`, asserted). After the fix the
  dust starts at the floor (90 percent within 0.14 units on the hit frame) and rises gradually
  (0.24, 0.43, 0.72 units over the next frames, about 1.2 by frame 50).
- Two side findings while chasing it: injected jets (initial velocity on the flow objects) had no
  effect at all (bakes with and without were identical), so they are off and the grid moves the air
  (the chest pushes it out from underneath); finer time steps (40 per frame, CFL 1) changed nothing
  and cost 12 times the bake time, so they are back to 16 and 3. The domain is now 4.6 units tall
  (dust was cut at 3.4).
- Mistake on the way: a test setup changed domain settings while the domain still pointed at the full
  detail cache, which Blender then cleared (test 3's bake). `v7_dust.py` now points the domain at its
  cache folder before any other setting.
- Proportionality: the left side (hardest hit) has more dust than the right at every stage and its
  cloud is higher. The knock scales with impact energy; the squeeze with how much of the underside
  comes down at once.
- Dust strength retuned (shader gain 110) since the false column had inflated the earlier look.
- Ending light in the dust file: `v7_ending.py` runs after `v7_dust.py`; the stage lights stop
  lighting volumes and the beam's haze appears only while the badge rises (frames 132 to 186), so the
  landing dust stays lit and no ghost shaft hangs over the landing. Video: `Chest reveal full with
  dust and light.mp4`.

### Owner adjustments after test 2
- Half the dust, settling 15 percent faster, camera pulled back so the chest is 10 percent smaller on
  screen (checked by projecting the chest body: 0.898 of the old width at frames 40, 120 and 213).
  Dust rebaked at full detail; video `Chest landing physics test 3.mp4`.

### Lock inside
- Owner noticed a rectangle inside the keyhole moving right to left and asked if a real lock works
  like that. It is the bolt: the sideways slide is right, the brightness was not (a closed lock is
  dark inside). Darkened the bolt only (`tools/v7_lock_dark.py`); before and after in Downloads
  (`Chest lock inside before and after.png`). The full detail dust video was rendered just before
  this change, so it still shows the bright bolt.

### Ending pose
- Owner: the badge out of the chest with a light shining down, cinematic; keep where it ended
  before. Built in `chest_reveal_v7_ending.blend` (`tools/v7_ending.py`); camera and badge unchanged.
- Iterations: a room wide haze greyed the whole frame (the studio light lit it) -> haze only inside
  the beam; it veiled the chest -> only above the chest; the badge rim read white -> found the wrong
  (Star Ascent) rim picture shared by name and loaded the coin's own; specks over the open lid ->
  only above the badge, with the particle cache reset.
- Pictures in Downloads: `Chest ending pose.png` (last frame), `Chest ending pose before and after.png`.

## Version 6 (2026-11-18): core animation only (entry, straight on camera, unlock before lid, new badge)

Owner's review of version 5: the chest must start off screen and drop in; a straight on camera with
the closed chest large (85 to 90% of the width) and centred, no camera rotation, then a smooth zoom
out as the lid opens; the latch must visibly unlock before the lid opens, with a pause, and never
intersect the lid; the badge must be the app's 3 Days Total badge; all smoke, glows and light effects
removed for now (they will be developed separately); nothing else redesigned.

### What changed

- New file `chest_reveal_v6.blend` (from version 5; earlier files unchanged). Scripts:
  `tools/v6_setup.py`, `tools/anim_reveal_v6.py`; switches added to `anim_all.py`, `anim_landing.py`.
- Badge: asked the owner first, because the brief named Emerald Sprout as the one to remove while the
  animation used Star Ascent, and the app's 3 Days Total model is Emerald Sprout. Owner chose the app's
  3 Days Total model: `badge/sprout_badge_mobile.usdz`, checked byte for byte against the app's file.
- Entry: frames 1 to 6 have no chest in view (projected: 0% of its points inside the frame); it enters
  from frame 7 (after the second review; first pass: 1 to 3).
- Camera: 0 degrees off frontal, 10 degrees above, 50 mm, fixed orientation; impact shake removed.
  Close framing: the closed chest centred at 88% of the width. Zoom out f84 to f136, eased, translation
  only, to the wide framing (chest 72% of the width, badge and open lid inside a 6% border). A first
  solve gave a framing that only rose (the open chest and badge fit a portrait frame at nearly the same
  size), which would not read as a zoom out, so the wide framing is set to a clear pull back.
- Unlock before lid: the mystery beat (keyhole glow, rattles, lid pressure) is gone; after the landing
  the bolt strains (f44), clicks (f50), the clasp kicks out and hangs, swings up (f60) and seats on its
  mount (f68); pause; lid from f84. The lid is at exactly 0 until f84 (the landing jolt is removed too)
  and the clasp is still while locked.
- Effects off: smoke (domain, emitters, collision modifiers), every glow and inner light, beam, haze,
  overhead light, rays, backdrop, flash, glint, dust, sparkles, compositor glow. Hidden or disabled,
  not deleted. Badge key, rake and rim lights kept at fixed neutral strengths.

### Second review (same day): low camera at the start

- Owner: the opening view should look up at the chest, slightly tilted up, so it feels a little bigger
  than the viewer, still showing the whole chest. Now: 35 mm, camera 0.8 units above the floor, about
  7 degrees up, chest still 88% of the width and centred. The zoom out now also tilts down to the 10
  degree view (needed to see into the chest and frame the badge), eased with the pull back.
- The low camera saw the chest at the top edge on frame 1, so the physics drop starts at the top of
  the fall (frames 1 to 6 empty) and the whole timeline after it moved 6 frames later.
- A full frame range clipping check (the old one skipped frames before 50) found the clasp's small
  strain wiggle before the click touching the slider; the clasp is now still until it is released.

### Verified

- Clipping, every frame 1 to 213 (rings, clasp, lid, badge): none. Earlier: Getting there: with the lid shut the
  clasp tongue grazes the bolt's slider between about 1 and 8 degrees out (measured by turning it in
  steps); the release now passes that range in one frame, and the landing jolts that moved it are off.
- Framing, every frame projected: frames 1 to 6 empty; from frame 31 nothing within 2% of an edge;
  the badge fully inside after the zoom out. Frames 10 to 30: entering, then the tumble overruns the edges
  (entering from the left, then up to about 9% past the right edge around the second impact). Kept
  because the real physics drop with less sideways travel merged the first two impacts into one, and
  the brief asks for a still camera.
- Looked at: half size preview of all frames (landing, latch close ups every second frame, reveal
  every fourth frame) and the full size preview (below).

## Version 5 (2026-11-17): smoke, golden overhead light, slow badge turn and bounce

Owner's brief: straight on camera; lighting like their golden reference image (warm broad light from
above, a much fainter glow inside); smoke that moves like the smoke in their chest opening video
(fills the opening, billows, spills over the edges and falls down the outside, then thins); a slow
elegant badge turn into the front pose with a small controlled settling bounce; keep the landing,
unlock and opening. New file `chest_reveal_v5.blend` (from version 4; older files unchanged).

### What changed

- **Smoke: a real simulation** (`tools/v5_smoke.py`, Mantaflow gas, baked cache `cache_smoke/`,
  1.3 GB, kept out of Git). Studied the video frame by frame: a bright pool filling the opening, a
  soft billow under the lid, then mist pouring over the front edge and sliding down the outside like
  dry ice, gone in about 2 seconds. Four test bakes at low resolution, rendered and compared:
  1. one source inside, light buoyancy: filled the chest, then hung above it as a cloud;
  2. heavy smoke: stayed in the chest as a flat pool (simulated smoke takes up no room, so a full
     chest never overflows by itself);
  3. added sources along the front and side rims that push the mist over the edge: it spilled,
     but thin;
  4. heavier and a stronger front push: fills, billows, pours over the front past the lock, slides
     down the front and sides, spreads on the floor, thins. Chosen.
  Final bake at resolution 80 with noise upres 2 (finer wisps). After the spill, the smoke's density
  is keyed down (from f158 to a fifth by f222) so the floor pool never becomes a blanket. The body,
  inside frame, lid and rim collide with it; the moving lid pushes it. Pale grey white, lit by the
  overhead light and the faint inner glow.
- **Light: matched to the golden reference** (`tools/v5_light.py`). A broad champagne spot high
  above and a little in front of the badge (in front so the badge's shadow does not darken the open
  chest), soft streaked rays fanning down from above the frame, a warm dark backdrop glowing behind
  the badge, slight extra bloom for the badge's warm rim. The chest's old light column and inner
  lights are now a faint secondary glow. New FX property `overhead`: off until the lid swings
  (f114), up to about a third when the lid stops (f135), two thirds as the badge rises, full when
  the badge faces front (f179), then steady.
- **Camera:** 2 degrees off frontal (version 4 was 5), lock centred; same landing framing, slow push
  during the mystery and the gentle push and tilt up for the reveal. No orbit.
- **Badge** (`tools/anim_reveal.py`): rises out of the smoke from f128 (smooth start, no jump),
  turns 200 degrees while rising (fastest about 6 degrees per frame, mid rise) and eases into the front
  at f179; it carries 0.15 units past its rest (f176), dips 0.06 below (f183), corrects 0.015 (f190)
  and is settled at f197; then barely floats to the end (f222). The version 4 scale pulse and big
  sparkle burst are gone; a soft highlight sweeps the face as it arrives; a few sparkles remain.
- **Timing:** landing, mystery, unlock and opening unchanged (impacts at f10.8, f15.7, f26.1; unlock
  f86 to f102; lid f108 to f135, 0.9 s). Smoke from f112, overflow f140 to f175, thinning to f222.
  Badge rise 1.6 s, bounce 0.7 s, hold 0.8 s. Total 222 frames (7.4 s).

### Rig changes in version 5

- New: `Reveal Overhead Light`, `Reveal Overhead Rays`, `Reveal Backdrop` (children of the chest
  root), FX property `overhead`; `Reveal Smoke Domain` (hidden before its cache starts, f105) and the
  emitters `Reveal Smoke Emitter`, `... Front`, `... Left`, `... Right`, with density and push keyed on
  their Fluid modifiers; Fluid collision modifiers on the body and lid envelopes, the inside frames
  and the upper lid rim (render unaffected).
- The overhead light keys sit in the 04 Opening strip (one NLA strip per object and section starts
  at its earliest key, so keys in 05 would have covered the opening).
- Found and fixed on the way: drivers on a newly added property stay invalid until the depsgraph is
  rebuilt (the overhead light first rendered at zero); the smoke domain renders as a grey box before
  its cache starts (seen in the first full preview, frames 2 to 103).

### Verified

- Clipping (world space overlaps, every frame): rings, lid, badge: none. Hasp: the same hidden
  tongue against bolt contact inside the lock case as version 2 (frames 12 to 64).
- Framing: every frame projected into the camera; nothing within 2% of the frame edge.
- Badge motion read back from the scene every few frames (heights and angles above).
- Looked at: the reference video frame by frame; four smoke tests at 7 frames each; the detailed
  smoke at six frames; a full half size preview (all 222 frames, as sheets of the landing, the
  mystery and unlock every second frame, and the reveal every third frame); the hero frame next to
  the golden reference; the final render (below).

### Final render

- `render/chest_reveal_v5.mp4` (also `~/Downloads/chest_reveal_v5.mp4`): 1080 x 1920, 30 fps, 222
  frames, EEVEE 32 samples, motion blur, about 24 minutes on this M2 with no warnings.
  `render/v5_stages_overview.png` and `render/v5_stills/`: impact, unlock, lid swing, smoke billow,
  spill past the lock, bounce peak, bounce dip, hero pose. Frames in `render/v5_frames/` (not in Git).

### Not verified or open

- Motion judged from frame sheets, crops and measured values, not by watching at full speed.
- The rim of the badge reads whiter than in the golden reference (the reference's warm halo is
  stronger); pushing bloom further started to haze everything else.
- A faint line still shows where the floor meets the backdrop (much softer than at first).
- The smoke cache (1.3 GB) is not in Git: on another machine, rebake before rendering (README).

## Version 4 (2026-11-17): inside framing, smoother front board joints

Owner: the inside should show the structure that reinforces a real chest, and the hinges from the
inside (a game screenshot as inspiration, not a copy); and the front planks around the keyhole,
started by another chat, should look smooth and natural.
- Added: corner posts and bottom and top rails in the body; a rail and two thick arched ribs at both
  ends of the lid (`tools/build_inside_frame.py`). New objects only; no existing geometry changed.
- Owner review of the first pass: lid ribs (then under the iron straps) should be thicker and at the
  ends; the inside iron hinge plates with bolts and the wall battens under them had to go. Done.
- Then: the ribs should not be smooth curves but straight pieces, the way wood is really cut. Each
  rib is now five straight pieces with flat faces and its back trimmed to the lid's curve. The five
  front faces are equal in length (0.85 to 0.87 units each), as in the owner's inspiration.
- Front joints: the earlier version read as soft dark bands, with a pale painted looking stripe under
  the top joint and a smudged middle joint. Now a thin crack, a rounded eased edge and soft contact
  shading (`tools/front_plank_seams.py`).
- Checked: full size renders of frames 70 and 220 against version 3, and no overlaps between the new
  parts and the lid, body, hinges or badge in every third frame. New file `chest_reveal_v4.blend`.
- Not done: video (owner asked for stills).


## Version 3 (2026-11-17): real wood inside

Owner: the wooden texture should also be inside the chest, so it looks made from real wood.
- Cause: the inside used one plank picture projected over the whole chest, so the floor and lid
  underside showed one board stretched into flat streaks; and the glow card inside the chest was
  opaque, so the floor and lower walls were never visible behind it.
- Fix: boards with seams on every inside surface (`tools/build_inside_wood.py`), and the glow card
  became an added glow that is full while shut and fades to 4% as the lid opens. Lights, timing,
  rig and all outside materials unchanged. New file `chest_reveal_v3.blend`; version 2 kept.
- Checked: frames 89, 98, 112, 124, 130 and 220 rendered at full size against the version 2 stills;
  the lid seam glow before opening matches; inside boards read on the lid underside and walls.
- Tried and rejected: halving the inside light (no visible gain, the card was the cause); the card
  at 35% and 12% (still a pale veil over the lower wood).


## Version 2 (2026-11-17): real physics, mechanical unlock, head on camera

Owner's feedback on version 1: the first thud lingered on its corner before tipping, which did not
look like real physics; the physics should be basically real. A reviewer's list (landing, unlock,
lid, light, climax, framing, timing) and then a head on camera requirement were implemented on top.
New file `chest_reveal_v2.blend`; version 1 (`chest_reveal.blend`) is unchanged.

### What changed

- **Landing: real rigid body physics.** `tools/rigid2d.py` (Newton impacts, restitution 0.2,
  Coulomb friction 0.6, real gravity for a 0.7 m chest, the chest's own footprint and centre of mass).
  The corner hit now turns into rotation immediately, as it physically must; no hand timing.
  Chosen from a sweep of drop tilt, tumble, drift and restitution for three distinct, decreasing
  thuds without toppling: corner (speed 43.5), far side (18.7, 5 frames later), rock back (13.0,
  10 frames later), tap (2.5). Settled at f28.5. It tumbles about 44 degrees in the air and rocks up to
  14 degrees on the far edge, which reads as a clear silhouette from the front.
- Rejected on the way: Blender's rigid body solver (a flat drop with restitution 0.5 did not bounce
  at all, so it cannot model these impacts here) and restitution 0.25 to 0.5 in my solver (the chest
  flipped over every time; a heavy wooden chest landing on a corner keeps far less energy).
- **Rings:** pendulum driven by the physics, hinge moved to the clip free point found by a pivot
  search. The hardware allows only 0 to about 14 degrees (mount plate inward, cover lip outward), so the
  rings flip out, clack and settle rather than swing widely. A wider swing needs the covers reshaped.
- **Dust:** emitted from the two boots that actually touch on each impact (only the boots reach the
  floor), flattened, spreading outward along the floor, scaled by impact speed (28, 12, 8 puffs).
- **Unlock:** keyhole flares, the bolt clicks back, the clasp kicks clear (to 26 degrees, a dark gap
  opens) and hangs a beat, swings up and over and lands on its own mount at 124 degrees with a bounce,
  then a pause while the seam light swells. Rattles before it stay within the bolt's play.
- **Lid:** 27 frames: creeping start (resistance), swing peaking about 9 degrees per frame, natural
  deceleration, gentle stop at 108 degrees, tiny settle.
- **Light:** the column is two soft layers with drifting streaks and a slow irregular flicker,
  strongest at the chest and fading upward, growing with the opening; a thin haze is lit only by the
  light leaving the chest (round soft footprint). Interior glow and its lights lowered; bloom threshold
  raised. A first haze version showed its box as a lit rectangle; fixed with a round falloff and a
  narrower spill light.
- **Badge climax:** rises and turns, slowing into the front facing pose at f172; a thin light sweeps a
  highlight across its face, flash, a ring of sparkles, a small scale pulse, then it settles and floats.
  20% larger; dedicated key, raking and rim lights (light linked to the badge) so the relief reads.
- **Camera:** head on (5 degrees off frontal, 15 degrees above, 50 mm), chosen from four rendered
  candidates (`previews/camcmp/grid.png`). Wide for the landing, slow push toward the lock during the
  mystery, gentle push and tilt up for the reveal. Landing jolt on the first impact only.
- **Other:** a dark wood board under the chest (its pale flat bottom showed while falling), timeline
  starts with the chest entering at frame 2, total 228 frames (7.6 s).

### Rig changes in version 2

- Ring pivots moved to the clip free point (0.36 below the seam) with measured limits.
- New: `Reveal Badge Glint` (sweeping light, child of the badge), `Reveal Badge Rake` and
  `Reveal Badge Rim` lights, `Reveal Light Beam Outer`, `Reveal Light Haze`, `Reveal Underside`,
  FX property `glint`, stored camera framings on the dolly.
- The landing now lives on `Reveal Chest Drop` (baked physics); Rock and Shake stay at zero there.

### Verified

- Physics solver: a flat drop with restitution 0.5 rebounds exactly a quarter of the drop height.
- The boot corner never goes below the floor (the physics resolves contacts; baked at 4 samples per frame).
- Clipping (world space overlaps, every moving frame): rings, lid, badge: none. Hasp: the tongue
  touches the bolt during the landing rattles and while pressure lifts the lid (frames 12 to 64); both
  parts are inside the lock case behind the glowing keyhole card, so it is not visible. The model has
  no play there.
- Framing: every frame projected into the camera; nothing comes within 2% of the frame edge.
- Looked at: contact sheets of every frame of three half resolution previews, crops of the lock
  through the unlock, full resolution key frames, and the final render.

### Final render

- `render/chest_reveal_v2.mp4` (also in ~/Downloads): 1080 x 1920, 30 fps, 228 frames, EEVEE 32
  samples, motion blur. `render/landing_v1_vs_v2.mp4`: old landing (left) and new (right).
  `render/v2_stages_overview.png` and `render/v2_stills/`: key moments. Frames in `render/v2_frames/`
  (kept out of Git).
- The first final pass logged EEVEE "shadow buffer full" warnings on frames 167 to 186 (the climax,
  when all badge lights are on). The badge-only lights no longer cast shadows; those frames were
  rendered again with no warnings and swapped in. Before and after looked nearly identical.

### Not verified or open

- Motion judged from frame sheets, crops and numbers, not by watching playback at full speed.
- Ring swing is small because of the hardware (see above).
- Real physics makes the first two impacts 5 frames apart (corner then far side); the rhythm is
  BOOM BOOM .. boom rather than evenly spaced. Faking a longer gap is what looked wrong in version 1.
- The landing framing is wider than the rest because the real tip over the corner travels about 1.5
  units sideways; the camera then pushes in.

## Version 1 (2026-11-17)

Authored landing shaped like rocking physics but slowed, three quarter camera, first rig, effects and
report. Kept in `chest_reveal.blend` and `render/chest_reveal_v1.mp4`. Main issues found later: the
chest paused on its corner after the first hit, the clasp release read poorly, the light column was
uniform, the interior washed out, the badge climax was weak.

## Shared notes

- Source chest: `claude_attempt_20261117/chest_simple.blend`. Its rig did not exist (the partial
  rig was on the older chest in another scene); the reveal rig was built on object copies that share
  the original meshes and materials, matching every copied part's position exactly at rest.
- Placeholder badge: the app's Star Ascent coin (copy). EEVEE, not Cycles (hours per pass on this Mac).
