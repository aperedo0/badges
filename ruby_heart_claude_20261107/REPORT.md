# Ruby Heart (Claude), version 6

Picked up from Codex's version 25 (`royal_heart_compass_20261106/ruby_heart/candidate25`, untouched).

## What changed

* **Gold frame:** traced from the first reference: a wide band (0.39 units, about 7% of the width) with a rounded outer edge, a broad face, a bright ridge and a short slope down to the gem. The notch and tip are sharp; the outline is one smooth curve. The frame wraps the edge, and the back mirrors the front. Gold color (1.0, 0.44, 0.07), measured against the reference band, with the owner's brushed grain (`coin_brush_grain.npz`) scaled up so the streaks are 0.05 units or wider.
* **Gem shape:** a faceted dome that stands about 0.59 units out of the frame, front and back (owner asked to push it out, Nov 7 and again Nov 8). Its heights come from one smooth dome, so the side outline is clean. Every facet is exactly flat, so no cracks.
* **Gem look:** a new shader mode in the preview app: a thin ruby on a mirror foil, like a closed back setting. Each facet shows one direction of the studio light, so there are no shards, and the red holds while turning. A reflection floor keeps the dim fill light behind the camera from veiling the red. The color is ruby red (owner, Nov 8: version 4 read red orange): green absorbed most, a little blue let through, so the shadows are wine red and lit facets coral red. The light inside the stone is capped so the brightest facets stay red instead of washing to salmon; white comes only from glints.
* **Offline preview:** `tools/foilsim.py` replicates the shader and matches the app to within 1% average color (`tools/screen_render.py`).

## Files

* Model: `candidate06/model.usdz` (27,000 triangles, 903 KB; passes `usdchecker --arkit`), Blender checkpoint `candidate06/source/ruby_heart_v6.blend`.
* App pictures: `candidate06/app/` (front, early turn, both sides, back). Side by side: `candidate06/compare_all.png`. Outline at 4x: `candidate06/outline4x.png`. Earlier versions stay in their own folders.

## App state

* Badge Studio Preview shows version 6. Codex's previous preview model is backed up at `runtime_backup/preview_coin_before_claude.usdz`. Original shader and Swift files are in `runtime_backup/` with checksums.
* Preview app changes (additive, other gems untouched): `BadgeCrestGemSurface.metal` gains profile 10 (`crestHeartFoil`); `Badge3DLiveBadge.swift` maps the material `CrestGem_HeartFoil` to it and sets its exposure. The USDZ alone cannot carry this look: production would need the same shader addition.
* Production app (`screen_time`) untouched. Nothing committed.

## Uncertain or set aside

* At the front, the two big facets beside the center read lighter coral red than the rest; when turning they go crimson and the white glints appear.
* The facet layout is traced from the first (pink) reference, not from the second one.
* The badge guide warns against chasing number targets; color was finally chosen by eye.
