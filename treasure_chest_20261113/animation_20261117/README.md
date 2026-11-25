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

### Falling sand options (2026-11-21)

Owner: "more options, and the opacity should be like 60% of what it is now", then "I am talking about the falling
sand btw, and the more uniform same thing falling sand. Unless I say other wise i am talking about the same."
`v12_dust.py` now has `SAND_OPACITY` (0.6; each grain is that see through), `SAND_SIZES`, `SAND_WIDE` and
`SAND_DUR`. `temple/tools/look_options.py` (run before `tools/v12_render.py` with `OPT_SAND=NOW|A|B|C|D`, nothing
saved) renders the options: A opacity only; B grains all one size; C finer grains, five trickles; D one even fine
spill of about 1,900 very fine grains. Sheet: `~/Downloads/Chest sand options.png`. Waiting for the owner's pick;
the saved scene has the opacity at 0.6 and otherwise the sand of the fifth pass.
- The owner then sent a picture (a dark screenshot; with the contrast stretched it shows a soft curtain of dust
  with fine upright strands and no separate grains): "I want it more like this". **Mistake:** I put that soft
  curtain into the saved scene and started rendering the arrival again. The owner had asked for examples only:
  "no no no don't change it, only show me examples ... when did i approve that". The render was stopped before it
  wrote any video, and the scene's sand is back to the fifth pass exactly (separate grains, solid, no curtain:
  `SAND_OPACITY` 1, `DUST_VEIL` 0, `SAND_GRAINS` 1). The soft curtain exists only as an option in
  `v12_dust.py` and `temple/tools/look_options.py` (`OPT_SAND=S1..S5`, nothing saved). Examples sheet:
  `~/Downloads/Chest sand examples.png` (the owner's picture, the sand as it is, five soft examples). No pick yet.
  The arrival's frames in `render/v12_frames/arrival` were rendered again from the unchanged scene on 2026-11-21
  (the first set was deleted by the mistaken render); the videos in Downloads are the fifth pass, untouched.
- 2026-11-21, later: the owner picked the soft curtain ("go with the soft curtain but dont render it. because maybe
  we will make more changes to the scene"). The saved scene now has it (`DUST_VEIL` 1, `SAND_GRAINS` 0,
  `DUST_CLOUD` 0.012 in `v12_dust.py`); **nothing has been rendered with it**: the videos in Downloads still show
  the grains of the fifth pass, and `render/v12_frames/arrival` is empty (the next render makes it).
- The owner asked "can you add noise to the scene?". Examples only so far: `~/Downloads/Chest noise examples.png`
  (none, light 4, medium 8, strong 13 of 255, added to finished frames in a picture editor, not in Blender).
  Not in the scene; waiting for their pick and for where it should be added (in the videos or by the app).
- 2026-11-22: the owner sent a clip (frames 33 to 134 of `~/Downloads/Chest reveal first version (old)/Chest reveal
  whole scene preview.mp4`, matched exactly): "I want it to look and come down like it looks in this short clip. I
  don't want you to change the light or anything. I think the smoke should already look like this in the clip. I
  just want it to come down like that, you know, where it like comes down and then slowly disperses away, because I
  would imagine that real sand would kind of disperse ... you're going to change the scene, but you're not going to
  re-render it yet." Measured in that clip (the first version's six cards): the dust shows about 0.2 s after the
  landing at the top of the picture, comes down at about an eighth of the picture's height a second as a clump about
  a tenth of the picture tall, is strongest about 0.7 s after the landing, then thins (0.84 of its strongest at 1 s,
  0.51 at 1.67 s, 0.19 at 2.2 s) and is gone by about 2.4 s, a third of the way down; it never reaches the floor.
  The soft curtain keeps its look (colour, softness, strands, strength) and the light is untouched; only how it
  comes down changed (`v12_dust.py`): a short push out of the opening that the air soon takes out of it, then a slow
  drift (`VEIL_V0` 40 slowing to `VEIL_SPEED` 8.5 units a second), growing longer (`VEIL_STRETCH` 1.4) and wider
  (`VEIL_SPREAD` 0.35) and thinner as it spreads, breaking into finer strands, building up over 0.6 s (`VEIL_IN`) and
  thinning away from 1.4 to 2.5 s after the landing (`VEIL_FADE`). Before this it fell at 42 units a second to the
  floor without fading. Checked with the same sums mapped through the camera (a check render was not made, as the
  owner asked for no render): it covers the top third of the picture (left shaft from the top edge to about a
  quarter down, right shaft from 5 to 33 percent) and its strength over time stays within about a tenth of the
  clip's. Saved in `chest_reveal_v12_full.blend` (the state before is in the `.blend1`). **Nothing has been
  rendered with it.**

### Sound, first try (2026-11-21)

The owner asked whether sounds could be made rather than downloaded, then: "Make the sounds, find the last export
of the video and add them on top ... I'll hear what you got and then we'll take it from there ... we can work
through time, or would be better to just download." Every sound is made from scratch in code
(`sound/tools/s1_make_sounds.py`; numpy and scipy, about 4 seconds), no recordings. The script writes
`sound/s1/mix.wav`, one file per group (`stem_*.wav`; the wav files are not in Git, the script rebuilds them the
same every time) and `sound/s1/cues.json` (26 cues with their frames). The mix was laid under the last export,
`~/Downloads/Chest reveal whole scene preview.mp4` (fifth pass), as a new file
`~/Downloads/Chest reveal whole scene preview with sound.mp4`: the picture is copied, not rendered again
(its picture checksum matches the original's), and the original is untouched.

Timing was measured on that video (chest corner lands frame 45, other side 49, settles 60; lock 355; clasp 373;
lid 389 to 416) and taken from the scene's keys for the rest (torch pairs 425 + 15 each; gold 421 to 537; the cold
burst peaks 413). Sounds: hall rumble and draft throughout; air rushing past the falling chest; two heavy wood and
iron impacts and a settle; the side rings knocking; sand letting go high up and landing; three rattles (wood
knocks of the lid, the hasp, the rings) matching the rattle shapes; a faint airy tone that breathes with the
keyhole glow and flares at the click; bolt, click, clasp; the lid's creak (stick and slip through wood and hinge
resonances) and its stop; the cold light bursting out; smoke rushing out; each torch pair catching and then
burning (roar and crackle, farther pairs quieter and duller); a low open chord of D swelling with the gold light.
All of it goes through a made stone hall reverb about 3 seconds long. Loudness (0 to minus, dB): empty temple
about 49 below full, chest landing 15 (its peak 1.6), waiting 28, lock and lid 23, torches 26, ending 30.
Not judged by ear: nothing here has been listened to by me.
- Second try (`sound/tools/s2_make_sounds.py`, output `sound/s2/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 2.mp4`, picture checksum identical to the original).
  The owner: "there's a sound that I think that's just in the background. I want those sounds removed. I only want
  sounds for, like, the chest opening, falling every time it hits the floor, the smoke that comes down [the sand],
  pretty much just those ... they sound a little too cartoony ... I want like a realistic direction."
  Kept: the chest's contacts with the floor (45, 49, 60, 62.5) with the side rings knocking, the sand pouring and
  landing, the bolt, the lock, the clasp, the lid's creak and its stop. Removed: hall rumble and draft, the keyhole
  tone, the air rush of the fall, the cold burst, the smoke rising from the chest, the torches, the warm swell, and
  the rattles (not in the owner's list; asked). Realism: every hit is a short rough contact striking dozens of
  closely packed, heavily damped resonances (wood, iron, stone) instead of a few clean tones; the low end is a thump
  of noise, not a falling tone; a box landing on a corner makes two or three contacts milliseconds apart; the lid
  creak is an iron hinge sticking and slipping in bursts and shaking the lid, with no narrow singing resonance; the
  clasp lifting is a short scrape, not a sliding tone. Measured: the share of a hit's energy in its 20 strongest
  single frequencies fell from 97 to 76 percent for the lock click and from 97 to 80 for the clasp.
- Third try (`sound/tools/s3_make_sounds.py`, output `sound/s3/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 3.mp4`, picture checksum identical). The owner: sounds
  for the three idle rattles too; "the thud in the beginning doesn't sound accurate ... the second thud doesn't
  really sound like it's there"; "you went the right direction, but I want more realism".
  - Landing timed from the scene (lowest corner of each side every quarter frame): left corner at video frame 44.6
    (44 units a second), right side flat at 49.6 (23), left side back down at 60.1 (8), last settle at 61.9. In the
    second try the second thud was 5 dB too quiet and too like the first. Now: first peak 1.0 dB below full, second
    1.9 below (fuller and lower, a whole side at once), third 12.8 below.
  - Rattles: contacts found from `rattle()` as rendered (copied into the script): lid drops, edges landing as it
    rocks, the hop, a short scrape when it twists, hasp and side rings swinging back. Strength follows speed within
    a rattle; the three rattles set about equally noticeable (`KIND_DB`; the first moves slowest). Peaks about 15,
    11 and 12 dB below full.
  - Realism: the hollow box's air resonance in every knock on the chest, loose planks and straps chattering after
    hard hits, faster hits shorter and brighter, a short bright click from the stone floor, slight density
    (`tanh`), and a room built from the hall's size and surfaces (first echoes at their true delays up to three
    bounces, then the stone tail), with each sound placed where it happens and heard from the camera.
- Fourth try (`sound/tools/s4_make_sounds.py`, output `sound/s4/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 4.mp4`, picture checksum identical). The owner: "I want
  them to sound more light/light hearted without sounding fake, still very real." The third try made lighter: the
  deep thump about a third as strong and nothing below 75 Hz; wood a little higher and crisper, the hollow box
  sound higher (235 Hz) and softer; metal a touch longer and brighter, clinks 3 dB more present; the big landing
  4 dB lower against the rest; a drier hall (tail about 1.3 s, was 2.6; 6 dB less of it); a shorter, higher,
  softer lid creak; no added density. Measured: below 200 Hz the landing went from 96 to 81 percent of its sound
  and the opening from 19 to 6; the lid stop's echo falls 30 dB in 0.52 s (was 0.98). Thuds: first peak 1.0 dB
  below full, second 4.3 below (kept clearly there), third 11.6 below.
- Fifth try (`sound/tools/s5_make_sounds.py`, output `sound/s5/` with a torches stem, video
  `~/Downloads/Chest reveal whole scene preview with sound 5.mp4`, picture checksum identical). The owner: "they
  sound like this like deep metal. They really should sound like wood. Like the drops should sound like wood
  hitting wood. I don't need a creak sound for when the chest opens, just a quick unlock, you know, when the latch
  opens. And then I want to hear the fire, when the fires go on, I want to hear them turn on."
  - Wood: every knock is a wooden body made as noise in thirds of an octave, each band dying at
    tau = 1 / (pi f eta) with eta about 0.03 (wood), plus a few heavily damped low board resonances. Below about
    250 Hz a box this size barely radiates and its joints damp it, so the low end is weaker and shorter. The landing
    excites the chest and a wooden floor, led by a hard first touch for the crisp knock. Iron straps, the stone
    floor's ring and the side ring clinks after the landing are gone; the latch and rings in the rattles are light
    wooden ticks with a brief click. Measured dry against the fourth try: the landing's sound sits at about 280 Hz in
    the middle (was 166), ringing tones 3 to 15 dB weaker (now close to plain noise), 4 dB less left after 0.1 s.
  - The hall's first echoes are short scattered bursts, not single clicks (those comb filtered into a metallic,
    tube like colour).
  - Opening: only the lock click when the keyhole flashes (frame 355) and the latch flipping up with a light clack
    (frame 373). No bolt scrape, no creak, no knock when the lid stops.
  - Torches: at frames 425 + 15 per pair (when each pair's flame shows), a soft whump, a rush as the flame climbs, a
    burst of crackles, then a quiet steady burn to the end. Each torch is placed where it stands: the far pairs come
    later (up to 80 ms), quieter and more echoey.
  - Levels (mix, against full): landing peak 2.7 below in the middle of the two ears (1.0 in one), second thud 5.7,
    third 15.2; rattles about 31 loudness; lock and latch peaks 6.6; first torches peak 10.3, last 16.3; the steady
    burn about 46 loudness.
- Sixth try: the owner's own downloaded recordings (`sound/tools/s6_use_downloads.py`, output `sound/s6/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 6.mp4`, picture checksum identical). Four Pixabay files
  the owner downloaded: fire, luggage drop, door lock, footsteps on a wood floor. The owner: keep the downloads
  "pristine because we're going to work off of those"; copies are in `sound/sources/` (not in Git) with their
  checksums in `sound/sources/checksums.txt`, checked unchanged in Downloads afterwards. The script only decodes
  them; every change is made to the decoded sound in memory.
  - Drops: the luggage drop on the three landings (frames 44.6, 49.6, 60.1): full, 4 dB softer and pitched a hair
    lower, 12 dB softer with less crack and pitched a hair higher; each cut off with a short fade before the next
    lands; the handling noise before the hit left out. The fourth, tiny settle at 61.9 has no sound.
  - Lock: the door lock once, the key turn included, its clack on the keyhole's flash (frame 355).
  - Rattles: one footstep per knock found in the rattle motion (23 steps cut from the recording, never the same
    twice in a row): wood knocks as the step itself (the jolt 2 semitones lower, rocking 1 lower, the shiver's taps
    shorter and 2 higher); metal knocks (the gold latch, the side rings) as a step made 5 to 7 semitones higher,
    shorter and with its low end removed, so only a click is left. Knocks more than 20 dB under a rattle's
    strongest are left out. Each rattle's strongest knock is 8 dB under the first landing (loudness over 50 ms).
  - Fire: one sound for all torches, from 9.5 s into the recording, faded in over half a second as the first pair
    lights (frames 425 to 440), then on to the end; its deep rumble below 80 Hz (half its energy was below 64 Hz) is
    left out; about 17 dB under the first landing.
  - Everything else is gone (sand, latch, all made sounds). A light touch of the hall's echo on all four.
- Seventh try (`sound/tools/s7_use_downloads_dry.py`, output `sound/s7/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 7.mp4`, picture checksum identical, downloads checked
  unchanged). The owner: "I do not like the hall echo on any of those recordings. remove them." The sixth try with
  no echo at all; levels were set on the dry sounds, so they stand.
- Eighth try (`sound/tools/s8_lid_drawer.py`, output `sound/s8/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 8.mp4`, picture checksum identical, all five downloads
  checked unchanged). The owner asked for a sound when the chest opens, then: "I downloaded a drawer opening effect.
  try that". The seventh try plus the drawer recording (`freesound_community-drawer-41055.mp3`, copied into
  `sound/sources/`, checksum added) on the lid, dry: its slide starts on frame 393 as the lid starts to lift, is
  strongest from about 397 to 403 while the lid moves fastest, and is gone at 410 as the lid comes to rest. Its own
  length fits, so it is not stretched. Level: its loudest twentieth of a second is 9 dB under the first landing.
- Ninth try (`sound/tools/s9_higher_rattles.py`, output `sound/s9/`, video
  `~/Downloads/Chest reveal whole scene preview with sound 9.mp4`, picture checksum identical, all five downloads
  checked unchanged). The owner: "the footsteps that are used for when the chest moves, I want it to be a higher
  pitch. So show me those sounds." The eighth try with every footstep in the three rattles 5 semitones higher
  (`RATTLE_UP`; wood and metal alike, so their order from low to high stays), which also makes each knock about a
  quarter shorter, as a recording played faster would. The middle of each rattle's sound moved up by a third (rattle
  1: 548 to 721 Hz). Each rattle is exactly as loud as before (loudest twentieth of a second unchanged); its sharpest
  peak is 1 to 3 dB higher, being a shorter click. Everything else is the eighth try.
  **Turned down:** "I prefer the previous rattle. so change it back". The eighth try (`sound/s8/`, video
  `Chest reveal whole scene preview with sound 8.mp4`) is the current sound again; the ninth is kept only for
  comparison.

### The great door and two fire bowls (2026-11-22)

The owner sent a picture of the ending made from the scene itself (the same view as another agent's still,
`render/Codex_Treasure_Chamber.png`): the long hall replaced by a wall with a big arched wooden double door, and a
stone fire bowl on a block at each front pillar's foot in place of the torches. Their words: "I overall wasn't a fan
of the long hall with a bunch of fires. I think we could have collapsed it a little bit. So I want to go with this.
The main things I want you to take from this is ... above the pillars, behind them there's that like brick looking
stuff. That is going to be darkened up for sure. There's going to be a new fire source, and that fire source is
visible ... you're going to create the door and everything. Now, if other things were changed, you don't change them.
Like the pillars were changed, you don't change the pillars ... This is mainly about what's behind the pillars and
beyond. Anything from the pillars to the view doesn't change except for the fire. The fire does change."

**Which file.** The owner, while this was being built: "there's a codex file ... I don't want you touching that file.
I want you to touch the one that codex duplicated from, which should be the main file."
- `chest_reveal_v12_full.blend` is the main file and now holds the door version.
- `chest_reveal_v12_long_hall.blend` is the main file exactly as it was before this change (the long hall, with the
  soft curtain sand and its slow fall). Open it to go back.
- `Codex_Treasure_Chamber.blend` is another agent's copy: never opened or changed here (same checksum before and
  after, `72f47176...`).

**What was built** (`tools/v14_door.py`, run inside the main file; safe to run again; nothing is deleted):
- The wall stands just behind the two front pillars and the big arch between them (its face at y 62; the arch ends
  at 60.8). Coursed stone like the wall above the arch, at a sixth of its colour (`WALL_DARK` 0.16; the hall's thin
  air glows a little in front of it, so the stone has to be that dark to read clearly darker than the picture's).
- The door fills the arch: 26.4 wide and 42 tall (the chest is 5.5 wide), its round top on the big arch's centre, set
  0.9 back in the wall. Two leaves of six upright planks each, real planks with gaps, boards meeting under the strap
  hinges, each plank its own piece of the Poly Haven Rough Wood scan (the one the chest's planks came from; copied to
  `temple/resources/cache/polyhaven_rough_wood`, recorded in `temple/resources/SOURCES.json`). The scan gives light,
  dark, relief and roughness; the brown is the door's own. Ironwork: a band round the edge and down the middle, four
  strap hinges with pointed ends, two tall pull handles, 39 studs; plain dark forged iron (the torches' rusted iron
  turned orange and speckled in the firelight).
- The fire bowls: an eight sided stone bowl on a stepped square block at (15.4, 50) and its mirror, in front of each
  front pillar (they stand at 17.2, 58). 5.6 wide and 4.8 tall with the block. In the picture they are larger against
  the frame; here they are sized to the scene's slimmer pillars, which the owner said not to change.
- The fire is the first torch pair's own (flame, glow, embers, coals, light), moved into the bowls: a tall flame with a
  lower one each side (the same shader with a wider shape, `Temple Bowl Flame`), over a heap of glowing coals. It
  still follows `lit_0` on `Temple Torch Control`, so it catches at the same moment the first torches did (scene
  frame 126 on, about 14.2 s into the whole video) and the fire in the sound tries still fits.
- Switched off, kept in the file (102 objects): the small arch and its pillars, the long hall with its pillars, ribs,
  vault, end wall and far doorway, the fog behind the wall, all twelve slim torches with the other ten fires, and the
  lights of the hall (the far glow and its light on the floor, the four bay glows, the two moon shafts down the hall,
  the warm edge lights behind the front pillars, the torches' sheen lights).
- Lights. The two warm lights that glowed on the big arch and the wall above it are at 15 percent and skip the door
  (`ARCH_DIM`; they stood for six pairs of torches at half the pillars' height). New: `Temple Door Glow` (the door's
  own soft firelight, follows `lit_0`), `Temple Bowl Fill 00/06` (the floor's light back up onto each bowl). The fires
  light everything the torches lit except the moss at the pillars' feet (right beside a fire it became bright yellow
  blobs). In the dark the moonlight on the wall above the arch reaches the top of the door. The wall and door throw
  no shadow for the two cool side lights that stand behind the wall's line.

**Checked** with stills only, in the open Blender (dark wait at scene frame 49, lid opening 100, fires catching 132
and 150, 200, the ending 290); **no video was rendered**, so the videos in Downloads still show the long hall.
- In front of the pillars nothing moved: between stills from before and after, the chest and platform differ by
  0.13 (dark wait) and 0.57 (ending) of 255, the floor at the bottom by 0.00 and 0.10.
- Against the owner's picture in the ending (average colour, 0 to 255): door planks 47, 28, 13 (picture 53, 28, 12);
  the lower pillar in the firelight 104, 72, 38 (picture 166, 93, 41: theirs glows stronger).
- Sheet for the owner: `~/Downloads/Chest door scene.png` (their picture, the ending before, the ending now, the
  fires catching, the dark start).

**Not done, for the owner to decide:** the flames keep the look of the torches' fire, paler than the orange in the
picture; the big arch between the pillars is unchanged apart from its dimmer glow; the bowls could be larger; the
falling sand and the two streaks of night light are untouched and still fall in front of the door.

#### The door, second round (same day)

The owner, after the first sheet: "I want to see the ending by itself, not in a line of stuff ... by itself in the
downloads folder." And on the scene: "the brick thing that goes behind the pillars, like above the arch ... That needs
to be darkened to match the scene, to match the mock-up ... there's some depth before the door. That needs to be a
little longer. The mock-up is longer. Also, the metal and the wood are like totally off ... the door and the metal
just look cheap ... Make it look as close as possible to the inspiration. Also the flame is fine but the things
holding the flame can look a whole lot more like the inspiration."

Sizes and tones were read off the owner's picture this time (shares of the door, average colours of small patches),
and `tools/v14_door.py` was rebuilt round them. Where the description above differs, this is what the main file has:
- **Arch.** The big arch's stones and the wall above it are multiplied by 0.38, 0.18, 0.08 as the gold light comes up
  (`ARCH_END`, driven by the story's `gold`), so they end dark and warm; in the dark part of the story they are
  exactly as before (the dark wait measures 0.00 of 255 different there). The two lights that glowed on them are at
  6 percent (`ARCH_DIM`).
- **Depth.** The wall's face is right against the back of the big arch (y 60.9, no gap between the two) and the door
  sits 7.1 back in it (`DOOR_DEPTH`; it was 0.9), at the end of a round tunnel of plain dark warm stone.
- **Wood.** The chest's own plank maps (colour, roughness, relief; they are in the file already), set upright: four
  planks to a leaf, each board a different stretch of the map, some turned round, with long soft streaks added, in
  a darker, browner colour. The first try (a scan of grey weathered timber tinted brown, six narrow planks) was
  scratched and busy.
- **Iron.** Thick, with real edges: the band round the edge 1.8 wide and 0.42 proud, the middle band 2.0 wide, strap
  hinges 2.1 tall with three studs each, studs 1.16 across, pull handles a square bar between two chamfered blocks.
  One even dark tone with shallow hammer marks (two tones mixed by noise read as blotches).
- **Light on the door.** The hall's cool light from above and its pale top light skip the door (they greyed the
  wood); it is lit by the fires, `Temple Door Glow` (now with soft shadows, so the iron stands off the wood), two
  small glints for edges and studs (`Temple Door Glint L/R`) and the moon in the dark. The fires' halo in the air
  is 1.2 (the torches had 2: it veiled the door).
- **Fire bowls.** Eight sided, upright sides flaring a little to a thick rim, 6 wide, on a square block that narrows
  upward between a foot and a cap; eleven lumps of charcoal on the glowing bed. 5.2 tall in all. At (15, 50) and its
  mirror. The loose stones of the fallen roof that lay under them are hidden by a mask on the heap (14 stones;
  nothing removed). The flame is unchanged ("the flame is fine").
- **Measured against the picture** in the ending (average colour, 0 to 255; picture first): planks 49, 24, 9 and
  49, 30, 18; the middle iron band 43, 31, 22 and 52, 38, 26; arch stones 41, 30, 20 and 42, 36, 33; the bowl's
  block 53, 36, 22 and 50, 34, 18. What is left is a thin grey veil from the hall's air.
- **In front of the pillars** nothing moved: chest and platform 0.08 (dark wait) and 0.87 (ending) of 255, floor 0.00
  and 0.06.
- The scene's lens keeps everything behind the chest a little soft (it is focused on the chest); the picture is
  sharp all over. Not changed: it is part of the view.
- Picture for the owner: `~/Downloads/Chest door ending.png` (the ending by itself). Still no video rendered.

#### The door, third round (same day)

The owner, after `Chest door ending.png`: "in the tunnel thing, there's like an inner shape that you put there that
wasn't there before ... There's like another little layer. It's one tunnel ... The door does look better. The metal
does look better on the door as well ... but they can look even more like the inspiration. And same thing with the
fire. Actually, the fire overall regressed. It might look more like the inspiration, but it doesn't look good. It
needs to look a lot more like the inspiration because the inspiration had the proportions correct."

- **One tunnel.** In the second round the tunnel was a little narrower than the big arch (13.9 against 14.36), so
  a ring of wall showed between the two. Now `Temple Door Tunnel` carries the arch's own inner surface straight on
  to the door: the same radius and steps round the curve, the arch's own stone (its joints depend only on the angle
  round the arch, so they run on down the tunnel), lit by the same lights as the arch. Its two sides below the arch,
  behind the pillars, are the coursed stone of the wall above the arch. `Temple Door Wall` is only the flat dark
  face round it. The door grew with it: 28.6 wide, 43.3 tall.
- **Wood.** Clear grain lines that wander a little (a wave pattern along each plank, also as relief), each plank
  darker along its two edges, a deeper red brown.
- **Iron.** Darker, hammer marks larger and deeper. Two far lights from high on either side are seen only as glints
  in the iron (`Temple Door Glint L/R`, reflections only, on the ironwork only). A first try lit the whole door with
  them at four times the strength and washed wood and stone pale: a rough surface throws back even a "reflections
  only" light as a pale veil.
- **Fire bowls.** Every proportion is the picture's, measured on it as shares of the bowl's width (foot 0.57, sides
  flaring from 0.62 to 0.96, a rim band standing a little proud; the block's foot 0.98, body 0.94 narrowing to 0.84,
  cap 0.89; bowl and block about equally tall). Two things are allowed for, because the picture looks down into its
  bowls and this camera sees them almost from the side: the block stands nearer the camera than the bowl's middle
  and looks about a tenth wider than it is (built that much narrower), and with no view of the bowl's mouth the
  bowl's side carries its height (built a quarter taller). The bowl is 6 wide across its flat sides and 2.8 tall,
  the block 5.3 wide at its foot and 2.6 tall. What was wrong in the second round: the block was wider than the bowl
  (an eight sided bowl is narrower across its flat sides than across its corners) and lighter than it.
  The bowl and its block are separate objects now, each with its own light from the firelit floor and the middle of
  the hall, so the bowl is the lit part; a sunk panel on each of the bowl's eight sides; sixteen lumps of charcoal,
  eight heaped in the middle. The flame is the same fire, the tall one a little wider, the two low ones closer in.
- **Measured against the picture** (ending, average colour 0 to 255; picture first): planks 49, 24, 9 and 44, 23, 13;
  the middle iron band 43, 31, 22 and 47, 34, 23; arch stones 41, 30, 20 and 43, 36, 33; the bowl's side 51, 32, 16
  and 58, 38, 18; its block 53, 36, 22 and 47, 31, 15.
- **In front of the pillars** nothing moved: chest and platform 0.09 (dark wait) and 0.89 (ending) of 255, floor 0.00
  and 0.06; the arch and the wall above it in the dark wait 0.00.
- Picture for the owner: `~/Downloads/Chest door ending 2.png` (the ending by itself). Still no video rendered.

#### The door, fourth round (same day)

The owner, after `Chest door ending 2.png`: the flame is fine and its colour stays. "you need to work on the thing that
holds the fire ... the rocks ... look like they're sitting on top of a plate or something. There should be like rocks
under those rocks ... the overall shape needs work ... The shape of the bowl is different and it's also much lower to
the ground. And the position ... is actually fine. Now, what I do want you to work on is the biggest thing is
definitely the door. Like the wood is like a different color, the metal's darker, more gritty ... it's definitely
closer, definitely much closer, but it still needs a lot of work ... I also want to experiment with making ... a
super mini hallway ... longer ... so that it appears smaller ... Make that little hall ... long to the point where it
starts to match the inspiration in terms of size."

The picture was measured patch by patch this time (average colour and spread of small patches at several heights of
the door, on the planks, the bands and a strap), and the render the same way after every change.
- **Hall.** 14 deep behind the big arch (`DOOR_DEPTH`; it was 7.1). At that length the door's own parts are the
  picture's size on the screen: the two strap hinges as far apart and the handles as long, to within a hundredth.
  The door stays a tenth narrower than the picture's (it is a taller, narrower door, shaped by the scene's arch). At
  21 the door is 0.72 of its arch across, as in the picture, but an eighth smaller than the picture's door.
- **Wood.** Flowing grain cut into the surface: rings round a heart that wanders behind each board, so lines run up
  the plank and close into a long loop here and there, and come and go along it (drawn at one strength they read as
  tiger stripes). Over it the chest's own fine fibres and long soft streaks. A warm red brown, with little sheen (a
  full sheen laid a grey veil over the brown).
- **Iron.** Nearly black, beaten in shallow dents, pitted and scuffed lighter in patches; the rounded edges of every
  band, strap and handle are a second, worn, coppery metal (`Temple Door Iron Edge`, through the edge rounding's own
  material setting).
- **Light on the door.** One warm light from the upper left front, aimed at the door's middle and soft at its edge
  (`Temple Door Glow`, a spot now; only the door's own parts throw shadows in it, because a lamp could not really
  shine down the hall from the side), with a little even light straight on (`Temple Door Fill`). The fires no longer
  light the door's wood and iron: they lit its foot brightest, and in the picture the door is brightest about its
  middle.
- **Measured against the picture** (ending, average colour 0 to 255; picture first): planks beside the handles
  59, 28, 10 and 59, 26, 7; above the top straps 43, 22, 8 and 46, 20, 6; above the bottom straps 46, 23, 9 and
  48, 24, 8; the middle iron band 43, 31, 22 and 42, 29, 18. The band round the edge is lighter here on its left
  side (45, 31, 18 against 31, 22, 13), and the picture's iron has more contrast inside a strap than this one.
- **Fire bowls.** The picture looks down on its bowls, so much of what had been read as the block's height was the
  block's top seen from above. Now the block is low (1.55 high) and the bowl wide and low (6 wide, 2.25 high), sitting
  straight on the block on a wide foot, no stem, its sides flaring a little to a thick rim. It is full of charcoal to
  its rim and heaped in the middle: 29 lumps in three layers, lumps on lumps, the glowing bed deep underneath and
  seen only between them. The flame rises from the top of the heap. Position unchanged.
- **In front of the pillars:** chest and platform 0.12 (dark wait) and 1.00 (ending) of 255, floor 0.00 and 0.06, the
  arch and the wall above it in the dark wait 0.00.
- Picture for the owner: `~/Downloads/Chest door ending 3.png` (the ending by itself). Still no video rendered.
- The owner asked why the Mac was slow while this ran: the check stills. The open scene needs nearly all of the
  Mac's 8 GB while it renders (swap was at 6.0 of 7.2 GB). Say when stills are rendering.

### The current sounds on a Blender file's timeline (2026-11-23)

The owner: "add the sounds we have been working with to Codex_Temple_Fire.blend, sounds only". That file is Codex's
(see the rule below); the owner named it and the change, so this once it was opened and saved, with sound and nothing
else.

- **Why it needed fitting.** The sounds were never inside a Blender file: they are timed to the frames of the whole
  scene preview video and laid under it. A Blender file's timeline is the story played straight through, without the
  wait. Video frame to scene frame: arrival, video frame minus 28 (frames 0 to 77); the wait, video frames 124 to
  348, is not on the timeline (the chest is held on scene frame 49 by `tools/v12_render.py`); reveal and ending,
  video frame minus 299 (from 349 on).
- **`sound/tools/s8_for_blender.py`** cuts the eighth try's stems into five pieces on whole frames, with the mix's low
  cut and ceiling, into `sound/blend/` (24 bit; `strips.json` holds where each goes). Laid back on the video's
  frames the pieces add up to `sound/s8/mix.wav` (largest difference 3.4 sixteen bit steps, the two files' own
  noise; nothing in the mix is left uncovered).
- **`sound/tools/add_sound_to_blend.py`** (run inside Blender with the file open; safe to run again) adds one sound
  strip per piece to the Chest Reveal scene and packs each into the file:
  - Chest lands (three drops), from scene frame 16 (the drops at 16.6, 21.6 and 32.1);
  - Lock, from 49 (the key turns from 50.3, the clack on the keyhole flash at 56);
  - Lid opens (drawer), from 92 (the slide from 94 to 111);
  - Fire, from 126 as the fire catches, on to frame 561 (past the ending loop);
  - Waiting rattles (footsteps), the whole 225 frame wait, **muted** and parked from frame 50: there is no rattling
    on the scene's timeline for it to go with. It is there for whoever builds the waiting piece.
- **Checked.** Blender's own mixdown of the saved file's timeline (frames 0 to 290) against the pieces laid on those
  frames: identical (difference 0, timing offset 0 samples), the muted rattles silent. In Codex's file the lock
  flash (56) and the fire (126 to 140, the same control as the torches) are on the same frames as in the main
  file. A sound strip does not change a render even with the sequencer switch on (tested in an empty Blender 5.2.2
  scene: the same picture with and without one). The scene itself was not rendered.
- **Sounds only.** By name, everything in the saved file is what was in the original, plus the five sounds, with one
  difference: Blender leaves out unused data when it saves, and two unused pictures left from an earlier version of
  Codex's fire ("Brazier | East fuel and heat", "Brazier | West fuel and heat"; no material used them) went that
  way. The frame (290), the render settings and the playback range are as they were. The original is next to it
  as `Codex_Temple_Fire.blend1` (Blender's own backup, sha256 `ce9812c761b8b7e3...`); the saved file is
  `2db7f9bb6109a1ba...`, 4.6 MB bigger.
- **The rule stands:** Codex's other files were not opened. A Codex file is touched only when the owner names the
  file and the change.

### One command to render a file's four clips with the sound (2026-11-23)

The owner, after the sounds went into Codex's file: "how do I start the render and also make sure it goes to
downloads?"

- **`temple/tools/render_clips.sh`**: `zsh temple/tools/render_clips.sh` starts it and comes back at once (the
  render carries on by itself and keeps the Mac awake); `... status` says how far it is; `... stop` stops it, and
  starting again carries on from the frames that exist. It renders the four pieces with `tools/v12_render.py` from
  `FILE` (default `Codex_Temple_Fire.blend`, opened read only in background Blender, never saved), joins them as the
  whole scene (arrival, the wait, the reveal, the ending loop three times, 860 frames) and lays the eighth try's
  mix under it. One file comes out: `~/Downloads/<NAME> whole scene with sound.mp4` (default NAME: the file's name
  with spaces; a video already there is never written over, the new one gets a number). `PIECES=1` also writes the
  four pieces. Frames are kept in `render/<file>_frames/` with a note of the file they came from: after the Blender
  file has changed a plain start refuses, and `... fresh` throws the kept frames away and renders from the start.
- Tested without starting the real run (the owner starts it): three frames from Codex's file with the clip renderer
  (arrival 3, waiting 5, ending 0; 8 to 42 seconds each at 70 percent and 24 samples, kept so the run skips them);
  the ending frame against Codex's own still of frame 290: average difference 1.07 of 255. Start and stop were
  tried with a stand in that only waits; every refusal with a dry run (`DRY=1`).
- It refuses to start while the Blender app is open: the scene needs nearly all of the Mac's 8 GB.
- Why not Blender's own Render Animation: the file's timeline is the story played straight through, so that gives
  no wait and no rattles, 291 separate pictures at full size (the file is set to PNG), and no sound.

### A wider hall: the ceiling 50 percent wider, thinner ribs, no arches on the pillars (2026-11-23)

The owner, on a frame of the Codex Temple Fire video (the reveal's frame 75, scene frame 125): the ceiling "should
be about overall 50% wider. So the building is 50% wider"; its holes of light "Don't change that at all"; the ribs
follow, and "the ends of those aren't going to be in view"; the ribs "half their height. Not width"; "on top of the
pillar there are these arches. You're gonna remove the arches"; "Don't change anything I didn't talk about"; and
"duplicate the latest codex one. So that one stays untouched."

- **File: `Claude_Temple_Wide.blend`**, a copy of `Codex_Temple_Fire.blend` (which is untouched: same checksum
  before and after, `2db7f9bb...`). Going back is opening the Codex file again. In the copy, the meshes that were
  replaced are also kept, named with " (before v15)".
- **`tools/v15_wide_vault.py`** (run inside the copy; safe to run again; nothing is deleted):
  - The ceiling was half a circle 15 from the middle; now half an ellipse 22.5 from the middle, as high as before.
    The two openings are cut with the same two plugs, so they sit at the same place over the floor with the same
    outline; the shafts, their plates and the night sky are not touched. On the wider curve the ceiling is higher
    above them, so in the picture the openings sit a little higher.
  - The four ribs follow the wider curve and stand 0.7 out of the ceiling (1.4 before), as wide along the hall as
    before. Their feet are 21.8 from the middle; the picture is never wider than 20.6 there, in any frame.
  - `Temple Arcade Arches` is switched off, and the slab that stood on the arches is taken out of
    `Temple Aisle Walls` (it would stand inside the wider ceiling). The flat ceilings over the side aisles start at
    22.5 (19.4 before): left there, their edges were a dark wedge in both top corners of the picture.
  - Stone patterns: the ceiling's courses and the ribs' stones were laid out by the angle round the circle. Both
    meshes now carry "arc" (the distance round the curve) and the two materials read that, so the stones keep
    their size (courses 2.3; rib stones 1.66 long, 35 where there were 27).
  - `Temple Wide Light Blockers` (new, never seen by the camera): the ceiling throws no shadows, so the slab and
    the aisle ceilings were the hall's roof against the world's light, which does cast shadows. Without them the
    front floor came out 5 to 7 of 255 brighter. The blockers lie on the back of the new ceiling and stand where
    the slab's top was, so they keep that light out without shading the ceiling from the lights in the hall.
- **Checked** on the same frame with the clip renderer (70 percent, 24 samples) against the kept frame of the
  Codex render, average difference of 255: chest 0.05, floor 0.01, platform 0.02, pillar shafts 0.01 and 0.08,
  door 0.16. The opening (arrival 20) and the ending (ending 0) were looked at too: lower half 0.18 and 0.02.
- For the owner: `~/Downloads/Chest wide ceiling.png` (the frame) and `Chest wide ceiling before and after.png`.
  No video was rendered. For one: `FILE=Claude_Temple_Wide.blend zsh temple/tools/render_clips.sh`.

### The ceiling blended into the walls, with the arches kept (2026-11-23)

After seeing the wider hall the owner turned around: "I actually do like the things above the pillars ... I want
them to remain"; the ribs should "still ... shrink a bit to how you did before"; and "I want a way to blend the top
with the bottom ... I see like a brick just kind of like floating in the air ... I want it to all blend seamlessly
... give me some ideas for how to blend it." They picked in two steps: "I like C", then "Let's try C and a darker
cieling stone and no shine on the arch's edge".

- **File: `Claude_Temple_Ceiling.blend`**, a fresh copy of `Codex_Temple_Fire.blend` (untouched, checksum
  `2db7f9bb...`), so the ceiling has its original width and the arches stand. `Claude_Temple_Wide.blend` keeps the
  wider hall as it was.
- **What looking showed** (`temple/tools/blend_options.py`: pictures only, run before the clip renderer, saves
  nothing; ideas A to F and the second round's settings are described in it):
  - The pale patch at the foot of the ceiling was the stone's shine seen at a flat angle, mirroring the room's
    soft overall light. Darker stone alone left it; with the shine or the world light off it went.
  - The "floating brick" was a rib that stopped at the top of the wall with a flat underside and nothing under it.
  - The line that was left ("this line caused from it going from light to dark") is the front face of the arch on
    the pillars, seen from the side as a thin sliver under the ceiling, with the same shine. Chest closed: the
    arch's underside 25 of 255, the sliver 47, the ceiling beside it 41. The small bright dots sat on it too.
  - Darker ceiling stone moves the ceiling by 1 of 255 with the chest closed (up there the dark picture is haze and
    shine, not the stone's colour) and by up to 8 with it open; it does not touch that line.
- **`tools/v16_ceiling_blend.py`** (run inside the copy; safe to run again; nothing is deleted; every material node
  it adds is named "v16 ...", and the ribs' old mesh is kept as "Temple Vault Ribs (before v16)"):
  - The ribs stand 0.7 out of the ceiling (1.4 before), as wide as before, and sink into the ceiling over the
    lowest 24 degrees of the curve, so they have no foot.
  - `Temple Vault Masonry` and `Temple Vault Rib Stone`: no shine at the foot, back in full 12 above it; colour
    times 0.5.
  - `Temple Stone Wall` (the arches) and `Temple Stone Dark` (the wall on them): no shine on the faces that look
    across the hall. Everything else about those two stones is as it was.
- **Checked** from the saved file with the clip renderer (70 percent, 24 samples) against the kept frames of the
  Codex render, average difference of 255: chest closed (waiting 36), chest open (reveal 75) and the opening
  (arrival 20): chest, floor, platform, pillar shafts and door all 0.03 or less, the door's arch 0.10. The ending
  (ending 0): chest 0.04, door 0.02, pillars 0.11, and the floor 0.6 darker (1.0 at the very front). That is the
  darker ceiling mirrored faintly in the floor: with the stone's colour left alone the floor is unchanged (0.01).
- With the stone darker the ribs are quiet in the top corners, most of all with the chest open.
- For the owner: `~/Downloads/Chest ceiling blended before and after.png`; the ideas were shown on
  `Chest ceiling blend ideas.png` and `Chest ceiling line ideas.png`. No video was rendered. For one, with Blender
  closed: `FILE=Claude_Temple_Ceiling.blend zsh temple/tools/render_clips.sh`.

### The shafts of night light hold steady: no sudden change at second 2 (2026-11-23)

The owner, on the whole scene video of the Codex file: "the light on the left shifts, like very sudden very sharp
shifts ... between the 2 and 3 second mark ... find out and if so fix it. I still want the light and the sand. just
no sudden light change".

- **What it was.** At second 2.00 exactly (video frame 60, scene frame 32, the chest's third impact) the right side
  of the left shaft goes from a soft edge to a wider beam with a hard edge in one frame (a strip about 70 pixels wide
  gets 5 to 11 of 255 brighter) and stays so. It is the only such jump in the 860 frames (every frame was compared
  with the one before). The copy had it too: same two frames, same numbers.
- **Why.** Nothing in the scene switches there. Each shaft's shape is the shadow of a mask (`Temple Shaft Mask L`,
  `R`) in the light of a spot 270 above it. The renderer keeps shadows at several levels of detail and lights the
  air with the finest level that happens to be in memory, and that depends on what the camera sees. With the
  chest's body in view at rest the shaft got a finer level; with the chest in the air, hidden or not yet in the
  picture, the coarsest. Found by rendering frames 59 and 60 again and again with one thing changed: not the dust's
  clock, the landing dust, the grit, motion blur, the other lights' shadows, the shadow memory, the surfaces the
  shafts may light, or any single part of the chest; the jump goes when the left shaft's light is off, when the
  chest's meshes are hidden, and when they are unseen by the camera.
- **`tools/v17_steady_beams.py`** (run inside `Claude_Temple_Ceiling.blend`; two numbers): Resolution Limit of
  `Temple Shaft L` and `Temple Shaft R` 10 (was 0.001), so they always use the coarsest level. Limits 1.2, 2 and 3
  still jump; 5, 10 and 40 do not and give the same picture.
- **Checked** from the saved file (70 percent, 24 samples): frame 59 to 60 changes 0.49 of 255 in the top left
  (2.21 before; the frames around it 0.38 and 0.54, which is the dust arriving); frames 20, 44, 50 and 123 of the
  arrival are the same there to 0.1; the arrival's last frame and the wait's first are the same. Against the copy
  before the fix: chest 0.10 or less, floor, platform and door 0.01 or less in the closed and open frames; the
  shafts themselves 2.5 (left) and 1.5 (right) on average: the left one is a little wider on its left side and
  more even inside, and keeps its hard right edge. In the ending the floor is again as in the Codex render (0.00;
  it was 0.6 darker after the ceiling change): the shafts now put about that much more light on the stone.
- For the owner: `~/Downloads/Chest light jump before and after.png`. No video was rendered.

### The front planks sit tight together, and what the white specks are (2026-11-24)

The owner, on the reveal in the new video (`Claude Temple Ceiling whole scene with sound.mp4`): "I am seeing these
white specks at the bottom, find out why they are happening. Also I notice that the wood planks have some tiny gaps
between them, bring the wood planks closer so that no gaps exist, adjust anything else you need to adjust".

**Status: both changes are in `Claude_Temple_Ceiling.blend`, saved 2026-11-24 19:49** (`tools/v18_tight_planks.py`
and `tools/v19_no_sparkle.py`). Blender's window was in use by another chat, so the owner was asked and picked:
save without a window, and of the three speck choices the first (the sparkle under the chest goes, the grit stays).
`Claude_Temple_Ceiling.blend1` is the file as it was before (the one the video of 2026-11-24 was rendered from).
No new video has been rendered; the kept pictures in `render/Claude_Temple_Ceiling_frames` are from before, so the
next whole scene render needs `fresh`.

- **The planks.** The chest's front is three flat sheets (`R Simple Front Plank01`, `02`, `03`) shaped by their
  material. The material they are rendered with is the one set on the object, `Chest tone | Simple wood plank0x`;
  the untoned `Simple wood plank0x` on the mesh is not rendered (editing it changes nothing: that cost a round of
  tests). Along each long edge the material rounded the edge off and pulled it in, on top of a notch that the lower
  planks' height pictures have along their upper edge, and painted the groove nearly black. At video size that is a
  black line one to two pixels wide with a dotted blue white glint on the lower plank's notched edge.
- **`tools/v18_tight_planks.py`** (run inside `Claude_Temple_Ceiling.blend`; nodes named "v18 ...", old numbers kept
  on the material, `V18_UNDO=1` puts it back): at each long edge the surface runs to a level both neighbours share
  (0.62 in height picture units, the lower plank's own level), back on the plank's own shape 0.02 away; against the
  iron rims the wood keeps its own level; the painted line becomes a hairline (0.5 of the colour, 0.006 wide) and
  the shading toward the edge lighter (0.86 over 0.04). The planks still overlap like boards on a wall (that is in
  their pictures). Lid, sides and back are single sheets with their joints painted in; not touched.
- **Checked** (70 percent, 24 samples, nothing saved): against the video's own frames the change stays inside the
  plank area in the reveal (frames 0, 60, 75, 100, 160, 240), the arrival (60, 123) and the ending (0); about 2000
  to 5000 pixels each, nothing elsewhere. The glint is gone at 16 times zoom.
- **The specks are three different things** (reveal frame 60 is the owner's picture):
  1. *Sparkle under the chest, reveal frames 42 to 63 (video seconds 13.0 to 13.7).* The gold ring inlaid in the
     platform (`Temple Dais Gold Rings`), its stretch behind the chest, seen through the gap under the chest, less
     than a pixel thick. `Temple Chest Burst` (the light that bursts out as the lid opens) reaches it only over the
     top of the chest's back wall, at the edge of that wall's shadow, so in each frame a few points of the shiny
     metal catch it and they change from frame to frame. Not light leaking through the chest (a solid test box
     inside its walls changed nothing), not the sparks.
  2. *Still dots on the platform left and right.* The grit the feet kick up on landings 1, 2 and 4: particle
     systems `Reveal Dust Grit Boot ...` (274 grains, size 0.008, lifetime 400 frames, so they lie there to the end).
  3. *Faint dots on the platform's front edge.* Pale chips in the stone's own pattern (`Temple Dais Stone`).
- **Fixes tested for 1.** Taking the ring out of the burst light's receivers removes the sparkle but also makes a
  strip of the right pillar and bits of the floor 2 to 4 of 255 darker late in the reveal (the scene's light groups
  get reshuffled): rejected. Making that stretch dull (not metal) made it sparkle more. Clean: in `Temple Gold
  Inlay`, behind the chest only (within 2.2 to 2.5 of the middle across, beyond 1.7 to 2.0 deep, in the chest's own
  directions), base colour and Specular Tint go to black, with Metallic and Roughness left as plain numbers; then
  frames 44 to 62 change only on that line and frames 75 to 240 not at all. The faint gold line under the chest
  goes with it.
- **`tools/v19_no_sparkle.py`** is that clean fix (nodes named "v19 ...", no number of the material changed,
  `V19_UNDO=1` takes it out). One thing the first tests missed: before the chest lands, that stretch of the ring is
  in plain view (the temple stands empty for a second), and always dark it would have left a hole in the ring. So
  the stretch is dark only once the chest stands in front of it: a number on the material, "v19 chest is down",
  is keyed 0 at scene frame 34 and 1 at 46 (the chest is flat at 32; the line fades under the landing dust). The
  arrival's held frames, the waiting and the reveal all sit at scene frame 49 or later.
- **Saved without a window and checked** (2026-11-24). A list of everything in the file a render depends on
  (objects, meshes, materials, node groups, lights, collections, actions, caches, scenes) was taken before the two
  scripts, after them, and again from the saved file: the three plank materials and `Temple Gold Inlay` changed,
  one action was added ("v19 chest is down"), nothing else. Pictures rendered from the saved file with
  `tools/v12_render.py` (70 percent, 24 samples): arrival 0 (the empty temple) is the video's own picture, pixel
  for pixel within 1 of 255; arrival 0 to 62 change nowhere outside the planks; from arrival 66 on, the waiting
  and reveal 0 to 62 only the planks and the line under the chest change; reveal 75 to 240 and the ending only the
  planks. In the gap under the chest the brightest pixel in reveal 44 to 62 went from 160 to 238 (of 255) down to
  19 to 40, on a background of about 8.
- **Test method.** `ONLY=60` alone and `ONLY=0,60` differ on the moving hasp (its blur follows the frame rendered
  before); compare like with like.
- For the owner: `~/Downloads/Chest planks before and after.png`, `~/Downloads/Chest white specks explained.png`,
  and from the saved file `~/Downloads/Chest planks and specks now.png`.
