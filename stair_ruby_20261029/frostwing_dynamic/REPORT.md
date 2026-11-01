# Frostwing Crystal

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate01/comparison.jpg) | [Every side](./candidate01/every_side.jpg) | [Slow full turn](./candidate01/full_turn.mp4)

## Reference details

* Seven swept silver feather layers on each side
* Blue crystal channels between the feathers
* Open upper and lower silver return arcs
* Long closed faceted ice blade and independent central diamond
* Brushed metal grain and narrow bright edge highlights

## Files

Final model: `mobile/frostwing_dynamic_badge_mobile.usdz`. Editable complete Blender scene: `source/frostwing_dynamic.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate01`.

## Dynamic gemstones

Every stone is an independent closed convex cut. Its color absorption, reflections, refraction and internal light paths respond to rotation under the fixed studio. No gemstone appearance photograph or fixed emission image is bound to it. The preview restores its named crest material with the runtime optics described in [RUNTIME.md](../RUNTIME.md). The USDZ by itself retains a plain fallback material.

Resting facet highlights differ from the static reference because they now come from actual light directions. Frostwing uses two convex sections under the center setting to retain its pinched long outline. The stairway's concave guiding star uses four separately cut stones. The editable scene retains ordinary fallback materials; final optical review takes place in the simulator.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 106,512 triangles and 8.9 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the non gemstone reference finish, while physical metal reflections change during rotation. The gemstones use the separate runtime optical path instead of that appearance fill. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
