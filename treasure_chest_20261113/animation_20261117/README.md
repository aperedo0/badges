# Treasure chest badge reveal animation

**Newest: `chest_reveal_v11_torches.blend`** (2026-11-19, version 10 plus torches, see Version 11). **Before that: `chest_reveal_v10_temple_polish.blend`** (the temple's end look polished for iPhone screens, see Version 10; `chest_reveal_v9_temple.blend` is the version before, see Version 9). **Core: `chest_reveal_v7.blend`** (2026-11-18; landing dust in `chest_reveal_v7_dust.blend`, ending light in `chest_reveal_v7_ending.blend`, see Version 7). Version 6: `chest_reveal_v6.blend`, scene **Chest Reveal**: 30 fps, frames 1 to 213
(7.1 s), 1080 x 1920 portrait, EEVEE. Version 6 is the owner's core animation pass (see Version 6
below): the chest drops in from off screen into a large straight on view, the clasp unlocks before
the lid opens, the camera pulls back, and the app's 3 Days Total badge rises. No smoke or special
lighting (to be developed separately). Version 5 (smoke, golden light) and the earlier files are kept
unchanged. All are copies of `claude_attempt_20261117/chest_simple.blend`; that file and the other
scenes in these copies are unchanged. The chest in the scene is a set of object copies that share the
original mesh data, so no chest geometry was edited (version 3 changes inside materials; version 4
adds new framing objects and changes the three front plank materials).

## Watch it

Cleanup on 2026-11-18 (owner): frame sequences, previews, stills and comparison pictures, Blender
backups, versions 1 to 4 and the version 5 smoke cache were removed (receipts in
`cleanup_runs/chest_animation_20261118/` at the repository root). Versions 1 to 4 and the older stills
are in Git history; the smoke rebakes with `tools/v5_bake_smoke.py`. The videos below remain. Paths
below that no longer exist are kept as a record of what each version produced.

- `render/chest_reveal_v6_preview.mp4`: version 6 preview (full size). `render/v6_stills/`: key moments.
- `render/chest_reveal_v5.mp4`: version 5 (smoke, golden light, new badge rise). `render/v5_stills/`: key moments.
- `render/v4_stills/` and `render/inside_frame_before_after.png`: version 4 stills (inside framing), no video yet.
- `render/v3_stills/0220.png` and `render/inside_wood_before_after.png`: version 3 still (wood inside).
- `render/chest_reveal_v2.mp4`: final render of version 2 (full resolution, motion blur).
- `render/landing_v1_vs_v2.mp4`: the old and new landing side by side.
- `render/v2_stills/` and `render/v2_stages_overview.png`: key moments.
- `render/chest_reveal_v1.mp4`: version 1 for comparison.
- In Blender: open the file, scene **Chest Reveal**, press play. Timeline markers name every beat.

## Version 2 in short

- **Landing is real physics.** `tools/rigid2d.py` drops a rigid box with the chest's real footprint,
  height and centre of mass under real gravity (the chest taken as 0.7 m wide), resolving every floor
  contact with Newton's impact law (restitution 0.2) and Coulomb friction (0.6). Dropped tilted 20
  degrees with a gentle tumble and slight drift it gives: corner hit (f10.8), far side slam (f15.7),
  rock back (f26.1), tap (f28.1), settled f28.5. The result is baked onto `Reveal Chest Drop` at 4
  samples per frame with straight segments. Blender's own rigid body solver was tested first and did
  not apply restitution at all in this setup (a flat drop with restitution 0.5 did not bounce), so it
  was not used.
- **Rings** are a physical pendulum driven by that motion, limited by the real hardware: the mount
  plate stops them swinging toward the wall and the rolled cover's lip stops them at about 14 degrees
  outward (measured clip free to 16).
- **Unlock is mechanical:** keyhole flares, the bolt clicks back, the freed clasp kicks clear of the
  lock face and hangs open for a beat, then swings up and over and lands against its own mount
  (measured free to 128 degrees).
- **Lid**: heavy slow start, decisive swing (peak about 9 degrees per frame), natural deceleration,
  gentle stop at 108 degrees.
- **Light**: two layer soft light column with drifting streaks and flicker, a thin haze lit only by
  the light leaving the chest, interior glow toned down so the wood stays visible.
- **Badge climax** at f172: it slows into the front facing pose, a glint sweeps its face, a flash and
  a ring of sparkles, then it settles and floats. Badge 20% larger (model scale 0.68).
- **Camera** (owner's head on request): 5 degrees off frontal, 15 degrees above, 50 mm. Wide for the
  landing (the real tip over the corner travels across the frame), slow push toward the lock during
  the mystery, gentle push and tilt up to the hero framing during the reveal.

## Version 7 (side rings that really swing, landing dust)

- **`chest_reveal_v7.blend`**: version 6 with free swinging side rings. Before, each ring's top bar
  sat in a rolled cover whose ends droop to follow the ring, so the ring hit the cover after about
  15 degrees and the simulated ring spent the landing pressed against that stop (the right ring
  looked glued on at an angle). `tools/v7_rings.py` (on copies of the two ring and cover meshes)
  trims the cover to its straight middle with the beaded collars, closes the cut ends, opens the bore,
  eases the ring's top up at most 0.05 units onto the barrel's axis and moves the pivot onto that
  axis. A ring now turns 0 to 170 degrees without touching anything. The swing is then rebaked with
  `anim_rings.py` and `RING_OUTER_DEG=170, RING_START_STILL=True, RING_PIVOT_UP=0.026, RING_F_END=150`
  in its globals: the ring starts still in the world (the toss spun the chest, not the loose ring)
  and is driven only by gravity and the chest's real motion.
- **`chest_reveal_v7_dust.blend`**: version 7 plus the landing dust, kept separate from the core
  file. The dust follows the physics of the landing (plan, audited twice by an independent agent:
  `badges/plans/chest_dust_physics_20261118.md`, not in Git):
  1. `tools/v7_squeeze.py` (Blender's Python, numpy) reruns the landing at 2400 samples per second,
     follows the gap under the chest and solves where the trapped air leaves (inviscid depth averaged
     mass balance, only where the gap is under 0.5 units; deeper gaps are left to the gas grid). Air
     leaves only where the gap is closing; a lifting side draws air in. Floor dust lifts where that
     air (and its wall jet along the floor) is faster than about 2 m/s and is used up; the boots that
     hit throw out the dust under them by the impact's energy. Writes `physics/dust_sources.json`
     (per opening and frame: dust, jet speed) and checks that the air leaving equals the volume lost.
  2. `tools/v7_dust.py` builds the Mantaflow gas: a low poly stand in of the chest pushes the air;
     46 openings around the chest's base (each a loose cluster of small round puffs on the floor under
     its gap, moving with the chest) release the solved dust and jets, at most 80 units/s; idle ones
     are parked above the domain (switching initial velocity during a bake crashes Blender 5.2).
     Dusty air is only slightly heavy; it settles at 25 micrometre dust speed (0.37 units/s) through a
     falling fade in the dust shader. Grit flies only from the boots that hit, under real gravity,
     carried by the simulated air, and comes to rest on the floor.
  Result: on the first hit all the dust comes from the left end (measured from the baked grid); the
  right side gives none until the right end lands.
- **Rebuild:** run `tools/v7_squeeze.py`, open `chest_reveal_v7_dust.blend` (or a copy of
  `chest_reveal_v7.blend`), run `tools/v7_dust.py` inside Blender (globals `DUST_RES`, `DUST_NOISE`,
  `DUST_CACHE`, `DUST_END` for test bakes), save, then bake in background:
  `blender -b chest_reveal_v7_dust.blend --python tools/v7_bake_dust.py`. The bake script refuses to
  run if any source other than the openings and the grit is switched on, and frees old particle bakes
  first (a baked particle cache ignores changed settings). The cache folder (`cache_dust/`) is not in
  Git; rebake it after a checkout (about 1.5 hours at full detail).

- **Camera pulled back** (`tools/v7_camera_pullback.py`, core, dust and ending files): the chest is
  10 percent smaller on screen in every frame (measured 0.898 of the old width at frames 40, 120 and
  213). The camera moves back along its own view by a ninth of its distance to the chest, keyed every
  other frame because the dolly's own move changes that distance.
- **Dust release fix**: idle openings are parked above the domain and keyed down on the frame they
  fire; every key is constant (Blender 5.2 ignored the interpolation preference from Python, so they
  slid through the domain and drew a column of dust, the flash). No injected jets (they had no effect);
  the grid moves the air. Domain 4.6 units tall. `chest_reveal_v7_dust.blend` also carries the ending
  light (`v7_ending.py` after `v7_dust.py`): the full animation with dust and light renders from it.
- **Dust amount and settling** (owner, same day): half the dust (shader gain 110 to 55) and settling
  15 percent faster (the falling top at 0.43 units/s instead of 0.37, about 27 micrometre dust;
  dissolve 130 frames instead of 150).
- **Lock inside** (`tools/v7_lock_dark.py`, in the core, dust and ending files): the bolt seen through
  the keyhole (R Lab Chest Key Driven Slider) slides right to left as it unlocks, like a real chest
  lock, but it was lit like the brass outside and read as a glowing rectangle. It now has a dark
  version of the aged bronze (object level, the shared mesh is unchanged), so the keyhole is a
  shadowy hole with the bolt's edge just catching light.
- **`chest_reveal_v7_ending.blend`**: the ending pose (badge risen over the open chest), lighting
  only, camera and badge animation unchanged (`tools/v7_ending.py`, safe to run again): one warm spot
  high above the badge whose beam shows in a haze that exists only inside the beam and above the
  chest; the studio lights and surroundings dim; a stronger warm back light on the badge; a few slow
  specks drifting in the beam above the badge. Fades in from frame 132 to 186. Also fixes the badge's
  rim: the app's 3 Days Total coin and the earlier Star Ascent coin name their rim pictures the same,
  so Blender had reused Star Ascent's silver picture (the rim read white); the coin's own champagne
  pictures are loaded from `badge/sprout_badge_mobile.usdz`, and the ring gets the brushed
  (anisotropic) reflection the app adds at runtime.

## Version 6 (core animation, no effects)

- **Entry:** frames 1 to 6 are empty (the physics drop now starts at the top of the fall); the chest
  drops in from above the frame, tips and settles centred by frame 35. It is about 88% of the frame
  width (side rings included), so its tumble pokes past the right edge by up to about 9% around the
  second impact (frames 22 to 30).
- **Camera:** straight on (0 degrees off frontal), 35 mm, no shake. Opening shot low and looking up
  (camera 0.8 units above the floor, tilted up about 7 degrees), so the chest looms a little; still
  until the lid starts (f90), then it rises and pulls back while tilting down to 10 degrees above
  (f142), eased at both ends; the chest ends at about 72% of the width with the badge fully in frame.
  Framings solved from the real geometry by `tools/v6_setup.py` (stored on the dolly).
- **Unlock, then lid:** hold after landing; the bolt creeps (f50) and clicks back (f56); the clasp
  kicks clear and hangs, swings up and over (f66) and lands on its mount (f74); pause; the lid opens
  from f90 (heavy start, stop f117). The lid stays fully shut until then (no pressure lift, no jolt
  on landing) and the clasp is still while locked.
- **Badge:** the app's 3 Days Total model (`badge/sprout_badge_mobile.usdz`, an exact copy of the app's
  `Badge3DModelEmeraldSprout` file) replaces Star Ascent (kept in the excluded collection
  `Reveal Badge Star Ascent (off)`). Rises from f116, turns into the front at f167, small bounce,
  settled f185, hold to f213 (7.1 s).
- **Off:** smoke, every glow, beam, haze, the overhead light, rays and backdrop, flash, glint, dust,
  sparkles and the compositor glow (hidden or disabled, nothing deleted). Ordinary studio lights and
  the badge's plain key, rake and rim lights only. The mystery beat (keyhole glow and rattles) is out.

## Version 5 (smoke, golden light, badge bounce)

- **Smoke** (`tools/v5_smoke.py`, baked with Mantaflow into `cache_smoke/`, not in Git): a gas
  simulation in a box around the chest (open sides, closed floor). Heavy smoke (negative density
  buoyancy) so it settles and falls instead of floating up. Four sources keyed with the lid: a core
  that billows up through the opening as the lid swings, and thin sources along the front and side
  rims that push the mist over the edge, where its weight carries it down the outside (simulated
  smoke takes up no room, so a filling chest never overflows by itself). A drifting cloud texture
  makes the emission uneven; the body, the inside frame, the lid and the rim collide with it, so the
  moving lid pushes it. Resolution 80 with noise upres 2. It dissolves over about 2 seconds.
  Rebake: run `v5_smoke.py`, then `blender -b chest_reveal_v5.blend --python tools/v5_bake_smoke.py`
  (or Bake All on the domain), then save.
- **Light** (`tools/v5_light.py`): a broad champagne spot high above and a little in front of the
  badge (`Reveal Overhead Light`, lights the badge, the open chest, the haze and the smoke), soft
  streaked rays fanning down from above the frame (`Reveal Overhead Rays`, a card behind the chest),
  a warm dark backdrop that glows behind the badge (`Reveal Backdrop`). The chest's own light column
  and interior lights are cut to a faint secondary glow. New FX property `overhead` drives all of it
  and the badge's key, rake and rim lights (now warm).
- **Camera**: 2 degrees off frontal (was 5) so the lock is centred; same push in and tilt up.
- **Badge**: rises out of the smoke from f128, turns a little over half a turn while rising and eases
  into the front at f179; carries 0.15 past its rest (f176), dips 0.06 below (f183), corrects 0.015
  (f190), settled at f197, then barely floats. No scale pulse; a soft highlight sweeps its face as it
  arrives; the sparkle burst is down to a few.

## Inside wood (version 3)

`tools/build_inside_wood.py` (run inside Blender, safe to repeat). The inside walls, floor, rim tops,
lid underside and lid end caps had one plank picture stretched over them (flat orange streaks). Now
they are separate boards cut from the outside front's own plank pictures at the outside's scale:
along the length on the long walls, floor and lid, along the depth on the end walls, following the
lid's arch, each board with its own picture, strip, direction and tone, dark seams, rounded edges and
contact shading in the corners. Materials `Simple wood inside body` and `Simple wood inside lid`.
The glow card inside the chest (`Reveal Magic Core`) used to be opaque and hid the floor and lower
walls; it is now an added glow driven by `seam_glow`: full while the lid is shut (the seam glow looks
as before), fading to 4% (`CORE_SEE_THROUGH`) as the lid opens, so the wood shows. Lights unchanged.

## Inside framing (version 4)

`tools/build_inside_frame.py` (run inside Blender, safe to repeat, reuses objects by name, deletes
nothing). Inspired by real chest construction (owner's game screenshot as inspiration, not a copy).
Body, parented to `Reveal Chest Shake`: `Inside Body Frame` (square posts in the four inside corners,
a bottom and a top rail). Lid, parented to `Reveal Lid Hinge`: `Inside Lid Frame` (rail around the
lid's lower edge and two thick ribs at both ends of the lid, against the end caps, `RIB_W`,
`RIB_D`). Each rib is five straight pieces of equal visible length (`RIB_PIECES`, joints placed by
`equal_joints`; owner: shaped the way a person would cut wood, not a smooth curve): flat front faces,
backs trimmed to the lid's curve.
`render/v4_stills/lid_end_rib_inside_view.png` shows one from inside the lid. The owner had the inside hinge plates, bolts and wall battens removed; the script unlinks
any earlier ones (`REMOVED`). Positions come from ray casts
on the inside surfaces. Wood parts use `Simple wood inside frame` (outside plank picture, grain along
each part, a touch darker than the boards, rounded edges by a bevel modifier). Checked: no new part overlaps the lid, body, hinges or
badge in any third frame of the animation.

## Front board joints (version 4)

`tools/front_plank_seams.py` (first written by another chat, refined here): each of the three front
plank materials gets a thin dark crack at its top and bottom joint, a quarter round eased edge in the
displacement, and soft contact shading beside the joint. Settings at the top (`GAP`, `ROUND`,
`GROOVE`, `DARK`, `CONTACT`).

## Sections (NLA tracks, one strip per controller per section)

| Track | Frames | What happens |
|---|---|---|
| 00 Rest | 1 | Starting value of every channel, held underneath everything |
| 01 Landing | 1 to 45 | Physics fall and landing, rings, dust from the touching boots, lid and hasp rattle, camera jolt |
| 02 Mystery | 32 to 86 | Camera push, keyhole glow and pulses, small rattles within the bolt's play, lid pressure and seam line |
| 03 Unlock | 82 to 108 | Flare, bolt click, clasp kicks free, swings up and over, lands on its mount, pause |
| 04 Opening | 108 to 222 | Lid opening, faint inner glow, overhead light coming up (keys to the end), sparkle stream |
| 05 Badge Reveal | 82 to 222 | Camera to hero framing, badge rise and turn, front at f179, bounce settled f197, hold |
| (smoke) | 104 to 222 | Baked simulation; its sources are keyed on the emitter objects (`Reveal Smoke Emitter*`) |

Each strip holds its last value forward and every section continues from the previous one, so a
section can later be triggered on its own (for the app's swipe: play 01 and 02, wait, play 03 to 05).

## Rig (collection Reveal Rig)

Chest frame: x = width (+x is the far right end), y = depth (front is -y), z up, origin on the floor
under the chest centre. Everything is an empty; mesh parts are parented, never deformed.

- `Reveal Chest Root`: placement and the chest's 32 degree yaw. Static.
- `Reveal Chest Drop`: the baked physics landing (location x, z and rotation y), plus yaw.
- `Reveal Chest Rock` > drives `Reveal Chest Tilt`: an optional hand tilt control whose drivers keep
  the touching boot corner pinned to the floor. Zero in version 2 (the physics owns the landing).
- `Reveal Chest Shake`: small shocks (zero in the landing). Parent of every body part.
- `Reveal Lid Hinge` (rotation x, negative opens), `Reveal Hasp Pivot` (child of the lid, negative
  swings out), `Reveal Lock Bolt` (location x, negative retracts), `Reveal Ring Pivot L/R`.
- `Reveal Badge Root` > `Reveal Badge Model` (badge import, Y up to Z up, scale 0.68).
- `Reveal FX Controls`: `keyhole_glow`, `seam_glow`, `interior_glow`, `beam`, `flash`, `glint`,
  `overhead` drive every glow and FX light (gains at the top of `tools/build_fx.py` and
  `tools/v5_light.py`).
- Smoke: `Reveal Smoke Domain` (settings and look) and the emitters `Reveal Smoke Emitter`, `... Front`,
  `... Left`, `... Right` (children of the chest root; density and push keyed on their Fluid modifier).
- `Reveal Camera Dolly` > `Reveal Camera Shake` > `Reveal Camera`; the three framings are stored on
  the dolly and set in `tools/build_stage.py` (`CAM_REST`, `CAM_MID`, `CAM_HERO`).

All drivers are simple expressions, so they work with Python auto run off.

## Replace the badge

The placeholder is the app's Star Ascent coin (`badge/star_ascent_badge_mobile.usdz`, a copy). Delete
the meshes under `Reveal Badge Model`, import the new model into collection Reveal Badge and parent
it to `Reveal Badge Model`, which turns a USD Y up badge to Blender's Z up and scales it.

## Rebuild from scripts

```sh
python3 tools/rigid2d.py physics/landing.json w0=1.5 vx0=-3 roll=20 e=0.2 mu=0.6 drop=11 seconds=2.0
```
then inside Blender, in this order:
```python
T = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools/"
for s in ("build_scene.py", "build_stage.py", "build_fx.py", "v5_light.py", "anim_all.py",
          "build_inside_wood.py", "front_plank_seams.py", "build_inside_frame.py", "v5_smoke.py"):
    exec(open(T + s).read())
exec(open(T + "check_clipping.py").read())   # result in CLIP
exec(open(T + "check_framing.py").read())    # result in FRAMING
```
then bake the smoke (see Version 5) and save. Version 6 (from version 5's file) instead runs
`v6_setup.py` and then `anim_all.py` with
`REVEAL="anim_reveal_v6.py", CAM_SHAKE=0, FX_PARTICLES=False, HASP_RATTLE=0, LID_RATTLE=0, LANDING_T0=0`
in its globals. All are safe to run again and never delete objects. Timing: `T` dict at the top of
`anim_reveal.py`. Ring physics: top of `anim_rings.py`. Dust and sparkles: top of `anim_fx.py`.
`tools/camera_compare.py` renders camera candidates side by side.

Render: `blender -b chest_reveal_v5.blend --python tools/render_anim.py -- OUTDIR pct=100 samples=32 blur=1`
(version 2 took about 15 s per frame on this M2; the smoke makes version 5 slower).

## Version 8 mist and beam specks (2026-11-19)

The owner turned down the version 7 opening fog (a thick cloud sitting on the rim) and its specks
(too many, clumped, showing outside the beam). `chest_reveal_v8_mist.blend` (a copy of
`chest_reveal_v7_dust.blend`) replaces both; the version 7 files and the `cache_opening` folder are untouched.

- `tools/v8_mist.py`: thin, see through mist that only the cool light inside the chest shows. It fills the
  shut chest, is dragged up by the swinging lid, lifts by its warmth and thins out. No glow of its own. Cache: `cache_smoke_mist` (ignored by Git).
- `tools/v8_motes.py`: about 100 specks laid out evenly as the resting camera sees them, each at its own
  depth in the beam, none in front of the badge. They only add light, and how much follows the beam: its
  fade in over time, its cone edge and its lower fade. No bake. The version 7 speck particles stay in the
  file, switched off.
- `tools/v8_bake.py` bakes the mist in background Blender (MIST_RES, MIST_NOISE); `tools/v8_render.py`
  renders frames from the front camera (FRAMES, OUT, PCT, SAMPLES, optional MIST_GAIN, MOTE_GAIN).
- The light inside the chest is two lights (owner saw sparkle inside the lid and bright dashes on the
  front): one light on the chest floor skimmed the lid at a shallow angle, so the wood grain's bumps
  sparkled, and it leaked through the plank seams. Now `Reveal Opening Light` lights the mist only,
  `Reveal Opening Glow` (a soft point light, no mirror glints, low and toward the front so it meets the
  open lid squarely) lights the wood and the badge, and `Reveal Opening Light Blocker` (shadow only, inside
  the walls) stops leaks. Both lights are at full strength before the lid moves and fade once it is open
  (owner: "it starts bright and then fades, does not start low then grow").
- Specks a tenth of their size (owner: "a tenth of their size ... much, much smaller"): their true radius
  is far below a pixel, so `v8_motes.py` draws each one pixel wide and dims it by how much smaller than a
  pixel it really is; `v8_render.py` tells them the pixel size for the render size. Judge them at full
  size (`~/Downloads/Chest last frame tiny specks.png`, 1080 by 1920): at smaller sizes a pixel is bigger.
- Third look (`~/Downloads/Chest opening mist test 3.mp4`, res 64, 60 percent size): real physics only.
  The owner asked whether a real chest would push smoke up; it would not, so the upward push on the source
  and the source that kept feeding smoke after the opening are gone. One fill of slightly warm smoke, made
  while the lid is shut, moved by the lid, its warmth and the badge. Specks shrunk to about one pixel
  (owner: "HUGE"). No slow motion copies.
- Second look: thicker mist (res 80, `~/Downloads/Chest opening mist test 2.mp4`).
- First look for the owner: res 72, no detail pass, half size, 24 samples
  (`~/Downloads/Chest opening mist test 1.mp4`). Run `v8_mist.py` only before a new bake: it changes the
  simulation settings, which outdates the cache.

## Version 9 temple background (2026-11-19)

The owner's mockup (`~/Downloads/Ancient stone temple with emerald badge.png`) put the chest in an old stone
temple; only the background was to be built (its green floor light left out on purpose). `chest_reveal_v9_temple.blend`
is a copy of `chest_reveal_v8_mist.blend` with collection **Reveal Temple** added; the chest, badge, mist, specks,
beam and their lights are unchanged, and the temple's own lights reach only the temple (light linking).
Render: `~/Downloads/Chest temple background.png` (frame 213, full size) and `... vs mockup.png`.

- Built in the chest's frame (`Temple Root` copies `Reveal Chest Root`), positions solved through the resting
  camera so pillars, arch and floor land where the mockup has them: front pillars about 58 units behind the
  chest, the apse arch about 87. Natural perspective is kept (the camera is unchanged).
- `tools/v9_temple_geo.py`: platform (dais) whose top is exactly the old floor, so the chest still lands on it
  (every landing contact checked inside it); one worn top stone with a chipped edge, two gold inlay rings, six
  base blocks; slightly oval (4.45 by 3.6) so its front sits where the mockup has it. Flagstones with real gaps,
  chipped corners and tiny tilts, growing with distance so the far floor reads as large flags. Round pillars
  with square chamfered plinths and capitals and a rounded base ring; smaller engaged pillars carry the low
  elliptical apse arch (one continuous band); arcades, vault, dark side aisles, rounded apse. Crack decals
  where the mockup has them. The old `Reveal Floor` is hidden, not deleted.
- `tools/v9_temple_mat.py`: three CC0 Poly Haven scans for relief (`temple/resources/SOURCES.json`, cache not in
  Git): weathered grey olive stone with pale flaked patches and moss low down and on ledges; dark damp flags
  with patchy moss in the joints; warm worn stone for the dais.
- `tools/v9_temple_light.py`: warm light from high over the hall, rakes on the front pillars' inner faces, warm
  pools on the floor, a soft glow in the apse, a warm key and a front fill on the dais only. The owner said
  the streaks first cast in the apse looked like a curtain ("just get rid of that"): that light is off and
  the apse wall is one smooth surface. Shadow pool raised to 1024 MB (full size renders overflowed 512).
- `tools/v9_temple_fog.py`: soft wisps hugging the far pillar bases (cards: beyond EEVEE's volume range) and a
  thin ground mist volume beside the dais. The near mist follows the beam light's energy, so it comes up with
  the light from above (frames 132 to 186) and never mixes with the landing dust.
- Run order inside Blender: geo, mat, light, fog (each safe to run again, nothing deleted). Test renders use
  `tools/v8_render.py`; `temple/tools/side_by_side.py` and `regions.py` compare with the mockup.
- Two independent reviews (57, then 62 of 100) drove the second pass: round pillars, larger flags, darker
  sides, one piece dais top, no joint lines on the arches, mist in place of near fog cards.
- Left as is: the beam's brightness (the mockup's rays are brighter and more golden), the pillars' slight
  lean from the camera's 10 degree downward tilt, and the white landing grit on the dais (both part of the
  existing scene).

## Version 10 temple polish: the look at the very end (2026-11-19)

Owner after version 9: the scene "looks ok", make it "more epic, more cinematic", and for now only the look at
the very end (the whole animation's light comes later). The movie will ship without the badge (the phone draws
the badge on top), but the badge stays in every render as a guide until the very end.
`chest_reveal_v10_temple_polish.blend` is a copy of version 9; version 9 and its scripts are untouched.
Pictures: `~/Downloads/Chest temple epic options.png` (before, A, B), `Chest temple epic A.png`, `... B.png`,
`Chest temple on phone shapes.png`.

- `tools/v10_frame.py`: picture 1080 by 2340 (9 by 19.5, every current iPhone; an older 9 by 16 phone crops top
  and bottom). Lens 35 to 28.72 mm so the view's width is unchanged. The pillars looked slanted because the
  resting camera looked down 10 degrees: drivers on the camera now keep it level whenever the dolly looks down
  and shift the lens instead (the dolly's animation is untouched; the low opening shot is unchanged).
- `tools/v10_temple_geo.py` (copy of the version 9 script): the apse is replaced by a long corridor of ribs and
  pillars ending in a far doorway of light, so arches nest behind the badge. Two flicker bugs fixed: walls cut
  on the same curve as an arch's underside showed as rows of bars (cuts now sit inside the arch stones, and
  never wider than the wall itself).
- `tools/v10_temple_mat.py` (copy): light touch only. Pillars and arches take their relief from the plain rock
  scan (the block wall scan read as camouflage blotches); big walls use soft noise relief; damp patches on the
  floor away from the dais; less mirror shine on the dais edge.
- `tools/v10_temple_light.py`: a dark hall lit from behind and above. One strong light at the far doorway
  (ribs and pillars stand dark against glowing air, inner edges catch it), warm edge lights on the big pillars
  and under the big arch, a soft pool on the small arch, two faint columns of light between the pillars, faint
  cool light from the aisles, thin air that thickens with distance. Only the far light and the two columns
  light the air: in version 9 every temple light also lit the beam's haze, which greyed the top of the picture.
  The beam from above is a little more golden and its haze has rays that fan out from the light and a hot core.
- `tools/v10_lens.py`: soft focus behind the chest (f 0.9 at this scene's scale), darker corners and a gentle
  grade in the compositor after the existing glow. No film grain (bad for a compressed phone movie).
- Options shown to the owner: A (as saved) and B, more glow in the hall (far light's share in the air 3.2,
  small arch light 42000, high light 15000; not saved). `temple/tools/shot.sh NAME [PCT]` renders a test of frame
  213; `TWEAK` and `HIDE` change values for one render without saving.
- Not done yet: the light over the rest of the 7 seconds, the movie without the badge, the badge's path for
  the app, and the one test picture in Cycles.

### Version 10, second polish round (same day)

The owner picked option A, kept the beam as it is, and asked to try: the long hall behind the badge, cool
against gold, a floor that catches the light, older looking stone, glowing platform rings, richer stonework,
a test with other badges, and an ending that keeps moving ("the user will decide when to continue"). Not
wanted for now: the badge lighting its surroundings. Still unanswered: whether words or buttons sit over the
movie, and where.

- Long hall: the arch behind the chest is now round and tall (rise 15.3, was 9.6), so the corridor's receding
  ribs show above the badge. The far doorway's strong light keeps its narrow cone; a second wide light at 12
  percent (`Temple Corridor Glow`) lights the vault and ribs. At full strength they went cream white right
  above the badge. Rule kept from the badge tests: everything behind the badge stays darker than a badge's rim.
- Cool against gold: `Temple Cool L/R` shine from the side aisles a little behind the big pillars, so each
  pillar has a blue outer edge, a dark middle and a warm inner edge.
- Floor: damp patches (softer than a mirror: sharp wet glints read as white specks), a stronger warm pool
  round the dais (`Temple Beam Spill`), and `Temple Mist Rim`, a low warm light behind the chest that lights
  only the air, so the ground mist glows at its edges.
- Stone: pillar shafts carry 16 shallow grooves (a bump in the shared stone material; each pillar's points
  store their direction round the pillar and whether they are on the shaft, UV maps `PillarDir` and
  `PillarShaft`), chipped corners on the big and small pillars' blocks, moss tufts on the plinth ledges
  (`Temple Moss Tufts`), fallen blocks and small stones by the big pillars (`Temple Fallen Blocks`).
- Rings: the dais's gold rings glow softly (emission 0.55, deep gold; stronger or paler read as white or pink).
- Other badges: `temple/tools/other_badge.py` (through `BADGE_USDZ=... temple/tools/shot.sh NAME`) shows another
  of the app's models in place of the scene's badge for one render, never saved. Golden Sands and the Gold
  crown both stand clear of the hall.
- Moving ending: `tools/v10_motion.py` (the beam's haze keeps drifting past frame 213, its rays shimmer, the
  rings breathe once per loop) and `temple/tools/loop_test.py` plus `loop_join.py` (render the frames after
  the reveal and blend the tail into the start so they repeat without a jump). The chest's mist simulation
  ends at frame 213 and is held on its last frame in this first test.

## Version 11 torches (2026-11-19)

The owner wants the whole reveal more epic and added: "we can put some torches ... the fire can wake up the
hall". They also explained the app's flow: the user swipes up to flip the lock and later decides when to
continue, so the movie becomes four pieces (arrival once, a waiting loop, the reveal once, an ending loop).
Decisions so far: torches on the pillars and down the hall, none beside the platform; an idle rattle may bump
the lid a hair; the swipe works about 2 seconds after the landing (the dust has to clear faster); the mist in
the chest stays as a thin drifting layer in the ending; three rattles on an even 2.5 second beat (each over
within 0.8 seconds), delivered next to a one rattle clip, so the app's rule is the same for both.
`chest_reveal_v11_torches.blend` is a copy of version 10 (which keeps the look without torches).
Picture: `~/Downloads/Chest temple torches before and after.png`.

- `tools/v11_torches.py` (run after the version 10 scripts): six pairs of torches (big pillars, small pillars,
  four bays of the long hall), each an iron bracket and cup with a small flame card drawn by a shader, its own
  small light, and a soft glow light per bay. `Temple Torch Control` has `lit_0` to `lit_5` (0 to 1): flame
  size, flame brightness and all torch lights follow them, as do the warm edge lights on the big pillars
  (`lit_0`) and the pool on the small arch (`lit_1`). All are 1 for now; keying them lights the hall pair by pair.
- The far doorway's gold light is gone (it showed the hall before anything woke it): faint cold moonlight now.
- `temple/tools/shot.sh` now renders from the version 11 file (`BLEND=` and `FRAMES_DIR=` choose another).
- Agreed order of the light moments, so they build instead of piling up: the lid cracks and cold light bursts
  from the chest; the badge rises and the torches catch pair after pair into the distance; the badge settles
  and the golden beam comes to full with the rings. The camera holds still inside both loops. One time effects
  (landing dust) end before a loop starts. Not built yet: all of that timing, the waiting loop with its
  rattles, the reframed start for the tall screen, and the pieces as separate clips.

### Version 11, torches second design and new stone (same day)

The owner on the first torches: "maybe we can do even better on the fire", with a picture
(`~/Downloads/Flaming Iron Torch on Stone Wall.png`: a goblet shaped iron cup on an arm and a bolted plate, a
big flame with tongues and sparks), and: "do you think we can make some genuine enhancements to the texture
beneath the badge and the concrete floor?". Pictures: `~/Downloads/Chest temple new torches and stone before
and after.png`, `... details.png`, `Chest temple new torches and stone.png` (full size), and the clip
`Chest temple torch fire close up.mp4`.

- `tools/v11_torches.py` rewritten: forged iron sconces (oval plate with four bolts, square arm, socket with a
  collar, goblet cup with a thick rim; hammered and rusted iron), turned 35 degrees toward the camera so the
  arm and cup read. The fire is two cards per torch (a larger, deeper layer behind a brighter one, each with its
  own shape), drawn by one shader: a bulb as wide as the cup, leaning, split into tongues by upright streaks of
  noise that stream upward, fine veins, a yellow heart low in the middle. Colours are kept toward yellow: under
  this scene's view transform (AgX) a bright pure red orange turns salmon pink. Glowing coals in the cup, a
  few one pixel embers on their own card. Only the two big torches' lights cast shadows (twelve shadowed fire
  lights overflowed the shadow memory at full size).
- `tools/v11_stone.py` (run after `v10_temple_mat.py` and `v11_torches.py`): the floor and the platform get
  two more CC0 scans. Flagstones: rock_face_04 laid large, its height map darkening cracks and hollows, grimy
  joints, bitten edges, water only in the hollows of the damp areas, the scan's pale grit toned down (it would
  be light specks at phone size). Platform: rock_3, pitted, dirt in the pits, a few long broken cracks across
  the top, quieter moss. The mossy bed in the joints is darker (it glowed yellow green under firelight).
  `Temple Floor Firelight L/R` bring the big torches' light to the floor at a low angle (floor only, no
  shadows, follow `lit_0`); that raking light is what shows the stone's relief. The platform's key light is lower.
- `temple/tools/closeup.py` (through `CLOSE="position;target;lens;width;height"` with `temple/tools/shot.sh`)
  renders one spot through a temporary camera, never saved.
- Run order for version 11: the version 10 scripts (geo, mat, light, lens, motion), then `v11_torches.py`,
  then `v11_stone.py`.
- To watch: a full size frame now takes about 5 minutes (it was about 70 seconds in version 10). The scene
  needs speeding up before the whole movie is rendered. Not checked yet: the new floor from the low opening camera.

### Version 11, fire third version and platform options (same day)

The owner on the pitted platform: "something about the texture beneath the badge, the circle object it rests on
that I do not like.. idk what it is", and on the torches: "it can use some work. it's kind of there but not fully."

- Fire (`tools/v11_torches.py`): the second flame was drawn as paint (a shape with see through edges laid over
  the picture) and read as a cartoon blob. Now every layer only adds light (Add Shader of transparent and
  emission), so overlapping layers burn pale yellow at the heart and the thin edges stay deep orange and see
  through. Three layers per torch (wide dim back, body, small hot heart) with their own shapes, fine bright
  threads inside (ridged noise), the whole fire breathing taller and shorter, and a soft glow card round it.
  Sconce closer to the owner's picture: a stout rounded bowl with a thick rim band, a collar, a thicker arm, a
  bigger plate and bolts; iron darker and more metallic with bigger hammer marks; `Temple Torch Sheen NN`
  lights reach only the iron (collection `Temple Torch Iron Only`) and give it the fire's sheen.
- Platform (`tools/v11_dais.py`, run by `v11_stone.py`): `DAIS_STYLE` chooses `pitted` (the scan, what the
  owner did not like: speckled, blotchy, paler than the floor), `dressed` (dark, smooth, honed, a soft sheen),
  `carved` (dressed plus a carved band of two grooves and short radial marks inside the gold rings) or
  `marble` (dark polished stone with pale veins and the carved band). The saved file still has `pitted` until
  the owner picks; `DAIS_STYLE=... temple/tools/shot.sh NAME` renders a style without saving it.
- The firelight now reaches the platform as well as the floor (`Temple Firelight Receivers`): lit apart from
  the floor, the platform looked pasted on.
- Pictures: `~/Downloads/Chest platform options.png`, `Chest temple torch fire close up 2.mp4`.

### Version 11, small changes on 2026-11-20

- Platform: the owner asked to see "B with C's color". `DAIS_STYLE=carved_dark` is the carved stone in the
  marble's near black colour, matte and without veins (`~/Downloads/Chest platform B in C colour.png`). The saved
  file still has `pitted` until the owner picks.
- Floor ("a teeny tiny bit less detailed, the stone at the very bottom almost draws my attention to it"): relief
  0.9 to 0.62 (`FLOOR_RELIEF`), bump 0.45 to 0.32, cracks darkened to 0.48 where they went to 0.3, bitten edges
  a little paler, the stones closer in tone to each other. Saved.
- Torches ("the torch is sitting on a seam. it would never do that in real life"): each pillar has 16 grooves, so
  a band between two ridges is 0.78 wide on the big pillars and the old plate (1.1 wide) always crossed a
  ridge. Each torch now points at the exact middle of a band (`TORCH_TURN` 45, then snapped), and the plate is
  a slim strap (0.64 wide) with four bolts in a column, so it fits inside the band
  (`~/Downloads/Chest torch off the seam.png`). Saved.
