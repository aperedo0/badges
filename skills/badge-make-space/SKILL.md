---
name: badge-make-space
description: Clean obsolete badge attempts, duplicate model outputs, screenshots and intermediate files only inside /Users/antonioperedo/Desktop/badges. Use for make space or folder cleanup requests in this repository. Preserve Git history, current editable badges, required resources and explicitly kept versions. This is not the Mac or simulator cleanup skill.
---

# Badge folder cleanup

Keep this repository small by retaining the current usable badge collection, not every attempt that produced it. The owner approved this approach on November 14, 2026. Work only inside `/Users/antonioperedo/Desktop/badges`. An invocation authorizes routine removal of inspected obsolete outputs here, not cleanup elsewhere.

For a cleanup request in this repository, use this skill instead of the global `make-space` skill. Do not run the Mac cleanup command, touch other repositories, clean simulators or chats, or move files to a drive. Preserve `.git` and its history. Never stage, commit, rewrite history or run Git cleanup commands.

## Establish what stays

Read `AGENTS.md` and any applicable saved run state. Cleanup must not resume badge work, start a new run, change its pacing, or resume a paused app. Keep the current checkpoint and exact next action. If the owner also asked to save Blender, save their complete current scene through the live connection before cleanup. Do not load another file or discard unsaved work. Report an unavailable or system paused Blender honestly; a file copy is not a new Blender save.

Inventory the entire repository, including deeply nested candidates, source extractions and old working folders. Count bytes and files by type and folder. Report working files separately from Git history. A roughly 2 GB working collection is a useful target from the owner's request, not permission to remove necessary assets or pretend the whole folder fits when Git alone exceeds that size.

Build a current model index with one authoritative export and one complete editable Blender file per distinct badge, plus the resources actually needed to open, edit and continue it. Include explicit comparison versions, such as Ruby Heart Version 1 and Version 2. Keep the active chest checkpoint, reference, rig source, immutable construction input and resume notes.

Use current selection records, owner approvals, installed preview asset hashes, version manifests and actual file contents to choose the retained version. A higher candidate number, newer modification time or a stale gallery entry alone does not prove it is current. A rejected newer trial must not replace the approved model. Keep a current unfinished working version too when necessary to resume.

Compare across runs of the same badge. A verified current compact model can supersede the older authoring copies in a different dated folder. Do not keep one candidate from every old run and call all of them current. The saved model index from the November cleanup is useful evidence, not a permanent list of what must stay.

## Check dependencies before deleting

* Keep owner references, active material images, actual linked images and libraries, required source scripts, templates and current build inputs. Preserve any resource shared by retained badges.
* Verify that a packed Blender checkpoint contains its material images and matches the intended export before treating its import extraction as disposable. Keep required app texture metadata and runtime recognized geometry conventions.
* An image filename stored in a file browser history or a custom property is not proof of a live dependency. Conversely, a texture following a relative path can be essential even when its filename is generic.
* A current model being editable does not prove an old generator can run without its input arrays. Establish whether those inputs are needed for the current workflow before deleting them. Do not promise old attempts remain rebuildable after their outputs are removed.
* Preserve the preview project and assets it actually uses. Never edit app code or break the preview to save a duplicate export. Keep a separate preview copy when the app needs that location.

Keep the original source files when a current build depends on them. Do not preserve every obsolete source extraction, fitting array or candidate snapshot merely because it has a source sounding name or an unused historical script mentions it.

## Remove the obsolete material

Usual removal candidates are superseded Blender and USDZ attempts, redundant export copies, automatic Blender backups, imported USD and texture extractions already embedded in a verified current model, old fit arrays, diagnostic renders, enlarged crops, turn recordings, screenshots and caches. Source code, plans, templates and references generally cost little and need individual judgment rather than broad extension deletion.

There is no default quota of old candidates to keep. Retain an earlier version only for a concrete current dependency, an explicit owner request or a genuinely unresolved comparison. Preserve the current rig and controls even when temporary test recordings are discarded.

Do not replace the cleanup with compression or identical copy consolidation while leaving thousands of unnecessary outputs. APFS clones can share physical storage, but their logical byte total is not the amount of disk space freed.

Use the helper for inventory and for applying a reviewed exact file list. It does not choose versions or infer which textures are safe to delete. Read [the manifest format](references/manifest.md) when preparing the list.

```sh
python3 skills/badge-make-space/scripts/repo_cleanup.py inventory --out cleanup_runs/RUN/inventory.json
python3 skills/badge-make-space/scripts/repo_cleanup.py apply cleanup_runs/RUN/manifest.json --receipt cleanup_runs/RUN/receipt.jsonl
```

Replace `RUN` with the actual cleanup identifier. Inspect the keep index and removal reasons before applying. No extra confirmation is needed for clearly obsolete files within the cleanup the owner requested. Ask only where the current version or an essential dependency cannot be resolved from available evidence, or the proposed action exceeds the authorized scope. Continue unaffected cleanup while that question is pending.

The helper validates every keep and removal fingerprint before deleting anything, rejects protected and linked paths, and records deletion receipts. If a file changed, stop that apply and refresh the plan. Do not force stale checks through. Do not use the dated one off cleanup scripts as automatic deletion recipes.

## Verify and report

Verify retained file hashes, both explicit comparison versions, the saved active checkpoint and current model dependencies. Check USDZ archives for integrity where relevant. Update the model index to the retained paths. Use only small text receipts and indexes; do not create new review images or another large backup inside this folder.

Report bytes removed, working files remaining, Git history size, total folder size and current free disk space. Distinguish logical removed bytes from measured free space changes. Name any unresolved ambiguity rather than declaring all remaining files absolutely necessary. Keep badge work paused if it was paused.

Give a scoped commit command using the commit message skill. Include this cleanup's exact tracked deletions and audit files, not unrelated edits or new files from another chat. Do not delete or move Git history to meet a folder size target.
