# Gem optics in the owner's Badge Studio

Use this reference only for gem work in the badges workspace. Inspect the current files before changing them; these locations describe the working preview created on October 29.

The separate preview is at `/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025/preview`. Its badge renderer is `ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift`.

`BadgeCrestGemSurface.metal` traces the studio environment through closed convex facets for materials named `CrestGem_Ice`, `CrestGem_Sapphire` and `CrestGem_Ruby`. The Swift renderer recursively attaches the shader to each independently named gem mesh. Do not combine several disconnected stones into one mesh. `GemFacetPlanes.swift` checks the actual exported planes; the current limit is 256 per stone.

The older `DiamondGem` uses `BadgeGemSurface.metal`. Its approved optical constants and single row plane upload remain separate. New crest work is not permission to retune Diamond, the stage, lights or production app.

RealityKit exposes these texture slots as half precision reads. The crest uploader stores two plane rows: rounded coefficients, then their residual multiplied by 1024. The crest shader reconstructs both rows before tracing. Preserve this pairing and its tolerance together. Diamond keeps its old upload. A mesh can validate correctly yet still develop chipped tips if this pairing is broken.

The gem appearance contains no photograph or fixed emission map. The base color texture slot at runtime contains numeric plane coefficients, not a picture. The custom slot contains the existing fixed studio environment. Intrinsic optical density is sampled in model space along refracted paths. Ice also has bounded internal reflective cleavage planes. Reflection meshes reverse the intrinsic field's Y coordinate, matching the flipped geometry.

The USDZ stores a plain UsdPreviewSurface fallback. It cannot carry the custom Metal function by itself. Runtime logs include `Badge gem attached` or `Badge gem FAILED`; inspect the relevant stone count for both the model and its floor reflection. Still inspect the actual rotation, because attachment alone cannot prove the look.

Working sources, validation and the integration patch are in `/Users/antonioperedo/Desktop/badges/stair_ruby_20261029`. `check_runtime_gems.py` runs the preview's actual Swift convexity routine on exported geometry and its reflection. `runtime_integration.patch` and `RUNTIME.md` describe the separate preview changes. Read them before integrating these models elsewhere. Production integration remains the owner's decision.
