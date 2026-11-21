# Treasure chest badge reveal animation

**Newest: `chest_reveal_v12_full.blend`** (2026-11-20, the whole reveal in four pieces, see Version 12). **Before that: `chest_reveal_v11_torches.blend`** (the end look with torches, see Version 11). **Before that: `chest_reveal_v10_temple_polish.blend`** (the temple's end look polished for iPhone screens, see Version 10; `chest_reveal_v9_temple.blend` is the version before, see Version 9). **Core: `chest_reveal_v7.blend`** (2026-11-18; landing dust in `chest_reveal_v7_dust.blend`, ending light in `chest_reveal_v7_ending.blend`, see Version 7). Version 6: `chest_reveal_v6.blend`, scene **Chest Reveal**: 30 fps, frames 1 to 213
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
- Floor, second step (the owner could not see the first: "is the floor calmer? I can't really tell"): the scan's
  light and dark are pulled 45 percent toward one even tone (`FLOOR_EVEN`), relief 0.36, bump 0.2, cracks only
  darkened to 0.68, stones closer in tone, and the firelight is aimed further back (y 7, was minus 3) so it no
  longer rakes the stones nearest the camera. Saved. `~/Downloads/Chest floor calmer before and after.png` shows
  the real bottom of the picture (`BORDER="0,0,1,0.3"` with `temple/tools/shot.sh` renders only that part of
  the real frame, in about 20 seconds).
- Torch shapes (the owner: "let's change the shape of the fire and torches I think it can be more tasteful"):
  `TORCH_STYLE` in `v11_torches.py` chooses `goblet` (the stout cup with a tall fire, still the saved one),
  `slim` (a slender torch leaning out of two iron rings, a small teardrop of fire) or `bowl` (a shallow dish
  on a curved arm, a low wide quiet fire). Each shape sets where the flame starts, its card and the flame's
  own shape (`SHAPE`). `TORCH_STYLE=... temple/tools/shot.sh NAME` renders one without saving
  (`~/Downloads/Chest torch shape options.png`).
- The owner picked the slim torch ("Let's go with A"): `TORCH_STYLE` now defaults to `slim` and the scene is saved
  with it. `TORCH_LEAN` (degrees, default 17) leans it out from the pillar; 0 stands it straight up, further out
  from the stone (0.8, leaning 0.4) so its fire stays clear. Both shown in
  `~/Downloads/Chest slim torch leaning or straight.png` (close up, and the real frame's band through
  `BORDER="0,0.6,1,0.86"`). The saved scene leans until the owner picks.

## Version 12: the whole reveal in four pieces (2026-11-20, built overnight)

The owner locked in the straight slim torch, the dark carved platform and the calmer floor, then: "create the
entire scene ... make sure everything we talked about is implemented and then render the scene and leave it in
the downloads folder". `chest_reveal_v12_full.blend` is a copy of version 11 (which keeps the end look alone).
The badge is still in every render as the owner's guide; the phone will draw it in the app.
Plan and progress: `badges/plans/chest_reveal_v12_full_scene_20261120.md` (not in Git).

**The four pieces** (the user swipes up to flip the lock, and later decides when to continue):

| Piece | Frames | What it is |
|---|---|---|
| 1 Arrival, once | 124 (4.1 s) | 1 s of empty temple, the chest drops in, dust clears, everything comes to rest |
| 2 Waiting, loops | 225 (7.5 s) | rattles at 0, 2.5 and 5.0 s, each over within 0.8 s; the first 75 frames loop alone (one rattle) |
| 3 Reveal, once | 164 (5.5 s) | lock flips, lid opens, badge rises, torches catch, gold beam |
| 4 Ending, loops | 90 (3 s) | badge floating; fire, mist, dust in the beam and rings alive |

Rule for the app in the waiting loop: take the clip's time modulo 2.5 s; under 0.8 s a rattle is playing, so
wait until 0.8 s, otherwise start the reveal at once. The same rule serves the one rattle clip.
The ending loop's first frames are blended with its last (so it repeats without a jump); to pass from the reveal
into it with no flicker in the flames, play the unblended ending frames once (`render/v12_frames/ending`
0 to 89), then the loop (`ending_loop`). The whole preview does that.

- `tools/v12_story.py` (inside Blender, after the version 10 and 11 scripts): keys the story on the real timeline
  (scene frames -28 to 213; Blender keeps the scene's first frame at 0, the story's start is in
  `Temple Story["start"]`). Numbers on the empty `Temple Story` drive everything: `gold` (0 moonlight, 1 the
  gold ending; the temple's lights follow it), `rings` (flash at the landing f17 and f22, pulse at the click f56
  and when the badge settles f186, soft glow at the end), `burst` and `rays` (cold light from the chest when the
  lid cracks at f90: on the floor and pillars through `Temple Chest Burst`, in the hall's air through
  `Temple Burst Rays`), `keyhole`, `seam`, `dustfall` (dust shaken from above), `drift` (the chest's mist keeps
  drifting at the end). Torch pairs catch near to far from f120, 9 frames apart, each with a flare
  (`lit_0` to `lit_5`). The camera is level through the whole movie and the chest sits low in the tall picture
  at the start (`START_SHIFT`); it pushes toward the lock from the swipe (f50) to f88. The chest now falls from
  9 units higher so it is out of the picture before it drops. The studio surroundings that lit the chest are
  dim from the start (they flattened the dark temple). The far doorway is a faint slit (bright, it sat on the
  lid like a glowing pill once the camera rose).
- `tools/v12_render.py` (background Blender, `PIECE=arrival|waiting|reveal|ending`): adds what a straight playback
  cannot: the arrival's tail (chest held at f49 while the landing dust clears and the side rings swing to rest),
  the waiting loop (chest held at f49; three different rattles as delta transforms on the lid, clasp, body
  and rings; keyhole glow breathing; the line of light at the lid's seam follows the lid's lift), the reveal with
  rings at rest and no landing dust, and the ending with the mist held on its last simulated frame. Nothing in
  the scene's animation is touched: rig parts get delta transforms, and the story's numbers are set after its
  action is taken off, in that process only. `ONLY="3,40"` renders chosen frames for tests.
- `temple/tools/v12_run_all.sh`: renders the four pieces (resumes where it stopped), joins the ending loop and
  writes the videos to Downloads (`Chest reveal whole scene preview.mp4` and one file per piece).
- Things learned: a light's reach into mist and haze cannot be limited to chosen objects (light linking covers
  surfaces only), so a light that should not brighten the chest's mist needs volume 0, and rays need their own
  light that does not look at the mist. Custom numbers set from Python need `update_tag()` before drivers see
  them. Animated values cannot be overridden by setting them at render time: use delta transforms, or take the
  action off.
- Known small things: five grains of landing grit are still in the air at f49 and hang there during the waiting
  loop (they are far below a pixel in the preview). The platform's carving is shading, not cut geometry (it
  reads from both cameras). This render is a preview: half size, 24 samples.

### Version 12, first render checked and two fixes (2026-11-20, about 3:30 AM)

The first render (half size, 24 samples) took 2 hours. Checked by measuring the difference between the last
frame of each piece and the first frame of the next (mean difference per pixel, 0 to 255; two neighbouring
frames of the ending differ by 0.25):

| Join | First render | After the fix |
|---|---|---|
| arrival into waiting | 0.01 | same |
| waiting into itself (three rattles, and one rattle) | 0.00 | same |
| waiting into reveal | 0.40, top third 1.07: the dust from above came back | 0.01 |
| reveal into ending | 0.03 | same |
| ending loop into itself | 0.52 (flames blended over 24 frames) | same |

- Fix 1: on the straight timeline the dust shaken from above is still falling at frame 50, so it popped back in
  when the reveal started. `v12_render.py` now holds `dustfall` past its end for the reveal and the ending.
- Fix 2: the cold burst made the floor at the bottom of the picture flash white (bottom eighth of the picture
  at 77 of 255, now 37; the hall above is unchanged). `Temple Chest Burst` sits just above the chest's rim and a
  little back (0, 0.2, 3.1), so the chest's own walls shade the floor all round it.
- Reveal frames 0 to 136 were rendered again; the other pieces are unchanged.
- The live Blender was closed during the first render (it holds 6 GB) and reopened with
  `chest_reveal_v12_full.blend` afterwards.

### Cleanup on 2026-11-20 (owner: "go through this folder and find things to delete to make space")

Receipts in `cleanup_runs/make_space_20261120/` at the repository root. Removed from this folder:
- Blender's automatic backups (`*.blend1`) and the test and preview frames of versions 7 to 11
  (`render/v7_check`, `v7_full_frames`, `v7_opening_frames`, `v8_mist_frames`, `v9_temple_frames`, `v10_frames`,
  `v11_frames`): 3.1 GB. The videos and pictures made from them are in the owner's Downloads.
- `chest_reveal_v5.blend`, `v6`, `v7_dust`, `v7_ending` and `v8_mist`: 1.3 GB. Kept: `chest_reveal_v7.blend`
  (the core animation), `v9_temple`, `v10_temple_polish`, `v11_torches`, `v12_full`. None of the kept files names
  another version file (checked inside the files).
- `cache_opening/` (the version 7 opening fog the owner turned down; only `v7_dust` used it): 5.8 GB.
- `cache_dust` frames 96 to 213: 9.7 GB. Version 12 reads the landing dust only up to frame 95 (the arrival
  piece; two arrival frames rendered again afterwards were identical). Playing a kept scene straight through in
  Blender shows no landing dust after frame 95. To get it back: `tools/v7_squeeze.py`, `v7_dust.py`, then
  `blender -b <file> --python tools/v7_bake_dust.py` (about 1.5 hours).
Sections above that name the removed files are kept as a record of what each version was.

### Version 12, second pass after the owner's notes (2026-11-20, about 3:45 AM)

The owner watched the first version and said (speech to text, shortened):
- about an arch in the dark start: "when it's dark, that texture ... looks a little cheap. I want it to look better";
- "The smoke animation should animate the entire way out, and I want it to animate out smoothly ... if you have to,
  extend the clip";
- the platform's gold rings: "I don't want them to light up ... They're just colored that way";
- "I don't ever want the camera to pull in"; "the camera animation is a little too fast ... slow and cinematic,
  smooth and cinematic";
- "the lights come on very fast ... dark scene and suddenly it's like a light scene. I want them to come on a
  little slower ... they could appreciate the lights coming on and what it does to the environment".

What changed (run order inside Blender after the version 10 and 11 scripts: `v12_story.py`, `v12_slow.py`,
`v12_dark.py`; then `blender -b chest_reveal_v12_full.blend --python tools/v12_bake_mist.py` once):

| Piece | Frames | Change |
|---|---|---|
| 1 Arrival, once | 124 (4.1 s) | rings never flash; dark look |
| 2 Waiting, loops | 225 (7.5 s), first 75 loop alone | dark look |
| 3 Reveal, once | 231 (7.7 s), scene frames 50 to 280 | no camera push; slower camera, slower lights, mist plays out |
| 4 Ending, loops | 90 (3 s), from scene frame 280 | no mist left in the chest |

- Rings: plain gold metal, emission 0, no driver (`v12_story.py`).
- Camera: never moves toward the chest. The rise and pull back as the lid opens keeps its path but takes frames
  90 to 205 (was 90 to 142) with one long ease (`v12_slow.py`; the original move is in
  `temple/v12_camera_original.json`; the dolly has its own action `v12 Camera Dolly Slow` over its old NLA tracks).
  The badge stays inside the picture through the whole move (its top is never closer than 21 percent of the
  height to the top edge).
- Lights: torch pairs catch from frame 126, 15 frames apart (was 120 and 9), each rising over 14 frames and
  settling over 20; `gold` runs 122 to 238 (was 118 to 186); the beam and the room's change 130 to 228 (was 132
  to 186); the cold burst rises with the lid to frame 114 and is gone by 228.
- Mist from the chest: simulation baked again to frame 286 with the same settings (588 s; the old cache is in
  `cache_smoke_mist_before_v12`, 176 MB, delete it once the new one is approved). How thick it reads fades from
  full at frame 190 to nothing at 272 while it keeps moving. Nothing is left in the chest at the end: asked which
  smoke they meant and whether any should stay, the owner answered "the mist that pours out of the chest ... I
  want the mist to drift all the way out, none left at the end" (on 2026-11-19 they had chosen a thin layer that
  stays). `Reveal Chest Haze`, a faint drifting layer, is kept in the file switched off (`CHEST_HAZE` 0).
- The dark look (`v12_dark.py`): arches built of stones (joints as relief and old dirt, each stone its own tone,
  a roll along the inner edge, a hood along the outer edge, a keystone; materials `Temple Arch Stone*`), coursed
  masonry on the back wall and the long hall (`Temple Wall Masonry`), relief from a real height map; one cool
  light from high on the left raking across the arches (`Temple Moon Key`, shadows only from pillars and
  arches); the flat blue fill from the front far down while dark; two faint slanted shafts into the long hall
  (`Temple Moon Shaft A/B`) and the two front shafts slanted the same way (straight down they read as pale
  poles). All of it fades with `gold`. The moss tufts are quieter (they turned yellow green in the moonlight).
- A driver on the camera that read the camera's own lens made a dependency cycle; the lens is a number now.
- Render: 70 percent size (756 by 1638, twice the pixels of the first version), 24 samples, shadow detail kept
  at the half size level (full size overflowed the shadow memory), dithering 1.5 and a higher quality encode
  (crf 14) against bands and blocks in the dark. Full size frames take 25 to 37 seconds each, 70 percent about
  11. The waiting loop's 51 quiet frames per beat are rendered once and reused for the other two beats.
- The first version's videos are in `~/Downloads/Chest reveal first version (old)/`.
- Second pass rendered 2026-11-20, 4:12 to 6:02 AM (reveal 41 min, ending 25, arrival 20, waiting 22). Checked with
  `temple/tools/v12_check.py`: every join between pieces differs by 0.00 to 0.01 per pixel (0 to 255); the ending
  loop's seam (0.49) equals the difference between two of its neighbouring frames (0.50). Through the reveal the
  picture's change from frame to frame has no spike (median 0.64, a smooth rise to about 8 at the middle of the
  camera's move and back down), and its brightness climbs steadily from 2.0 to 5.5 seconds (28, 29, 40, 38, 47,
  50, 57, 60, 62, 63 of 255, every half second). Videos and `Chest reveal key moments.png` are in Downloads.

### Version 12, third pass after the owner's second review (2026-11-20, about 6:15 AM)

The owner watched the second pass and said (speech to text, shortened):
- "you improve that one part and it looks good, it looks like stone, and then now the pillars look kind of like
  Play-Doh. So now you got to improve the pillars";
- the camera "goes back and then there's like a sharp up ... very quick. I want that to be like a fluid motion,
  like it should be like an arc ... you can also make the badge come out a little slower";
- "the one before had like two light streaks, almost as if ... parts of the roof were missing ... The night light
  was shining through, and I like that. And then in those same areas ... dust came and fell ... I want it to be
  higher quality dust ... like the chest falling kind of made some of the dust from above come down ... add that
  back in";
- with a picture of the far end of the hall: "this pattern in the back ... does not look good, maybe we can ...
  blur it so it doesn't look so jaggedy".

Run order inside Blender after the version 10 and 11 scripts: `v12_story.py`, `v12_slow.py`, `v12_dark.py`,
`v12_pillars.py`, `v12_dust.py`; then `blender -b chest_reveal_v12_full.blend --python tools/v12_bake_mist.py`
once (the badge is a collider in the mist, so the mist is baked again whenever the badge's timing changes).

| Piece | Frames | Change |
|---|---|---|
| 1 Arrival, once | 124 (4.1 s) | two shafts of night light; dust falls in them after the landing |
| 2 Waiting, loops | 225 (7.5 s), first 75 loop alone | shafts, new pillars |
| 3 Reveal, once | 241 (8.0 s), scene frames 50 to 290 | camera on one arc, badge 1.3 times slower |
| 4 Ending, loops | 90 (3 s), from scene frame 290 | new pillars |

- Camera (`v12_slow.py`): one arc round the chest (pivot 0, 0, 3 in the chest's frame) from the old start
  framing to the old end framing, frames 90 to 232 (4.7 s), with the lens shift on the same single ease
  (speed rises over 35 percent of the move, holds, falls over 35 percent). The camera is level all the way and
  its lens shift is keyed directly. Why the old one jerked: the path, the tilt (turned into lens shift by a
  formula with a kink) and the camera's own distance each ran on their own timing. Measured on five fixed
  points of the hall and chest, frame by frame at full size: none ever changes direction, the fastest moves
  9.1 pixels a frame, and the largest change of speed between two frames is 0.29 pixels.
- Badge: its rise, turn and settle take 1.3 times as long (front at about frame 182, settled about 206), in its
  own action `v12 Badge Slow` over its old NLA track. The reveal ends at frame 290 (was 280); the mist fades
  from frame 200 to 282 and its simulation runs to 296.
- Pillars (`v12_pillars.py`): 16 real concave flutes with sharp ridges cut into each shaft (the old grooves were
  only shading), crisper plinths and capitals. Ridges stand where the painted ones were, so each torch still sits
  in the middle of a flute (the plate now stands 0.085 off the bottom of the flute, about 2 pixels, not visible).
  A first build stacked each shaft from three drums with seams; shown the stills, the owner said "I don't like the
  drums. Just make it look like real stone." So each shaft is one solid piece, and its colour, relief and
  roughness all come from the same scan (Poly Haven plastered_stone_wall, with its height map added to
  `temple/resources`), wrapped round the shaft through its own UV map `PillarUV` (two repeats; box projection
  smeared on a round shaft) and projected flat on the square blocks. Matte (roughness about 0.86; at 0.6 the
  ridges drew glossy lines), faint stains running down the shaft, a little dirt in grooves and pits.
  7,042 faces per pillar. Stills: `~/Downloads/Chest pillars solid stone.png`.
- Far end of the hall: the long hall's pillars are plain round shafts (their stepped plinths and flared capitals
  stacked into a jagged outline), the hall's air beyond the small arch is twice as thick (`AIR_CORRIDOR` 3.2), the
  far light sits beyond the air (no bright dot), and the joints of the far ribs are only hinted at (`RIB_JOINT`
  0.15; at full strength they drew a dotted line through the haze).
- The two shafts of night light (`Temple Shaft L/R`, placed in `v12_story.py`): straight down at (-10, 36) and
  (11.5, 47), lit from very high (z 330) so the streak is as strong at the floor as under the roof, air boost 40.
  The second pass had slanted them like the moonlight, which took them out of the hall's air: they vanished.
- Dust from above (`v12_dust.py`), only inside the two shafts, driven by `dustfall` (seconds since the impact at
  frame 17), over by 2.5 s: (1) `Temple Dust Grit L/R`, five loose threads of very fine pale grains per shaft
  (about 2,800 grains), pouring from single points, falling with gravity and drag, each drawn as the short
  streak it would blur to; (2) `Temple Dust Cloud L/R`, a thin veil of fine dust that comes down slower behind
  the grit, spreads and thins away. The old six cards with scrolling streaks are kept in the file, switched off.
  Tried and dropped on the way: solid grains lit only from above (brown blocks), and dense bright streams (white
  ropes like poured milk).
- `v12_render.py`: in the arrival `dustfall` is stepped by hand and `streak` is 1, so the renderer's own motion
  blur cannot smear the fine grains away in some frames and not in others.
- The videos of the second pass are in `~/Downloads/Chest reveal second version (old)/`.

### Cleanup of the older chest building folders (2026-11-20, 7:05 AM)

Owner: "if making or deleting the older chest folders will have no issue on the current ones, then sure".
Checked first: every kept Blender file under `treasure_chest_20261113` (the five reveal scenes, `chest_simple`,
`chest_claude`, `source_copy`, phase06 `master`, phase05 `14_edge_review/master`, phase01 `candidate43/chest`,
the root file) was decompressed and searched for image names, and version 12 was checked in Blender before and
after (86 images packed; the only missing image, a phase04 comparison picture, was missing before).
Removed, 405 files, 1.37 GB (receipt `cleanup_runs/make_space_20261120/receipt_old_chest_folders.jsonl`):
arrays (`.npz`, `.npy`) of older material steps in phase01 to phase06 (851 MB), `phase06/material_rollout/
baseline.blend` (158 MB; its source and its result are both kept), and renders and candidate maps in phase03 to
phase06 that no kept Blender file names (298 MB). 788 MB of it is in Git history and can be restored from there.
Not touched: `claude_attempt_20261117` (the chest in use), every other Blender file, every text file, every
`resources` folder, anything named reference or owner, `BC_final_polish`, `14_edge_review`, `phase01/candidate43`.
The old generators of the detailed chest can no longer be run again from their arrays.
- Third pass rendered 2026-11-20, 7:15 to 9:05 AM (reveal 47 min, arrival 19, ending 20, waiting 21), 70 percent
  size, 24 samples. Checked with `temple/tools/v12_check.py`: every join between pieces differs by 0.00 to 0.04
  per pixel (0 to 255); the ending loop's seam (0.57) is in the range of two of its neighbouring frames (0.38).
  Through the reveal the picture's change from frame to frame is one hump (0, rising to 5.4 at the middle of the
  camera's move, back to 0.4) and no frame changes more than 1.32 times the frames either side of it. The dust
  from above is continuous where the arrival's two parts meet (frames 77 and 78). Videos and
  `Chest reveal key moments.png` are in Downloads; the second pass is in `Chest reveal second version (old)`.

### Version 12, fourth pass after the owner's third review (2026-11-20, about 9:20 AM)

The owner watched the third pass and said (speech to text, shortened), with three pictures (the top of a front
pillar, the top of the picture at the start, the two arches in the gold light):
- "the light at the end, it twinkles way too fast ... It's got to be like a third of this current speed";
- on top of a pillar: "It has this weird shape. I don't know what that shape is";
- the top of the screen at the beginning: "it doesn't look like an enclosed space. It should look like an enclosed
  place";
- "I want it to start off darker. I want there to be more mystery about what's behind ... it's got to be revealed.
  I feel like I see too much of the background, especially that top wall ... it's showing way too much";
- the arches: the nearest one's strip "has a certain length, and then the next one ... way longer. And it doesn't
  look congruent because one of them is thin and then the one's not thin";
- "I want it to look like a movie scene ... A cool reveal, that's what I'm looking for";
- the smoke: "It seems to be doing some not very physics-like things ... Just make sure it's in line with actual
  physics. Like, it should be interacting with the box correctly".

Run order inside Blender after the version 10 and 11 scripts: `v12_story.py`, `v12_slow.py`, `v12_dark.py`,
`v12_pillars.py`, `v12_hall.py`, `v12_dust.py`, `v12_mood.py`, `v12_mist.py`; then
`blender -b chest_reveal_v12_full.blend --python tools/v12_bake_mist.py` once.

- Fire (`v12_mood.py`). Which light: measured in the rendered ending, the picture changes most from frame to
  frame at the torches, and their light was built on beats of 7.6 and 3.3 frames (4 and 9 times a second). The
  torches' light, flames, glow, coals and sparks all run at a third of that speed (`FIRE_SPEED`).
- The odd shape (`v12_dark.py`). A colour coded render (`temple/tools/ids.py` before `tools/v12_render.py`)
  showed it was the foot of the moulding along the big arch's outer edge: that edge is buried in the side arches,
  so only a short upright stub showed on each front pillar. The big arch has no outer moulding now, and all
  mouldings are thin (`TRIM_OUT` 0.1; at 0.3 to 0.4 their sides caught the moonlight as bright bars).
- Enclosed (`v12_hall.py`). The vault over the front hall was a smooth dark shell that read as empty black. It is
  now coursed stone 1.6 thick with ribs across it (at y 18, 29.8, 41.6 and where it meets the wall), broken open
  in two ragged holes exactly where the two shafts come down (boolean, baked into the mesh; the cutters
  `Temple Vault Hole L/R` stay in the file, hidden), with a dim night sky above (`Temple Night Sky`) and a faint
  cool light from below (`Temple Vault Bounce`, 14,000 in the dark, only on the vault and its ribs). From the
  start camera only the right opening is in the picture; the left one is just above its top edge. The vault is
  out of the shafts' and torches' light (the shafts burned the openings' edges white).
- Darker start (`v12_mood.py`). Dark levels only; the gold ending is unchanged. Moonlight on the top wall and
  arches 420,000 to 80,000; side fills, the long hall's lights and floor light lower (table in the script). The
  far hall did not get darker until the room's ambient light (the world) was lowered: it is what makes the haze
  glow. It starts at 0.35 of its level and comes up with the gold. Measured on the start picture (0 to 255):
  top wall 20 to 6, big arch 38 to 16, far hall 50 to 22, front pillars 31 to 16, whole picture 28 to 16; the
  chest's own lights are untouched.
- Matching arches (`v12_hall.py`). The small arch ran straight into a tunnel of its own radius (15.3), so its
  underside seemed 30 units long against the big arch's 5.6. The long hall is now wider and higher than the arch
  (16.6), its vault is its own object with dark masonry (`Temple Corridor Vault`), and each rib is a full arch
  from 13.7 out to the vault. Its pillars and torches did not move (the pillars now stand free of the walls).
- Smoke (`v12_mist.py`). Seen frame by frame against the chest, the smoke rose a little, stalled, lay flat at
  the rim and faded where it lay. It now has three times the lift (in the scene's units a normal lift crawled:
  the chest is 5.5 units wide, which the simulation reads as metres) and 96 cells in place of 64, so every wall
  of the chest and lid is two to three cells thick. It leaves the chest as a rising plume, passes the badge and
  thins. Baked at 96: see `render/v12_bake_mist_4.log`.
- Stills: `~/Downloads/Chest third review check.png`. The third pass's videos are in
  `~/Downloads/Chest reveal third version (old)/`.
- Later the same morning the owner added: the lights shining down are "a teeny bit too bright. Maybe make them
  70% or 80%"; "this is supposed to be a worn down temple ... it's not going to be a perfect circle shining down
  ... not a well-defined shape"; and the sand: "It is way too much sand ... just a little bit of sand, enough to
  be noticeable ... like 20% of the current amount", "maybe don't make the sand so white ... It'd probably be the
  color of the stone" (a suggestion).
  - Shape (`v12_hall.py`): each opening in the vault is now an uneven broken outline with straight edges and
    corners, longer one way than the other. The same outline is a plate above the vault (`Temple Shaft Mask L/R`,
    not seen by the camera) that only the shaft's light is blocked by, so the light takes the opening's shape in
    the air and on the floor. The shaft lights are wider than the opening (the plate cuts them), still strongest
    in the middle (blend 0.8), a little soft at the edge (light size 0.6).
  - Level: measured on the start picture, each streak against the dark beside it. A first try was far too faint
    (a third); now the left streak is at 65 to 83 percent of what it was and the right, set by the same measure,
    at about 75 (`SHAFT_SHAPE` left 1.15, right 0.87; `SHAFT_LEVEL` 0.75 for the dark part of the story; the gold
    ending keeps its level).
  - Sand (`v12_dust.py`): three thin trickles of about 180 grains per shaft (it was five of about 550: 514
    grains against 2,769), the veil of fine dust behind them at a third, and the grains grey like the stone
    with far less shine of their own.
- A bake was lost on the way: running `v12_mist.py` again in the open Blender while the bake ran in the background
  made Blender clear the baked files (writing a simulation setting clears them, even with the same value).
  `v12_mist.py` and `v12_slow.py` now write those settings only when they differ. Do not change the mist's
  settings in the open Blender while a bake runs.
- Fourth pass rendered 2026-11-20, 10:13 AM to 12:18 PM. Checked with `temple/tools/v12_check.py`: joins 0.00 to
  0.01, the ending loop's seam 0.55 against 0.29 between two neighbouring frames, no jolt in the reveal, the sand
  continuous where the arrival's two parts meet, the start picture's average brightness 18 of 255 (it was 28),
  the ending's change from frame to frame 0.32 (it was 0.42, mostly the torches).
- Smoke, second pass. In that render the main puff rose and left, but what spilled over the rim had cooled and
  hung beside the chest as a flat sheet at rim height for over a second. `v12_mist.py` now gives it more lift
  (`MIST_LIFT` 5; even the thinned smoke keeps rising) and lets it thin sooner (`MIST_THIN` 50 frames, was 68);
  `v12_slow.py` shows it a little thinner (`MIST_GAIN` 10, was 13: at 96 cells it keeps more of its body).
  Baked at 96 cells in 2,556 s (`render/v12_bake_mist_6.log`). The smoke has left the chest by about frame 200
  (5 s into the reveal). Reveal frames 40 to 240 were rendered again; the other pieces are unchanged.

### Version 12, fifth pass: the first render for the app's timing (2026-11-20, about 2:00 PM)

The owner, after the fourth pass (speech to text, shortened):
- the "twinkle" was not the torches: "at the very end, there's a light that looks like it's shining on the badge
  from the top ... that light like changes ... The fire was fine." And: "I actually want this render to be rendered
  without the badge and without the light at the top that comes at the very end ... I'm going to actually do that
  part probably in the app." This render is the one they will use "to get all the timing right".
- the light through the keyhole before the chest opens "a little bit brighter";
- the waiting rattles "more noticeable, probably like 2 times as strong ... lengthen out the animation a teeny tiny
  bit so that it still feels smooth ... the third one, maybe we can even go up to 3x";
- the sand: "it comes down and then it opacities out ... I just don't like that look. I prefer just a little bit
  of sand, very short. Just looks like it comes like almost all the way down";
- "in the beginning, the background can be about 10% brighter ... really not much";
- "the bottom half of the chest from the front is not lit well ... I want the entire front of the chest to be lit
  like the top of the chest is".

What changed:
- No badge, no beam (`v12_render.py`, on unless `BADGE=1`): every part of the badge and its own lights, the
  beam's visible shaft in the air (`Reveal Overhead Light` volume 0), its haze (`Reveal Ending Haze`) and its
  specks (`Reveal Beam Specks`) are left out. Kept: the light the beam throws on the chest, the platform and the
  floor, and the badge's push on the mist (baked in). The badge's path for the app is in
  `~/Downloads/Chest reveal badge path.csv`: per frame of the reveal clip, its centre (x from the left, y from
  the top, as shares of the picture), its width as a share of the picture's width, and its turn in degrees (0 is
  facing the viewer). It clears the chest's rim at about clip frame 84, faces front at 132 (4.4 s) and has
  settled by about 156 (5.2 s).
- Fire back at its own speed (`FIRE_SPEED` 1 in `v12_mood.py`).
- Keyhole: `KEYHOLE_GLOW` 1.7 (was 1.2) in `v12_story.py`.
- Rattles (`v12_render.py`): each lasts 30 frames (1 s; was 24) with the same shapes played a little slower, and
  is 2, 2 and 3 times as strong (`STRONG`). The lid now lifts up to 0.9, 1.5 and 0.6 degrees. The waiting loop is
  still 225 frames with a rattle every 75; the one rattle clip is still its first 75 frames.
  **For the app: a rattle is over 1.0 s into each 2.5 s beat (it was 0.8 s).**
- Sand (`v12_dust.py`): each trickle lets go within a tenth of a second and its grains fall at nearly one speed,
  so it stays a short clump all the way to the floor (the last grain lands 2.1 s after the impact); nothing
  fades in the air; the soft veil behind it is off (`DUST_VEIL` 0). Grains a little larger and lighter so that
  the short clump can be seen (the first try at this was nearly invisible).
- Start (`v12_mood.py`): dark levels and the world's dark level up 12 percent (`DARK_LIFT`).
- Chest front (`v12_mood.py`): `Temple Chest Front`, a soft warm light low in front of the chest, on the chest
  only, fading as the gold light comes (190 in the dark; 700 washed the wood pale). Measured on the waiting
  picture (0 to 255): front lower half 51 to 73, front upper half 50 to 56, lid top unchanged at about 31.
- Fifth pass rendered 2026-11-20, 2:11 to 4:10 PM (arrival 20 min, waiting 24, ending 23, reveal 49), 70 percent
  size, 24 samples, without the badge and the beam. Checked with `temple/tools/v12_check.py`: joins 0.00 to 0.07
  per pixel (0 to 255), the ending loop's seam 0.35 against 0.34 between two neighbouring frames, no jolt in the
  reveal (largest change from frame to frame 3.65 against a median of 1.37). Videos, `Chest reveal key moments.png`
  and `Chest reveal badge path.csv` are in Downloads; the fourth pass is in `Chest reveal fourth version (old)`.
