# Celestial Orbit

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./candidate02/comparison.jpg) | [Every side](./candidate02/every_side.jpg) | [Slow full turn](./candidate02/full_turn.mp4)

## Reference details

* Opposed pale blue and deep blue crescent forms
* Tall four point faceted crystal in a long silver compass frame
* Four independent blue cardinal lens gems and metal settings
* Nested silver orbit rings and blue starfield outer band
* Raised minute ticks, radial sun marks and three rounded metal studs
* Complete matching reverse and continuous silver edge

## Files

Final model: `mobile/celestial_orbit_badge_mobile.usdz`. Editable complete Blender scene: `source/celestial_orbit.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `candidate02`.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use 84,372 triangles and 8.0 MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the reference finish, while physical metal reflections change during rotation. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
