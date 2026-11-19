---
name: shader-aov-diagnostics
description: Optional technique. Export the exact values a Blender material feeds its shader (base color, roughness, metallic, masks, height, normals) as temporary Shader AOV passes, verify each one, and read them beside the beauty render to tell whether a problem is the material data, the geometry or the lighting. Includes a tested background script that never changes the production material. Use when a material input might be wrong, flat, empty or clipped, when a highlight or patch has an unknown cause, when an image might not reach the surface through the expected UV map, or when asked for AOVs or diagnostic render passes. Blender side only. The app's look still needs the app test.
---

# Shader AOV diagnostics

An option, not a rule. Use it when you need numbers instead of guesses about what actually reaches the shader. The owner's word and the workspace `AGENTS.md` (Claude sees it as `CLAUDE.md`) always win. Paths below are relative to `skills/shader-aov-diagnostics/`; `Blender` is `/Applications/Blender.app/Contents/MacOS/Blender`.

## What it found on the chest

* A pigment mask read all zero. The script that built it had read a 16 bit scan through an 8 bit path, so the image was flat before Blender loaded it. Reading at 16 bit restored the brown and charcoal mottling; the other 14 passes stayed identical.
* A sharp break in an edge highlight had no matching break in the wear, roughness or normal passes. That pointed at the light, and the cause was a tilted area light (see `fair-lighting-checks`).

## Steps

1. Run on a saved file in background Blender, never in the owner's live scene. The script changes the scene only in memory and never saves. If the live scene has unsaved changes, first check `[i.name for i in bpy.data.images if i.is_dirty]` (images made or edited live are lost unless saved or packed), then save a copy through the Blender connection: `bpy.ops.wm.save_as_mainfile(filepath=COPY, copy=True)`.
2. List the material: one line per node with every link and every changed constant, plus the object's material slots, UV maps, and each image's size, bit depth, float buffer, color space and source.
   `Blender -b scene.blend --python-exit-code 1 -P scripts/run_aovs.py -- config.json --list`
3. Write `config.json` with only the signals in question. Each one is a real socket; never invent a composite field the material does not contain.
4. Run without `--list`. It copies the mesh and material (production untouched), adds one AOV per signal plus a surface scope pass, renders the beauty and raw 32 bit EXR passes, then writes previews, `sheet.png`, `summary.md`, `statistics.json` and `verification.json`. A failure exits 1.
5. Read `summary.md` first; it is cheap. The verdicts:
   * **varies**: the signal carries data.
   * **constant input, expected**: an unlinked socket; the pass holds its value.
   * **FLAT FROM A LINKED SIGNAL**: a texture or mask that should vary does not. Expected for a Value or RGB node or one flat face; otherwise check bit depth, color space, mapping, the UV map, the node chain, and the script that wrote the image.
   * **path verified, the zero is real**: a zero pass proven by a small full resolution control render that feeds the AOV a 1.
   * **PATH BROKEN or no surface in crop**: the AOV never reached the file, or the control crop missed the object.
6. Open `sheet.png` beside the beauty render and the reference crop. Only then decide.
7. Fix that one cause, run again into a new `out` folder, and confirm only the intended passes changed (compare the two `statistics.json` files).
8. Report which passes were verified, what they showed, and what changed in the render.

## Config

```json
{
  "object": "Lab Chest Lower Rim",
  "material": "optional, default first slot",
  "out": "/absolute/output/folder",
  "resolution": [1600, 800],
  "samples": 32,
  "border": [0.23, 0.81, 0.20, 0.68],
  "signals": [
    {"name": "Rough", "kind": "VALUE", "node": "Principled BSDF", "socket": "Roughness"},
    {"name": "Color", "kind": "COLOR", "node": "Principled BSDF", "socket": "Base Color"},
    {"name": "Pigment", "kind": "VALUE", "node": "Character pigment.png", "output": "Color"},
    {"name": "ShadingNormal", "kind": "COLOR", "node": "Principled BSDF", "socket": "Normal"},
    {"name": "TrueNormal", "kind": "COLOR", "geometry": "True Normal"}
  ]
}
```

`socket` reads an input (its link, or its constant when unlinked). `output` reads a node output. `geometry` reads the Geometry node. Optional `scene` and `camera` pick a scene and camera by name.

## Notes

* AOVs are written per material, so other objects read zero. The scope pass limits statistics to the target object and needs at least 100 fully covered pixels; frame closer if it says fewer.
* A linked Normal input is what the shader shades with; True Normal is the bare flat faces. An unlinked Normal input stores (0, 0, 0), so the script reads the smooth shading normal it really uses and says so.
* A `VALUE` signal read from a color output becomes one gray value (noted in `summary.md`); use `COLOR` to see the channels. An unlinked constant keeps its own kind automatically.
* Pass names get an `AOV_` prefix inside Blender, so a signal called Depth, Image or Normal never collides with Blender's own passes.
* Diagnostics attach to the scene's first enabled view layer, and only that layer renders.
* Previews stretch values outside 0 to 1 and show normals as `normal * 0.5 + 0.5`; the EXR files keep the raw numbers. `sheet.png` has no labels; `summary.md` gives the order.
* `scripts/aov_tools.py` is the reusable core from the chest work (`attach`, `configure_files`, `read_outputs`, `statistics`).

## Never

* Save AOV nodes or passes into a production material.
* Change a parameter only because a pass looks unusual. The beauty render decides.
* Add passes just in case.

## Badges

Coins carry two UV sets, and editing through the wrong one changes nothing (`AGENTS.md` section 2, rule 2). `--list` shows the UV Map node feeding each image and which map renders (the one unlinked images use); an image's Color output as a signal shows how it lands. That is the map Blender samples. Then confirm the USDZ reads the same set: `usdcat model.usdz | grep varname`. The app test still decides the final look.
