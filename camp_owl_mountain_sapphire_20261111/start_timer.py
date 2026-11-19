"""Verify delivery and start just this owner's delayed continuation timer."""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import sys
import time

import overnight_runtime as runtime
from scheduled_resume import authorized

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT / 'timer_config.json').read_text())
run = runtime.Run(ROOT)
progress = json.loads((ROOT / 'progress.json').read_text())
assert authorized(run.update(), progress, config)
assert runtime.queue_cli(config['codex']) == config['codex']
assert str(runtime.locate_rollout(config['thread_id'])) == config['rollout']
with (ROOT / '.start_controller.lock').open('a') as controller:
    fcntl.flock(controller, fcntl.LOCK_EX | fcntl.LOCK_NB)
    with (ROOT / '.scheduled_start.lock').open('a') as probe:
        try:
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('The saved timer is already running; no duplicate started')
        fcntl.flock(probe, fcntl.LOCK_UN)
    message = ('Timer delivery test only. Do no badge work. The owner requested '
               'resuming the four campfire, owl, mountain and sapphire badges at '
               '2:44 AM America/Los_Angeles on November 12, 2026. Verify only the '
               'scheduled timer in ' + str(ROOT / 'schedule.json') +
               ', preserve its start time, finish timer setup if needed, and end this turn.')
    delivery = subprocess.run([config['codex'], 'queue', '--thread', config['thread_id'],
                              '--resume', '--message', message],
                             cwd=ROOT.parent, capture_output=True, text=True, timeout=20)
    (ROOT / 'transport_test.json').write_text(json.dumps(dict(
        epoch=time.time(), thread_id=config['thread_id'], returncode=delivery.returncode,
        accepted=delivery.returncode == 0,
        actual_delivery_observed=False,
        output=delivery.stdout.strip(), error=delivery.stderr.strip()), indent=2) + '\n')
    if delivery.returncode:
        raise SystemExit('Queue transport failed; timer was not started')
    with (ROOT / 'scheduled_resume.log').open('a') as log:
        process = subprocess.Popen([sys.executable, str(ROOT / 'scheduled_resume.py')],
            cwd=ROOT.parent, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
            start_new_session=True)
    for _ in range(70):
        if process.poll() is not None:
            raise RuntimeError('Scheduled helper exited; inspect scheduled_resume.log')
        metadata_path = ROOT / 'scheduled_start.json'
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            if (metadata.get('pid') == process.pid and metadata.get('caffeinate_pid')
                    and metadata.get('authorization') == config['authorization']):
                with (ROOT / '.scheduled_start.lock').open('a') as probe:
                    try:
                        fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(probe, fcntl.LOCK_UN)
                    except BlockingIOError:
                        os.kill(process.pid, 0)
                        os.kill(metadata['caffeinate_pid'], 0)
                        proof = dict(timer_alive=True, single_instance_lock_verified=True,
                            caffeinate_alive=True, target_epoch=config['target_epoch'],
                            thread_id=config['thread_id'], pid=process.pid,
                            queue_transport_accepted=True,
                            badge_work_started=False, checked_epoch=time.time())
                        (ROOT / 'scheduler_verification.json').write_text(
                            json.dumps(proof, indent=2) + '\n')
                        print(json.dumps(proof, indent=2), flush=True)
                        raise SystemExit(0)
        time.sleep(.1)
    raise RuntimeError('The delayed timer could not be verified')
