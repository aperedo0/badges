"""Remove only the reviewed obsolete capture and cache paths recorded in this audit."""
import hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
AUDIT=Path(__file__).resolve().parent

def run():
 plan=json.loads((AUDIT/'deletion_plan.json').read_text())
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
 before=shutil.disk_usage(ROOT).free;removed=[];skipped=[]
 for item in plan:
  rel=Path(item['path']);p=ROOT/rel
  if rel.is_absolute() or '..' in rel.parts or any(v in rel.parts for v in ('.git','.codex','.agents','.aws')):raise RuntimeError('Protected path '+str(rel))
  if not p.exists():continue
  if p.is_symlink():raise RuntimeError('Unexpected symbolic link '+str(rel))
  s=p.stat()
  if s.st_size!=item['bytes'] or abs(s.st_mtime-item['mtime'])>.001:
   skipped.append({'path':str(rel),'reason':'Changed since inventory'});continue
  with p.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
  p.unlink()
  removed.append({**item,'sha256':digest,'tracked':str(rel) in tracked})
 after=shutil.disk_usage(ROOT).free
 report={'time':time.time(),'before_free_bytes':before,'after_free_bytes':after,'observed_free_delta':after-before,'removed_count':len(removed),'logical_removed_bytes':sum(r['bytes'] for r in removed),'removed':removed,'skipped':skipped}
 (AUDIT/'removed_files.json').write_text(json.dumps(report,indent=2)+'\n')
 # Exact tracked deletions plus this chat's chest work. Do not stage unrelated changes.
 paths=['treasure_chest_20261113','cleanup_20261114']
 paths += sorted(r['path'] for r in removed if r['tracked'] and not r['path'].startswith('treasure_chest_20261113/'))
 (AUDIT/'commit_paths.txt').write_text('\n'.join(paths)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('removed','skipped')}))
 print('Skipped',skipped)
 print('Tracked deletion paths',sum(r['tracked'] for r in removed))
if __name__=='__main__':run()
