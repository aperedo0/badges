# Badge workspace cleanup — 2026-10-09

Executed after the owner approved the printed cleanup plan. The app repo was not modified.

Removed 21,116 files and 2,040 empty directories, with no errors or skipped changed files.
Workspace before: 8.705 GiB. After deletion: 457.03 MiB. Reduction: 8.259 GiB (8.868 GB).
Observed volume available-space increase during deletion: 7.650 GiB (8.214 GB). Folder-size reduction and volume free-space increase differ on APFS because allocated blocks can be shared and filesystem accounting is not identical to du.

| Folder | Removed MiB | Reason |
|---|---:|---|
| `badge_realitykit_iron/` | 4475.86 | Removed superseded crystal/forged coin revisions, previous versions, iterations, renders, work files and duplicate exports; retained authoritative reflection-fade tools and reference inputs. |
| `badge_updates_20261007/` | 928.93 | Removed the superseded anvil and silver-coin experiments; no current shipped source depends on this folder. |
| `badge_variants2_20261008/` | 2818.48 | Removed rejected Silver 2 finishes, older Iron 2 candidates, previous versions, preview installs, intermediate scenes and duplicate packaged exports; kept current source chains. |
| `lighting/` | 8.96 | Removed the obsolete ring-light EXR and comparison image; kept reusable measurement and environment-generation scripts. |
| `medallion/` | 45.88 | Removed intermediate renders/videos and Blender backup files; conservatively retained five original source scenes and scripts. |
| `silver2_metal_claude/` | 104.61 | Removed older candidate packages, dataset rollback copies, duplicate exports, comparison dumps and logs; kept c15 source textures/USD, calibrations and correction inputs. |
| `stills/` | 74.23 | Removed old coin/anvil renders, preview images, obsolete scene copies and the ring-light map; kept authoritative current pictures and their render inputs/tools. |

## Current shipped source chains

Iron 2 candidate 13 matches the app asset SHA-256 `3c2b245b3074c8f9a72f87630ff6317a581bd0e34e17e364b3f926d93e9517fd`.
- Master: `badge_variants2_20261008/iron2/scenes/iron2_badge_master.blend`.
- Editable USD and textures: `badge_variants2_20261008/iron2/mobile/` (duplicate packed USDZ deleted).
- Rebuild: `badge_variants2_20261008/scripts/{geometry,finish_textures,build}.py`, `source/`, `iron2/settings.json`, and `iron2/reports/`.

Silver 2 c15 matches the app asset SHA-256 `45c2dd04daf079a24ebe14bee2df4a31a9be9f1686aa7938215d650b65851928`.
- Exact editable final: `silver2_metal_claude/c15/pkg/`; every member matched the shipped USDZ before its redundant local packed copy was deleted.
- Geometry master: `badge_variants2_20261008/silver2/studio_revision_20261008/33/silver2/scenes/silver2_badge_master.blend`.
- Retained candidate 33 scripts, settings, source studio scene, texture maps and reports; this is the pre-solver, pre-6%-scale Blender geometry basis.
- Final-material pipeline: `silver2_metal_claude/README.md`, its scripts, `src/c33x/`, `src/base106/`, `src/mesh33.npz`, face mappings/reference, c10/c13 light measurements, c11 ID coverage, c14 correction input image/arrays, and c15 final texture/arrays/image.
- There is no final c15 Blender scene; the final scale/materials were authored in USD. Its retained editable package can be repacked, and the solver/source chain supports further iteration.

## Authoritative and uncertain files retained

- `AGENTS.md`, `CLAUDE.md`, all of `archive/`, and `.git` were preserved.
- The authoritative original coin shell in `badge_realitykit_silver/` was preserved unchanged.
- `badge_realitykit_iron/reflection_fix/fade_textures.py`, its working source/geometry/material inputs, and legacy app measurement references/tools were preserved.
- Current badge pictures `stills/work/v2/BadgeArt_silver2.png` and `BadgeArt_iron2.png`, their full render inputs, the reusable studio copy, and still-generation scripts were preserved.
- Uncertain historical provenance: all five original `medallion/*.blend` source scenes remain (37.8 MiB including retained scripts); only `.blend1` backups and visual outputs were removed.

Verification: all 644 retained paths have unchanged size and modification time; all 350 hashed source/reference files are byte-for-byte unchanged. No writes, builds, installations, commits or branch switches were performed in the app repo.
