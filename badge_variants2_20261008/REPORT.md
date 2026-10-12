## Silver 2 polished brushed finish24 (2026-10-08)

Silver 2 finish 24 replaces final 13 in the owner-authorized temporary preview. Iron 2 and both original coins are unchanged. All actual app/export checks and the texture exception are recorded in[Silver2report](silver2/REPORT.md). [Reference and app comparison](silver2/proof/reference_before_after_app.png),[all four](proof/all_four_badges_in_app.png). Previous Silver 2 final 13 is preserved in`silver2/previous/finish13/`. Historical sections below describe earlier validation states.

## Four badges available on Home (2026-10-08)

The temporary preview now cycles Silver2 → Iron2 → Silver → Iron. The original coins are exact backup copies in separate preview-only datasets, and both new shape assets are unchanged. All four actual models/reflections and two complete switch cycles passed simulator visual verification with no fallback or missing-floor frames. [Four-badge pictures, video and build proof](app_install_preview/all_four/README.md). The owner-requested preview remains uncommitted. No earned-badge or model-design changes.

## Home switch correction (2026-10-08)

Fixed the brief old flat coin and disappearing floor during switching. A single persistent renderer keeps the current actual badge/floor visible until the selected actual3D scene is ready. Cold, warm and rapid-tap 60fps recordings pass with zero intermediary artwork or blank-floor frames. Both models and their resting badge/floor pixels are unchanged. [Correction proof, recordings and build checks](app_install_preview/switch_fix/README.md).

The authorized preview code and two models remain uncommitted. BEHAVIOR_MAP.md is also dirty from outside this badge work and was preserved; current full status is recorded in app_install_preview/final_verification.json. Historical clean-status statements below describe the earlier export tests.

## Temporary app preview installed (2026-10-08)

The owner requested keeping Silver2 and Iron2 in the app with a Home switch. Final13 models now replace their own tier dataset files, and `BadgeHeroCard.swift` adds a view-local Badge preview switch, defaulting to Silver2. These three app files deliberately remain uncommitted; HEAD and branch unchanged. This explicit request overrides the usual badge-folder no-app-edit/always-restore rule for this preview only. Originals are backed up in `app_install_preview/`. No earned-tier, accounting, persistence, stage, lighting or other-screen changes. Both device builds and the UIOnly simulator build passed; actual repeated button taps verified both 3D models/reflections.

[Temporary installation proof and pictures](app_install_preview/README.md). The export-validation reports below describe the earlier testing phase, when original app assets were restored; their clean-status claims are historical, not the current intentional three-file diff.

# Silver 2 and Iron 2: texture revision

Geometry unchanged. Silver has richer polished warm/cool planes and leaf reflections; Iron has reference-derived fine worked-metal/scuff color and restrained satin reflections. Each exact final was verified in the real app, using temporary substitution and full restoration.

|Variant|Candidate|Triangles|Bytes|App white /1249|
|---|---|---:|---:|---:|
|Silver 2|13|42,664|2,945,023|1082|
|Iron 2|13|38,528|3,815,685|0|

[Silver report](silver2/REPORT.md), [Iron report](iron2/REPORT.md), [actual app comparison](proof/silver_2_and_iron_2_in_app.png), [floor comparisons](proof/floor_gaps_same_scale.png). Per-tier reports contain all checks, metrics, every iteration, material tables, explicit reference exceptions and remaining lighting/presentation limits. The first delivery is preserved in each `previous/first_shape_delivery/`. No original coin or production app asset was permanently replaced.

[Final restoration proof](proof/repo_final.json): full app git status empty, HEAD, original assets and all protected sources unchanged.
