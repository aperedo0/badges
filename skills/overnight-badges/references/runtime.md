# Run timer commands

Every command uses the absolute interpreter and script path. Set them once per shell:

```sh
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
OV=/Users/antonioperedo/Desktop/badges/skills/overnight-badges/scripts/overnight.py
RUN=/Users/antonioperedo/Desktop/badges/<run folder>
```

## Start

```sh
$PY $OV init --run-dir $RUN --thread "$CODEX_THREAD_ID" --badge crescent --badge mountain
$PY $OV watch --run-dir $RUN --start
$PY $OV status --run-dir $RUN
```

* Pacing is continuous; add `--pacing breaks` only when the owner asks for breaks. The workspace is the badges folder unless `--workspace` says otherwise.
* `--hours` sets a deadline and exists only for an explicit owner request.
* `init` refuses to overwrite an existing run.
* The watcher checks `codex queue --help` for `--thread`, `--message` and `--resume`, then finds this thread's rollout in the local state database (read only), or takes `--rollout` and `--codex`. Before calling recovery active, look at the watcher's process ID, `status` (watcher alive) and the first `recovery.jsonl` entry. A scoped `caffeinate` keeps the Mac awake while the watcher runs.

## Checkpoint

```sh
$PY $OV checkpoint --run-dir $RUN --badge crescent --blend /abs/crescent.blend --candidate /abs/candidate07 --next 'Fix the lower tip the review flagged'
$PY $OV checkpoint --run-dir $RUN --next 'Wait for the simulator capture' --busy-minutes 20
$PY $OV begin --run-dir $RUN          # breaks pacing only, after a break
```

A busy period is finite: up to 60 minutes in continuous pacing, never past the work block with breaks. A checkpoint on a blocked badge sets it back to working.

## Done, blocked, complete

```sh
$PY $OV done --run-dir $RUN --badge crescent \
  --blend /abs/crescent.blend --usdz /abs/candidate09/model.usdz --report /abs/REPORT.md \
  --comparison /abs/candidate09/review/far_same_height.png \
  --front /abs/candidate09/app/front.png --back /abs/candidate09/app/back.png \
  --side-left /abs/candidate09/app/side_left.png --side-right /abs/candidate09/app/side_right.png \
  --turns /abs/candidate09/review/turns.png --review /abs/candidate09/review/review.md \
  --reduction 'Merged 12 meshes into 7 with the same look'
$PY $OV block --run-dir $RUN --badge mountain --reason 'Three versions at 74 to 76, same top fixes' --evidence /abs/candidate06/review
$PY $OV complete --run-dir $RUN
```

* `done` needs every file present and nonempty, a review that says `SHIPPABLE: yes` with `CLOSENESS` of 90 or more (a scoped score such as "gem improvement: 92/100" does not count), and a reduction note.
* `complete` needs every badge done or blocked. Deadline expiry is never completion.

## Pause, cancel, resume

```sh
$PY $OV pause --run-dir $RUN
$PY $OV cancel --run-dir $RUN
$PY $OV resume --run-dir $RUN         # then: watch --start
```

Pause or cancel only at the owner's request. `resume` keeps any existing deadline; `resume --hours 2` only with the owner's permission. A cancelled or complete run cannot resume.

## Diagnostics and tests

```sh
$PY $OV watch --run-dir $RUN --once --dry-run
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest discover -s /Users/antonioperedo/Desktop/badges/skills/overnight-badges/scripts -p 'test_overnight.py'
```

A dry run reports the action it would take with no network probe and no queued message. The tests use temporary folders, fake time and a mocked queue; they never send a real message.
