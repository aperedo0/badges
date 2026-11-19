---
name: overnight-badges
description: Build reference matched 3D badges overnight in Blender and a separate simulator preview, with 30 minute work blocks, 20 minute breaks, saved checkpoints and 10 minute connection recovery checks. Use when the owner requests overnight or unattended badge building, or explicitly requests this paced workflow. Ordinary daytime badge edits do not need overnight pacing unless requested.
---

# Overnight badge building

Make the badges closely match the owner's references, including the small details, and leave the finished models visible in the separate simulator preview. Use the existing app lighting and approved material finish. Build real relief and finished backs in Blender, with changing metal reflections.

## Start or resume

1. Read the workspace `AGENTS.md`. For BestSpent, use `/Users/antonioperedo/Desktop/badges/AGENTS.md` and [the badge workflow](references/badge-workflow.md). The owner's request takes priority over general taste guidance. Preserve the app contract and approved files.
2. Identify the references, requested badges, source files, preview project and current thread. Reuse available local context before asking questions. Inspect each reference and verify live Blender with an actual viewport capture.
3. Create a unique run folder in the badge workspace with reference copies and numbered candidates. To recover, open the existing `schedule.json` and saved Blender files. Never initialize over saved work or rebuild a completed badge.
4. Work for 30 minutes, then rest for 20, repeating until every badge is finished. There is no overall time limit. Do not infer a deadline from an earlier request, a wake time assumption or a token window. Only an explicit new owner instruction can add a deadline or stop the run. Breaks reduce activity; they do not guarantee a token allowance or reset a usage limit.
5. Read [the runtime instructions](references/runtime.md), then set up and verify the local timer before leaving work unattended. An overnight run authorizes recovery messages into that same thread. Creating or editing this skill alone does not start a run or timer.

## Work for 30 minutes

Focus each block on one badge or one remaining finish issue. Finish early when everything is ready; do not fill time with extra candidates. Move to the next unfinished badge when appropriate.

Check runtime `status` before major modeling, render and build operations. Treat `work_until_epoch` as a real deadline. Do not start an operation expected to run beyond it. Save before long operations and declare a finite busy period, bounded by the work deadline. Do not renew a busy period to hide a failed connection.

After each substantial geometry or material improvement, save the complete `.blend`, candidate, latest evidence, unresolved details and exact next action. Refresh the checkpoint during active work, before switching badges, starting a build or entering a break. Model activity and a local timer heartbeat are different things.

Make a small detail checklist from the actual reference: silhouette, proportions, negative spaces, feather or leaf shapes, head and eye, flame curves, ribbon folds, gem cuts and settings, rim profile, background texture and color, metal hue and moving highlights. Fix the shapes rather than hiding mistakes behind glow, grain or lighting changes.

Small details are part of done, not optional polish. Do not silently simplify them away to finish overnight.

Develop the complete badge in Blender first. Use the simulator for final native lighting and rotation checks. Compare at the same badge size. Check front, back, both sides, every tip and long edge at 4x, reflection and a slow full turn. Confirm captures show the loaded 3D model before material fitting. Launch screens and flat fallback art are invalid measurements.

If two or three candidates fail to move clearly closer, stop guessing. Save a comparison and diagnose geometry, UVs, material response or measured app light. Continue independent useful work while an optional owner question is pending. Do not mark a poor match finished to meet a clock.

## Rest for 20 minutes

Save the scene and next action before the work deadline. `status` advances an expired work block into its scheduled break. During the break, start no modeling, generation, render, build, material experiment or new candidate.

Prefer the verified local timer to wake this same thread after the break, avoiding model work during rest. Only release the turn for a scheduled break after verifying the timer is alive and targets this exact thread. Otherwise use an available interruptible waiting mechanism with individual waits no longer than 60 seconds, and report that automatic waking is unavailable. Ending a turn alone does not resume work later.

When the break ends, run `begin` for the next 30 minute block. An early recovery wake must honor the remaining break. An interruption never resets a partially used work block or creates a fresh overall time window.

## Recover every 10 minutes

The local timer lives independently of model connectivity. It checks every 10 minutes, sleeps locally and can queue a short continuation using the installed CLI's verified `queue` command. It reads only this run and this thread's local activity. It does not launch another agent or switch accounts.

On a recovery wake, first inspect `schedule.json`, deadline, completion states, saved candidate and Blender scene. A paused, cancelled, completed or expired run does no badge work. Recovery is not an owner request to resume a paused run or extend its window. If work is running normally, do no duplicate work. If inside a break, wait. If the connection failed, resume the saved next action when tools respond. Completed badges stay completed.

The timer must use a single instance lock, avoid duplicate messages for unchanged activity, respect finite busy periods, and stop on completion, owner requested pause or cancellation, or a deadline the owner explicitly requested. With the normal unlimited run, it does not stop after five hours or any other elapsed duration. Retry failed queue delivery at the next 10 minute check. Authentication, approval, usage limit and sandbox failures need attention rather than repeated network retries.

A skill cannot repair internet service, restart a closed app or operate a sleeping Mac. Verify the queue transport before claiming recovery is active. Keep the Mac awake for the active run with a scoped local helper when available; stop it when the timer exits. If recovery is unavailable, retain resumable state and report that limitation rather than substituting an untested scheduler or UI typing hack.

## Finish

Only mark a badge done after saving and visually reviewing its final USDZ, editable Blender scene, report, same size comparison, native front, back, both sides and full turn evidence. Runtime `done` requires these artifact paths and a review assertion. Preserve the previous approved final.

When every badge is done, run `complete`. This creates this run's own completion marker and stops its timer. A connection failure, missing reference or long elapsed time is not completion. Preserve an honest next action for unfinished work and continue on the next work block until it is finished. Honor a deadline only if the owner explicitly adds one. Pause or cancel promptly when the owner asks.

Leave the final badge open in the separate preview and verify its selection survives reopening. Deliver short comparisons, final model and source paths, and any real uncertainty. Keep the production app exactly as found. Do not commit or push for the owner.
