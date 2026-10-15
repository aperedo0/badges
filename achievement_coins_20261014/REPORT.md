# Five coin previews

[One comparison in Downloads](</Users/antonioperedo/Downloads/Coin badge previews.png>) shows the mockups above real Home captures at approximately matching coin sizes. These are review previews, not approved production assets.

The complete coins were inspected in Blender, including through the live MCP connection. Editable scenes are in [coins.blend](coins.blend). The approved shell mesh, UVs, normals, names and floor cut are preserved exactly. Bronze and gold recoloring follows the owner's permission. The reverse carries the same raised design.

| Preview | USDZ | Triangles | Bytes |
| --- | --- | ---: | ---: |
| Water drop | [Model](clean/mobile/clean_badge_mobile.usdz) | 56,694 | 4,225,246 |
| Teal hourglass | [Model](hourglass_teal/mobile/hourglass_teal_badge_mobile.usdz) | 94,296 | 4,634,143 |
| Gold hourglass | [Model](hourglass_gold/mobile/hourglass_gold_badge_mobile.usdz) | 94,296 | 4,666,952 |
| Sunrise | [Model](sunrise/mobile/sunrise_badge_mobile.usdz) | 62,864 | 4,153,318 |
| Emerald sprout | [Model](sprout/mobile/sprout_badge_mobile.usdz) | 65,170 | 4,616,675 |

The triangle guideline was exceeded for smooth curved relief on both faces, especially the hourglass bodies and columns. Every package remains below 5 MB. Device performance has not been measured.

The metals use live PBR shading. The water and emerald background also use fitted color/emission maps. Water and hourglass glass are opaque raised reliefs with a glass appearance, not the Diamond's optical ray-tracing shader.

Validation: all five returned `usdchecker --arkit: Success!`. Frozen shell equality, identity transforms, Y-up/meters, frame/floor bounds, texture resolution and mirrored reverse geometry passed. All five simulator preview builds returned `ScreenTime-UIOnly: ** BUILD SUCCEEDED **`; proof paths are in `build_results.json`. No full production build/test gate was run because these assets were only temporarily substituted in an isolated app copy.

Front, side, back and other-side app captures were inspected, including nearest-neighbor 4x crops. Remaining polish: the water's bright relief edges look rough at 4x; the sprout has small dark marks near its stem/soil and background, and uneven leaf-border highlights. These previews do not yet satisfy a claim of artifact-free edges at every angle.

The separate simulator is **Badge Coins Preview**, ID `85DF6D3B-6622-491A-8996-3ED0725DB273`. Sprout is left at rest there using the Silver preview slot, so the title still says Silver. A temporary 30-second first-frame deadline was used only in the isolated app copy to diagnose fallback captures, setting aside section 5's code guidance for diagnostics. That source change was restored byte for byte. The final installed preview renders Sprout with the original six-second deadline. Cold-start reliability on a phone remains untested.

The main app repo's Silver asset matches its original backup byte for byte. No production app code, approved source badge, commit or branch was changed. Temporary datasets and diagnostic source changes in the preview copy were restored.

`reliefs.npz`, `design.json`, canonical texture PNGs and `pack.py` preserve the exports' inputs. Do not rerun the initial `prepare.py` over the finished geometry. The Blender-first workflow is recorded in the root `AGENTS.md`.
