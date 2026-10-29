# Local run timer

Read this before unattended work. The helper uses Python 3 and its standard library. Installing this skill does not start a run.

## Initialize and verify once

Create a unique run directory in the badge workspace. Use the exact current UUID from `CODEX_THREAD_ID` or verified session metadata. Do not use another chat or a guessed name. Use the skill's absolute script path in actual tool calls.

```sh
python3 scripts/overnight.py init --run-dir /absolute/run/folder --thread CURRENT_UUID --badge crescent --badge mountain --hours 5
python3 scripts/overnight.py watch --run-dir /absolute/run/folder --start
python3 scripts/overnight.py status --run-dir /absolute/run/folder
```

Defaults are 30 minutes of work, 20 minutes of break, 10 minute checks and a five hour window. Override duration when the owner supplies one. Initialization refuses to overwrite an existing run. Record reference paths and the precise next action in the checkpoint.

The watcher verifies the installed `codex queue --help`, then finds this thread's rollout through the local state database in read only mode. Alternatively pass a verified `--rollout` path and `--codex` executable. This command was present on the owner's CLI; verify it for every new run. No app settings, accounts, production files or database records are changed.

Inspect the process ID, live watcher status and first `recovery.jsonl` entry before calling recovery active. A scoped `caffeinate` process follows the watcher when available. Keep the computer and desktop app running for local file work. [Official local task guidance](https://learn.chatgpt.com/docs/automations).

## Checkpoint and pace

```sh
python3 scripts/overnight.py checkpoint --run-dir /absolute/run/folder --badge crescent --blend /absolute/candidate/crescent.blend --candidate /absolute/candidate --next 'Inspect the upper crescent in Blender'
python3 scripts/overnight.py checkpoint --run-dir /absolute/run/folder --next 'Inspect the completed native build' --busy-minutes 8
python3 scripts/overnight.py status --run-dir /absolute/run/folder
python3 scripts/overnight.py begin --run-dir /absolute/run/folder
```

Checkpoint after substantial changes, before long operations and before breaks. Busy periods are finite and cannot outlast the work block. `status` advances expired work into its scheduled break, then into `ready`. It never fabricates new work blocks while offline. `begin` starts the next block only after the break. An interruption preserves the existing work and overall deadlines.

## Done, pause or cancel

After actually reviewing all artifacts, mark a badge done. The helper checks their existence, while the agent is responsible for their content and visual quality.

```sh
python3 scripts/overnight.py done --run-dir /absolute/run/folder --badge crescent --reviewed --blend /absolute/final/crescent.blend --usdz /absolute/final/crescent.usdz --report /absolute/final/REPORT.md --comparison /absolute/final/comparison.jpg --front /absolute/front.png --back /absolute/back.png --left /absolute/left.png --right /absolute/right.png --turn /absolute/full_turn.mp4
python3 scripts/overnight.py complete --run-dir /absolute/run/folder
python3 scripts/overnight.py pause --run-dir /absolute/run/folder
python3 scripts/overnight.py cancel --run-dir /absolute/run/folder
```

Only pause or cancel at the owner's request. `complete` requires all badges done and creates this run's completion marker. Between bounded probe or queue operations, the watcher checks for shutdown every five seconds; connection checks happen every ten minutes. Deadline expiry stops retries and preserves progress without claiming completion. Extending a deadline requires a new owner instruction.

When the owner explicitly resumes paused work or resolves an account issue, use `resume`, then restart `watch --start`. Existing deadlines stay in place. Add `resume --hours 2` only if the owner authorizes that extension. A run whose badges were already reviewed and done can record completion after expiry without doing more badge work.

## Recovery and diagnostics

The watcher queues into the existing thread rather than starting another worker. It skips healthy activity, finite busy periods and unexpired breaks. It can wake the thread after a break or retry a stalled connection on the ten minute cadence. It remembers activity after an accepted message, preventing duplicates until there is new activity or a new failure. Failed delivery retries at the next check.

A responding website proves reachability, not model service health. Authentication, approval and usage errors require attention rather than repeated network retries. Do not print chat contents or credentials. If queue transport is unavailable, retain the checkpoint and report that automatic recovery was not activated.

```sh
python3 scripts/overnight.py watch --run-dir /absolute/run/folder --once --dry-run
python3 -m unittest discover -s scripts -p 'test_overnight.py' -v
```

Dry runs inspect state and report an action without internet probes or queued messages. Tests use temporary directories, fake time and mocked queue delivery. Creating this skill must not send a real recovery message as a side effect.
