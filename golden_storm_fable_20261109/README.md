# Golden Storm (cloud and lightning bolt), rebuilt November 9, 2026

A preview entry only: **Ornate Golden Storm** in Badge Studio Preview. Production app files are untouched.
The model that was in that entry before is saved as `runtime_backup/golden_storm_before_fable.usdz`.
**Candidate 25 is the one in the simulator.** The Blender file is `golden_storm.blend`, scene **Golden Storm**.

## How it is built

The method the approved badges use, applied to this mockup:

* **Gold is real metal geometry.** The frame, the four points, the cloud outlines and spirals and the bolt's rim are
  solid pieces with flat tops and soft rounded shoulders. Their highlights come only from the app's studio light.
* **Enamel carries the owner's picture.** The blue field and ribbons, the pearl clouds and the bolt's yellow face are
  solid pieces at their own heights. Their colors are the mockup's own pixels, worked backwards through the app's
  color processing, on a surface that reflects nothing. Measured in the app, the blues and the pearl match the plan.
* **Thin gold lines stay painted.** A line under about 9 px wide in the mockup (3 phone pixels) is part of the enamel
  picture, whole, from end to end. Mixing a real piece with a painted remainder is what made ragged tips.
* **Every piece is a closed solid** with a mirrored back and side walls, stacked by height: blue lowest, clouds above,
  gold above what it borders, and the bolt tilted so it tucks under the upper cloud and crosses over the lower one.
* **Six pieces, seven meshes.** Gold body, blue enamel, pearl clouds, bolt face, bolt rim and gold frame. Each is one
  mesh, except the gold frame: its side walls use a darker gold, so they are a second mesh. Four materials, two
  pictures.

## The finish loop (owner's rules, November 9, 2026)

1. **Blender first.** Before a version goes anywhere near the simulator, sweep it inside the open Blender: close
   screenshots of every part of the badge (about ten times the phone's zoom), both angles, the back, and the whole
   badge at the phone's own size enlarged 4x. Fix and sweep again until it is clean. A sweep takes half a minute.
2. **Then the simulator.** Several screenshots, zoomed in, fix, repeat until no jagged edge is left.

```sh
$PY blender_zoom.py candidateNN          # the Blender sweep: sheets in candidateNN/blender_zoom/
$PY zoom.py candidateNN        # the front in three bands at 5x, each turning pose at 4x
$PY spots.py candidateNN       # twelve named trouble spots at 8x
$PY specks.py candidateNN      # counts single dark pixels in every pose
$PY light_centers.py candidateNN Pearl    # where the app's lights reflect straight into the camera (must be 0 on enamel)
$PY holes.py candidateNN       # every piece's triangles must cover its shape
```

Judge at the real screen pixels too: a 4x picture shown smaller can invent stripes that are not there.

## What made edges rough, and the fix (keep for other badges)

1. **Stair stepped outlines.** The shapes came from pixel masks. Fix: each outline is traced as a curve, smoothed along
   its length with real corners kept (`smooth_shape` in `build.py`), then measured at 3x.
2. **Painted shadows and glints traced as gold.** A dark painted shadow beside a line, or a bluish white glint on a
   ribbon, widened the gold into lumps and barbs. Fix: dark, not warm pixels are enamel (`segment.py`); only warm
   white glints inside gold count as gold.
3. **Bevels thinner than a phone pixel** broke into dots along curves. Fix: a soft shoulder about two phone pixels wide
   whose shading eases from 32 degrees to flat.
4. **Scattered mesh points on straight edges** gave the bolt's rim a saw tooth. Fix: the rim is even strips that run
   along the bolt's edges.
5. **Slits.** Triangles dropped beside curved edges showed the piece behind as whiskers. Fix: the keep test in `mesh`.
6. **Blotchy points.** Shading taken from the outline's direction went wild where a point runs into the frame. Fix: each
   point is two flat facets leaning away from one straight ridge line.
7. **Dead pixels on the pearl.** The app draws a dark pixel exactly where one of its eight lights reflects straight
   into the camera (the surface direction equals the half way direction between light and camera). Predicted and
   observed positions matched to the pixel (519, 679 against 520, 679). The app already patches fully black pixels
   (`coinPixel` in its image shader); a partly dark one slips through. Fix on the model: the enamel only glows, so
   its shading direction is free, and it gets one fixed direction at least 10 degrees away from every light
   (`ENAMEL_NORMAL`). On gold this cannot be done: one faint dark pixel remains in a highlight on the right of the
   frame (screen 763, 541). Removing that one is an app change.
8. **Removing painted gold too eagerly** left rows of dots and erased the ribbons' dividers. Fix: only bits up to 22 px
   that sit right beside a real gold piece are removed; the mockup's own thin lines stay whole.

Found by the Blender sweep (candidates 17 to 24), none of which the simulator pictures had shown clearly:

9. **Small bumps kept as corners.** The corner test looked 3 px each way, so every bump counted as a corner and
   survived the smoothing. Fix: a corner is a lasting change of direction, measured 12 px before and after.
10. **Saw tooth shoulders on narrow gold.** Shoulder points placed on their own did not line up with the outline's
    points. Fix: every outline point gets its own two shoulder points straight behind it.
11. **Blunt line ends.** A gold line that stops on the enamel ended in a round stub. Fix: its last 28 px are pared to a
    point and sink level with the enamel, where the mockup's painted line carries on.
12. **A painted band beside the real bolt rim** came out streaky. Fix: the whole rim is real gold, a flat outer band
    plus one wide inner bevel. A first try with a narrow step between two flat bands was clean in the big Blender
    zooms and broke into a dotted line in the simulator: the step was thinner than two phone pixels. The sweep's
    phone size picture is there to catch that kind of detail.
13. **Pale fringe beside gold lines.** Smoothing the hidden part of the picture let the pearl's color leak across a
    gold line into the blue. Fix: hidden pixels take the nearest enamel color on their own side.
14. **The bolt's rim poked through the cloud** as a tiny tab where the bolt passes under it. Fix: the bolt drops
    lower under the cloud.

## What was learned about color (candidates 01 to 09)

1. **Yellow.** The app turns a normal color picture into its wider working colors, which makes a pure yellow pale
   (blue rose from 0.01 to 0.20 on candidate02). Handing the bolt's picture over as raw numbers (`sourceColorSpace
   raw`) fixed it. Bright yellows still wash pale in the app's processing, so the bolt uses a slightly deeper, fully
   colored yellow.
2. **Gold color.** The app's light is bright, so a light gold base shows as pale champagne. A deeper, more orange base
   with no blue in it shows as rich gold.
3. **White patch on the frame.** The app has two low lights right in front of the badge's lower left. A flat frame top
   mirrors them as a white patch with a halo, so the frame's top leans 12 degrees outward.

## Candidates

| Candidate | What changed | Result in the app |
|---|---|---|
| 01 to 08 | First build through color and frame trials | See each folder |
| 09 | Frame top leans outward | Shown to the owner: "much better", with rough edges |
| 10 | Outlines as smooth curves, soft shoulders, straight bolt rim | Smooth gold, a few barbs and a nub left |
| 11, 12 | Nub at the lower right and ribbon barbs removed | Clean lines, dark specks on the pearl |
| 13 | Clean two facet points, smooth side walls | Specks still there |
| 14 | Pearl domes smoothed | Specks moved: they follow the lighting |
| 15 | Enamel shading pointed away from every light | Pearl specks gone |
| 16 | Ribbon dividers kept painted, whole | Clean |
| 17 | Needle under the crown kept painted | Clean in the simulator pictures; the Blender sweep then found rough spots |
| 18, 19 | Even shoulder rows, real corner test, tapered and sunk line ends, bolt tucked under the cloud | Blender only |
| 20, 21 | Clean fill beside gold | Blender only: bolt's painted inner band streaky |
| 22, 23 | Bolt rim all real gold, two flat bands | Clean in Blender. Simulator: dotted line on the narrow step |
| 24 | Bolt rim as a flat band plus one wide bevel | Clean in the Blender sweep, 0 dark pixels in 6 poses |
| 25 | Each piece's side walls joined to its faces: 12 meshes become 7 | **In the simulator.** Every triangle identical to 24; all nine simulator poses match 24 within 1 step of 255 |

Each folder holds `model.usdz`, the simulator captures in `app/`, `side_by_side.png`, `all_sides.png` and the zoom
pictures. `candidate24/before_after.png` puts candidate 17 next to candidate 24, and `candidate24/blender_zoom/`
holds its Blender sweep.

## Rebuild

```sh
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
$PY segment.py                      # trace the mockup's outline, pearl and blue
$PY build.py candidateNN            # pieces and their shapes
$PY holes.py candidateNN            # every piece must be fully covered
$PY textures.py candidateNN 0.3     # enamel pictures for the app
/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 pack.py candidateNN
echo candidateNN > candidate.txt
$PY ../ruby_heart_claude_20261107/tools/blender_link.py code blender_load.py     # into the open Blender
$PY blender_zoom.py candidateNN     # look at every sheet; only a clean sweep goes on to the simulator
$PY ../skills/badge-build/scripts/app_try.py candidateNN Badge3DPreviewGoldenStorm goldenStorm
$PY side_by_side.py candidateNN; $PY contact.py candidateNN; $PY zoom.py candidateNN; $PY spots.py candidateNN
```

Check that a rebuild really ran before trusting a recheck: once a broken edit made `build.py` fail quietly and the
old shapes stayed in place.

## Guidelines set aside

* Triangles: 63,572 against the usual 35,000 to 45,000. The file is 2.24 MB. The count keeps the mirrored back, full
  side walls and smooth gold edges.
* The badge skills were not used for this build, as the owner said.
