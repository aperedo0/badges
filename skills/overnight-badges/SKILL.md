---
name: overnight-badges
description: Codex only. Keep unattended badge work going overnight with saved run state, checkpoints, a done gate that reads the fresh review, blocked badges, crash and connection recovery into the same Codex thread, and optional pacing (continuous by default). The badge work itself runs through badge-plan, badge-plan-review, badge-build and badge-fresh-review. Use when the owner asks for overnight or unattended badge building. In Claude Code there is no recovery wake; use only the run state and checkpoints.
---

# Overnight badge building

This skill is a wrapper. It keeps a run alive and honest while nobody watches; it does not say how to build a badge. The badge work follows the normal skills, in order, for every badge:

1. **badge-plan**, then **badge-plan-review** until approved (skip only if the owner says so for this run).
2. **badge-build** in the open Blender, Blender first, the simulator only for versions ready to judge.
3. **badge-fresh-review** after every version, with its caps and its "go back when worse" rule.
4. **badge-quality's final piece reduction pass** (`badge-quality/references/finish-optimization.md`): build with as many pieces as the design needs first; once the look is final, keep that version as the baseline and look for fewer rendering pieces with the exact same look. Keep a version that cannot be reduced without changing its look, and say why.

A badge is **done** only when its latest `review.md` says `SHIPPABLE: yes` with `CLOSENESS` of 90 or more and the reduction pass is recorded. The `done` command checks both.

## Paths

* Workspace: `/Users/antonioperedo/Desktop/badges` (read its `AGENTS.md` first; the owner's word beats it).
* Production app: `/Users/antonioperedo/Desktop/screen_time`, never touched by a run.
* Preview app: `emerald_trophy_20261025/preview/ScreenTime.xcodeproj`, scheme `ScreenTime-UIOnly`; verify with XcodeBuildMCP session defaults.
* Blender: the open window, community bridge on port 9876 (`ruby_heart_claude_20261107/tools/blender_link.py`), Blender's official MCP plugin on 9877 for API lookup. If Blender closed, reopen it with `forge_tide_compass_20261103/start_blender.py`.
* Script: `/Users/antonioperedo/Desktop/badges/skills/overnight-badges/scripts/overnight.py`, run with `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`. Commands are in [the runtime notes](references/runtime.md).

## Start or resume

1. Identify the mockups, the badges, the current thread (`CODEX_THREAD_ID`) and any earlier run folder. Check the live Blender with an actual viewport capture.
2. A new run gets its own folder in the workspace and `init`. An existing run is resumed from its `schedule.json` and saved Blender files; never initialize over saved work and never restart a done badge.
3. **Pacing:** continuous by default (the owner removed scheduled breaks on November 12, 2026). Use `init --pacing breaks` (30 minute work blocks, 20 minute breaks) only when the owner asks for breaks; ask only if their request is unclear.
4. **No deadline** unless the owner sets one in a new instruction. Never infer one from an earlier request, a wake time or a token window.
5. Start the watcher (`watch --start`) and confirm it before leaving the run unattended. Creating or editing this skill never starts a run.

## While working

* Check `status` before long operations. Declare a finite busy period for a long build (`checkpoint --busy-minutes`); never renew one to hide a failure.
* Checkpoint after every real improvement, before switching badges and before a long operation: the saved `.blend`, the candidate folder, and the exact next action.
* **Stuck badge:** after three versions with no clear gain, or when a cap in badge-fresh-review is reached, run `block --badge NAME --reason ... --evidence <comparison or review folder>` and move to the next badge. The owner decides in the morning.
* **Unsaved changes in the open Blender** (`bpy.data.is_dirty` when you are about to load or switch files): someone worked there by hand and nobody can answer at night. Do not load or switch files; block that badge with the reason and continue with another badge that needs no file switch, or stop.
* With breaks: during a break start no modeling, render, build or new candidate; when it ends run `begin`.

## Recovery

The watcher checks every 10 minutes, independent of the model connection. It queues one short continuation into this same thread (`codex queue --thread ... --resume`) when the run is stalled for 15 minutes, after a connection error, or when a break has ended. It never starts another agent or switches accounts, and it stops on completion, pause, cancel or an owner deadline. Account, approval and usage limit errors need the owner and are not retried.

On a recovery wake, read `schedule.json` first. A paused, cancelled, complete or expired run does no badge work. If work is already running, do nothing. Otherwise resume the saved next action.

A skill cannot repair the network, reopen a closed app on a sleeping Mac or keep a thread alive without the queue transport. If `codex queue --help` lacks `--thread`, `--message` or `--resume`, the watcher refuses to start: keep the checkpoints and report that recovery is not active.

## Finish

1. Mark each finished badge `done` with its final files, its `review.md` and the reduction note. Keep the previous approved final.
2. When every badge is done or blocked, run `complete`; it writes the run's `COMPLETE` marker and stops the watcher.
3. Leave the final badge open in the preview. Report each badge: done (with its last review score) or blocked (with the reason and pictures). Keep the production app exactly as found; never commit or push for the owner.
