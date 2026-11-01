# Ruby Winged Crest

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate02/comparison.jpg) | [Every side](./candidate02/every_side.jpg) | [Slow full turn](./candidate02/full_turn.mp4)

## Reference details

* Seven separately swept feather layers per wing
* Open silver crown and curved inner returns
* Long closed ruby cut and six independent ruby accents
* Matching sculpted back with continuous silver sides

## Files

Final model: `mobile/ruby_wings_badge_mobile.usdz`. Editable complete Blender scene: `source/ruby_wings.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate02`.

## Dynamic gemstones

Every stone is an independent closed convex cut. Its color absorption, reflections, refraction and internal light paths respond to rotation under the fixed studio. No gemstone appearance photograph or fixed emission image is bound to it. The preview restores its named crest material with the runtime optics described in [RUNTIME.md](../RUNTIME.md). The USDZ by itself retains a plain fallback material.

Resting facet highlights differ from the static reference because they now come from actual light directions. Frostwing uses two convex sections under the center setting to retain its pinched long outline. The stairway's concave guiding star uses four separately cut stones. The editable scene retains ordinary fallback materials; final optical review takes place in the simulator.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 107,132 triangles and 9.1 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the non gemstone reference finish, while physical metal reflections change during rotation. The gemstones use the separate runtime optical path instead of that appearance fill. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
