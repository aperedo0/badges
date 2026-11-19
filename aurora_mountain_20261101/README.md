# Aurora Mountain

Aurora Mountain is a separate entry in Badge Studio Preview. Use **Choose Badge**, then **Aurora Mountain**. Production app files and the other badge assets are unchanged.

Final model: `mobile/aurora_mountain_badge_mobile.usdz`. Editable complete Blender scene: `source/aurora_mountain.blend`. The final reviewed working checkpoint is `candidate03`. The original owner reference is `reference.png`.

The crest has a custom double metal frame, a shaped silver sweep, raised indigo mountains, a winding solid gold path, a faceted guiding star, eleven smaller gold stars, and one closed faceted amethyst in its own beveled gold setting. Its rear repeats the complete sculpted design, with continuous finished side walls. The original coin shell is preserved as a hidden construction guide in Blender, and is excluded from export.

Read [REPORT.md](REPORT.md) for the comparison, validation and appearance limits. The model requires the private preview's existing crest optical renderer plus the isolated amethyst profile in `runtime_integration.patch`. A USDZ alone cannot carry that runtime shader. The original studio, Diamond shader and earlier gem profiles are unchanged.

Rebuild with the system Python 3.11 for `build_geometry.py` and `prepare_textures.py`. Run `build_live.py` through `../water_match_20261014/blender_live.py`, then `inspect_live.py`. After visually inspecting the complete Blender badge, run `pack.py` and `check_runtime_gem.py` with Blender's bundled Python. `validate_solids.py` checks each closed solid. `install_preview.py` installs only the separate preview entry and its scoped amethyst profile. The active candidate is in `candidate.txt`.

The preview project is `../emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`, bundle `com.antonioperedo.badgestudio.preview`, simulator **Badge Studio Preview**, identifier `C18E609E-6C2F-49C4-BCFE-E5D365F4E4E8`. Local launch arguments are `-hasCompletedOnboarding YES -CoinBadgePreview auroraMountain`.
