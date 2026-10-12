from pathlib import Path
import sys,json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];manifest=json.loads((ROOT/'manifest.json').read_text());repo=Path('/Users/antonioperedo/Desktop/screen_time')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
mode=sys.argv[1]
if mode=='stage':
 selection=json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv)>2 else json.loads((ROOT/'selection.json').read_text())
 for tier,num in selection.items():
  rec=manifest[tier];installed=Path(rec['asset']);backup=Path(rec['work'])/'source/installed.usdz'
  assert sha(installed)==rec['sha256'],(tier,'installed asset changed; do not overwrite')
  assert sha(backup)==rec['sha256'],(tier,'backup mismatch')
 for tier,num in selection.items():
  rec=manifest[tier];candidate=Path(num) if str(num).endswith('.usdz') else Path(rec['work'])/'candidates'/num/(tier+'_badge_mobile.usdz')
  assert candidate.exists(),candidate
  assert sha(candidate)==json.loads((candidate.parent/'build.json').read_text())['sha256']
  shutil.copyfile(candidate,rec['asset'])
 print('Temporarily staged',selection)
elif mode=='restore':
 for tier,rec in manifest.items():
  backup=Path(rec['work'])/'source/installed.usdz';assert sha(backup)==rec['sha256']
  if sha(rec['asset'])!=rec['sha256']:shutil.copyfile(backup,rec['asset'])
  assert sha(rec['asset'])==rec['sha256']
 print('All seven installed USDZ assets restored byte for byte.')
elif mode=='verify':
 before=json.loads((ROOT/'app_repo_before.json').read_text());print('snapshot keys',list(before))
 for key,args in [('head',['rev-parse','HEAD']),('branch',['branch','--show-current']),('status',['status','--porcelain'])]:
  value=subprocess.check_output(['git',*args],cwd=repo,text=True)
  assert value.strip()==before[key].strip(),(key,'repository state changed')
 for tier,rec in manifest.items():assert sha(rec['asset'])==rec['sha256'],tier
 # File checks include untracked files because the latest installed assets are untracked.
 records=before.get('files',before.get('hashes',{}))
 if isinstance(records,dict):
  changes=[]
  for name,digest in records.items():
   expected=digest['sha256'] if isinstance(digest,dict) else digest
   p=repo/name
   if not p.exists() or sha(p)!=expected:changes.append(name)
  assert not changes,changes
 report={'restored_assets':list(manifest),'snapshot_file_count':len(records),'repo_files_unchanged':True}
 (ROOT/'app_repo_verified.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
else:raise ValueError(mode)
