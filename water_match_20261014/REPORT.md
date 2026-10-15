# Water and raised rim prototype

The rim is a broad flat band with short bevels. Its front stands at Z 0.215; the dark face sits at Z 0.044, a recess of 0.171 units. The outer diameter remains 6.03 units. The band is 0.595 wide, including bevels; the full casing is 0.760 deep. The back has the same construction. This is the owner's October 14 exception to the old frozen-shell rule, still a prototype for review.

The droplet and bubbles now use smooth native Blender lathed reliefs instead of raster-derived surfaces. The fitted materials remove the previous pale pink patch and keep a dark background. The cyan still looks paler than the reference. These are opaque reflective reliefs with reference-fitted color and emission maps, not refractive water simulations.

The front, two oblique side poses and back were inspected in real Home renders, including 4x crops. A scroll recording was also checked; scroll automation pauses then advances unevenly, so it is useful for extra poses rather than a smooth presentation video. No outline gaps were visible in those captures. Geometry validation proves the only open shell boundary is the intentional floor cut.

`clean/mobile/clean_badge_mobile.usdz`: 3,654,326 bytes, 37,556 triangles. SHA-256 `b01c90aa0bf10a8dce48599cfbc6e773e7ef83f1f6e3cdef620417ad5fadadf6`.

Validation: `/usr/bin/usdchecker --arkit`: `Success!`; identity transforms, USD Y up, texture paths, frame bounds, floor cut and original silver checksum passed (`validation.json`). The temporary `ScreenTime-UIOnly` simulator build returned `SUCCEEDED`, 33,863 ms (`build_results.json`). No production code or installed main-repo assets were changed, and the temporary Silver dataset was restored byte for byte. The full production three-scheme/test gate was not run for this external model preview.

Editable complete coin: `water.blend`. Shared geometry: `shell_geometry.npz`, `shell_design.json`, `shell_template.usdz`. The template has calibration materials; the finished prototype's materials are in the Water USDZ. Canonical fitted maps are in `clean/textures/`.

Owner comparison: `~/Downloads/Coin badge previews.png`, only one compact picture. App crops are unretouched. The app's floor, reflection, light and backdrop remain unchanged.
