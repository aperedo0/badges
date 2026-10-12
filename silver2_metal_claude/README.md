# Silver 2 star made metal (Claude, 2026-10-09)

Base: Codex candidate 33 (geometry, leaves, per face UV islands unchanged). Only the star's two color atlases change, plus a new emissive atlas on the two star materials.

How: c00_calib renders the star with an even albedo 0.5 to measure the app's light on every point of every face (inverse of the app's AgX transform, smooth cubic fit per face). c02_emis_calib proved emissive shows 1:1. solve2.py then sets, per texel, albedo = min(1, target / light) and emissive = the rest (max 1), where target is the reference star's own color on the same face (sampled inside the face, smoothed, highlights above display 0.78 compressed by 0.6). make_candidate.py writes the atlases and packs the usdz; try.sh tests in the app and restores; compare.py makes side by sides.

c03: installed in the owner's Home preview (Badge3DModelSilver data set). Per face app vs target within 5 display levels; white pixels 678. Final 24 backup: src/installed_final24.usdz.

## 2026-10-09 later: 6% bigger, leaves matched too (c15, installed)

scale_usd.py scales every mesh by 1.06 about (0, -2.455, 0) (src/base106; float gap unchanged, width 6.39, top 2.657). c10_calib measures the star (albedo 0.5), c13_calib the leaves (albedo 0.12, so no highlight saturates), c11_id gives a coverage mask (leaves emissive green, star red). solve3.py: star per face as before; leaves per texel by rasterizing every leaf triangle in UV, light from the leaf calib inside the mask (smoothly extended past edges), target = reference leaves' inside (black background and outer rim line removed, smoothly extended), then albedo + emissive like the star. c15 = c14 plus one correction pass. Leaves went from about 66 to about 19 display levels off the reference; white pixels 347. try.sh now restores whatever file was installed before the test.
