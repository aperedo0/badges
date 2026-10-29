# Frostwing Crystal

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate02/comparison.jpg) | [Every side](./candidate02/every_side.jpg) | [Slow full turn](./candidate02/full_turn.mp4)

## Reference details

* Seven swept silver feather layers on each side
* Blue crystal channels between the feathers
* Open upper and lower silver return arcs
* Long closed faceted ice blade and independent central diamond
* Brushed metal grain and narrow bright edge highlights

## Files

Final model: `mobile/frostwing_badge_mobile.usdz`. Editable complete Blender scene: `source/frostwing.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate02`.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 106,448 triangles and 9.2 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the reference finish, while physical metal reflections change during rotation. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
