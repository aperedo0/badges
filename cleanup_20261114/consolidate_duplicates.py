"""Share identical asset storage using independent APFS clones, preserving file paths."""
import ctypes, hashlib, json, os, shutil, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REPORT=Path(__file__).resolve().parent
lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
clone=lib.clonefile
clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int]
clone.restype=ctypes.c_int
def sha(p):
 with p.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
def run(manifest):
 groups=json.loads(Path(manifest).read_text())
 before=shutil.disk_usage(ROOT).free
 results=[];skipped=[]
 for group in groups:
  paths=[ROOT/p for p in group['paths'] if (ROOT/p).is_file()]
  if len(paths)<2:continue
  src=paths[0]
  if sha(src)!=group['sha256']:
   skipped.append({'path':str(src.relative_to(ROOT)),'reason':'Source changed since inventory'});continue
  for dst in paths[1:]:
   if sha(dst)!=group['sha256']:
    skipped.append({'path':str(dst.relative_to(ROOT)),'reason':'Target changed since inventory'});continue
   # A clone has its own inode. Later writes to either file remain independent.
   if src.stat().st_ino==dst.stat().st_ino:continue
   tmp=dst.with_name(dst.name+'.cleanup_clone_tmp')
   if tmp.exists():raise RuntimeError('Unexpected temporary file '+str(tmp))
   if clone(os.fsencode(src),os.fsencode(tmp),0):
    error=ctypes.get_errno()
    skipped.append({'path':str(dst.relative_to(ROOT)),'reason':os.strerror(error)})
    continue
   try:
    shutil.copystat(dst,tmp)
    if sha(tmp)!=group['sha256'] or sha(dst)!=group['sha256']:raise RuntimeError('Concurrent change or clone verification failure')
    os.replace(tmp,dst)
    results.append({'path':str(dst.relative_to(ROOT)),'shares_with':str(src.relative_to(ROOT)),'bytes':group['bytes'],'sha256':group['sha256']})
   finally:
    if tmp.exists():tmp.unlink()
 after=shutil.disk_usage(ROOT).free
 report={'time':time.time(),'before_free_bytes':before,'after_free_bytes':after,'observed_free_delta':after-before,'consolidated_files':len(results),'logical_duplicate_bytes':sum(r['bytes'] for r in results),'files':results,'skipped':skipped}
 (REPORT/'duplicate_consolidation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('files','skipped')}))
 print('Skipped',len(skipped))
if __name__=='__main__':
 import sys
 run(sys.argv[1])
