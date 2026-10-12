"""Temporary Silver-slot preview. Always restore after build/install, even on failure.
Only the existing USDZ file may be changed. No app source changes.
"""
from pathlib import Path
import subprocess,json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
APP=Path('/Users/antonioperedo/Desktop/screen_time')
ASSET=APP/'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelSilver.dataset/silver_badge_mobile.usdz'
BACKUP=ROOT/'source/app_asset_before.usdz'
BEFORE=ROOT/'source/app_repo_before.json'
ACTIVE=ROOT/'source/active_trial.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=APP)
def snapshot():
    paths=git('ls-files','-z').decode().split('\0')
    return dict(head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),status=git('status','--porcelain=v1','--untracked-files=all').decode(),files={p:sha(APP/p) for p in paths if p and (APP/p).is_file()})
action=sys.argv[1]
if action=='stage':
    assert not ACTIVE.exists(),'A test is already staged. Restore it first.'
    trial=ROOT/sys.argv[2]
    if not BEFORE.exists():
        BEFORE.write_text(json.dumps(snapshot(),indent=2)+'\n');shutil.copy2(ASSET,BACKUP)
    assert sha(ASSET)==sha(BACKUP),'Dataset was changed externally; do not overwrite it.'
    ACTIVE.write_text(json.dumps({'trial':str(trial)}))
    shutil.copy2(trial/'copper_flame.usdz',ASSET)
    print('STAGED',trial,sha(ASSET))
elif action=='restore':
    trial=Path(json.loads(ACTIVE.read_text())['trial']) if ACTIVE.exists() else ROOT
    if sha(ASSET)!=sha(BACKUP):shutil.copy2(BACKUP,ASSET)
    assert ASSET.read_bytes()==BACKUP.read_bytes()
    baseline=json.loads(BEFORE.read_text());after=snapshot()
    assert baseline==after,'App repository changed; inspect before/after snapshots.'
    (trial/'app_restore_verification.json').write_text(json.dumps({'restored_byte_for_byte':True,'all_tracked_file_hashes_unchanged':True,'tracked_files':len(after['files']),'head':after['head'],'branch':after['branch'],'status':after['status'],'silver_sha256':sha(ASSET)},indent=2)+'\n')
    ACTIVE.unlink(missing_ok=True)
    print('RESTORED: byte-for-byte asset and entire tracked repository verified',len(after['files']),'files')
