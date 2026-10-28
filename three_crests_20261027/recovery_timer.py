"""Check this badge task every ten minutes and queue recovery only when stalled."""
from pathlib import Path
import os,sys,json,time,sqlite3,subprocess,urllib.request,datetime,fcntl

ROOT=Path(__file__).resolve().parent
THREAD='01a16b8e-9f81-76d1-8bd7-d0a939464547'
CODEX=str(Path.home()/'.local/bin/codex')
DEADLINE=1793188158 # Five hours after the requested badge work began.
def log(event,**values):
 with (ROOT/'recovery_timer.jsonl').open('a') as f:
  f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**values})+'\n')
def decision(phase,finished,stale,network_ok,had_outage,error):
 if finished:return 'stop'
 if phase=='break':return 'break'
 if not network_ok:return 'offline'
 if had_outage or error or stale>=900:return 'queue'
 return 'working'
def run():
 lock=(ROOT/'recovery_timer.lock').open('w')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:return
 (ROOT/'recovery_timer.pid').write_text(str(os.getpid()))
 c=sqlite3.connect('file:'+str(Path.home()/'.codex/state_5.sqlite')+'?mode=ro',uri=True)
 row=c.execute('select rollout_path from threads where id=?',(THREAD,)).fetchone();c.close()
 if not row:raise RuntimeError('This task could not be located.')
 rollout=Path(row[0]);outage=False;last_queued_mtime=0
 log('started',thread=THREAD,interval_seconds=600,expires_epoch=DEADLINE)
 while time.time()<DEADLINE:
  if (ROOT/'COMPLETE').exists():log('completed');return
  try:
   state=json.loads((ROOT/'schedule.json').read_text());phase=state.get('phase','work')
   if phase=='break' and time.time()>=state.get('break_until_epoch',0):phase='work'
   try:
    with urllib.request.urlopen(urllib.request.Request('https://developers.openai.com',method='HEAD'),timeout=15) as response:online=response.status<500
   except urllib.error.HTTPError as e:online=e.code<500
   except Exception:online=False
   mtime=rollout.stat().st_mtime;stale=time.time()-mtime;error=False
   with rollout.open('rb') as f:
    f.seek(max(0,rollout.stat().st_size-200000));lines=f.read().splitlines()
   for line in lines:
    try:d=json.loads(line)
    except Exception:continue
    if d.get('type')!='event_msg':continue
    p=d.get('payload',{});kind=p.get('type','').lower()
    if kind in ['task_started','turn_started']:error=False
    if 'error' in kind or 'failed' in kind:
     msg=str(p).lower()
     error=any(s in msg for s in ['connect','network','stream','timeout','timed out','dns'])
   action=decision(phase,False,stale,online,outage,error)
   log('check',action=action,stale_seconds=round(stale),online=online)
   if action=='offline':outage=True
   if action=='queue' and mtime>last_queued_mtime:
    prompt=('Automatic recovery check requested by the owner. If the three badge task was interrupted by a connection failure, continue from three_crests_20261027/schedule.json and the saved Blender files. Preserve the requested 30 minute work and 20 minute break schedule. Do not restart completed work. If work is already running normally, no extra work is needed. Stop this timer when all three badges are complete.')
    result=subprocess.run([CODEX,'queue','--thread',THREAD,'--message',prompt],cwd=ROOT.parent,capture_output=True,text=True,timeout=45)
    log('recovery_queued' if result.returncode==0 else 'queue_failed',returncode=result.returncode,detail=(result.stdout+result.stderr)[-1000:])
    if result.returncode==0:last_queued_mtime=rollout.stat().st_mtime;outage=False
  except Exception as e:log('check_error',message=str(e))
  time.sleep(600)
 log('expired')
if __name__=='__main__':
 if '--self-test' in sys.argv:
  assert decision('work',False,0,True,False,False)=='working'
  assert decision('break',False,2000,True,True,True)=='break'
  assert decision('work',False,0,False,False,False)=='offline'
  assert decision('work',False,0,True,True,False)=='queue'
  assert decision('work',True,2000,True,True,True)=='stop'
  print('Recovery decisions passed. Queue transport was checked against a nonexistent task.')
 elif '--start' in sys.argv:
  with (ROOT/'recovery_timer_output.log').open('a') as f:
   p=subprocess.Popen([sys.executable,str(Path(__file__).resolve())],stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
  subprocess.Popen(['/usr/bin/caffeinate','-i','-w',str(p.pid)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
  print('Recovery timer started, PID',p.pid)
 else:run()
