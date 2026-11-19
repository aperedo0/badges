"""Respect owner pacing, run status and any explicit deadline before an action."""
from pathlib import Path
import sys,json,time,datetime,math
R=Path(__file__).resolve().parent;s=json.loads((R/'schedule.json').read_text());now=time.time();needed=float(sys.argv[1]);action=sys.argv[2] if len(sys.argv)>2 else 'badge action'
continuous=s.get('pacing_mode')=='continuous'
limit=s.get('work_until_epoch')
remaining=float('inf') if continuous and limit is None else (limit or 0)-now
if s.get('deadline_epoch') is not None:remaining=min(remaining,s['deadline_epoch']-now)
badge=sys.argv[3] if len(sys.argv)>3 else s.get('active_badge')
held=badge in s.get('excluded_badges',[]) or s.get('badges',{}).get(badge,{}).get('status') in ['paused','cancelled','done']
allowed=s['status']=='active' and s['phase']=='work' and remaining>=needed and not held
report=dict(action=action,badge=badge,owner_hold=held,allowed=allowed,required_seconds=needed,remaining_seconds=None if math.isinf(remaining) else round(remaining,2),pacing_mode=s.get('pacing_mode','paced'),status=s['status'],phase=s['phase'],checked_utc=datetime.datetime.fromtimestamp(now,datetime.timezone.utc).isoformat());(R/'last_guard.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));sys.exit(0 if allowed else 75)
