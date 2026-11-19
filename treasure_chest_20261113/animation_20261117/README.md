# Treasure chest badge reveal animation

**Current: `chest_reveal_v7.blend`** (2026-11-18; landing dust in `chest_reveal_v7_dust.blend`, ending light in `chest_reveal_v7_ending.blend`, see Version 7). Version 6: `chest_reveal_v6.blend`, scene **Chest Reveal**: 30 fps, frames 1 to 213
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
