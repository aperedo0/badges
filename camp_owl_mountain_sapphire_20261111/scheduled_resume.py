"""Wait for the owner's exact start time, then watch this saved four badge run."""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import time

import overnight_runtime as runtime

ROOT = Path(__file__).resolve().parent


def authorized(state, progress, config):
    return (state['status'] == 'scheduled'
            and progress['status'] == 'scheduled'
            and state['thread_id'] == config['thread_id']
            and state.get('schedule_authorization') == config['authorization']
            and progress.get('schedule_authorization') == config['authorization']
            and state.get('owner_authorized_resume_epoch') == config['target_epoch']
            and progress.get('scheduled_resume_epoch') == config['target_epoch']
            and not state.get('owner_scheduled_authorization_consumed', False))


def activate(state, progress, config, now):
    if not authorized(state, progress, config):
        raise ValueError('Scheduled authorization was stopped or changed')
    if now < config['target_epoch']:
        raise ValueError('The owner requested start time has not arrived')
    if state['deadline_epoch'] is not None and now >= state['deadline_epoch']:
        raise ValueError('The saved deadline expired')
    state.update(status='active', phase='ready', block=0,
                 heartbeat_epoch=now, busy_until_epoch=0,
                 resumed_at_epoch=now, owner_scheduled_authorization_consumed=True)
    progress.update(status='working', phase='Scheduled overnight start reached',
                    resumed_at_epoch=now)
    return state, progress


def save_progress(progress):
    p = ROOT / 'progress.json'
    temporary = ROOT / '.progress.schedule.tmp'
    temporary.write_text(json.dumps(progress, indent=2) + '\n')
    os.replace(temporary, p)


def main():
    config = json.loads((ROOT / 'timer_config.json').read_text())
    run = runtime.Run(ROOT)
    with (ROOT / '.scheduled_start.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        progress = json.loads((ROOT / 'progress.json').read_text())
        if not authorized(run.update(), progress, config):
            return
        assert runtime.queue_cli(config['codex']) == config['codex']
        rollout = runtime.locate_rollout(config['thread_id'])
        assert str(rollout) == config['rollout']
        (ROOT / 'scheduled_start.json').write_text(json.dumps(dict(
            pid=os.getpid(), thread_id=config['thread_id'],
            authorization=config['authorization'], target_epoch=config['target_epoch']),
            indent=2) + '\n')
        run.log('owner_scheduled_wait_started', pid=os.getpid(),
                resume_epoch=config['target_epoch'])
        awake = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-w', str(os.getpid())],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (ROOT / 'scheduled_start.json').write_text(json.dumps(dict(
            pid=os.getpid(), caffeinate_pid=awake.pid,
            thread_id=config['thread_id'], authorization=config['authorization'],
            target_epoch=config['target_epoch']), indent=2) + '\n')
        try:
            while time.time() < config['target_epoch']:
                state = run.update()
                progress = json.loads((ROOT / 'progress.json').read_text())
                if not authorized(state, progress, config):
                    run.log('scheduled_wait_stopped', status=state['status'])
                    return
                time.sleep(min(5, max(.1, config['target_epoch'] - time.time())))

            def transition(state, now):
                progress = json.loads((ROOT / 'progress.json').read_text())
                _, progress = activate(state, progress, config, now)
                save_progress(progress)

            run.update(transition)
            run.log('owner_scheduled_resume_activated')
            runtime.watch(run, rollout, config['codex'])
        finally:
            awake.terminate()
            try:
                awake.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass


if __name__ == '__main__':
    main()
