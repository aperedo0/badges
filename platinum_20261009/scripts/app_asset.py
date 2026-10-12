"""Back up and temporarily preview Platinum through the existing Silver slot."""
from pathlib import Path
import subprocess,json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1];APP=Path('/Users/antonioperedo/Desktop/screen_time')
DS=APP/'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelSilver.dataset'
ASSET=DS/json.loads((DS/'Contents.json').read_text())['data'][0]['filename']
BEFORE=ROOT/'platinum/source/app_repo_before.json';BACKUP=ROOT/'platinum/source/app_asset_before.usdz';ACTIVE=ROOT/'platinum/source/active_trial.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=APP)
def snapshot():
 return {'head':git('rev-parse','HEAD').decode().strip(),'branch':git('branch','--show-current').decode().strip(),
  'status':git('status','--porcelain=v1','--untracked-files=all').decode(),
  'files':{p:sha(APP/p) for p in git('ls-files','-z').decode().split('\0') if p and (APP/p).is_file()}}
if sys.argv[1]=='stage':
 assert not ACTIVE.exists(),'Restore the active trial first.'
 trial=ROOT/'platinum'/sys.argv[2]
 if not BEFORE.exists():
  BEFORE.write_text(json.dumps(snapshot(),indent=2)+'\n');shutil.copy2(ASSET,BACKUP)
 assert sha(ASSET)==sha(BACKUP),'The asset changed externally.'
 ACTIVE.write_text(json.dumps({'trial':str(trial)}))
 try:shutil.copy2(trial/'badge.usdz',ASSET)
 except BaseException:
  shutil.copy2(BACKUP,ASSET);ACTIVE.unlink();raise
 print('Staged',trial)
else:
 trial=Path(json.loads(ACTIVE.read_text())['trial']) if ACTIVE.exists() else ROOT/'platinum/proof'
 if sha(ASSET)!=sha(BACKUP):shutil.copy2(BACKUP,ASSET)
 assert ASSET.read_bytes()==BACKUP.read_bytes()
 baseline=json.loads(BEFORE.read_text());after=snapshot();assert baseline==after,'The app repo changed externally.'
 trial.mkdir(exist_ok=True)
 (trial/'app_restore_verification.json').write_text(json.dumps({'restored_byte_for_byte':True,'all_tracked_file_hashes_unchanged':True,
  'tracked_files':len(after['files']),'head':after['head'],'branch':after['branch'],'status':after['status'],'asset_sha256':sha(ASSET)},indent=2)+'\n')
 ACTIVE.unlink(missing_ok=True);print('Restored original model; all',len(after['files']),'tracked files unchanged.')
