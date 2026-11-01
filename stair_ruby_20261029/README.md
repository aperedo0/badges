# Sapphire Stairway, Ruby Winged Crest and Frostwing gem repair

Open the separate Badge Studio simulator and tap **Choose Badge**, then scroll its menu to the badge you want. The entries are **Sapphire Stairway**, **Ruby Winged Crest** and **Frostwing Crystal**. These are private preview models; production app files were not edited. This was a continuous daytime build with no overnight schedule or timer.

The two new references have sculpted fronts, matching sculpted backs, continuous side walls and independently closed faceted gems. Frostwing keeps the approved metal body and replaces its fixed gem image with runtime optics. The new badge quality skill is tracked at `../skills/badge-quality` and installed in the owner's Codex skills folder.

| Badge | Final model | Editable Blender scene | Comparison |
| :--- | :--- | :--- | :--- |
| Sapphire Stairway | `sapphire_stairway/mobile/sapphire_stairway_badge_mobile.usdz` | `sapphire_stairway/source/sapphire_stairway.blend` | [Reference and preview](sapphire_stairway/candidate01/comparison.jpg) |
| Ruby Winged Crest | `ruby_wings/mobile/ruby_wings_badge_mobile.usdz` | `ruby_wings/source/ruby_wings.blend` | [Reference and preview](ruby_wings/candidate02/comparison.jpg) |
| Frostwing Crystal | `frostwing_dynamic/mobile/frostwing_dynamic_badge_mobile.usdz` | `frostwing_dynamic/source/frostwing_dynamic.blend` | [Reference and preview](frostwing_dynamic/candidate01/comparison.jpg) |

Read each badge's `REPORT.md` for details and limits. Gems now get their highlights from the studio, so their resting facet brightness differs from the fixed reference pictures. The models are intended for owner review in motion. The dark or bright facets are not painted to stay in one place.

## Runtime

Read [RUNTIME.md](RUNTIME.md) before integrating a model elsewhere. A USDZ by itself does not include the custom RealityKit shader. `runtime_integration.patch` records the private preview changes; `runtime/` contains the final renderer sources. The approved Diamond shader and the original studio lighting remain unchanged.

The preview project is `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. The simulator is **Badge Studio Preview**, identifier `DF439C70-9FD7-4EF7-998E-43AF5F83A588`.

## Rebuild a saved working checkpoint

Work in a new numbered candidate before making further changes. `design.json` and `candidate.txt` in each badge folder identify its design and working checkpoint. Keep the final `mobile/` model and the approved sources intact.

The saved `geometry.npz`, finish maps and design are enough for `rebuild.py KEY` using `/tmp/crest_image_env/bin/python` and the live Blender connection on port 9876. The script builds the complete scene, captures its Blender angles, packages and validates the USDZ with Blender's bundled Python, and copies it into the separate preview source.

For new geometry on the stairway or ruby, run `build_reference.py KEY`, `finish_maps.py KEY` and `prepare_metal.py KEY` before rebuilding. Those create a calibration model. Build the separate preview, select the matching badge, verify that the actual 3D model is visible, and run `capture_front.py KEY app_calibration`. `fit_metal.py KEY` measures that light for the non gemstone finish. Rebuild again to apply the fit. Never measure a splash screen or a different badge. Frostwing's repair starts from its saved approved body checkpoint; keep that body rather than regenerating its silhouette for an optical edit.

The gemstone builder in `dynamic_gems.py` creates real convex cuts, clears fixed gem imagery from hidden supports and assigns the named optical profile. The new ruby's long cut uses an explicit front ridge. Settings and body marks use the non gemstone reference fit. Their file textures are intentionally separate from gemstone appearance.

## Review evidence

Each active candidate contains native front, back and side captures, four times outline crops, an equal size comparison, a slow `full_turn.mp4`, topology validation and runtime attachment evidence. The video is a local review artifact and is excluded by the repository's existing video ignore rule. `make_motion_review.py` creates still contact sheets from completed videos.

`check_runtime_gems.py`, run with Blender's bundled Python, uses the actual Swift plane checker on exported stones and their mirrored geometry. It also checks the coefficient precision used during upload. The private preview's console confirms shader attachment to all 18 stones and all 18 reflected copies. These checks support the visual review; they do not prove reference identity.
