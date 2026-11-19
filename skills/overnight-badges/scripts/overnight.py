#!/usr/bin/env python3
"""Run state, checkpoints, optional pacing and bounded recovery into one existing Codex thread.

Pacing is continuous by default (the owner removed scheduled breaks on November 12, 2026); pass
`init --pacing breaks` only when the owner asks for 30 minute work blocks with 20 minute breaks.
"""
import argparse
from contextlib import contextmanager
import datetime
import fcntl
import json
import os
import re
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
CONTINUOUS_BUSY = 3600          # longest finite busy period in continuous pacing
WORKSPACE = '/Users/antonioperedo/Desktop/badges'
# What the badge tools actually write: app_try.py (front, side_left, back, side_right),
# review_pack.py (review/turns.png) and badge-fresh-review (review.md next to the pictures).
ARTIFACTS = ('blend', 'usdz', 'report', 'comparison', 'front', 'back', 'side_left', 'side_right', 'turns', 'review')
FINISHED = ('done', 'blocked')
PASS_SCORE = 90


def review_verdict(text):
    """Read a badge-fresh-review report: (shippable, closeness or None).

    Shippable needs an explicit 'SHIPPABLE: yes' and no 'SHIPPABLE: no' or 'not (yet) shippable'.
    Closeness is the first number after the word closeness ('CLOSENESS: 66', 'closeness80/100');
    scoped scores such as 'gem improvement: 92/100' never count as closeness.
    """
    low = text.lower()
    yes = re.search(r'shippable\s*:\s*yes\b', low) is not None
    no = re.search(r'shippable\s*:\s*no\b', low) or re.search(r'not\s+(yet\s+)?shippable', low)
    score = re.search(r'closeness\s*:?\s*(\d{1,3})(?:\s*/\s*100)?', low)
    return bool(yes and not no), (int(score.group(1)) if score else None)


def advance(state, now):
    if state['status'] != 'active':
        return
    if state['deadline_epoch'] is not None and now >= state['deadline_epoch']:
        state.update(status='window_expired', busy_until_epoch=0)
        return
    if state.get('pacing', 'breaks') == 'continuous':
        if state['phase'] != 'work':
            state['phase'] = 'work'
        if now >= state['work_until_epoch']:
            # roll into the next block with no break; the block number keeps recovery dedupe per block
            state.update(block=state['block'] + 1, work_until_epoch=now + WORK)
            if state['deadline_epoch'] is not None:
                state['work_until_epoch'] = min(state['work_until_epoch'], state['deadline_epoch'])
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

    def init(self, thread, badges, hours=None, now=None, pacing='continuous', workspace=WORKSPACE):
        now = time.time() if now is None else now
        thread = str(uuid.UUID(thread))
        if not badges or len(set(badges)) != len(badges) or (hours is not None and hours <= 0):
            raise ValueError('Supply unique badge names and a positive duration')
        if pacing not in ('continuous', 'breaks'):
            raise ValueError('Pacing is continuous or breaks')
        with self.locked():
            if self.path.exists():
                raise ValueError('Run exists. Read its state and resume; do not initialize again')
            state = dict(version=2, thread_id=thread, workspace=str(Path(workspace).resolve()), pacing=pacing,
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
        item.pop('blocked_reason', None)
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
        limit = now + CONTINUOUS_BUSY if state.get('pacing') == 'continuous' else state['work_until_epoch']
        state['busy_until_epoch'] = min(now + busy_minutes * 60, limit)
    state.update(heartbeat_epoch=now, checkpoint_seq=state['checkpoint_seq'] + 1)


def done(state, now, badge, files, reduction):
    """Mark a badge done: every artifact exists, its fresh review says shippable with closeness of
    90 or more, and the final piece reduction pass is recorded (what was reduced, or why not)."""
    active(state)
    if state['badges'][badge]['status'] == 'done':
        raise ValueError('Badge is already reviewed and complete')
    paths = {key: str(Path(files[key]).expanduser().resolve()) for key in ARTIFACTS}
    if not all(Path(value).is_file() and Path(value).stat().st_size for value in paths.values()):
        raise ValueError('Every final artifact must exist and be nonempty')
    shippable, score = review_verdict(Path(paths['review']).read_text(errors='replace'))
    if not shippable or score is None or score < PASS_SCORE:
        raise ValueError('The fresh review must say SHIPPABLE: yes with CLOSENESS of at least %d (found shippable=%s, closeness=%s)'
                         % (PASS_SCORE, shippable, score))
    if not (reduction or '').strip():
        raise ValueError('Record the piece reduction pass: what was reduced with the same look, or why the version was kept')
    state['badges'][badge].update(status='done', artifacts=paths, reviewed=True, closeness=score,
                                  reduction=reduction.strip())
    state.update(heartbeat_epoch=now, checkpoint_seq=state['checkpoint_seq'] + 1)


def block(state, now, badge, reason, evidence=None):
    """Stop working on a badge that is stuck, with the reason and its pictures, so the run can end."""
    active(state)
    item = state['badges'][badge]
    if item['status'] == 'done':
        raise ValueError('Completed badges stay completed')
    if not (reason or '').strip():
        raise ValueError('Give the reason the badge is blocked')
    item.update(status='blocked', blocked_reason=reason.strip())
    if evidence:
        item['blocked_evidence'] = str(Path(evidence).expanduser().resolve())
    state.update(heartbeat_epoch=now, checkpoint_seq=state['checkpoint_seq'] + 1)


def pause(state, now):
    if state['status'] == 'complete':
        raise ValueError('Completed run stays complete')
    state.update(status='paused', busy_until_epoch=0)


def cancel(state, now):
    if state['status'] == 'complete':
        raise ValueError('Completed run stays complete')
    state.update(status='cancelled', busy_until_epoch=0)


def resume(state, now, hours=None):
    if state['status'] in ['complete', 'cancelled']:
        raise ValueError('Do not resume completed or cancelled runs')
    if hours is not None:
        if hours <= 0:
            raise ValueError('Duration must be positive')
        state['deadline_epoch'] = now + hours * 3600
    if state['deadline_epoch'] is not None and now >= state['deadline_epoch']:
        raise ValueError('Window expired; an owner authorized extension is needed')
    state['status'] = 'active'
    advance(state, now)


def complete(state, now):
    if state['status'] not in ['active', 'window_expired']:
        raise ValueError('Run is ' + state['status'])
    if not all(item['status'] in FINISHED for item in state['badges'].values()):
        raise ValueError('Unfinished badges remain (each must be done or blocked)')
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
    if result.returncode or any(flag not in help_text for flag in ('--thread', '--message', '--resume')):
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
    if state['phase'] == 'ready':
        # The woken thread writes to its rollout, so activity changes after every queue. Dedupe the
        # ready wake on the block alone and queue again only after the rollout has been idle for STALE.
        if state.get('last_queue_ready') == state['block']:
            recent = max(state.get('last_queue_epoch', 0), activity['modified_epoch'])
            if now - recent < STALE:
                return 'already_queued'
        return 'queue'
    if state.get('last_queue_basis') == basis(state, activity):
        return 'already_queued'
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
            ' and its saved Blender checkpoints before acting. Follow its pacing (continuous, or '
            'the 30 minute work and 20 minute break schedule when pacing is breaks). There is no '
            'overall time limit unless the owner explicitly set one. Resume the saved next action '
            'only if interrupted or the scheduled break has ended. Do no duplicate work if the '
            'run is healthy. Never restart completed badges. Stop this run timer when every badge '
            'is done or blocked. A paused, cancelled, expired or completed run must not '
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
                                     '--resume', '--message', recovery_message(run)], cwd=current['workspace'],
                                    capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                after = rollout_activity(rollout)
                current.update(last_queue_basis=basis(current, after), last_queue_epoch=queue_time, had_outage=False)
                if current['phase'] == 'ready':
                    current['last_queue_ready'] = current['block']
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
    for name in ['init', 'status', 'checkpoint', 'begin', 'done', 'block', 'complete', 'pause', 'cancel', 'resume', 'watch']:
        sub = commands.add_parser(name)
        sub.add_argument('--run-dir', required=True)
        if name == 'init':
            sub.add_argument('--thread', default=os.environ.get('CODEX_THREAD_ID'), required=not os.environ.get('CODEX_THREAD_ID'))
            sub.add_argument('--badge', action='append', required=True)
            sub.add_argument('--hours', type=float)
            sub.add_argument('--pacing', choices=['continuous', 'breaks'], default='continuous')
            sub.add_argument('--workspace', default=WORKSPACE)
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
            sub.add_argument('--reduction', required=True,
                             help='the piece reduction pass: what was reduced with the same look, or why the version was kept')
            for field in ARTIFACTS:
                sub.add_argument('--' + field.replace('_', '-'), dest=field, required=True)
        if name == 'block':
            sub.add_argument('--badge', required=True)
            sub.add_argument('--reason', required=True)
            sub.add_argument('--evidence', help='comparison picture or review folder that shows why')
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
            result = run.init(args.thread, args.badge, args.hours, pacing=args.pacing, workspace=args.workspace)
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
                    done(state, now, args.badge, {name: getattr(args, name) for name in ARTIFACTS}, args.reduction)
                elif args.command == 'block':
                    block(state, now, args.badge, args.reason, args.evidence)
                elif args.command == 'complete':
                    complete(state, now)
                elif args.command == 'pause':
                    pause(state, now)
                elif args.command == 'cancel':
                    cancel(state, now)
                elif args.command == 'resume':
                    resume(state, now, args.hours)
            result = run.update(change)
            if args.command == 'complete':
                blocked = [n for n, item in result['badges'].items() if item['status'] == 'blocked']
                (run.root / 'COMPLETE').write_text('Every badge done or blocked' +
                                                   (' (blocked: ' + ', '.join(blocked) + ')' if blocked else '') + '\n')
            if args.command == 'status':
                result['watcher_alive'] = watcher_alive(run.root)
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
