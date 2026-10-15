# Two hourglass coin prototypes

Both use the new broad flat rim with beveled edges and a recessed background, at the existing 6.03 diameter and floor cut. The complete coins were edited in live Blender. Glass and support profiles are continuous native lathes. Sand meshes now have a surface rising toward the right, a higher lower pile, and a fine continuous stream. The teal version uses dark brushed silver; the gold version uses warmer satin silver, gold sand and deep navy.

The shared geometry was measured once under the app's lighting. The two geometry arrays are identical, so that measurement also fitted the gold version. These are opaque embossed medallions with reference-fitted color and emission, not physically transparent hourglass vessels. Fine reference texture is softened to avoid subpixel grain on the phone.

Real Home front, back and both side poses were checked, including nearest-neighbor 4x crops. Gold also has an internal scroll recording. The app still adds its normal floor reflection and backdrop. No app lighting, code or production assets were changed. Tests used the separate `Badge Coins Preview` simulator, ID `85DF6D3B-6622-491A-8996-3ED0725DB273`, from `/tmp/achievement_coin_app_20261014`; the preview uses the Silver tier as a temporary slot.

Each model has 59,166 triangles, above the general 35,000 to 45,000 guide to retain smooth glass, posts and frame curves. Teal is 3,201,239 bytes; gold is 3,255,479 bytes. Both remain below 5 MB. Actual physical-device performance has not been measured. Exporting compact vertex normals reduced model data and the warmed app launch displayed correctly; cold installs can still show fallback art while shaders compile.

Both `/usr/bin/usdchecker --arkit` checks returned `Success!`; each `validation.json` records identity transforms, frame/floor bounds, resolved textures, watertight shell apart from the floor cut, and the untouched shipped silver checksum. `ScreenTime-UIOnly` simulator builds returned `SUCCEEDED`: teal 76,926 ms and gold 36,607 ms (`final_*_build.json`). The temporary private dataset was restored byte for byte after each build. The full production three-scheme/test gate was not run for these external asset previews.

Each subfolder contains its complete editable `.blend`, canonical geometry and maps, and `mobile/<name>_badge_mobile.usdz`. The raised rim is still a review prototype rather than an owner-approved replacement for shipped silver.
