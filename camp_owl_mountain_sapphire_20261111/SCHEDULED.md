# Scheduled overnight continuation

The owner requested two hours of waiting, then continuation with the overnight
skill on November 12, 2026. This explicitly replaces the earlier pause for
these four badges only. No badge work is authorized before 02:44:07 AM Pacific
on November 12, 2026, which is 10:44:07 UTC. The exact epoch is 1794480247.

schedule.json is authoritative for pacing. It has no overall deadline. Start
30 minute work blocks and take 20 minute breaks until all four badges are
reviewed and complete. Connection recovery checks run every ten minutes,
without bypassing account limits, approvals or permissions. The older royal
badge run stays paused. Planning skills remain skipped at the owner's request.

The local helper scheduled_resume.py holds a single instance lock, checks
the saved authorization while waiting and honors a new pause or cancellation.
At the start time it consumes this authorization once, activates the saved run
as ready and hands off to overnight_runtime.py. The copied skill runtime uses
the verified Codex queue transport with its resume option and the exact
existing owner thread. It creates no new agent or task. Keep Codex and the
Mac open; the helper prevents idle sleep while it lives.

Do not do badge work for a transport test message. Before any scheduled or
recovery continuation, read schedule.json, progress.json, PAUSED.md and the
saved candidate files. Stop if paused, cancelled, completed or expired. If
another worker is healthy, do no duplicate work. If still scheduled or in a
break, do no modeling, render, export or build. If active and ready, run begin
with overnight_runtime.py before working. Check status and the finite work
deadline before every major operation. Save checkpoints before long operations
and breaks. Never renew busy periods to conceal a failure.

At the first actual work block verify free disk space, the complete saved
Blender files and an actual live Blender viewport capture. No model was
rebuilt to set up this timer. PAUSED.md records the appearance work and
technical tests still needed. Some Blender files predate diagnostic array
edits, so load the intended candidate explicitly rather than restarting it.

Use the absolute script path in commands, for example:

```sh
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 /Users/antonioperedo/Desktop/badges/camp_owl_mountain_sapphire_20261111/overnight_runtime.py status --run-dir /Users/antonioperedo/Desktop/badges/camp_owl_mountain_sapphire_20261111
```

Replace status with begin only when phase is ready, or checkpoint when saving
work, with the corresponding arguments documented by the overnight skill.
Native clean finish checks, fresh reference reviews and lossless batching
remain part of completion. Mark done only with all real reviewed artifacts,
then complete when all four are finished so this run's watcher stops.

The installed skill's runtime was copied without changing its pacing or
quality requirements. The local copy only adds the queue resume option to
ensure the existing thread is woken. Five isolated scheduling tests cover an
early wake, changed authorization, pause or cancellation, one time activation
and the full work and break boundaries. Timer and transport evidence are in
scheduler_verification.json, transport_test.json and recovery.jsonl.
