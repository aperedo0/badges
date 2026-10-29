# Battle Steel

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate03/comparison.jpg) | [Every side](./candidate03/every_side.jpg) | [Slow full turn](./candidate03/full_turn.mp4)

## Reference details

* Hollow tall forged diamond frame
* Separate four facet steel center diamond
* Four angular steel wing tiers and hooked upper wings
* Complete rear with matching cracked steel finish
* Warm bronze bevels and continuous ring

## Files

Final model: `mobile/battle_steel_badge_mobile.usdz`. Editable complete Blender scene: `source/battle_steel.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate03`.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 111,268 triangles and 9.5 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the reference finish, while physical metal reflections change during rotation. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
