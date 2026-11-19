---
name: look-dev-loop
description: Optional working method for long Blender refinement of a material, prop or badge toward a reference, quality first with few AI tokens. Covers diagnosis, isolated candidates in local batches, draft then final renders, cached rendering, compact comparison sheets, checkpoints proven by a fingerprint script, and state files a new chat resumes from. Use when the owner asks to refine, polish or continue material or prop work, says token usage is back, asks for a recoverable checkpoint, or asks to save tokens. For badges it runs inside the badge skills.
---

# Look development loop

An option, not a rule. The owner's priority order on the chest was: highest visual quality first, then the fewest AI tokens for that quality, then efficient reusable local computation. Never trade quality for tokens; cut repeated work instead. The owner's word and the workspace `AGENTS.md` (Claude sees it as `CLAUDE.md`) always win. Paths below are relative to `skills/look-dev-loop/`.

## Resuming

1. Read the project's own `AGENTS.md` and `PROJECT_STATE.md` (agents do not load them from a subfolder on their own).
2. Check `git log` and the live Blender for newer work by another chat. On the chest, two chats worked at once.
3. Continue from the saved best version. Never restart working systems.

At every stop, rewrite `PROJECT_STATE.md` in under about 300 words.

## One round

1. Pick the largest visible difference from the reference.
2. Find its cause before changing anything (`fair-lighting-checks`, `shader-aov-diagnostics`, a gray clay render).
3. Make targeted changes, each aimed at one cause and tested alone against the same baseline. A batch may hold several settings of one change, or several changes plus their combination (the chest iron ran weathering, edge response, then combined). Hold the rest fixed.
4. Render draft crops of the candidates in one local batch.
5. Open the actual images. Compare each with the reference crop and the best previous version, close up and at normal viewing distance.
6. Keep what improves, revert what regresses, and note it either way.

Repeat while meaningful gains remain. If two or three tries at the same problem fail, change the technique, not the strength. On the chest: generated knot rings became a real scan region; dark scan cracks that a clay render showed were only color became physical cuts; painted, normal mapped grooves became real recessed geometry; a correction applied by image columns (which made stripes) became one aimed at convex areas of the actual mesh.

Stop when changes stop being visible, or when the rest is better judged in context, and say what still differs.

## Saving tokens

* **Short files in the project's own folder** (for example `treasure_chest_20261113/`) let a new chat start without the old conversation. Never edit the workspace `AGENTS.md` or `CLAUDE.md` unless the owner asks.
  * `AGENTS.md`: that project's goal and permanent rules.
  * `PROJECT_STATE.md`: current best file, settings that worked, failed approaches, remaining gaps, next step.
  * Experiment notes: one or two lines per experiment, including rejected ones and why. The chest kept them in each phase's `README.md`, `EXPERIMENTS.md` and `design.json`.
* Keep logs, full resolution renders and data on disk. Print one line per finished job.
* Write parameterized scripts with keys (`render.py KEY VIEW LIGHT`) and reuse the existing rig, cameras and render scripts instead of rewriting them. Build only the tooling the artwork needs now; this is not an infrastructure project.
* Cache renders by key, view and light, skip any file that exists, and use a new key when parameters change.
* Hold one render lock (`fcntl.flock` on a lock file) so two renders never run at once. A duplicate background job happened on the chest.
* Run background Blender with `--python-exit-code 1`; without it Blender exits 0 even when the script fails.
* Screen with drafts (small crop, low samples); render finals only for finalists (the chest used 64 to 128 samples, 1600 by 800 crops). Never judge scratches or pits from a small denoised draft.
* Make a compact labeled comparison sheet (reference crop, baseline, candidate, same scale) with the repo's Python 3.11 at `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, which has Pillow; Blender's Python does not. Open the sheet first; open full resolution only for fine detail.
* Do not reread unchanged files, redo settled research, regenerate working maps or reprocess unchanged textures.
* No subagents unless the project or a skill calls for them (the badge review skills do). Short progress messages.

## Checkpoints

* Before each round that could change the approved state, save one complete packed `.blend` on disk. One per round, not one per candidate.
* Prove it with `scripts/blend_fingerprint.py`. Snapshot when saving, then compare after a fresh reopen; for each candidate, compare against the round's snapshot and allow only this round's objects or materials to differ:

```sh
Blender -b --python-exit-code 1 -P scripts/blend_fingerprint.py -- snapshot ROUND.blend round.json
Blender -b --python-exit-code 1 -P scripts/blend_fingerprint.py -- compare round.json CANDIDATE.blend --allow "Lab Chest Lower Rim"
```

  It checks transforms, mesh positions, polygons, every UV layer, material, world and node group graphs, lights, cameras, render and color settings, and images. Missing or unpacked images always fail. It prints PASS or FAIL with the exact object, node or image that changed, and exits 1 on FAIL. To snapshot the owner's live scene without saving it, run it through the Blender connection: `ns = runpy.run_path(PATH); json.dump(ns['snapshot'](), open(OUT, 'w'))`.
* The owner commits by hand: hand over the command with the `commit-message` skill. Commit yourself only when the owner explicitly asks for a Git checkpoint, and then only this work's files.
* Put candidates under a `candidates/` folder (its `.blend`, image and data files are already in `.gitignore`) and commit only the round checkpoint and the selected master. The chest put about 6.7 GB of files into Git history, 3.9 GB of it in 104 saved `.blend` versions.
* Move a result into the owner's live scene with a guarded script that first checks a fingerprint of what it expects to replace, that `bpy.data.is_dirty` is false and that no render is running. Never rerun it on a scene that has already changed.
* Keep every candidate openable, and never overwrite the approved benchmark.

## Honest reporting

* Never say you inspected an image you did not open.
* Numbers help find problems but never prove a look.
* Report what still differs from the reference.
* Whoever the project names does the judging. The chest: the owner only, no AI reviewer. Badges: `badge-fresh-review`, then the owner.

## Blender habits from the chest

* Ctrl Z does not undo a viewport zoom or rotation. Before the owner explores, record the 3D view's location, rotation and distance (`region_3d.view_location`, `view_rotation`, `view_distance`) so you can put it back.
* To show the owner a result, load it into their open Blender and save, keeping their layout and their reference editor.

## Badges

For a badge, the workflow stays `badge-plan`, `badge-plan-review`, `badge-build`, `badge-fresh-review`, with Blender first and the app at the end (`AGENTS.md` sections 0 and 4). This skill adds the round loop, the token habits and the checkpoint script inside those steps. Where they differ, badge rules win: notes go in numbered candidate folders, a method change goes back to the plan, and two or three versions without clear gain means stop and show the owner (`AGENTS.md` section 6).
