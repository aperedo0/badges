# Bronze Phoenix

Open **Badge Studio** in the **Badge Studio Preview** simulator. Tap **Choose badge**, then **Bronze Phoenix**. Slowly scroll Home upward to turn it. Return to the top for its front.

The [reference comparison](phoenix/comparison.jpg), [every side](phoenix/every_side.jpg), [report](phoenix/REPORT.md), [editable Blender source](phoenix/phoenix.blend) and [final USDZ](phoenix/mobile/phoenix_badge_mobile.usdz) are kept here. The original reference is copied into the phoenix folder. This is a separate preview entry.

The custom medallion has raised bronze feathers, a recessed cracked center and three closed amber diamonds. The back repeats the sculpture. Bronze reflections move under the unchanged studio light, with a gentle polish and reference fill to retain the fine marks and color.

The private preview is `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`. Its menu and neutral floating placement addition are recorded in `private_preview.patch`. Production app code was not changed.

Rebuilding uses Blender 5.2 with the live add on on port 9876, its bundled Python for USD, and a Python environment with NumPy, Pillow and SciPy. Run `build_reference.py phoenix` and `finish_maps.py phoenix` with the image Python environment. This creates the complete relief, continuous side walls, matched rear and three independent gems. Preserve a numbered candidate before changing a reviewed model.

Run `prepare_metal.py phoenix` with the image environment and `rebuild.py phoenix` with the normal Python. Build and run the private project with XcodeBuildMCP, capture native lighting with `capture_front.py phoenix`, then run `fit_metal.py phoenix` with the image environment. Rebuild and run the fitted model. Check native front, spin and all sides with `capture_glints.py phoenix`, `capture_poses.py phoenix` and a recording of `turn_swipe.py`. Run `review.py phoenix` for the matching scale reference comparison, and `deliver.py` only after reviewing the result.
