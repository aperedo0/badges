---
name: free-asset-sources
description: Optional technique. Find, preview, download and cache free CC0 PBR textures, scanned height, roughness and normal maps, and studio HDRIs (Poly Haven, ambientCG, cgbookcase, TextureCan, 3dtextures.me), with license and source recorded. Use when a Blender material, surface detail or metal reflection could start from or be benchmarked against professional free data, when the owner names these sites or asks for free resources, or before writing a texture generator. Skip when cached data already works. For badges, scan detail usually reads as speckle at phone size.
---

# Free asset sources

An option, not a rule. The owner's word and the workspace `AGENTS.md` (Claude sees it as `CLAUDE.md`) always win. Paths below are relative to `skills/free-asset-sources/`.

## Where to look

| Site | Good for | How the script gets it |
|---|---|---|
| Poly Haven, polyhaven.com | Textures, HDRIs | Public API: lists maps, sizes, preview |
| ambientCG, ambientcg.com | Textures, metal, height data | Public v2 API listing, one zip per size |
| cgbookcase.com | Battered metal and similar | Direct map links; drop the `?quality=...&width=360` query or you get a 360 px thumbnail; its archive CDN once returned 403 |
| TextureCan, texturecan.com | Textures with DirectX and OpenGL normals | Direct zip link |
| 3dtextures.me | Hammered metal and similar | A Google Drive folder; fetch each file as `drive.google.com/uc?export=download&id=<id>` with `--save-as` |
| Material Maker, materialmaker.org | Procedural materials | An app: only for a clear gain with a simple setup; later chest prompts ruled out new installs, so check with the owner first |

## Steps

1. Look for caches the project already has: `find <project> -name SOURCES.json`.
2. List before downloading, and save the preview:
   `python3 scripts/fetch_free_asset.py polyhaven <id> --cache <dir> --preview` (or `ambientcg <id>`)
3. Look at the preview. Then download 1k or 2k of only the maps you need; go to 4k only when a close render proves the smaller size is the limit. Rendering a free professional material beside yours is also a cheap quality benchmark.
4. Take only what fits. A scan's height or roughness can be a separate grayscale channel while its color is ignored (the chest iron used ambientCG height and roughness and skipped their rust color).
5. Crop the region with character, and wide enough. On the chest, a crop centered on damaged pith put a cavity in the plank; a wider crop with the surrounding growth worked. Match the crop's aspect to the surface, and give every map of one material the same crop and rotation so they stay aligned.
6. Take height as PNG or EXR. `--fmt` applies to every map in one call, so `--fmt jpg` gives 8 bit height; fetch height in its own call if the others are JPG.
7. Normal maps: Blender expects OpenGL (`nor_gl` on Poly Haven, `NormalGL` on ambientCG). A DirectX map needs its green channel flipped.
8. Height, roughness, normal and mask images load as Non-Color. Keep 16 bit images at native precision: an 8 bit load path once flattened a whole mask (`shader-aov-diagnostics` caught it).
9. Keep downloaded caches out of Git, and pass `--record <path outside the cache>` so `SOURCES.json` can be committed with the maps you authored.

## Script

`scripts/fetch_free_asset.py` uses only the Python standard library.

```sh
python3 scripts/fetch_free_asset.py polyhaven rough_wood --cache DIR --preview          # list maps, save preview
python3 scripts/fetch_free_asset.py polyhaven rough_wood --cache DIR --res 2k \
    --maps Diffuse,Rough,nor_gl --fmt jpg --note "fine fibers only" --record resources/SOURCES.json
python3 scripts/fetch_free_asset.py polyhaven rough_wood --cache DIR --res 2k --maps Displacement --fmt png
python3 scripts/fetch_free_asset.py polyhaven studio_small_03 --cache DIR --res 1k --maps hdri
python3 scripts/fetch_free_asset.py ambientcg Metal003 --cache DIR --res 1K --fmt PNG
python3 scripts/fetch_free_asset.py url <direct file link> --cache DIR --name battered_metal_02 \
    --page https://www.cgbookcase.com/textures/battered-metal-02 --license CC0 [--save-as height.png]
```

Cached files are never downloaded twice. Running again for more maps adds them to the same `SOURCES.json` entry and keeps the earlier note. A link that returns a web page instead of a file stops with an error rather than being recorded.

## What the chest work found (November 2026)

Worked:
* **Poly Haven Rough Wood** was the best natural wood. Its knotted interior region became the approved plank.
* **ambientCG Metal055A** (fine surface), **Metal003** (pits) and **Metal025** (weathering) worked as separate grayscale channels.
* **Poly Haven Studio Small 03** (1k HDRI): desaturated for neutral checks, tinted warm (1, 0.88, 0.72) in the final iron review.
* A fine scan normal inside the knot core gave it a clearer fibrous interior.

Did not work:
* Poly Haven Wood Cabinet Worn Long: too fine and polished. TextureCan wood0034: too cartoon.
* TextureCan Metal 0009 and cgbookcase Battered Metal 02: cloudy, stone like reflections.
* cgbookcase ships 8 bit height. Saving it as 16 bit adds no detail.
* A scan normal across the whole board added broad streaks and stray highlights.
* A scan alone looked too quiet beside a stylized reference. Scans carry fine detail well; the big forms stay authored.

Records: `treasure_chest_20261113/phase04/wood_lab/resources/SOURCES.json`, `phase04/wood_lab/timber_refinement/final_fibers/resources/SOURCES.json` (the knot growth source), `phase05/lower_iron/resources/SOURCES.json`, `phase05/iron_fidelity/resources/SOURCES.json`.

## Badges

* A badge is about 40 points wide on the Badges screen, and the app shows fine grain about 2.5 times stronger than Blender. Keep marks at least about 0.05 units wide (`AGENTS.md` sections 3 and 4). A scan is more useful as a calm microtexture with its broad light bands removed, the way the coin brush grain came from the owner's photo (`coin_brush_grain.npz`).
* Textures 512 or 1024, file under 5 MB.
* An HDRI is for Blender work only; the app's light is fixed.
* Normal maps on shiny badge metal looked blotchy (`AGENTS.md` section 4).
* The app reads only UsdPreviewSurface image maps. Bake through the UV set the material's reader names (`AGENTS.md` section 2, rule 2).

## Never

* Pay, sign up, or do a complicated install to get an asset.
* Use an asset whose license you cannot record.
* Send the owner's name, project or email in a request; the script's user agent is generic.
