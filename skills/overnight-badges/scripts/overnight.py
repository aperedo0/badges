#!/usr/bin/env python3
"""Saved badge pacing and bounded recovery into one existing Codex thread."""
import argparse
from contextlib import contextmanager
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid

WORK, BREAK, RETRY, STALE = 1800, 1200, 600, 900
ARTIFACTS = ('blend', 'usdz', 'report', 'comparison', 'front', 'back', 'left', 'right', 'turn')


def advance(state, now):
    if state['status'] != 'active':
        return
    if state['deadline_epoch'] is not None and now >= state['deadline_epoch']:
        state.update(status='window_expired', busy_until_epoch=0)
        return
    if state['phase'] == 'work' and now >= state['work_until_epoch']:
        state.update(phase='break', break_until_epoch=state['work_until_epoch'] + BREAK,
                     busy_until_epoch=0)
    if state['phase'] == 'break' and now >= state['break_until_epoch']:
        state['phase'] = 'ready'


class Run:
    def __init__(self, directory):
        self.root = Path(directory).expanduser().resolve()
        self.path = self.root / 'schedule.json'

    @contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / '.state.lock').open('a') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            yield

    def save(self, state):
        fd, name = tempfile.mkstemp(prefix='.schedule.', dir=self.root)
        try:
            with os.fdopen(fd, 'w') as handle:
                json.dump(state, handle, indent=2)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, self.path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def update(self, change=None, now=None):
        now = time.time() if now is None else now
        with self.locked():
            state = json.loads(self.path.read_text())
            before = json.dumps(state, sort_keys=True)
            advance(state, now)
            if change:
                change(state, now)
            if json.dumps(state, sort_keys=True) != before:
                self.save(state)
            return state

    def init(self, thread, badges, hours=None, now=None):
        now = time.time() if now is None else now
        thread = str(uuid.UUID(thread))
        if not badges or len(set(badges)) != len(badges) or (hours is not None and hours <= 0):
            raise ValueError('Supply unique badge names and a positive duration')
        with self.locked():
            if self.path.exists():
                raise ValueError('Run exists. Read its state and resume; do not initialize again')
            state = dict(version=1, thread_id=thread, workspace=str(Path.cwd()),
                         status='active', phase='work', block=1, started_epoch=now,
                         deadline_epoch=now + hours * 3600 if hours is not None else None,
                         work_until_epoch=min(now + WORK, now + hours * 3600) if hours is not None else now + WORK,
                         break_until_epoch=None, busy_until_epoch=0,
                         heartbeat_epoch=now, checkpoint_seq=0,
                         active_badge=badges[0], next_action='Inspect references and source files',
                         badges={name: {'status': 'pending'} for name in badges})
            self.save(state)
            return state

    def log(self, event, **fields):
        record = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      event=event, **fields)
        with (self.root / 'recovery.jsonl').open('a') as handle:
            handle.write(json.dumps(record) + '\n')


def active(state):
    if state['status'] != 'active':
        raise ValueError('Run is ' + state['status'])


def begin(state, now):
    active(state)
    if state['phase'] != 'ready':
        raise ValueError('The current work block or required break has not ended')
    state.update(phase='work', block=state['block'] + 1,
                 work_until_epoch=min(now + WORK, state['deadline_epoch']) if state['deadline_epoch'] is not None else now + WORK,
                 busy_until_epoch=0, heartbeat_epoch=now,
                 checkpoint_seq=state['checkpoint_seq'] + 1)


def checkpoint(state, now, badge=None, next_action=None, blend=None,
               candidate=None, reference=None, busy_minutes=None):
    active(state)
    if badge:
        item = state['badges'][badge]
        if item['status'] == 'done':
            raise ValueError('Completed badges must not be restarted')
        state['active_badge'] = badge
        item['status'] = 'working'
        for name, value in [('blend', blend), ('candidate', candidate), ('reference', reference)]:
            if value:
                item[name] = str(Path(value).expanduser().resolve())
    elif any([blend, candidate, reference]):
        raise ValueError('Artifact checkpoints require a badge name')
    if next_action:
        state['next_action'] = next_action
    if busy_minutes is not None:
        if state['phase'] != 'work' or busy_minutes < 0:
            raise ValueError('Busy periods are only allowed during a work block')
        state['busy_until_epoch'] = min(now + busy_minutes * 60, state['work_until_epoch'])
    state.update(heartbeat_epoch=now, checkpoint_seq=state['checkpoint_seq'] + 1)


def done(state, now, badge, files, reviewed):
    active(state)
    if state['badges'][badge]['status'] == 'done':
        raise ValueError('Badge is already reviewed and complete')
    if not reviewed:
        raise ValueError('Visually review the native front and complete turn first')
    paths = {key: str(Path(files[key]).expanduser().resolve()) for key in ARTIFACTS}
    if not all(Path(value).is_file() and Path(value).stat().st_size for value in paths.values()):
        raise ValueError('Every final artifact must exist and be nonempty')
    state['badges'][badge].update(status='done', artifacts=paths, reviewed=True)
    state.update(heartbeat_epoch=now, checkpoint_seq=state['checkpoint_seq'] + 1)


def complete(state, now):
    if state['status'] not in ['active', 'window_expired']:
        raise ValueError('Run is ' + state['status'])
    if not all(item['status'] == 'done' for item in state['badges'].values()):
        raise ValueError('Unfinished badges remain')
    state.update(status='complete', completed_epoch=now, busy_until_epoch=0,
                 next_action='Owner review in the separate badge preview')


def watcher_alive(root):
    with (Path(root) / '.watcher.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return False
        except BlockingIOError:
            return True


def locate_rollout(thread):
    home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
    for path in sorted(home.glob('state*.sqlite'), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as database:
                row = database.execute('select rollout_path from threads where id=?', (thread,)).fetchone()
            if row and Path(row[0]).is_file():
                return Path(row[0]).resolve()
        except sqlite3.Error:
            continue
    raise ValueError('Cannot locate this thread rollout. Supply its verified path with --rollout')


def queue_cli(supplied=None):
    candidate = supplied or str(Path.home() / '.local/bin/codex')
    if not Path(candidate).is_file():
        candidate = shutil.which('codex')
    if not candidate:
        raise ValueError('No installed Codex CLI found')
    result = subprocess.run([candidate, 'queue', '--help'], capture_output=True, text=True, timeout=15)
    help_text = result.stdout + result.stderr
    if result.returncode or '--thread' not in help_text or '--message' not in help_text:
        raise ValueError('This CLI does not provide the required queue transport')
    return str(Path(candidate).resolve())


def online():
    request = urllib.request.Request('https://developers.openai.com', method='HEAD')
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status < 500
    except urllib.error.HTTPError as error:
        return error.code < 500
    except (OSError, urllib.error.URLError):
        return False


def rollout_activity(path):
    stat = path.stat()
    failure = None
    with path.open('rb') as handle:
        handle.seek(max(0, stat.st_size - 250000))
        lines = handle.read().splitlines()
    for line in lines:
        try:
            row = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        if row.get('type') != 'event_msg':
            continue
        payload = row.get('payload', {})
        kind = str(payload.get('type', '')).lower()
        if kind in ['task_started', 'turn_started']:
            failure = None
        if 'error' not in kind and 'failed' not in kind:
            continue
        message = json.dumps(payload).lower()
        if any(word in message for word in ['unauthorized', 'authentication', 'quota', 'usage limit',
                                            'rate limit', 'approval', 'permission denied']):
            failure = 'attention'
        elif any(word in message for word in ['connect', 'network', 'stream', 'timeout', 'timed out', 'dns']):
            failure = 'connection'
    return dict(mtime_ns=stat.st_mtime_ns, modified_epoch=stat.st_mtime, failure=failure)


def basis(state, activity):
    return [state['phase'], state['block'], state['checkpoint_seq'], activity['mtime_ns']]


def decide(state, now, activity, network):
    if state['status'] != 'active':
        return 'stop'
    if activity['failure'] == 'attention':
        return 'attention'
    if state['phase'] == 'break':
        return 'break'
    if not network:
        return 'offline'
    if state.get('last_queue_basis') == basis(state, activity):
        return 'already_queued'
    if state['phase'] == 'ready':
        return 'queue'
    if now < state.get('busy_until_epoch', 0):
        return 'busy'
    recent = max(state['heartbeat_epoch'], activity['modified_epoch'])
    if activity['failure'] == 'connection' or now - recent >= STALE:
        return 'queue'
    if state.get('had_outage') and now - recent >= 60:
        return 'queue'
    return 'working'


def recovery_message(run):
    return ('Owner authorized overnight badge continuation. Read ' + str(run.path) +
            ' and its saved Blender checkpoints before acting. Honor the 30 minute work and '
            '20 minute break schedule. There is no overall time limit unless the owner explicitly set one. Resume the saved next action '
            'only if interrupted or the scheduled break has ended. Do no duplicate work if the '
            'run is healthy. Never restart completed badges. Stop this run timer when all badges '
            'are reviewed and complete. A paused, cancelled, expired or completed run must not '
            'do badge work. This message does not authorize resuming a paused run or extending '
            'a deadline. Do not bypass approvals, account limits or permissions.')


def check(run, rollout, cli, dry_run=False, now=None):
    clock = time.time if now is None else lambda: now
    now = clock()
    if dry_run:
        with run.locked():
            state = json.loads(run.path.read_text())
        advance(state, now)
    else:
        state = run.update(now=now)
    if state['status'] != 'active':
        return dict(action='stop', status=state['status'])
    activity = rollout_activity(rollout)
    network = True if dry_run or state['status'] != 'active' or state['phase'] == 'break' else online()
    action = decide(state, now, activity, network)
    if dry_run:
        return dict(action=action, dry_run=True, network='not_probed')
    if action == 'offline':
        run.update(lambda s, t: s.update(had_outage=True), now=now)
    elif action == 'attention':
        run.update(lambda s, t: s.update(status='needs_attention', next_action='Resolve the reported approval, account or usage issue'), now=now)
    elif action == 'queue':
        # Recheck under the state lock: a completion or new checkpoint may
        # have arrived during the network request.
        with run.locked():
            current = json.loads(run.path.read_text())
            queue_time = clock()
            advance(current, queue_time)
            fresh = rollout_activity(rollout)
            if decide(current, queue_time, fresh, True) != 'queue':
                run.save(current)
                return dict(action='changed_before_queue')
            result = subprocess.run([cli, 'queue', '--thread', current['thread_id'],
                                     '--message', recovery_message(run)], cwd=current['workspace'],
                                    capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                after = rollout_activity(rollout)
                current.update(last_queue_basis=basis(current, after), last_queue_epoch=queue_time, had_outage=False)
                run.save(current)
                run.log('recovery_queued', block=current['block'], phase=current['phase'])
            else:
                run.log('queue_failed', returncode=result.returncode)
    run.log('check', action=action)
    return dict(action=action)


def watch(run, rollout, cli):
    with (run.root / '.watcher.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        run.log('started', pid=os.getpid(), interval_seconds=RETRY)
        (run.root / 'watcher.json').write_text(json.dumps({'pid': os.getpid(), 'thread_id': run.update()['thread_id']}))
        caffeinate = shutil.which('caffeinate')
        awake = subprocess.Popen([caffeinate, '-i', '-w', str(os.getpid())],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if caffeinate else None
        try:
            next_check = 0
            while True:
                state = run.update()
                if state['status'] != 'active':
                    run.log('stopped', status=state['status'])
                    return
                now = time.time()
                if now >= next_check:
                    try:
                        if check(run, rollout, cli)['action'] in ['stop', 'attention']:
                            return
                    except Exception as error:
                        run.log('check_failed', error_type=type(error).__name__)
                    next_check = time.time() + RETRY
                # A scheduled break wake should not acquire an extra ten
                # minutes of delay just because the timer started later.
                if state['phase'] == 'break':
                    next_check = min(next_check, state['break_until_epoch'])
                time.sleep(min(5, max(.1, next_check - time.time())))
        finally:
            if awake:
                awake.terminate()
                awake.wait(timeout=5)


def start(run, rollout, cli):
    if watcher_alive(run.root):
        return dict(watcher_alive=True, **json.loads((run.root / 'watcher.json').read_text()))
    with (run.root / 'watcher.log').open('a') as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'watch',
                                    '--run-dir', str(run.root), '--rollout', str(rollout), '--codex', cli],
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(50):
        if process.poll() is not None:
            raise RuntimeError('Watcher exited before activation; inspect watcher.log')
        if watcher_alive(run.root) and (run.root / 'watcher.json').exists():
            metadata = json.loads((run.root / 'watcher.json').read_text())
            if metadata['pid'] == process.pid:
                return dict(watcher_alive=True, **metadata)
        time.sleep(.1)
    raise RuntimeError('Watcher activation not verified; inspect watcher.log')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['init', 'status', 'checkpoint', 'begin', 'done', 'complete', 'pause', 'cancel', 'resume', 'watch']:
        sub = commands.add_parser(name)
        sub.add_argument('--run-dir', required=True)
        if name == 'init':
            sub.add_argument('--thread', default=os.environ.get('CODEX_THREAD_ID'), required=not os.environ.get('CODEX_THREAD_ID'))
            sub.add_argument('--badge', action='append', required=True)
            sub.add_argument('--hours', type=float)
        if name == 'resume':
            sub.add_argument('--hours', type=float)
        if name == 'checkpoint':
            sub.add_argument('--badge')
            sub.add_argument('--next', dest='next_action')
            for field in ['blend', 'candidate', 'reference']:
                sub.add_argument('--' + field)
            sub.add_argument('--busy-minutes', type=float)
        if name == 'done':
            sub.add_argument('--badge', required=True)
            sub.add_argument('--reviewed', action='store_true')
            for field in ARTIFACTS:
                sub.add_argument('--' + field, required=True)
        if name == 'watch':
            sub.add_argument('--rollout', type=Path)
            sub.add_argument('--codex')
            mode = sub.add_mutually_exclusive_group()
            mode.add_argument('--start', action='store_true')
            mode.add_argument('--once', action='store_true')
            sub.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    run = Run(args.run_dir)
    try:
        if args.command == 'init':
            result = run.init(args.thread, args.badge, args.hours)
        elif args.command == 'watch':
            if args.dry_run and not args.once:
                raise ValueError('Dry run requires --once')
            state = run.update() if not args.dry_run else json.loads(run.path.read_text())
            if state['status'] != 'active':
                result = dict(action='stop', status=state['status'])
            else:
                rollout = args.rollout.resolve() if args.rollout else locate_rollout(state['thread_id'])
                cli = None if args.dry_run else queue_cli(args.codex)
                if args.once:
                    result = check(run, rollout, cli, args.dry_run)
                elif args.start:
                    result = start(run, rollout, cli)
                else:
                    watch(run, rollout, cli)
                    result = dict(action='stopped')
        else:
            def change(state, now):
                if args.command == 'begin':
                    begin(state, now)
                elif args.command == 'checkpoint':
                    checkpoint(state, now, **{name: getattr(args, name) for name in ['badge', 'next_action', 'blend', 'candidate', 'reference', 'busy_minutes']})
                elif args.command == 'done':
                    done(state, now, args.badge, {name: getattr(args, name) for name in ARTIFACTS}, args.reviewed)
                elif args.command == 'complete':
                    complete(state, now)
                elif args.command in ['pause', 'cancel']:
                    if state['status'] == 'complete':
                        raise ValueError('Completed run stays complete')
                    state.update(status='paused' if args.command == 'pause' else 'cancelled', busy_until_epoch=0)
                elif args.command == 'resume':
                    if state['status'] in ['complete', 'cancelled']:
                        raise ValueError('Do not resume completed or cancelled runs')
                    if args.hours is not None:
                        if args.hours <= 0:
                            raise ValueError('Duration must be positive')
                        state['deadline_epoch'] = now + args.hours * 3600
                    if state['deadline_epoch'] is not None and now >= state['deadline_epoch']:
                        raise ValueError('Window expired; an owner authorized extension is needed')
                    state['status'] = 'active'
                    advance(state, now)
            result = run.update(change)
            if args.command == 'complete':
                (run.root / 'COMPLETE').write_text('All badges reviewed and complete\n')
            if args.command == 'status':
                result['watcher_alive'] = watcher_alive(run.root)
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
