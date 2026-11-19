"""Owner authorized one scheduled restart of this existing badge task."""
from pathlib import Path
import fcntl,importlib.util,json,os,subprocess,time
R=Path(__file__).resolve().parent
P=Path('/Users/antonioperedo/.agents/skills/overnight-badges/scripts/overnight.py')
spec=importlib.util.spec_from_file_location('badge_overnight',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
config=json.loads((R/'timer_config.json').read_text());run=m.Run(R)
with (R/'.scheduled_start.lock').open('a') as lock:
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise SystemExit(0)
 state=run.update()
 if state['status']!='scheduled' or state.get('owner_authorized_resume_epoch')!=config['target_epoch']:raise SystemExit(0)
 (R/'scheduled_start.json').write_text(json.dumps(dict(pid=os.getpid(),thread_id=config['thread_id'],target_epoch=config['target_epoch']),indent=2)+'\n')
 run.log('owner_scheduled_wait_started',pid=os.getpid(),resume_epoch=config['target_epoch'])
 awake=subprocess.Popen(['/usr/bin/caffeinate','-i','-w',str(os.getpid())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  while time.time()<config['target_epoch']:
   state=run.update()
   if state['status']!='scheduled' or state.get('owner_authorized_resume_epoch')!=config['target_epoch']:
    run.log('scheduled_wait_stopped',status=state['status']);raise SystemExit(0)
   time.sleep(min(5,max(.1,config['target_epoch']-time.time())))
  def authorized_restart(s,now):
   if s['status']!='scheduled' or s.get('owner_authorized_resume_epoch')!=config['target_epoch']:raise ValueError('Scheduled authorization changed')
   if now<config['target_epoch']:raise ValueError('Owner requested start time has not arrived')
   s.update(status='active',phase='ready',block=0,heartbeat_epoch=now,busy_until_epoch=0,resumed_at_epoch=now,owner_scheduled_authorization_consumed=True)
  run.update(authorized_restart);run.log('owner_scheduled_resume_activated')
  m.watch(run,Path(config['rollout']),config['codex'])
 finally:
  awake.terminate()
  try:awake.wait(timeout=5)
  except subprocess.TimeoutExpired:pass
