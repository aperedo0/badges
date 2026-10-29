# Lunar Compass

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate02/comparison.jpg) | [Every side](./candidate02/every_side.jpg) | [Slow full turn](./candidate02/full_turn.mp4)

## Reference details

* Raised concentric silver rings around a blue constellation band
* Five independent closed faceted sapphire lenses and sculpted settings
* Raised silver crescent with the reference lunar surface
* Long compass points and diagonal rays around the central sapphire
* Sixty separate clock ticks, raised studs and four diagonal ornaments
* Complete matching reverse and continuous silver side walls

## Files

Final model: `mobile/lunar_compass_badge_mobile.usdz`. Editable complete Blender scene: `source/lunar_compass.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate02`.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 88,876 triangles and 8.3 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the reference finish, while physical metal reflections change during rotation. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
